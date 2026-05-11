"""
API v1 endpoints
"""
# 直接从 v1 目录导入模块
from app.api.v1 import auth, projects, tasks
from app.api.v1.endpoints import gantt
from app.api.v1.endpoints import websocket
from app.api.v1 import scheduler, reports

__all__ = ["auth", "projects", "tasks", "gantt", "websocket", "scheduler", "reports"]