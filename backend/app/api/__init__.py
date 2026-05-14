"""
API 模块初始化
"""
from app.core.database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt_handler import verify_token
from typing import Optional

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """获取当前用户"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权"
        )
    token = credentials.credentials
    return verify_token(token)

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """获取当前活跃用户"""
    return current_user

# 创建依赖项模块对象
class Deps:
    """依赖项容器"""
    get_db = staticmethod(get_db)
    get_current_user = staticmethod(get_current_user)
    get_current_active_user = staticmethod(get_current_active_user)
    security = security

deps = Deps()

__all__ = ["deps", "get_db", "get_current_user", "get_current_active_user", "security"]