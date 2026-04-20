"""
Issue Model - Project Issue/Bug Tracking System
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .user import Base


class IssueStatus(PyEnum):
    """Issue status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class IssuePriority(PyEnum):
    """Issue priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(PyEnum):
    """Issue type enumeration"""
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    QUESTION = "question"


class Issue(Base):
    """Issue model for bug/feature tracking"""
    
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    issue_type = Column(Enum(IssueType), default=IssueType.BUG)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN)
    priority = Column(Enum(IssuePriority), default=IssuePriority.MEDIUM)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # Optional link to task
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Labels/Tags
    labels = Column(String(500))  # Comma separated labels
    
    # Tracking
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="issues")
    task = relationship("Task")
    assignee = relationship("User", foreign_keys=[assignee_id])
    reporter = relationship("User", foreign_keys=[reporter_id])
    comments = relationship("IssueComment", back_populates="issue", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Issue(id={self.id}, title='{self.title}', status='{self.status.value}')>"


class IssueComment(Base):
    """Issue comment model"""
    
    __tablename__ = "issue_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    
    # Mention support
    mentioned_users = Column(String(500))  # Comma separated user IDs
    
    # Reactions (JSON string for simplicity)
    reactions = Column(Text)  # JSON: {"👍": [user_ids], "👎": [user_ids]}
    
    # Edit tracking
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    issue = relationship("Issue", back_populates="comments")
    user = relationship("User")
    
    def __repr__(self):
        return f"<IssueComment(id={self.id}, issue_id={self.issue_id})>"


class IssueAttachment(Base):
    """Issue attachment model"""
    
    __tablename__ = "issue_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    issue = relationship("Issue")
    user = relationship("User")
    
    def __repr__(self):
        return f"<IssueAttachment(id={self.id}, filename='{self.filename}')>"