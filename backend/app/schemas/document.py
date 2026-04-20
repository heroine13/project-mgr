"""
Document Version Control Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ Document Schemas ============

class DocumentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    project_id: Optional[int] = None
    is_public: bool = False


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    project_id: Optional[int] = None
    is_public: Optional[bool] = None


class DocumentResponse(DocumentBase):
    id: int
    current_version: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    total: int
    items: List[DocumentResponse]
    page: int
    page_size: int


# ============ Document Version Schemas ============

class DocumentVersionBase(BaseModel):
    version_notes: Optional[str] = None


class DocumentVersionCreate(DocumentVersionBase):
    filename: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class DocumentVersionResponse(DocumentVersionBase):
    id: int
    document_id: int
    version_number: int
    filename: str
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    is_initial: bool
    is_current: bool
    isarchived: bool
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentVersionListResponse(BaseModel):
    total: int
    items: List[DocumentVersionResponse]


# ============ Document with Versions ============

class DocumentWithVersions(DocumentResponse):
    versions: List[DocumentVersionResponse] = []
    
    class Config:
        from_attributes = True


# ============ Document Comment Schemas ============

class DocumentCommentBase(BaseModel):
    content: str = Field(..., min_length=1)
    line_number: Optional[int] = None


class DocumentCommentCreate(DocumentCommentBase):
    pass


class DocumentCommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class DocumentCommentResponse(DocumentCommentBase):
    id: int
    document_id: int
    version_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentCommentListResponse(BaseModel):
    total: int
    items: List[DocumentCommentResponse]


# ============ Document Compare Schemas ============

class DocumentCompareRequest(BaseModel):
    version_id_1: int
    version_id_2: int


class DocumentCompareResponse(BaseModel):
    document_id: int
    version_1: DocumentVersionResponse
    version_2: DocumentVersionResponse
    changes: dict  # Could contain line-by-line diff