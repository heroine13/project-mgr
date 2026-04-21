"""
Audit Log Models - System Operation Tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..models.user import Base


class AuditLog(Base):
    """Audit log for tracking all system operations"""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User who performed the action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    username = Column(String(100))  # Cache username for display
    
    # Action details
    action = Column(String(50), nullable=False, index=True)  # create, update, delete, login, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # task, project, user, etc.
    resource_id = Column(Integer, nullable=True, index=True)
    
    # Changes (JSON)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    
    # Additional info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default="success")  # success, failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    # Table indexes for query performance
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_created_action', 'created_at', 'action'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}', resource='{self.resource_type}:{self.resource_id}')>"


class AuditLogSummary(Base):
    """Daily audit log summary for quick stats"""
    
    __tablename__ = "audit_log_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)
    
    # Counts
    total_actions = Column(Integer, default=0)
    login_count = Column(Integer, default=0)
    create_count = Column(Integer, default=0)
    update_count = Column(Integer, default=0)
    delete_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Unique users
    unique_users = Column(Integer, default=0)
    
    # Most active user
    most_active_user_id = Column(Integer, nullable=True)
    most_active_user_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AuditLogSummary(date='{self.date}', total={self.total_actions})>"