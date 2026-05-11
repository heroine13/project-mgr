"""
Document Version Control API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentWithVersions,
    DocumentVersionCreate,
    DocumentVersionResponse,
    DocumentVersionListResponse,
    DocumentCommentCreate,
    DocumentCommentUpdate,
    DocumentCommentResponse,
    DocumentCommentListResponse,
)
from ...crud import document as crud_document

router = APIRouter()


# ============ Document Endpoints ============

@router.post("/", response_model=DocumentResponse, status_code=201)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new document"""
    return crud_document.create_document(db, document, current_user.id)


@router.get("/", response_model=DocumentListResponse)
def get_documents(
    project_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get documents with filters"""
    skip = (page - 1) * page_size
    documents, total = crud_document.get_documents(
        db, project_id, category, search, skip, page_size
    )
    return DocumentListResponse(
        total=total,
        items=documents,
        page=page,
        page_size=page_size,
    )


@router.get("/{document_id}", response_model=DocumentWithVersions)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get document with all versions"""
    document = crud_document.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a document"""
    document = crud_document.update_document(db, document_id, document_update)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document"""
    success = crud_document.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return None


# ============ Document Version Endpoints ============

@router.post("/{document_id}/versions", response_model=DocumentVersionResponse, status_code=201)
def create_version(
    document_id: int,
    version: DocumentVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new version for a document"""
    try:
        db_version = crud_document.create_version(db, document_id, version, current_user.id)
        return db_version
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{document_id}/versions", response_model=DocumentVersionListResponse)
def get_versions(
    document_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all versions of a document"""
    skip = (page - 1) * page_size
    versions, total = crud_document.get_document_versions(db, document_id, skip, page_size)
    return DocumentVersionListResponse(total=total, items=versions)


@router.get("/{document_id}/versions/current", response_model=DocumentVersionResponse)
def get_current_version(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current version of a document"""
    version = crud_document.get_current_version(db, document_id)
    if not version:
        raise HTTPException(status_code=404, detail="No version found")
    return version


@router.post("/{document_id}/versions/{version_id}/rollback", response_model=DocumentVersionResponse)
def rollback_version(
    document_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rollback to a specific version"""
    try:
        version = crud_document.rollback_version(db, document_id, version_id)
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        return version
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{document_id}/versions/{version_id}", status_code=204)
def delete_version(
    document_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a version"""
    try:
        success = crud_document.delete_version(db, version_id)
        if not success:
            raise HTTPException(status_code=404, detail="Version not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return None


# ============ Document Comment Endpoints ============

@router.post("/{document_id}/comments", response_model=DocumentCommentResponse, status_code=201)
def create_comment(
    document_id: int,
    version_id: int,
    comment: DocumentCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a comment on a document version"""
    # Verify document and version exist
    document = crud_document.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    version = crud_document.get_version(db, version_id)
    if not version or version.document_id != document_id:
        raise HTTPException(status_code=404, detail="Version not found")
    
    db_comment = crud_document.create_comment(
        db, document_id, version_id, current_user.id, comment.content, comment.line_number
    )
    return db_comment


@router.get("/{document_id}/comments", response_model=DocumentCommentListResponse)
def get_comments(
    document_id: int,
    version_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comments for a document"""
    skip = (page - 1) * page_size
    comments, total = crud_document.get_comments(
        db, document_id, version_id, skip, page_size
    )
    return DocumentCommentListResponse(total=total, items=comments)


@router.put("/{document_id}/comments/{comment_id}", response_model=DocumentCommentResponse)
def update_comment(
    document_id: int,
    comment_id: int,
    comment_update: DocumentCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a comment"""
    comment = crud_document.update_comment(db, comment_id, comment_update.content)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/{document_id}/comments/{comment_id}", status_code=204)
def delete_comment(
    document_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment"""
    success = crud_document.delete_comment(db, comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return None