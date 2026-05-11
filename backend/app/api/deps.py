"""
API 依赖项模块
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
    # 可以在这里添加用户是否活跃的检查
    return current_user

# 导出
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "security"
]