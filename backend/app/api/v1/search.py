"""
Document Search and Category API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.search import (
    DocumentCategoryCreate,
    DocumentCategoryUpdate,
    DocumentCategoryResponse,
    DocumentCategoryTreeResponse,
    DocumentCategoryListResponse,
    SearchRequest,
    SearchResponse,
    SearchHistoryListResponse,
    SavedSearchCreate,
    SavedSearchResponse,
    SavedSearchListResponse,
)
from ...crud import search as crud_search

router = APIRouter()


# ============ Document Category Endpoints ============

@router.post("/categories", response_model=DocumentCategoryResponse, status_code=201)
def create_category(
    category: DocumentCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new document category"""
    return crud_search.create_category(db, category.model_dump(), current_user.id)


@router.get("/categories", response_model=DocumentCategoryListResponse)
def get_categories(
    parent_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get document categories"""
    skip = (page - 1) * page_size
    categories, total = crud_search.get_categories(db, parent_id, is_active, skip, page_size)
    return DocumentCategoryListResponse(total=total, items=categories)


@router.get("/categories/tree", response_model=list)
def get_category_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get category tree (hierarchical)"""
    return crud_search.get_category_tree(db)


@router.get("/categories/{category_id}", response_model=DocumentCategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get category by ID"""
    category = crud_search.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=DocumentCategoryResponse)
def update_category(
    category_id: int,
    category_update: DocumentCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a category"""
    category = crud_search.update_category(db, category_id, category_update.model_dump(exclude_unset=True))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a category"""
    success = crud_search.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return None


# ============ Search Endpoints ============

@router.post("/search", response_model=SearchResponse)
def advanced_search(
    search_request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Perform advanced search"""
    result = crud_search.advanced_search(db, search_request, current_user.id)
    
    # Add to search history
    if search_request.query:
        crud_search.add_search_history(
            db, current_user.id, search_request.query, result["total"],
            search_request.model_dump()
        )
    
    return SearchResponse(**result)


@router.get("/search/history", response_model=SearchHistoryListResponse)
def get_search_history(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's search history"""
    history = crud_search.get_search_history(db, current_user.id, limit)
    return SearchHistoryListResponse(total=len(history), items=history)


@router.delete("/search/history", status_code=204)
def clear_search_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clear user's search history"""
    crud_search.clear_search_history(db, current_user.id)
    return None


# ============ Saved Search Endpoints ============

@router.post("/search/saved", response_model=SavedSearchResponse, status_code=201)
def create_saved_search(
    saved_search: SavedSearchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a saved search"""
    return crud_search.create_saved_search(
        db, current_user.id, saved_search.name, saved_search.query,
        {"filters": saved_search.filters}
    )


@router.get("/search/saved", response_model=SavedSearchListResponse)
def get_saved_searches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's saved searches"""
    saves = crud_search.get_saved_searches(db, current_user.id)
    return SavedSearchListResponse(total=len(saves), items=saves)


@router.delete("/search/saved/{saved_search_id}", status_code=204)
def delete_saved_search(
    saved_search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a saved search"""
    success = crud_search.delete_saved_search(db, saved_search_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Saved search not found")
    return None