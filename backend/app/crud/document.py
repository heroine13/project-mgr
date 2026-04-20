"""
Document Version Control CRUD Operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from datetime import datetime

from ..models.document import Document, DocumentVersion, DocumentComment
from ..schemas.document import DocumentCreate, DocumentUpdate, DocumentVersionCreate


# ============ Document CRUD ============

def create_document(db: Session, document: DocumentCreate, user_id: int) -> Document:
    """Create a new document"""
    db_document = Document(
        name=document.name,
        description=document.description,
        category=document.category,
        tags=document.tags,
        project_id=document.project_id,
        is_public=document.is_public,
        created_by=user_id,
        current_version=1,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """Get document by ID"""
    return db.query(Document).filter(Document.id == document_id).first()


def get_documents(
    db: Session,
    project_id: Optional[int] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[Document], int]:
    """Get documents with filters"""
    query = db.query(Document)
    
    if project_id:
        query = query.filter(Document.project_id == project_id)
    if category:
        query = query.filter(Document.category == category)
    if search:
        query = query.filter(
            or_(
                Document.name.ilike(f"%{search}%"),
                Document.description.ilike(f"%{search}%"),
            )
        )
    
    total = query.count()
    documents = (
        query
        .order_by(Document.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return documents, total


def update_document(
    db: Session,
    document_id: int,
    document_update: DocumentUpdate,
) -> Optional[Document]:
    """Update a document"""
    db_document = get_document(db, document_id)
    if not db_document:
        return None
    
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db.commit()
    db.refresh(db_document)
    return db_document


def delete_document(db: Session, document_id: int) -> bool:
    """Delete a document"""
    db_document = get_document(db, document_id)
    if not db_document:
        return False
    
    db.delete(db_document)
    db.commit()
    return True


# ============ Document Version CRUD ============

def create_version(
    db: Session,
    document_id: int,
    version: DocumentVersionCreate,
    user_id: int,
) -> DocumentVersion:
    """Create a new version for a document"""
    db_document = get_document(db, document_id)
    if not db_document:
        raise ValueError("Document not found")
    
    # Get next version number
    latest_version = (
        db.query(func.max(DocumentVersion.version_number))
        .filter(DocumentVersion.document_id == document_id)
        .scalar()
    ) or 0
    
    new_version_number = latest_version + 1
    
    # Mark old current version as not current
    db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id,
        DocumentVersion.is_current == True,
    ).update({"is_current": False})
    
    # Create new version
    db_version = DocumentVersion(
        document_id=document_id,
        version_number=new_version_number,
        filename=version.filename,
        file_path=version.file_path,
        file_size=version.file_size,
        mime_type=version.mime_type,
        version_notes=version.version_notes,
        is_initial=(new_version_number == 1),
        is_current=True,
        created_by=user_id,
    )
    
    # Update document current version
    db_document.current_version = new_version_number
    
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version


def get_version(db: Session, version_id: int) -> Optional[DocumentVersion]:
    """Get version by ID"""
    return db.query(DocumentVersion).filter(DocumentVersion.id == version_id).first()


def get_document_versions(
    db: Session,
    document_id: int,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[DocumentVersion], int]:
    """Get all versions of a document"""
    query = db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id)
    total = query.count()
    versions = (
        query
        .order_by(DocumentVersion.version_number.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return versions, total


def get_current_version(db: Session, document_id: int) -> Optional[DocumentVersion]:
    """Get current version of a document"""
    return (
        db.query(DocumentVersion)
        .filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.is_current == True,
        )
        .first()
    )


def rollback_version(db: Session, document_id: int, version_id: int) -> Optional[DocumentVersion]:
    """Rollback to a specific version"""
    db_version = get_version(db, version_id)
    if not db_version or db_version.document_id != document_id:
        return None
    
    # Mark all versions as not current
    db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id,
    ).update({"is_current": False})
    
    # Mark target version as current
    db_version.is_current = True
    
    # Update document current version
    db_document = get_document(db, document_id)
    if db_document:
        db_document.current_version = db_version.version_number
    
    db.commit()
    db.refresh(db_version)
    return db_version


def delete_version(db: Session, version_id: int) -> bool:
    """Delete a version"""
    db_version = get_version(db, version_id)
    if not db_version:
        return False
    
    # Cannot delete current version if it's the only one
    if db_version.is_current:
        other_versions = (
            db.query(DocumentVersion)
            .filter(
                DocumentVersion.document_id == db_version.document_id,
                DocumentVersion.id != version_id,
            )
            .count()
        )
        if other_versions == 0:
            raise ValueError("Cannot delete the only version")
    
    db.delete(db_version)
    db.commit()
    return True


# ============ Document Comment CRUD ============

def create_comment(
    db: Session,
    document_id: int,
    version_id: int,
    user_id: int,
    content: str,
    line_number: Optional[int] = None,
) -> DocumentComment:
    """Create a comment on a document version"""
    db_comment = DocumentComment(
        document_id=document_id,
        version_id=version_id,
        user_id=user_id,
        content=content,
        line_number=line_number,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments(
    db: Session,
    document_id: Optional[int] = None,
    version_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[DocumentComment], int]:
    """Get comments for a document or version"""
    query = db.query(DocumentComment)
    
    if document_id:
        query = query.filter(DocumentComment.document_id == document_id)
    if version_id:
        query = query.filter(DocumentComment.version_id == version_id)
    
    total = query.count()
    comments = (
        query
        .order_by(DocumentComment.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return comments, total


def update_comment(
    db: Session,
    comment_id: int,
    content: str,
) -> Optional[DocumentComment]:
    """Update a comment"""
    db_comment = db.query(DocumentComment).filter(DocumentComment.id == comment_id).first()
    if not db_comment:
        return None
    
    db_comment.content = content
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, comment_id: int) -> bool:
    """Delete a comment"""
    db_comment = db.query(DocumentComment).filter(DocumentComment.id == comment_id).first()
    if not db_comment:
        return False
    
    db.delete(db_comment)
    db.commit()
    return True


# ============ Utility Functions ============

def get_document_categories(db: Session) -> List[str]:
    """Get all document categories"""
    categories = (
        db.query(Document.category)
        .filter(Document.category.isnot(None))
        .distinct()
        .all()
    )
    return [c[0] for c in categories if c[0]]