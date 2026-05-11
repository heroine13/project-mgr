"""
Internationalization (i18n) API - Translation Management
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Optional
from pydantic import BaseModel

router = APIRouter(tags=["国际化"])


# === Schemas ===

class LanguageResponse(BaseModel):
    id: int
    code: str
    name: str
    native_name: str
    is_active: bool = True
    is_default: bool = False


class TranslationKeyResponse(BaseModel):
    id: int
    key: str
    module: str
    description: Optional[str] = None
    created_at: str


class TranslationValueResponse(BaseModel):
    id: int
    key_id: int
    language_code: str
    value: str
    is_translated: bool = False


class TranslationUpdateRequest(BaseModel):
    language_code: str
    value: str


# === 模拟数据 ===

LANGUAGES = [
    {"id": 1, "code": "zh-CN", "name": "简体中文", "native_name": "简体中文", "is_active": True, "is_default": True},
    {"id": 2, "code": "en", "name": "English", "native_name": "English", "is_active": True, "is_default": False},
    {"id": 3, "code": "ko-KR", "name": "한국어", "native_name": "한국어", "is_active": True, "is_default": False},
]

TRANSLATION_KEYS = [
    {"id": 1, "key": "navigation.dashboard", "module": "navigation", "description": "仪表盘"},
    {"id": 2, "key": "navigation.projects", "module": "navigation", "description": "项目"},
    {"id": 3, "key": "navigation.tasks", "module": "navigation", "description": "任务"},
    {"id": 4, "key": "common.save", "module": "common", "description": "保存"},
    {"id": 5, "key": "common.cancel", "module": "common", "description": "取消"},
]

TRANSLATION_VALUES = [
    {"id": 1, "key_id": 1, "language_code": "zh-CN", "value": "仪表盘", "is_translated": True},
    {"id": 2, "key_id": 1, "language_code": "en", "value": "Dashboard", "is_translated": True},
    {"id": 3, "key_id": 2, "language_code": "zh-CN", "value": "项目", "is_translated": True},
    {"id": 4, "key_id": 2, "language_code": "en", "value": "Projects", "is_translated": True},
    {"id": 5, "key_id": 3, "language_code": "zh-CN", "value": "任务", "is_translated": True},
    {"id": 6, "key_id": 3, "language_code": "en", "value": "Tasks", "is_translated": True},
]


# === API Endpoints ===

@router.get("/languages", response_model=dict)
def get_languages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取语言列表"""
    start = (page - 1) * page_size
    end = start + page_size
    items = LANGUAGES[start:end]
    return {
        "items": items,
        "total": len(LANGUAGES),
        "page": page,
        "page_size": page_size
    }


@router.get("/keys", response_model=dict)
def get_translation_keys(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    module: Optional[str] = None
):
    """获取翻译Key列表"""
    keys = TRANSLATION_KEYS.copy()
    
    if search:
        keys = [k for k in keys if search.lower() in k["key"].lower()]
    if module:
        keys = [k for k in keys if k["module"] == module]
    
    start = (page - 1) * page_size
    end = start + page_size
    items = keys[start:end]
    
    return {
        "items": items,
        "total": len(keys),
        "page": page,
        "page_size": page_size
    }


@router.get("/values", response_model=dict)
def get_translation_values(
    key_id: Optional[int] = None,
    language_code: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """获取翻译值列表"""
    values = TRANSLATION_VALUES.copy()
    
    if key_id:
        values = [v for v in values if v["key_id"] == key_id]
    if language_code:
        values = [v for v in values if v["language_code"] == language_code]
    
    start = (page - 1) * page_size
    end = start + page_size
    items = values[start:end]
    
    return {
        "items": items,
        "total": len(values),
        "page": page,
        "page_size": page_size
    }


@router.put("/keys/{key_id}/value")
def update_translation(
    key_id: int,
    data: TranslationUpdateRequest
):
    """更新翻译值"""
    for v in TRANSLATION_VALUES:
        if v["key_id"] == key_id and v["language_code"] == data.language_code:
            v["value"] = data.value
            v["is_translated"] = True
            return {"success": True, "data": v}
    
    # Create new if not exists
    new_id = len(TRANSLATION_VALUES) + 1
    new_value = {
        "id": new_id,
        "key_id": key_id,
        "language_code": data.language_code,
        "value": data.value,
        "is_translated": True
    }
    TRANSLATION_VALUES.append(new_value)
    return {"success": True, "data": new_value}


@router.get("/stats")
def get_i18n_stats():
    """获取i18n统计信息"""
    total_keys = len(TRANSLATION_KEYS)
    total_values = len(TRANSLATION_VALUES)
    translated = sum(1 for v in TRANSLATION_VALUES if v["is_translated"])
    
    return {
        "total_keys": total_keys,
        "total_values": total_values,
        "translated": translated,
        "untranslated": total_values - translated,
        "completion_rate": round(translated / total_values * 100, 1) if total_values > 0 else 0
    }
