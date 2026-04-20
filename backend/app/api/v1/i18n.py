"""
Internationalization Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.i18n import (
    LanguageCreate,
    LanguageUpdate,
    LanguageResponse,
    LanguageListResponse,
    TranslationKeyCreate,
    TranslationKeyUpdate,
    TranslationKeyResponse,
    TranslationKeyListResponse,
    TranslationCreate,
    TranslationUpdate,
    TranslationResponse,
    TranslationListResponse,
    TranslationWithAllLanguages,
    UntranslatedKeysResponse,
)
from ...crud import i18n as crud_i18n

router = APIRouter()


# ============ Language Endpoints ============

@router.post("/languages", response_model=LanguageResponse, status_code=201)
def create_language(
    language: LanguageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new language"""
    try:
        return crud_i18n.create_language(db, language)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/languages", response_model=LanguageListResponse)
def get_languages(
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get languages"""
    skip = (page - 1) * page_size
    languages, total = crud_i18n.get_languages(db, is_active, skip, page_size)
    return LanguageListResponse(total=total, items=languages)


@router.get("/languages/{language_id}", response_model=LanguageResponse)
def get_language(
    language_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get language by ID"""
    language = crud_i18n.get_language(db, language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    return language


@router.put("/languages/{language_id}", response_model=LanguageResponse)
def update_language(
    language_id: int,
    language_update: LanguageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a language"""
    try:
        language = crud_i18n.update_language(db, language_id, language_update)
        if not language:
            raise HTTPException(status_code=404, detail="Language not found")
        return language
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/languages/{language_id}", status_code=204)
def delete_language(
    language_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a language"""
    try:
        success = crud_i18n.delete_language(db, language_id)
        if not success:
            raise HTTPException(status_code=404, detail="Language not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return None


# ============ Translation Key Endpoints ============

@router.post("/keys", response_model=TranslationKeyResponse, status_code=201)
def create_translation_key(
    key_data: TranslationKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new translation key"""
    try:
        return crud_i18n.create_translation_key(db, key_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/keys", response_model=TranslationKeyListResponse)
def get_translation_keys(
    module: Optional[str] = Query(None),
    is_approved: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get translation keys"""
    skip = (page - 1) * page_size
    keys, total = crud_i18n.get_translation_keys(db, module, is_approved, search, skip, page_size)
    return TranslationKeyListResponse(
        total=total,
        items=keys,
        page=page,
        page_size=page_size,
    )


@router.get("/keys/{key_id}", response_model=TranslationKeyResponse)
def get_translation_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get translation key by ID"""
    key = crud_i18n.get_translation_key(db, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="Translation key not found")
    return key


@router.put("/keys/{key_id}", response_model=TranslationKeyResponse)
def update_translation_key(
    key_id: int,
    key_update: TranslationKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a translation key"""
    key = crud_i18n.update_translation_key(db, key_id, key_update)
    if not key:
        raise HTTPException(status_code=404, detail="Translation key not found")
    return key


@router.delete("/keys/{key_id}", status_code=204)
def delete_translation_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a translation key"""
    success = crud_i18n.delete_translation_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Translation key not found")
    return None


# ============ Translation Endpoints ============

@router.post("/translations", response_model=TranslationResponse, status_code=201)
def create_translation(
    translation: TranslationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update a translation"""
    # Get language
    language = crud_i18n.get_language_by_code(db, translation.language_code)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    # Get key
    key = crud_i18n.get_translation_key_by_value(db, translation.key)
    if not key:
        raise HTTPException(status_code=404, detail="Translation key not found")
    
    return crud_i18n.create_or_update_translation(
        db, key.id, language.id, translation.value, current_user.id
    )


@router.get("/translations", response_model=TranslationListResponse)
def get_translations(
    language_id: Optional[int] = Query(None),
    key_id: Optional[int] = Query(None),
    is_reviewed: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get translations"""
    skip = (page - 1) * page_size
    translations, total = crud_i18n.get_translations(
        db, language_id, key_id, is_reviewed, skip, page_size
    )
    return TranslationListResponse(total=total, items=translations)


@router.get("/keys/{key_id}/translations", response_model=dict)
def get_key_translations(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all translations for a specific key"""
    key = crud_i18n.get_translation_key(db, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="Translation key not found")
    
    translations = crud_i18n.get_all_translations_grouped(db, key_id)
    return {
        "key_id": key.id,
        "key": key.key,
        "description": key.description,
        "module": key.module,
        "translations": translations,
    }


@router.post("/translations/{translation_id}/review", response_model=TranslationResponse)
def review_translation(
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark translation as reviewed"""
    translation = crud_i18n.review_translation(db, translation_id, current_user.id)
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    return translation


@router.delete("/translations/{translation_id}", status_code=204)
def delete_translation(
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a translation"""
    success = crud_i18n.delete_translation(db, translation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Translation not found")
    return None


# ============ Utility Endpoints ============

@router.get("/untranslated", response_model=UntranslatedKeysResponse)
def get_untranslated_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get keys that are missing translations"""
    untranslated = crud_i18n.get_untranslated_keys(db)
    return UntranslatedKeysResponse(total=len(untranslated), items=untranslated)


@router.get("/export/{language_code}")
def export_translations(
    language_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export translations for a specific language"""
    translations = crud_i18n.get_translations_by_language_code(db, language_code)
    return {
        "format": "json",
        "language": language_code,
        "translations": translations,
    }