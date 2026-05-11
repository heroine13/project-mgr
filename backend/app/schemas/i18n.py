"""
Internationalization Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ============ Language Schemas ============

class LanguageBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    native_name: Optional[str] = None
    is_default: bool = False
    is_active: bool = True
    display_order: int = 0


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    native_name: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class LanguageResponse(LanguageBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LanguageListResponse(BaseModel):
    total: int
    items: List[LanguageResponse]


# ============ Translation Key Schemas ============

class TranslationKeyBase(BaseModel):
    key: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    module: Optional[str] = None


class TranslationKeyCreate(TranslationKeyBase):
    pass


class TranslationKeyUpdate(BaseModel):
    description: Optional[str] = None
    module: Optional[str] = None
    is_approved: Optional[bool] = None


class TranslationKeyResponse(TranslationKeyBase):
    id: int
    is_approved: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TranslationKeyListResponse(BaseModel):
    total: int
    items: List[TranslationKeyResponse]
    page: int
    page_size: int


# ============ Translation Schemas ============

class TranslationBase(BaseModel):
    value: str = Field(..., min_length=1)


class TranslationCreate(TranslationBase):
    language_code: str
    key: str


class TranslationUpdate(BaseModel):
    value: str = Field(..., min_length=1)
    is_reviewed: Optional[bool] = None


class TranslationResponse(TranslationBase):
    id: int
    key_id: int
    language_id: int
    is_machine_translated: bool
    is_reviewed: bool
    created_by: Optional[int]
    reviewed_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TranslationListResponse(BaseModel):
    total: int
    items: List[TranslationResponse]


# ============ Translation with All Languages ============

class TranslationWithAllLanguages(BaseModel):
    key_id: int
    key: str
    description: Optional[str]
    module: Optional[str]
    translations: Dict[str, str]  # {language_code: value}
    is_approved: bool


class TranslationExportResponse(BaseModel):
    """Export translations in specific format"""
    format: str  # json, csv
    languages: List[str]
    data: dict


# ============ Untranslated Keys Response ============

class UntranslatedKeyResponse(BaseModel):
    key_id: int
    key: str
    missing_languages: List[str]


class UntranslatedKeysResponse(BaseModel):
    total: int
    items: List[UntranslatedKeyResponse]