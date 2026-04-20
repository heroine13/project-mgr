"""
Internationalization CRUD Operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional, List, Dict
from datetime import datetime

from ..models.i18n import Language, TranslationKey, Translation
from ..schemas.i18n import LanguageCreate, LanguageUpdate, TranslationKeyCreate, TranslationKeyUpdate, TranslationCreate, TranslationUpdate


# ============ Language CRUD ============

def create_language(db: Session, language: LanguageCreate) -> Language:
    """Create a new language"""
    # If this is the default language, unset other defaults
    if language.is_default:
        db.query(Language).update({"is_default": False})
    
    db_language = Language(
        code=language.code,
        name=language.name,
        native_name=language.native_name,
        is_default=language.is_default,
        is_active=language.is_active,
        display_order=language.display_order,
    )
    db.add(db_language)
    db.commit()
    db.refresh(db_language)
    return db_language


def get_language(db: Session, language_id: int) -> Optional[Language]:
    """Get language by ID"""
    return db.query(Language).filter(Language.id == language_id).first()


def get_language_by_code(db: Session, code: str) -> Optional[Language]:
    """Get language by code"""
    return db.query(Language).filter(Language.code == code).first()


def get_languages(
    db: Session,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Language], int]:
    """Get languages with filters"""
    query = db.query(Language)
    
    if is_active is not None:
        query = query.filter(Language.is_active == is_active)
    
    total = query.count()
    languages = query.order_by(Language.display_order, Language.name).offset(skip).limit(limit).all()
    return languages, total


def update_language(db: Session, language_id: int, language_update: LanguageUpdate) -> Optional[Language]:
    """Update a language"""
    db_language = get_language(db, language_id)
    if not db_language:
        return None
    
    update_data = language_update.model_dump(exclude_unset=True)
    
    # Handle default language
    if update_data.get("is_default") and not db_language.is_default:
        db.query(Language).filter(Language.id != language_id).update({"is_default": False})
    
    for field, value in update_data.items():
        setattr(db_language, field, value)
    
    db.commit()
    db.refresh(db_language)
    return db_language


def delete_language(db: Session, language_id: int) -> bool:
    """Delete a language"""
    db_language = get_language(db, language_id)
    if not db_language:
        return False
    
    # Prevent deleting the only language
    total_languages = db.query(Language).count()
    if total_languages <= 1:
        raise ValueError("Cannot delete the only language")
    
    db.delete(db_language)
    db.commit()
    return True


# ============ Translation Key CRUD ============

def create_translation_key(
    db: Session,
    key_data: TranslationKeyCreate,
    user_id: Optional[int] = None,
) -> TranslationKey:
    """Create a new translation key"""
    # Check if key already exists
    existing = db.query(TranslationKey).filter(TranslationKey.key == key_data.key).first()
    if existing:
        raise ValueError(f"Translation key '{key_data.key}' already exists")
    
    db_key = TranslationKey(
        key=key_data.key,
        description=key_data.description,
        module=key_data.module,
        created_by=user_id,
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


def get_translation_key(db: Session, key_id: int) -> Optional[TranslationKey]:
    """Get translation key by ID"""
    return db.query(TranslationKey).filter(TranslationKey.id == key_id).first()


def get_translation_key_by_value(db: Session, key: str) -> Optional[TranslationKey]:
    """Get translation key by key value"""
    return db.query(TranslationKey).filter(TranslationKey.key == key).first()


def get_translation_keys(
    db: Session,
    module: Optional[str] = None,
    is_approved: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[TranslationKey], int]:
    """Get translation keys with filters"""
    query = db.query(TranslationKey)
    
    if module:
        query = query.filter(TranslationKey.module == module)
    if is_approved is not None:
        query = query.filter(TranslationKey.is_approved == is_approved)
    if search:
        query = query.filter(TranslationKey.key.ilike(f"%{search}%"))
    
    total = query.count()
    keys = query.order_by(TranslationKey.module, TranslationKey.key).offset(skip).limit(limit).all()
    return keys, total


def update_translation_key(
    db: Session,
    key_id: int,
    key_update: TranslationKeyUpdate,
) -> Optional[TranslationKey]:
    """Update a translation key"""
    db_key = get_translation_key(db, key_id)
    if not db_key:
        return None
    
    update_data = key_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_key, field, value)
    
    db.commit()
    db.refresh(db_key)
    return db_key


def delete_translation_key(db: Session, key_id: int) -> bool:
    """Delete a translation key"""
    db_key = get_translation_key(db, key_id)
    if not db_key:
        return False
    
    db.delete(db_key)
    db.commit()
    return True


# ============ Translation CRUD ============

def create_or_update_translation(
    db: Session,
    key_id: int,
    language_id: int,
    value: str,
    user_id: Optional[int] = None,
) -> Translation:
    """Create or update a translation"""
    # Check if translation exists
    db_translation = (
        db.query(Translation)
        .filter(
            and_(
                Translation.key_id == key_id,
                Translation.language_id == language_id,
            )
        )
        .first()
    )
    
    if db_translation:
        db_translation.value = value
        db_translation.created_by = user_id
    else:
        db_translation = Translation(
            key_id=key_id,
            language_id=language_id,
            value=value,
            created_by=user_id,
        )
        db.add(db_translation)
    
    db.commit()
    db.refresh(db_translation)
    return db_translation


def get_translation(
    db: Session,
    key_id: int,
    language_id: int,
) -> Optional[Translation]:
    """Get translation by key and language"""
    return (
        db.query(Translation)
        .filter(
            and_(
                Translation.key_id == key_id,
                Translation.language_id == language_id,
            )
        )
        .first()
    )


def get_translations_for_key(
    db: Session,
    key_id: int,
) -> List[Translation]:
    """Get all translations for a specific key"""
    return db.query(Translation).filter(Translation.key_id == key_id).all()


def get_translations(
    db: Session,
    language_id: Optional[int] = None,
    key_id: Optional[int] = None,
    is_reviewed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Translation], int]:
    """Get translations with filters"""
    query = db.query(Translation)
    
    if language_id:
        query = query.filter(Translation.language_id == language_id)
    if key_id:
        query = query.filter(Translation.key_id == key_id)
    if is_reviewed is not None:
        query = query.filter(Translation.is_reviewed == is_reviewed)
    
    total = query.count()
    translations = query.offset(skip).limit(limit).all()
    return translations, total


def review_translation(
    db: Session,
    translation_id: int,
    user_id: int,
) -> Optional[Translation]:
    """Mark translation as reviewed"""
    db_translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not db_translation:
        return None
    
    db_translation.is_reviewed = True
    db_translation.reviewed_by = user_id
    
    db.commit()
    db.refresh(db_translation)
    return db_translation


def delete_translation(db: Session, translation_id: int) -> bool:
    """Delete a translation"""
    db_translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not db_translation:
        return False
    
    db.delete(db_translation)
    db.commit()
    return True


# ============ Utility Functions ============

def get_untranslated_keys(db: Session) -> List[Dict]:
    """Get keys that are missing translations for some languages"""
    languages = db.query(Language).filter(Language.is_active == True).all()
    keys = db.query(TranslationKey).all()
    
    untranslated = []
    for key in keys:
        existing_languages = [
            t.language_id for t in db.query(Translation).filter(Translation.key_id == key.id).all()
        ]
        missing = [lang.code for lang in languages if lang.id not in existing_languages]
        if missing:
            untranslated.append({
                "key_id": key.id,
                "key": key.key,
                "missing_languages": missing,
            })
    
    return untranslated


def get_translations_by_language_code(
    db: Session,
    language_code: str,
) -> Dict[str, str]:
    """Get all translations for a specific language code"""
    language = get_language_by_code(db, language_code)
    if not language:
        return {}
    
    translations = (
        db.query(TranslationKey.key, Translation.value)
        .join(Translation, Translation.key_id == TranslationKey.id)
        .filter(Translation.language_id == language.id)
        .all()
    )
    
    return {t[0]: t[1] for t in translations}


def get_all_translations_grouped(
    db: Session,
    key_id: int,
) -> Dict[str, str]:
    """Get all translations for a key, grouped by language code"""
    translations = get_translations_for_key(db, key_id)
    return {t.language.code: t.value for t in translations}