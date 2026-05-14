"""System Settings API - 系统设置接口（含AI配置）"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.system_settings import SystemSettingsService

router = APIRouter(prefix="/settings", tags=["系统设置"])


# === Schemas ===

class AIConfigRequest(BaseModel):
    ai_api_key: str = ""
    ai_provider: str = "openai"
    ai_model: str = "gpt-4"
    ai_base_url: str = ""


class AIConfigResponse(BaseModel):
    ai_api_key: str = ""  # 不暴露真实Key
    ai_provider: str = "openai"
    ai_model: str = "gpt-4"
    ai_base_url: str = ""
    configured: bool = False


class SettingsBatchUpdateRequest(BaseModel):
    settings: Dict[str, str]


class SettingsResponse(BaseModel):
    data: Dict[str, str]


# === Endpoints ===

@router.get("/ai", response_model=AIConfigResponse)
async def get_ai_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取AI配置（隐藏API Key）"""
    ai_settings = SystemSettingsService.get_ai_settings(db)
    configured = bool(ai_settings.get("ai_api_key", ""))
    return AIConfigResponse(
        ai_api_key="",
        ai_provider=ai_settings.get("ai_provider", "openai"),
        ai_model=ai_settings.get("ai_model", "gpt-4"),
        ai_base_url=ai_settings.get("ai_base_url", ""),
        configured=configured
    )


@router.post("/ai")
async def update_ai_config(
    request: AIConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新AI配置并热加载"""
    config_data = {
        "ai_api_key": request.ai_api_key,
        "ai_provider": request.ai_provider,
        "ai_model": request.ai_model,
        "ai_base_url": request.ai_base_url,
    }
    SystemSettingsService.save_batch(db, config_data, category="ai")

    # 热更新环境变量
    import os
    os.environ["AI_API_KEY"] = request.ai_api_key
    os.environ["AI_PROVIDER"] = request.ai_provider or "openai"
    os.environ["AI_MODEL"] = request.ai_model or "gpt-4"
    os.environ["AI_BASE_URL"] = request.ai_base_url

    # 重新初始化AI客户端
    try:
        import app.services.ai as ai_module
        import importlib
        importlib.reload(ai_module)

        status = "active" if ai_module.AI_API_KEY else "demo_mode"
        message = "AI服务已重新配置" if ai_module.AI_API_KEY else "AI服务未配置API密钥"
    except Exception as e:
        status = "error"
        message = f"重新配置AI服务失败: {str(e)}"

    return {"success": True, "message": message, "status": status}


@router.get("/all", response_model=SettingsResponse)
async def get_all_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有设置"""
    data = SystemSettingsService.get_all(db)
    return SettingsResponse(data=data)


@router.put("/batch")
async def update_settings_batch(
    request: SettingsBatchUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量更新设置"""
    for key, value in request.settings.items():
        SystemSettingsService.save(db, key, str(value))
    return {"success": True, "message": "设置已更新"}
