"""
Audit Log Service - System Operation Tracking
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.audit import AuditLog, AuditLogSummary
from app.models.user import User
import json


class AuditService:
    """Service for audit logging"""
    
    @staticmethod
    def log_action(
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        description: Optional[str] = None,
        status: str = "success"
    ):
        """Log an action to the audit log"""
        # Get username
        user = db.query(User).filter(User.id == user_id).first()
        username = user.username if user else "unknown"
        
        # Create audit log entry
        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description,
            status=status
        )
        
        db.add(audit_log)
        db.commit()
        
        return audit_log
    
    @staticmethod
    def log_create(
        db: Session,
        user_id: int,
        resource_type: str,
        resource_id: int,
        new_value: dict,
        **kwargs
    ):
        """Log a create action"""
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action="create",
            resource_type=resource_type,
            resource_id=resource_id,
            new_value=new_value,
            description=f"Created {resource_type} #{resource_id}",
            **kwargs
        )
    
    @staticmethod
    def log_update(
        db: Session,
        user_id: int,
        resource_type: str,
        resource_id: int,
        old_value: dict,
        new_value: dict,
        **kwargs
    ):
        """Log an update action"""
        # Calculate changed fields
        changed_fields = []
        for key in new_value:
            if old_value.get(key) != new_value.get(key):
                changed_fields.append(key)
        
        description = f"Updated {resource_type} #{resource_id}: {', '.join(changed_fields)}" if changed_fields else f"Updated {resource_type} #{resource_id}"
        
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action="update",
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            description=description,
            **kwargs
        )
    
    @staticmethod
    def log_delete(
        db: Session,
        user_id: int,
        resource_type: str,
        resource_id: int,
        old_value: dict,
        **kwargs
    ):
        """Log a delete action"""
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action="delete",
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            description=f"Deleted {resource_type} #{resource_id}",
            **kwargs
        )
    
    @staticmethod
    def log_login(
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success"
    ):
        """Log a login action"""
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action="login",
            resource_type="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            description="User logged in",
            status=status
        )
    
    @staticmethod
    def log_logout(
        db: Session,
        user_id: int,
        **kwargs
    ):
        """Log a logout action"""
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action="logout",
            resource_type="auth",
            description="User logged out",
            **kwargs
        )


# Decorator for automatic audit logging
def audit_log(action: str, resource_type: str):
    """Decorator for automatic audit logging"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would need db session and user context
            # Simplified implementation
            return func(*args, **kwargs)
        return wrapper
    return decorator