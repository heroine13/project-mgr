"""
API v1路由整合
"""
from fastapi import APIRouter

# 导入所有端点模块
from app.api.v1 import auth, projects, tasks
from app.api.v1.endpoints import gantt, websocket
from app.api.v1 import notifications, export, integration
from app.api.v1.issues import router as issues_router
from app.api.v1.resources import router as resources_router
from app.api.v1.documents import router as documents_router

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

# 注册导出路由
api_router.include_router(export.router, tags=["数据导出"])

# 注册Issue路由
api_router.include_router(issues_router, prefix="/issues", tags=["Issue管理"])

# 注册资源管理路由
api_router.include_router(resources_router, prefix="/resources", tags=["资源成本管理"])

# 注册文档管理路由
api_router.include_router(documents_router, prefix="/documents", tags=["文档版本控制"])