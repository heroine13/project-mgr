"""
Audit Log API Endpoints - System Operation Tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.crud.user_mgmt import create_audit_log as _create_audit_log
from app.models.user import User
from app.models.audit import AuditLog, AuditLogSummary

router = APIRouter(prefix="/audit", tags=["审计日志"])


# === Schemas ===

class AuditLogResponse(BaseModel):
    """Audit log response"""
    id: int
    user_id: int
    username: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[int]
    old_value: Optional[dict]
    new_value: Optional[dict]
    ip_address: Optional[str]
    description: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditStatsResponse(BaseModel):
    """Audit statistics response"""
    total: int
    today: int
    this_week: int
    this_month: int
    by_action: dict
    by_resource: dict
    top_users: List[dict]


# === API Endpoints ===

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs with filters"""
    # Only admin can view audit logs
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以查看审计日志")
    
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if resource_id:
        query = query.filter(AuditLog.resource_id == resource_id)
    if status:
        query = query.filter(AuditLog.status == status)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    # Order by created_at descending
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()
    
    return {"logs": logs, "total": total, "page": skip // limit + 1, "page_size": limit}


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single audit log entry"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以查看审计日志")
    
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="审计日志不存在")
    
    return log


@router.get("/stats", response_model=AuditStatsResponse)
async def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit log statistics"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以查看审计统计")
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total count
    total = db.query(AuditLog).count()
    
    # Today count
    today = db.query(AuditLog).filter(AuditLog.created_at >= today_start).count()
    
    # This week count
    this_week = db.query(AuditLog).filter(AuditLog.created_at >= week_start).count()
    
    # This month count
    this_month = db.query(AuditLog).filter(AuditLog.created_at >= month_start).count()
    
    # By action
    by_action = {}
    actions = db.query(AuditLog.action, db.func.count(AuditLog.id)).group_by(AuditLog.action).all()
    for action, count in actions:
        by_action[action] = count
    
    # By resource type
    by_resource = {}
    resources = db.query(AuditLog.resource_type, db.func.count(AuditLog.id)).group_by(AuditLog.resource_type).all()
    for resource, count in resources:
        by_resource[resource] = count
    
    # Top users
    top_users = []
    users_stats = (
        db.query(AuditLog.user_id, AuditLog.username, db.func.count(AuditLog.id).label('count'))
        .group_by(AuditLog.user_id, AuditLog.username)
        .order_by(db.func.count(AuditLog.id).desc())
        .limit(10)
        .all()
    )
    for user_id, username, count in users_stats:
        top_users.append({
            "user_id": user_id,
            "username": username,
            "count": count
        })
    
    return {
        "total": total,
        "today": today,
        "this_week": this_week,
        "this_month": this_month,
        "by_action": by_action,
        "by_resource": by_resource,
        "top_users": top_users
    }


@router.get("/export")
async def export_audit_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export audit logs"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以导出审计日志")
    
    query = db.query(AuditLog)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    logs = query.order_by(AuditLog.created_at.desc()).all()
    
    if format == "json":
        return {
            "exported_at": datetime.now().isoformat(),
            "count": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "username": log.username,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "description": log.description,
                    "status": log.status,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
        }
    
    # CSV format
    csv_lines = ["ID,User,Action,Resource Type,Resource ID,Description,Status,IP,Created At"]
    for log in logs:
        csv_lines.append(
            f"{log.id},{log.username},{log.action},{log.resource_type},{log.resource_id or ''},"
            f"\"{log.description or ''}\",{log.status},{log.ip_address or ''},{log.created_at.isoformat()}"
        )
    
    return "\n".join(csv_lines)


@router.delete("/logs/cleanup")
async def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up old audit logs"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以清理审计日志")
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    deleted = db.query(AuditLog).filter(AuditLog.created_at < cutoff_date).delete()
    db.commit()
    
    return {
        "status": "success",
        "message": f"已删除 {deleted} 条 {days} 天前的审计日志",
        "deleted_count": deleted
    }