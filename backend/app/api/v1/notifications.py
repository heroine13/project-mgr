"""
通知管理 API 端点
提供通知列表、标记已读、偏好设置等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.notification import Notification, NotificationPreference, EmailQueue
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/notifications", tags=["通知管理"])
security = HTTPBearer()


# === Pydantic Schema ===

class NotificationCreate(BaseModel):
    """创建通知的请求体"""
    user_id: int
    type: str
    title: str
    content: Optional[str] = None
    related_data: Optional[dict] = None
    link: Optional[str] = None


class NotificationResponse(BaseModel):
    """通知响应"""
    id: int
    user_id: int
    type: str
    title: str
    content: Optional[str]
    related_data: Optional[dict]
    link: Optional[str]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """通知偏好更新"""
    email_task_created: Optional[bool] = None
    email_task_updated: Optional[bool] = None
    email_task_assigned: Optional[bool] = None
    email_task_completed: Optional[bool] = None
    email_comment_mentioned: Optional[bool] = None
    email_comment_replied: Optional[bool] = None
    email_project_updated: Optional[bool] = None
    site_task_created: Optional[bool] = None
    site_task_updated: Optional[bool] = None
    site_task_assigned: Optional[bool] = None
    site_task_completed: Optional[bool] = None
    site_comment_mentioned: Optional[bool] = None
    site_comment_replied: Optional[bool] = None
    site_project_updated: Optional[bool] = None
    email_frequency: Optional[str] = None


class NotificationPreferenceResponse(BaseModel):
    """通知偏好响应"""
    id: int
    user_id: int
    email_task_created: bool
    email_task_updated: bool
    email_task_assigned: bool
    email_task_completed: bool
    email_comment_mentioned: bool
    email_comment_replied: bool
    email_project_updated: bool
    site_task_created: bool
    site_task_updated: bool
    site_task_assigned: bool
    site_task_completed: bool
    site_comment_mentioned: bool
    site_comment_replied: bool
    site_project_updated: bool
    email_frequency: str
    
    class Config:
        from_attributes = True


# === API 端点 ===

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的通知列表
    """
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_deleted == False
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return notifications


@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取未读通知数量
    """
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
        Notification.is_deleted == False
    ).count()
    
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记单条通知为已读
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    notification.is_read = True
    notification.read_at = datetime.now()
    db.commit()
    
    return {"message": "通知已标记为已读"}


@router.post("/read-all")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记所有通知为已读
    """
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
        Notification.is_deleted == False
    ).update({
        "is_read": True,
        "read_at": datetime.now()
    })
    db.commit()
    
    return {"message": "所有通知已标记为已读"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除单条通知
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    notification.is_deleted = True
    db.commit()
    
    return {"message": "通知已删除"}


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的通知偏好设置
    """
    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        # 如果不存在，创建默认偏好设置
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
        db.commit()
        db.refresh(preference)
    
    return preference


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_notification_preferences(
    preferences: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新当前用户的通知偏好设置
    """
    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        # 如果不存在，创建新的偏好设置
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
    
    # 更新非空字段
    update_data = preferences.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(preference, key, value)
    
    preference.updated_at = datetime.now()
    db.commit()
    db.refresh(preference)
    
    return preference


# === 便捷函数：创建通知 ===

def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    content: Optional[str] = None,
    related_data: Optional[dict] = None,
    link: Optional[str] = None
):
    """
    创建通知的便捷函数
    """
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        content=content,
        related_data=related_data,
        link=link
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification