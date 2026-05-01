"""
User Management Models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from enum import Enum as PyEnum
from .user import Base


class UserStatus(PyEnum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Role(Base):
    """User roles"""
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(String(1000))  # JSON string of permissions
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"<Role(name='{self.name}')>"


class UserProfile(Base):
    """Extended user profile"""
    
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)
    
    # Profile info
    avatar = Column(String(500))
    phone = Column(String(20))
    department = Column(String(100))
    position = Column(String(100))
    location = Column(String(200))
    
    # Preferences
    theme = Column(String(20), default="light")
    language = Column(String(10), default="zh-CN")
    timezone = Column(String(50), default="Asia/Shanghai")
    
    # Notification preferences
    email_notification = Column(Boolean, default=True)
    push_notification = Column(Boolean, default=True)
    
    # Stats
    last_login_at = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id})>"


class AuditLog(Base):
    """Audit log for user actions"""
    
    __tablename__ = "user_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100))  # e.g., 'project', 'task'
    resource_id = Column(Integer)
    details = Column(String(1000))  # JSON string of details
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', user_id={self.user_id})>"


class Department(Base):
    """Department/Organization unit"""
    
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=True)
    parent_id = Column(Integer, nullable=True)  # For hierarchical structure
    description = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Self-referential for hierarchy
    children = relationship("Department", backref=backref("parent", remote_side=[id]))
    
    def __repr__(self):
        return f"<Department(name='{self.name}')>"