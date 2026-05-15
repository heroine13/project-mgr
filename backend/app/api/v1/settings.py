"""System Settings API - 系统设置接口（含AI配置）"""

from fastapi import APIRouter, Depends, HTTPException, Query
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

class ModelItem(BaseModel):
    id: str
    name: str
    isDefault: bool = False


class ProviderConfig(BaseModel):
    """单个Provider的完整配置"""
    name: str
    baseUrl: str = ""
    api: str = "openai-completions"
    apiKey: str = ""
    models: List[ModelItem] = []
    defaultModelId: str = ""


class AIConfigRequest(BaseModel):
    # 当前激活的配置（直接存整个ProviderConfig）
    current: ProviderConfig = ProviderConfig(name="openai")
    # 所有已添加的自定义provider名称列表
    customProviderNames: List[str] = []


class AIConfigResponse(BaseModel):
    # 当前激活的配置（apiKey不暴露）
    current: Dict = {}
    current_api_key: str = ""  # 隐藏
    # 所有已添加的自定义provider名称
    customProviderNames: List[str] = []
    # 预定义provider列表
    preset_providers: List[Dict] = []
    configured: bool = False


class SettingsBatchUpdateRequest(BaseModel):
    settings: Dict[str, str]


class SettingsResponse(BaseModel):
    data: Dict[str, str]


# 预定义provider
PRESET_PROVIDERS = [
    {"value": "openai", "label": "OpenAI", "baseUrl": "https://api.openai.com/v1", "api": "openai-completions"},
    {"value": "anthropic", "label": "Anthropic Claude", "baseUrl": "", "api": "anthropic-messages"},
    {"value": "azure", "label": "Azure OpenAI", "baseUrl": "", "api": "openai-completions"},
]


# === Endpoints ===

def _load_provider_config(db: Session, provider_name: str) -> Optional[Dict]:
    """从数据库加载某个provider的完整配置"""
    settings = SystemSettingsService.get_by_category(db, "ai")
    key = f"provider_{provider_name}"
    data = settings.get(key)
    if data:
        try:
            return json.loads(data)
        except:
            return None
    return None


def _save_provider_config(db: Session, provider_name: str, config: ProviderConfig) -> None:
    """保存某个provider的完整配置到数据库"""
    config_data = {
        "name": config.name,
        "baseUrl": config.baseUrl,
        "api": config.api,
        "apiKey": config.apiKey,
        "models": [
            {"id": m.id, "name": m.name, "isDefault": m.isDefault}
            for m in config.models
        ],
        "defaultModelId": config.defaultModelId,
    }
    SystemSettingsService.save(db, f"provider_{provider_name}", json.dumps(config_data, ensure_ascii=False), category="ai")


@router.get("/ai", response_model=AIConfigResponse)
async def get_ai_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有AI配置"""
    all_settings = SystemSettingsService.get_all(db)
    
    # 从所有setting里提取custom provider配置
    custom_names = []
    current_config = None
    
    for key, value in all_settings.items():
        if key.startswith("provider_"):
            p_name = key.replace("provider_", "")
            try:
                config = json.loads(value)
                custom_names.append(p_name)
                if p_name == current_user.username:
                    current_config = config
            except:
                continue
    
    # 如果没有当前用户的配置，尝试加载第一个custom provider
    if not current_config and custom_names:
        try:
            current_config = json.loads(all_settings.get(f"provider_{custom_names[0]}", "{}"))
        except:
            current_config = {}
    
    if not current_config:
        current_config = {"name": "openai", "baseUrl": "", "api": "openai-completions", "apiKey": "", "models": [], "defaultModelId": ""}
    
    # 隐藏API Key
    current_config_hidden = dict(current_config)
    current_config_hidden["apiKey"] = ""
    configured = bool(current_config.get("apiKey", ""))
    
    return AIConfigResponse(
        current=current_config_hidden,
        current_api_key="",
        customProviderNames=custom_names,
        preset_providers=PRESET_PROVIDERS,
        configured=configured
    )


@router.post("/ai")
async def update_ai_config(
    request: AIConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新AI配置并热加载"""
    
    config = request.current
    
    # 获取当前provider名称（自定义provider用name作为key）
    provider_name = config.name
    
    # 保存当前provider配置
    _save_provider_config(db, provider_name, config)
    
    # 同步customProviderNames到数据库（方便查询）
    names_json = json.dumps(request.customProviderNames, ensure_ascii=False)
    SystemSettingsService.save(db, "customProviderNames", names_json, category="ai")
    
    # 热更新环境变量
    import os
    os.environ["AI_API_KEY"] = config.apiKey
    os.environ["AI_PROVIDER"] = config.name
    os.environ["AI_MODEL"] = config.defaultModelId or "gpt-4"
    os.environ["AI_BASE_URL"] = config.baseUrl or ""
    os.environ["AI_API_PROTOCOL"] = config.api or "openai-completions"

    # 重新初始化AI客户端
    try:
        import app.services.ai as ai_module
        import importlib
        importlib.reload(ai_module)
        ai_module.reload_config()

        status = "active" if ai_module.AI_API_KEY else "demo_mode"
        message = "AI服务已重新配置" if ai_module.AI_API_KEY else "AI服务未配置API密钥"
    except Exception as e:
        status = "error"
        message = f"重新配置AI服务失败: {str(e)}"

    return {"success": True, "message": message, "status": status}


@router.delete("/ai/provider")
async def delete_ai_provider(
    provider_name: str = Query(..., alias="provider"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除自定义Provider及其所有模型"""
    
    from app.models.system_setting import SystemSetting
    db.query(SystemSetting).filter(
        SystemSetting.key == f"provider_{provider_name}"
    ).delete()
    
    # Remove from customProviderNames
    all_settings = SystemSettingsService.get_all(db)
    names_json = all_settings.get("customProviderNames", "[]")
    try:
        names = json.loads(names_json) if names_json else []
    except:
        names = []
    names = [n for n in names if n != provider_name]
    SystemSettingsService.save(db, "customProviderNames", json.dumps(names, ensure_ascii=False), category="ai")
    db.commit()
    
    return {"success": True, "message": f"Provider '{provider_name}' 已删除"}


@router.get("/all")
async def get_all_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有设置"""
    data = SystemSettingsService.get_all(db)
    return {"data": data, "success": True}


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
