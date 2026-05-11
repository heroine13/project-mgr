"""
Document Search and Category Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ Document Category Schemas ============

class DocumentCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: int = 0
    is_active: bool = True


class DocumentCategoryCreate(DocumentCategoryBase):
    pass


class DocumentCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class DocumentCategoryResponse(DocumentCategoryBase):
    id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentCategoryTreeResponse(DocumentCategoryResponse):
    """Category with children for tree view"""
    children: List[DocumentCategoryResponse] = []


class DocumentCategoryListResponse(BaseModel):
    total: int
    items: List[DocumentCategoryResponse]


# ============ Search Schemas ============

class SearchRequest(BaseModel):
    """Advanced search request"""
    query: str = ""
    category_id: Optional[int] = None
    project_id: Optional[int] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    file_type: Optional[str] = None
    created_by: Optional[int] = None
    
    # Pagination
    page: int = 1
    page_size: int = 20
    
    # Sorting
    sort_by: str = "relevance"  # relevance, date, name
    sort_order: str = "desc"  # asc, desc


class SearchResultItem(BaseModel):
    """Single search result item"""
    id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    project_id: Optional[int]
    tags: List[str]
    created_at: datetime
    highlight: Optional[str] = None  # Search term highlighting


class SearchResponse(BaseModel):
    """Search results response"""
    total: int
    items: List[SearchResultItem]
    page: int
    page_size: int
    took_ms: int  # Search time in milliseconds
    facets: dict  # Search facets for filtering


# ============ Search History Schemas ============

class SearchHistoryResponse(BaseModel):
    id: int
    user_id: int
    query: str
    result_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SearchHistoryListResponse(BaseModel):
    total: int
    items: List[SearchHistoryResponse]


# ============ Saved Search Schemas ============

class SavedSearchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    query: str = Field(..., min_length=1)
    filters: Optional[str] = None


class SavedSearchCreate(SavedSearchBase):
    pass


class SavedSearchResponse(SavedSearchBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SavedSearchListResponse(BaseModel):
    total: int
    items: List[SavedSearchResponse]


# ============ Document with Category ============

class DocumentWithCategory(BaseModel):
    """Document with category information"""
    id: int
    name: str
    description: Optional[str]
    category_id: Optional[int]
    category_name: Optional[str]
    project_id: Optional[int]
    tags: List[str]
    current_version: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True