"""System Settings API - 系统设置接口（含AI配置）"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional, List
from pydantic import BaseModel
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.system_settings import SystemSettingsService
from app.services.ai import reload_config

router = APIRouter(prefix="/settings", tags=["系统设置"])


# === Schemas ===

class ModelInfo(BaseModel):
    id: str
    name: str


class AIConfigRequest(BaseModel):
    ai_api_key: str = ""
    ai_provider: Optional[str] = None  # 自定义provider名称或预定义
    ai_provider_name: str = ""  # 自定义provider显示名
    ai_provider_base_url: str = ""
    ai_api: str = "openai-completions"  # 接入协议
    ai_model: str = ""  # 选中的模型ID
    ai_models: List[ModelInfo] = []  # 可用模型列表


class AIConfigResponse(BaseModel):
    ai_api_key: str = ""  # 不暴露真实Key
    ai_provider: str = ""
    ai_provider_name: str = ""
    ai_provider_base_url: str = ""
    ai_api: str = "openai-completions"
    ai_model: str = ""  # 当前选中的模型ID
    ai_models: List[ModelInfo] = []
    configured: bool = False
    # 预定义provider列表
    preset_providers: List[Dict] = []


class SettingsBatchUpdateRequest(BaseModel):
    settings: Dict[str, str]


class SettingsResponse(BaseModel):
    data: Dict[str, str]


# 预定义provider
PRESET_PROVIDERS = [
    {"value": "openai", "label": "OpenAI", "base_url": "https://api.openai.com/v1", "api": "openai-completions"},
    {"value": "anthropic", "label": "Anthropic Claude", "base_url": "", "api": "anthropic-messages"},
    {"value": "azure", "label": "Azure OpenAI", "base_url": "", "api": "openai-completions"},
    {"value": "custom", "label": "自定义", "base_url": "", "api": "openai-completions"},
]


# === Helpers ===

def _provider_label(provider_value: str) -> str:
    for p in PRESET_PROVIDERS:
        if p["value"] == provider_value:
            return p["label"]
    return provider_value


# === Endpoints ===

@router.get("/ai", response_model=AIConfigResponse)
async def get_ai_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取AI配置（隐藏API Key）"""
    ai_settings = SystemSettingsService.get_ai_settings(db)
    configured = bool(ai_settings.get("ai_api_key", ""))
    
    # 解析 models JSON
    models_json = ai_settings.get("ai_models", "[]")
    try:
        models = json.loads(models_json)
        ai_models = [ModelInfo(**m) for m in models] if models else []
    except:
        ai_models = []
    
    return AIConfigResponse(
        ai_api_key="",
        ai_provider=ai_settings.get("ai_provider", "openai"),
        ai_provider_name=ai_settings.get("ai_provider_name", ""),
        ai_provider_base_url=ai_settings.get("ai_provider_base_url", ""),
        ai_api=ai_settings.get("ai_api", "openai-completions"),
        ai_model=ai_settings.get("ai_model", ""),
        ai_models=ai_models,
        configured=configured,
        preset_providers=PRESET_PROVIDERS
    )


@router.post("/ai")
async def update_ai_config(
    request: AIConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新AI配置并热加载"""
    
    # 确定最终的 provider 名称
    provider_name = request.ai_provider or "openai"
    if request.ai_provider == "custom" and request.ai_provider_name:
        provider_name = request.ai_provider_name
    
    # models 列表
    models_json = json.dumps([{"id": m.id, "name": m.name} for m in request.ai_models], ensure_ascii=False)
    
    config_data = {
        "ai_api_key": request.ai_api_key,
        "ai_provider": provider_name,
        "ai_provider_name": request.ai_provider_name,
        "ai_provider_base_url": request.ai_provider_base_url,
        "ai_api": request.ai_api or "openai-completions",
        "ai_model": request.ai_model,
        "ai_models": models_json,
    }
    SystemSettingsService.save_batch(db, config_data, category="ai")

    # 热更新环境变量
    import os
    os.environ["AI_API_KEY"] = request.ai_api_key
    os.environ["AI_PROVIDER"] = provider_name
    os.environ["AI_MODEL"] = request.ai_model or "gpt-4"
    os.environ["AI_BASE_URL"] = request.ai_provider_base_url
    
    # 存储自定义信息
    os.environ["AI_API_PROTOCOL"] = request.ai_api or "openai-completions"

    # 重新初始化AI客户端
    try:
        import app.services.ai as ai_module
        import importlib
        importlib.reload(ai_module)
        reload_config()

        status = "active" if ai_module.AI_API_KEY else "demo_mode"
        message = "AI服务已重新配置" if ai_module.AI_API_KEY else "AI服务未配置API密钥"
    except Exception as e:
        status = "error"
        message = f"重新配置AI服务失败: {str(e)}"

    return {"success": True, "message": message, "status": status}


@router.post("/ai/models")
async def add_ai_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加模型到当前AI配置"""
    try:
        ai_settings = SystemSettingsService.get_ai_settings(db)
        models_json = ai_settings.get("ai_models", "[]")
        try:
            models = json.loads(models_json) if models_json else []
        except:
            models = []
        
        models.append({"id": "", "name": ""})  # 添加空条目待填写
        SystemSettingsService.save(db, "ai_models", json.dumps(models, ensure_ascii=False), category="ai")
        
        return {"success": True, "models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ai/provider")
async def delete_ai_provider(
    provider_value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除自定义Provider及其所有模型"""
    SystemSettingsService.save(db, "ai_provider", "openai", category="ai")
    SystemSettingsService.save(db, "ai_model", "", category="ai")
    SystemSettingsService.save(db, "ai_models", "[]", category="ai")
    return {"success": True, "message": "Provider已删除，模型已清空"}


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
