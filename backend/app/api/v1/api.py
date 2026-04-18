"""
API v1路由整合
"""
from fastapi import APIRouter

# 导入所有端点模块
from app.api.v1 import auth, projects, tasks
from app.api.v1.endpoints import gantt, websocket
from app.api.v1 import notifications

api_router = APIRouter()

# 注册认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册项目路由
api_router.include_router(projects.router, prefix="/projects", tags=["项目管理"])

# 注册任务路由
api_router.include_router(tasks.router, prefix="/tasks", tags=["任务管理"])

# 注册甘特图路由
api_router.include_router(gantt.router, prefix="/gantt", tags=["甘特图"])

# 注册WebSocket路由
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

# 注册通知路由
api_router.include_router(notifications.router, prefix="/notifications", tags=["通知管理"])