"""
Issue Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class IssueStatusEnum(str, Enum):
    """Issue status enumeration for API"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class IssuePriorityEnum(str, Enum):
    """Issue priority enumeration for API"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueTypeEnum(str, Enum):
    """Issue type enumeration for API"""
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    QUESTION = "question"


# ============ Issue Schemas ============

class IssueBase(BaseModel):
    """Base Issue schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    issue_type: IssueTypeEnum = IssueTypeEnum.BUG
    priority: IssuePriorityEnum = IssuePriorityEnum.MEDIUM
    project_id: int
    task_id: Optional[int] = None
    assignee_id: Optional[int] = None
    labels: Optional[str] = None


class IssueCreate(IssueBase):
    """Issue creation schema"""
    pass


class IssueUpdate(BaseModel):
    """Issue update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    issue_type: Optional[IssueTypeEnum] = None
    status: Optional[IssueStatusEnum] = None
    priority: Optional[IssuePriorityEnum] = None
    task_id: Optional[int] = None
    assignee_id: Optional[int] = None
    labels: Optional[str] = None
    is_resolved: Optional[bool] = None


class IssueStatusUpdate(BaseModel):
    """Issue status update schema"""
    status: IssueStatusEnum


class IssueAssigneeUpdate(BaseModel):
    """Issue assignee update schema"""
    assignee_id: int


class IssueResponse(IssueBase):
    """Issue response schema"""
    id: int
    status: IssueStatusEnum
    is_resolved: bool
    resolved_at: Optional[datetime]
    reporter_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class IssueListResponse(BaseModel):
    """Issue list response with pagination"""
    total: int
    items: List[IssueResponse]
    page: int
    page_size: int
    pages: int


# ============ Issue Comment Schemas ============

class IssueCommentBase(BaseModel):
    """Base IssueComment schema"""
    content: str = Field(..., min_length=1)


class IssueCommentCreate(IssueCommentBase):
    """IssueComment creation schema"""
    mentioned_users: Optional[str] = None


class IssueCommentUpdate(BaseModel):
    """IssueComment update schema"""
    content: str = Field(..., min_length=1)


class IssueCommentResponse(IssueCommentBase):
    """IssueComment response schema"""
    id: int
    issue_id: int
    user_id: int
    mentioned_users: Optional[str]
    reactions: Optional[str]
    is_edited: bool
    edited_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class IssueCommentListResponse(BaseModel):
    """IssueComment list response"""
    total: int
    items: List[IssueCommentResponse]


# ============ Issue Attachment Schemas ============

class IssueAttachmentResponse(BaseModel):
    """IssueAttachment response schema"""
    id: int
    issue_id: int
    user_id: int
    filename: str
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Issue with Details ============

class IssueWithComments(IssueResponse):
    """Issue with comments"""
    comments: List[IssueCommentResponse] = []
    
    class Config:
        from_attributes = True


class IssueStatsResponse(BaseModel):
    """Issue statistics response"""
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int
    by_priority: dict
    by_type: dict