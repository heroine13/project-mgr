"""
Database Models
"""

# Import all models to ensure SQLAlchemy can resolve all relationships
# Order matters: dependencies must be imported before dependents

from .user import User
from .user_mgmt import Role, UserProfile, Department
from .search import DocumentCategory, SearchHistory, SavedSearch
from .task import Task, TaskStatus, TaskPriority
from .project import Project
from .notification import Notification, NotificationPreference, EmailQueue
from .comment import Comment
from .gantt import GanttTask
from .document import Document, DocumentVersion, DocumentComment
from .resource import Resource, ResourceAllocation, CostRecord
from .issue import Issue, IssueComment, IssueAttachment
from .workflow import Workflow, ApprovalRequest, ApprovalAction, WorkflowTemplate
from .audit import AuditLog, AuditLogSummary
from .i18n import Language, TranslationKey, Translation

__all__ = [
    "User", 
    "Role",
    "UserProfile",
    "Department",
    "DocumentCategory",
    "SearchHistory",
    "SavedSearch",
    "Task", 
    "TaskStatus",
    "TaskPriority",
    "Project",
    "Notification", 
    "NotificationPreference", 
    "EmailQueue",
    "Comment",
    "GanttTask",
    "Document",
    "DocumentVersion",
    "DocumentComment",
    "Resource",
    "ResourceAllocation",
    "CostRecord",
    "Issue",
    "IssueComment",
    "IssueAttachment",
    "Workflow",
    "ApprovalRequest",
    "ApprovalAction",
    "WorkflowTemplate",
    "AuditLog",
    "AuditLogSummary",
    "Language",
    "TranslationKey",
    "Translation",
]
