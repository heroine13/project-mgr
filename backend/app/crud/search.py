"""
Document Search and Category CRUD Operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json
import time

from ..models.search import DocumentCategory, SearchHistory, SavedSearch
from ..models.document import Document
from ..models.project import Project
from ..models.task import Task
from ..schemas.search import SearchRequest, SearchResultItem


# ============ Document Category CRUD ============

def create_category(db: Session, category_data: dict, user_id: int) -> DocumentCategory:
    """Create a new document category"""
    db_category = DocumentCategory(
        name=category_data["name"],
        description=category_data.get("description"),
        parent_id=category_data.get("parent_id"),
        color=category_data.get("color"),
        icon=category_data.get("icon"),
        display_order=category_data.get("display_order", 0),
        is_active=category_data.get("is_active", True),
        created_by=user_id,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_category(db: Session, category_id: int) -> Optional[DocumentCategory]:
    """Get category by ID"""
    return db.query(DocumentCategory).filter(DocumentCategory.id == category_id).first()


def get_categories(
    db: Session,
    parent_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[DocumentCategory], int]:
    """Get categories with filters"""
    query = db.query(DocumentCategory)
    
    if parent_id is not None:
        query = query.filter(DocumentCategory.parent_id == parent_id)
    if is_active is not None:
        query = query.filter(DocumentCategory.is_active == is_active)
    
    total = query.count()
    categories = query.order_by(DocumentCategory.display_order, DocumentCategory.name).offset(skip).limit(limit).all()
    return categories, total


def get_category_tree(db: Session) -> List[Dict]:
    """Get category tree (hierarchical structure)"""
    # Get root categories (no parent)
    root_categories = (
        db.query(DocumentCategory)
        .filter(DocumentCategory.parent_id == None, DocumentCategory.is_active == True)
        .order_by(DocumentCategory.display_order, DocumentCategory.name)
        .all()
    )
    
    def build_tree(category: DocumentCategory) -> Dict:
        children = (
            db.query(DocumentCategory)
            .filter(DocumentCategory.parent_id == category.id, DocumentCategory.is_active == True)
            .order_by(DocumentCategory.display_order, DocumentCategory.name)
            .all()
        )
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "color": category.color,
            "icon": category.icon,
            "display_order": category.display_order,
            "children": [build_tree(c) for c in children]
        }
    
    return [build_tree(c) for c in root_categories]


def update_category(db: Session, category_id: int, category_data: dict) -> Optional[DocumentCategory]:
    """Update a category"""
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    for field, value in category_data.items():
        if value is not None:
            setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category"""
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    # Check if category has documents
    doc_count = db.query(Document).filter(Document.category_id == category_id).count()
    if doc_count > 0:
        # Instead of deleting, mark as inactive
        db_category.is_active = False
        db.commit()
        return True
    
    db.delete(db_category)
    db.commit()
    return True


# ============ Search Functionality ============

def advanced_search(
    db: Session,
    search_request: SearchRequest,
    user_id: int,
) -> Dict:
    """Perform advanced search across documents, projects, and tasks"""
    start_time = time.time()
    
    results = []
    facets = {
        "categories": {},
        "projects": {},
        "tags": {},
        "date_ranges": {}
    }
    
    # Search in Documents
    doc_query = db.query(Document).filter(Document.id.isnot(None))
    
    if search_request.query:
        doc_query = doc_query.filter(
            or_(
                Document.name.ilike(f"%{search_request.query}%"),
                Document.description.ilike(f"%{search_request.query}%"),
            )
        )
    
    if search_request.category_id:
        doc_query = doc_query.filter(Document.category_id == search_request.category_id)
    
    if search_request.project_id:
        doc_query = doc_query.filter(Document.project_id == search_request.project_id)
    
    if search_request.created_by:
        doc_query = doc_query.filter(Document.created_by == search_request.created_by)
    
    if search_request.date_from:
        doc_query = doc_query.filter(Document.created_at >= search_request.date_from)
    
    if search_request.date_to:
        doc_query = doc_query.filter(Document.created_at <= search_request.date_to)
    
    # Get total count
    total_documents = doc_query.count()
    
    # Apply sorting
    if search_request.sort_by == "date":
        sort_column = Document.created_at
    elif search_request.sort_by == "name":
        sort_column = Document.name
    else:
        sort_column = Document.id
    
    if search_request.sort_order == "asc":
        doc_query = doc_query.order_by(sort_column.asc())
    else:
        doc_query = doc_query.order_by(sort_column.desc())
    
    # Apply pagination
    skip = (search_request.page - 1) * search_request.page_size
    documents = doc_query.offset(skip).limit(search_request.page_size).all()
    
    # Build results
    for doc in documents:
        # Highlight matching text
        highlight = None
        if search_request.query:
            if doc.description and search_request.query.lower() in doc.description.lower():
                highlight = doc.description[:200] + "..."
        
        # Get category name
        category_name = None
        if doc.category_id:
            cat = get_category(db, doc.category_id)
            category_name = cat.name if cat else None
            # Update facets
            facets["categories"][category_name] = facets["categories"].get(category_name, 0) + 1
        
        # Parse tags
        tags = doc.tags.split(",") if doc.tags else []
        
        results.append(SearchResultItem(
            id=doc.id,
            title=doc.name,
            description=doc.description,
            category=category_name,
            project_id=doc.project_id,
            tags=tags,
            created_at=doc.created_at,
            highlight=highlight,
        ))
        
        # Update project facets
        if doc.project_id:
            facets["projects"][str(doc.project_id)] = facets["projects"].get(str(doc.project_id), 0) + 1
    
    # Calculate total
    total = total_documents
    
    # Calculate time taken
    took_ms = int((time.time() - start_time) * 1000)
    
    return {
        "total": total,
        "items": results,
        "page": search_request.page,
        "page_size": search_request.page_size,
        "took_ms": took_ms,
        "facets": facets,
    }


# ============ Search History CRUD ============

def add_search_history(
    db: Session,
    user_id: int,
    query: str,
    result_count: int,
    filters: Optional[dict] = None,
) -> SearchHistory:
    """Add search to history"""
    db_history = SearchHistory(
        user_id=user_id,
        query=query,
        filters=json.dumps(filters) if filters else None,
        result_count=result_count,
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


def get_search_history(
    db: Session,
    user_id: int,
    limit: int = 10,
) -> List[SearchHistory]:
    """Get user's search history"""
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == user_id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
        .all()
    )


def clear_search_history(db: Session, user_id: int) -> bool:
    """Clear user's search history"""
    db.query(SearchHistory).filter(SearchHistory.user_id == user_id).delete()
    db.commit()
    return True


# ============ Saved Search CRUD ============

def create_saved_search(
    db: Session,
    user_id: int,
    name: str,
    query: str,
    filters: Optional[dict] = None,
) -> SavedSearch:
    """Create a saved search"""
    db_saved = SavedSearch(
        user_id=user_id,
        name=name,
        query=query,
        filters=json.dumps(filters) if filters else None,
    )
    db.add(db_saved)
    db.commit()
    db.refresh(db_saved)
    return db_saved


def get_saved_searches(
    db: Session,
    user_id: int,
) -> List[SavedSearch]:
    """Get user's saved searches"""
    return (
        db.query(SavedSearch)
        .filter(SavedSearch.user_id == user_id)
        .order_by(SavedSearch.created_at.desc())
        .all()
    )


def delete_saved_search(db: Session, saved_search_id: int, user_id: int) -> bool:
    """Delete a saved search"""
    db_saved = (
        db.query(SavedSearch)
        .filter(SavedSearch.id == saved_search_id, SavedSearch.user_id == user_id)
        .first()
    )
    if not db_saved:
        return False
    
    db.delete(db_saved)
    db.commit()
    return True