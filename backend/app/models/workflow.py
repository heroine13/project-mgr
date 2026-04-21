"""
Workflow Models - Approval Workflow System
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from ..models.user import Base


class WorkflowStatus(PyEnum):
    """Workflow status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"


class ApprovalStatus(PyEnum):
    """Approval request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Workflow(Base):
    """Workflow definition"""
    
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    entity_type = Column(String(50), nullable=False)  # task, project, issue, etc.
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    
    # JSON configuration for workflow steps
    steps_config = Column(JSON, nullable=True)  # Array of step configurations
    
    # Owner
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    approval_requests = relationship("ApprovalRequest", back_populates="workflow", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workflow(id={self.id}, name='{self.name}', entity_type='{self.entity_type}')>"


class ApprovalRequest(Base):
    """Approval request for workflow"""
    
    __tablename__ = "approval_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to workflow
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    
    # Entity being approved (task, project, issue, etc.)
    entity_type = Column(String(50), nullable=False)  # task, project, issue
    entity_id = Column(Integer, nullable=False)
    
    # Current step index
    current_step = Column(Integer, default=0)
    
    # Status
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    
    # Requester
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Request data snapshot
    request_data = Column(JSON, nullable=True)
    
    # Result
    result = Column(Text, nullable=True)  # Approval comment
    decided_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="approval_requests")
    requester = relationship("User", foreign_keys=[requested_by])
    approvals = relationship("ApprovalAction", back_populates="request", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ApprovalRequest(id={self.id}, entity_type='{self.entity_type}', status='{self.status.value}')>"


class ApprovalAction(Base):
    """Individual approval action (per step)"""
    
    __tablename__ = "approval_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to approval request
    request_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=False)
    
    # Step number
    step = Column(Integer, nullable=False)
    
    # Approver
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Action
    action = Column(String(20), nullable=False)  # approve, reject
    comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    request = relationship("ApprovalRequest", back_populates="approvals")
    approver = relationship("User", foreign_keys=[approver_id])
    
    def __repr__(self):
        return f"<ApprovalAction(id={self.id}, step={self.step}, action='{self.action}')>"


class WorkflowTemplate(Base):
    """Pre-defined workflow templates"""
    
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    entity_type = Column(String(50), nullable=False)
    
    # Template steps (JSON array)
    steps = Column(JSON, nullable=False)
    
    # Is system template (cannot be deleted)
    is_system = Column(Boolean, default=False)
    
    # Owner
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<WorkflowTemplate(id={self.id}, name='{self.name}')>"