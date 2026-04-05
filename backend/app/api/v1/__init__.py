"""
API v1 endpoints
"""
from app.api.v1.endpoints import auth, projects, tasks, gantt, websocket

__all__ = ["auth", "projects", "tasks", "gantt", "websocket"]