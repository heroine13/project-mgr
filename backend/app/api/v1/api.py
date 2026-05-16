"""
API v1路由整合
"""
from fastapi import APIRouter

# 导入所有端点模块
from app.api.v1 import auth, projects, tasks
from app.api.v1.endpoints import gantt, websocket
from app.api.v1 import notifications, export, integration, settings as settings_api
from app.api.v1.issues import router as issues_router
from app.api.v1.resources import router as resources_router
from app.api.v1.documents import router as documents_router
from app.api.v1.i18n import router as i18n_router
from app.api.v1.search import router as search_router
from app.api.v1.kanban import router as kanban_router
from app.api.v1.team import router as team_router
from app.api.v1.backup import router as backup_router
from app.api.v1.audit import router as audit_router
from app.api.v1.reports_enhanced import router as reports_router
from app.api.v1.user_mgmt import router as user_mgmt_router
from app.api.v1.project_template import router as project_template_router
from app.api.v1.external import router as external_router
from app.api.v1.workflow import router as workflow_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.ai import router as ai_router
from app.api.v1.project_overview import router as overview_router
from app.api.v1.project_detail import router as project_detail_router

api_router = APIRouter()

# 注册认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册项目详情路由（必须在 projects 路由之前注册，否则 /projects/{project_id}/detail 会被 projects 路由拦截）
api_router.include_router(project_detail_router, prefix="/projects", tags=["项目详情"])

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
api_router.include_router(issues_router, prefix="/issues", tags=["问题管理"])

# 注册资源路由
api_router.include_router(resources_router, prefix="/resources", tags=["资源成本管理"])

# 注册文档路由
api_router.include_router(documents_router, prefix="/documents", tags=["文档管理"])

# 注册国际化路由
api_router.include_router(i18n_router, prefix="/i18n", tags=["国际化"])

# 注册文档搜索路由
api_router.include_router(search_router, prefix="/documents-search", tags=["文档搜索"])

# 注册看板路由
api_router.include_router(kanban_router, prefix="/kanban", tags=["看板"])

# 注册团队路由
api_router.include_router(team_router, prefix="/team", tags=["团队协作"])

# 注册备份路由
api_router.include_router(backup_router, prefix="/backup", tags=["备份管理"])

# 注册审计日志路由
api_router.include_router(audit_router, prefix="/audit", tags=["审计日志"])

# 注册报表路由
api_router.include_router(reports_router, prefix="/reports", tags=["报表增强"])

# 注册用户管理路由
api_router.include_router(user_mgmt_router, prefix="/users", tags=["用户管理"])

# 注册项目模板路由
api_router.include_router(project_template_router, prefix="/project-templates", tags=["项目模板"])

# 注册外部数据路由
api_router.include_router(external_router, prefix="/external", tags=["外部数据集成"])

# 注册工作流路由
api_router.include_router(workflow_router, prefix="/workflow", tags=["工作流"])

# 注册日历路由
api_router.include_router(calendar_router, prefix="/calendar", tags=["日历"])

# 注册AI助手路由
api_router.include_router(ai_router, prefix="/ai", tags=["AI助手"])

# 注册系统设置路由
api_router.include_router(settings_api.router, prefix="/settings", tags=["系统设置"])

# 注册项目总览路由
api_router.include_router(overview_router, prefix="/projects/overview", tags=["项目总览"])


