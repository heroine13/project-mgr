"""
Resource Management Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .user import Base


class ResourceType(PyEnum):
    """Resource type enumeration"""
    HUMAN = "human"        # 人力
    MATERIAL = "material"  # 物料
    EQUIPMENT = "equipment"  # 设备
    OTHER = "other"        # 其他


class AllocationStatus(PyEnum):
    """Allocation status"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Resource(Base):
    """Resource model for tracking resources"""
    
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    resource_type = Column(Enum(ResourceType), default=ResourceType.HUMAN)
    description = Column(Text)
    
    # Human resources
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to user if human
    
    # Cost info
    unit_cost = Column(Float, default=0)  # Cost per unit/hour
    currency = Column(String(10), default="CNY")
    
    # Availability
    is_available = Column(Boolean, default=True)
    max_capacity = Column(Float, default=0)  # Max hours per month
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    allocations = relationship("ResourceAllocation", back_populates="resource")
    
    def __repr__(self):
        return f"<Resource(id={self.id}, name='{self.name}', type='{self.resource_type.value}')>"


class ResourceAllocation(Base):
    """Resource allocation to projects/tasks"""
    
    __tablename__ = "resource_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # Optional task link
    
    # Allocation details
    allocation_type = Column(String(50))  # percentage, hours, units
    allocated_value = Column(Float, default=0)  # 50%, 20 hours, etc.
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # Cost tracking
    actual_usage = Column(Float, default=0)
    actual_cost = Column(Float, default=0)
    budgeted_cost = Column(Float, default=0)
    
    # Status
    status = Column(Enum(AllocationStatus), default=AllocationStatus.PENDING)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    resource = relationship("Resource", back_populates="allocations")
    project = relationship("Project")
    task = relationship("Task")
    
    def __repr__(self):
        return f"<ResourceAllocation(id={self.id}, resource_id={self.resource_id}, project_id={self.project_id})>"


class CostRecord(Base):
    """Cost record for tracking expenses"""
    
    __tablename__ = "cost_records"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    # Cost info
    category = Column(String(100))  # labor, material, equipment, other
    description = Column(Text)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="CNY")
    
    # Date info
    cost_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Approval
    is_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project")
    task = relationship("Task")
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<CostRecord(id={self.id}, project_id={self.project_id}, amount={self.amount})>"