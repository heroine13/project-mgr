"""
第三方集成 API 接口
提供日历和邮件集成接口
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.services.integration import calendar, email_integration, CalendarProvider, EmailProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/integration", tags=["第三方集成"])


# ==================== 请求模型 ====================

class CalendarEventCreate(BaseModel):
    """创建日历事件请求"""
    title: str
    start_time: datetime
    end_time: datetime
    description: str = ""
    location: str = ""
    attendees: List[str] = []
    reminder: int = 15


class CalendarEventUpdate(BaseModel):
    """更新日历事件请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class EmailSendRequest(BaseModel):
    """发送邮件请求"""
    to: List[str]
    subject: str
    body: str
    cc: List[str] = []
    bcc: List[str] = []
    html: bool = False


class TaskNotificationRequest(BaseModel):
    """任务通知请求"""
    to: List[str]
    task_title: str
    task_status: str
    task_url: str = ""


class ProjectUpdateRequest(BaseModel):
    """项目更新通知请求"""
    to: List[str]
    project_name: str
    update_content: str


# ==================== 日历接口 ====================

@router.get("/calendar/events", summary="获取日历事件")
async def get_calendar_events(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keywords: Optional[str] = Query(None, description="搜索关键词")
):
    """获取日历事件列表"""
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        events = calendar.get_events(start_date=start, end_date=end, keywords=keywords)
        
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "total": len(events),
                "events": events
            }
        }
    except Exception as e:
        logger.error(f"获取日历事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar/events/upcoming", summary="获取即将到来的事件")
async def get_upcoming_events(days: int = Query(7, ge=1, le=30)):
    """获取即将到来的日历事件"""
    try:
        events = calendar.get_upcoming_events(days=days)
        
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "days": days,
                "total": len(events),
                "events": events
            }
        }
    except Exception as e:
        logger.error(f"获取即将到来的事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar/events", summary="创建日历事件")
async def create_calendar_event(event: CalendarEventCreate):
    """创建新的日历事件"""
    try:
        event_data = event.model_dump()
        event_data["start_time"] = datetime.fromisoformat(str(event_data["start_time"]))
        event_data["end_time"] = datetime.fromisoformat(str(event_data["end_time"]))
        
        created_event = calendar.create_event(event_data)
        
        return {
            "code": 0,
            "msg": "事件创建成功",
            "data": created_event
        }
    except Exception as e:
        logger.error(f"创建日历事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/calendar/events/{event_id}", summary="更新日历事件")
async def update_calendar_event(event_id: str, event: CalendarEventUpdate):
    """更新日历事件"""
    try:
        event_data = {k: v for k, v in event.model_dump().items() if v is not None}
        
        updated_event = calendar.update_event(event_id, event_data)
        
        if updated_event:
            return {
                "code": 0,
                "msg": "事件更新成功",
                "data": updated_event
            }
        raise HTTPException(status_code=404, detail="事件不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新日历事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/calendar/events/{event_id}", summary="删除日历事件")
async def delete_calendar_event(event_id: str):
    """删除日历事件"""
    try:
        success = calendar.delete_event(event_id)
        
        if success:
            return {
                "code": 0,
                "msg": "事件删除成功"
            }
        raise HTTPException(status_code=404, detail="事件不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除日历事件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 邮件接口 ====================

@router.post("/email/send", summary="发送邮件")
async def send_email(email: EmailSendRequest):
    """发送邮件"""
    try:
        result = email_integration.send_email(
            to=email.to,
            subject=email.subject,
            body=email.body,
            cc=email.cc,
            bcc=email.bcc,
            html=email.html
        )
        
        return {
            "code": 0,
            "msg": "邮件发送成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/task-notification", summary="发送任务通知")
async def send_task_notification(notification: TaskNotificationRequest):
    """发送任务通知邮件"""
    try:
        result = email_integration.send_task_notification(
            to=notification.to,
            task_title=notification.task_title,
            task_status=notification.task_status,
            task_url=notification.task_url
        )
        
        return {
            "code": 0,
            "msg": "任务通知发送成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"发送任务通知失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/project-update", summary="发送项目更新通知")
async def send_project_update_notification(notification: ProjectUpdateRequest):
    """发送项目更新邮件"""
    try:
        result = email_integration.send_project_update(
            to=notification.to,
            project_name=notification.project_name,
            update_content=notification.update_content
        )
        
        return {
            "code": 0,
            "msg": "项目更新通知发送成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"发送项目更新通知失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/email/sent", summary="获取已发送邮件")
async def get_sent_emails(limit: int = Query(50, ge=1, le=100)):
    """获取已发送邮件列表"""
    try:
        emails = email_integration.get_sent_emails(limit=limit)
        
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "total": len(emails),
                "emails": emails
            }
        }
    except Exception as e:
        logger.error(f"获取已发送邮件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 配置接口 ====================

@router.get("/config/calendar", summary="获取日历配置")
async def get_calendar_config():
    """获取日历集成配置"""
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "provider": CalendarProvider.CALDAV.value,
            "supported_providers": [p.value for p in CalendarProvider]
        }
    }


@router.get("/config/email", summary="获取邮件配置")
async def get_email_config():
    """获取邮件集成配置"""
    config = email_integration.config
    # 隐藏敏感信息
    config["smtp_password"] = "***"
    
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "provider": EmailProvider.SMTP.value,
            "config": config,
            "supported_providers": [p.value for p in EmailProvider]
        }
    }