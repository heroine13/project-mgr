"""
API v1 endpoints
"""
from app.api.v1.endpoints import auth, projects, tasks, gantt, websocket
from app.api.v1 import scheduler, reports

__all__ = ["auth", "projects", "tasks", "gantt", "websocket", "scheduler", "reports"]