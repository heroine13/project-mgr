"""
Enhanced Notification Service - Real-time notifications with WebSocket
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationPreference
from app.models.user import User
import json


class EnhancedNotificationService:
    """Enhanced notification service with aggregation and real-time support"""
    
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        notification_type: str,
        title: str,
        content: Optional[str] = None,
        related_data: Optional[dict] = None,
        link: Optional[str] = None,
        priority: str = "normal"  # normal, high, urgent
    ):
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            content=content,
            related_data=related_data,
            link=link,
            is_read=False
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def get_notification_summary(
        db: Session,
        user_id: int,
        days: int = 7
    ):
        """Get notification summary for user"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Get counts by type
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_deleted == False,
            Notification.created_at >= start_date
        ).all()
        
        summary = {
            "total": len(notifications),
            "unread": sum(1 for n in notifications if not n.is_read),
            "by_type": {},
            "recent": []
        }
        
        for n in notifications:
            # Count by type
            if n.type not in summary["by_type"]:
                summary["by_type"][n.type] = {"total": 0, "unread": 0}
            summary["by_type"][n.type]["total"] += 1
            if not n.is_read:
                summary["by_type"][n.type]["unread"] += 1
        
        # Get 5 most recent
        recent = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_deleted == False
        ).order_by(Notification.created_at.desc()).limit(5).all()
        
        summary["recent"] = [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "content": n.content,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
                "link": n.link
            }
            for n in recent
        ]
        
        return summary
    
    @staticmethod
    def mark_all_as_read(
        db: Session,
        user_id: int
    ):
        """Mark all notifications as read"""
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_deleted == False
        ).update({
            "is_read": True,
            "read_at": datetime.now()
        })
        
        db.commit()
        return {"marked_count": count}
    
    @staticmethod
    def get_unread_by_type(
        db: Session,
        user_id: int,
        notification_type: Optional[str] = None
    ):
        """Get unread notifications grouped by type"""
        query = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_deleted == False
        )
        
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        
        notifications = query.order_by(Notification.created_at.desc()).all()
        
        # Group by type
        grouped = {}
        for n in notifications:
            if n.type not in grouped:
                grouped[n.type] = []
            grouped[n.type].append({
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "related_data": n.related_data,
                "link": n.link,
                "created_at": n.created_at.isoformat()
            })
        
        return grouped
    
    @staticmethod
    def delete_old_notifications(
        db: Session,
        user_id: int,
        days: int = 30
    ):
        """Delete old read notifications"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == True,
            Notification.is_deleted == False,
            Notification.created_at < cutoff_date
        ).update({"is_deleted": True})
        
        db.commit()
        return {"deleted_count": count}


# WebSocket notification helper
class NotificationWebSocket:
    """Helper for sending real-time notifications via WebSocket"""
    
    @staticmethod
    def prepare_notification_message(notification: Notification) -> dict:
        """Prepare notification message for WebSocket"""
        return {
            "type": "notification",
            "data": {
                "id": notification.id,
                "type": notification.type,
                "title": notification.title,
                "content": notification.content,
                "related_data": notification.related_data,
                "link": notification.link,
                "created_at": notification.created_at.isoformat()
            }
        }
    
    @staticmethod
    def prepare_batch_message(notifications: List[Notification]) -> dict:
        """Prepare batch notification message"""
        return {
            "type": "notification_batch",
            "data": {
                "count": len(notifications),
                "notifications": [
                    {
                        "id": n.id,
                        "type": n.type,
                        "title": n.title,
                        "created_at": n.created_at.isoformat()
                    }
                    for n in notifications
                ]
            }
        }