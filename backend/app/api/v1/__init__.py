"""
API v1 endpoints
"""
from app.api.v1.endpoints import auth, projects, tasks, gantt

__all__ = ["auth", "projects", "tasks", "gantt"]