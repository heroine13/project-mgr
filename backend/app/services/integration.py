"""
第三方集成服务
支持日历和邮件集成
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ==================== 日历集成 ====================

class CalendarProvider(Enum):
    """日历提供商"""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    CALDAV = "caldav"


class CalendarEvent:
    """日历事件"""
    
    def __init__(
        self,
        id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        location: str = "",
        attendees: List[str] = None,
        reminder: int = 15  # 提前提醒分钟数
    ):
        self.id = id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.location = location
        self.attendees = attendees or []
        self.reminder = reminder
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "start": self.start_time.isoformat(),
            "end": self.end_time.isoformat(),
            "description": self.description,
            "location": self.location,
            "attendees": self.attendees,
            "reminder": self.reminder
        }


class CalendarIntegration:
    """日历集成服务"""
    
    def __init__(self, provider: CalendarProvider = CalendarProvider.CALDAV):
        self.provider = provider
        self.events: List[CalendarEvent] = []
        self._initialize_demo_events()
    
    def _initialize_demo_events(self):
        """初始化演示事件"""
        now = datetime.now()
        
        # 添加一些示例事件
        self.events = [
            CalendarEvent(
                id="evt_001",
                title="项目进度会议",
                start_time=now + timedelta(hours=2),
                end_time=now + timedelta(hours=3),
                description="讨论本周项目进度",
                location="会议室A",
                attendees=["张三", "李四", "王五"],
                reminder=15
            ),
            CalendarEvent(
                id="evt_002",
                title="任务截止: UI设计",
                start_time=now + timedelta(days=1),
                end_time=now + timedelta(days=1, hours=1),
                description="完成项目UI设计稿",
                reminder=60
            ),
            CalendarEvent(
                id="evt_003",
                title="代码评审",
                start_time=now + timedelta(days=2),
                end_time=now + timedelta(days=2, hours=1),
                description="评审本周开发的功能",
                attendees=["开发团队"],
                reminder=30
            )
        ]
    
    def get_events(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        keywords: str = None
    ) -> List[Dict]:
        """获取日历事件"""
        events = self.events
        
        # 按日期过滤
        if start_date:
            events = [e for e in events if e.start_time >= start_date]
        if end_date:
            events = [e for e in events if e.start_time <= end_date]
        
        # 按关键词搜索
        if keywords:
            keyword = keywords.lower()
            events = [e for e in events if 
                     keyword in e.title.lower() or 
                     keyword in e.description.lower()]
        
        return [e.to_dict() for e in events]
    
    def create_event(self, event_data: Dict) -> Dict:
        """创建日历事件"""
        now = datetime.now()
        
        event = CalendarEvent(
            id=f"evt_{len(self.events) + 1:03d}",
            title=event_data.get("title", "新事件"),
            start_time=event_data.get("start_time", now),
            end_time=event_data.get("end_time", now + timedelta(hours=1)),
            description=event_data.get("description", ""),
            location=event_data.get("location", ""),
            attendees=event_data.get("attendees", []),
            reminder=event_data.get("reminder", 15)
        )
        
        self.events.append(event)
        logger.info(f"创建日历事件: {event.title}")
        
        return event.to_dict()
    
    def update_event(self, event_id: str, event_data: Dict) -> Optional[Dict]:
        """更新日历事件"""
        for event in self.events:
            if event.id == event_id:
                if "title" in event_data:
                    event.title = event_data["title"]
                if "description" in event_data:
                    event.description = event_data["description"]
                if "location" in event_data:
                    event.location = event_data["location"]
                if "start_time" in event_data:
                    event.start_time = event_data["start_time"]
                if "end_time" in event_data:
                    event.end_time = event_data["end_time"]
                
                logger.info(f"更新日历事件: {event.title}")
                return event.to_dict()
        
        return None
    
    def delete_event(self, event_id: str) -> bool:
        """删除日历事件"""
        for i, event in enumerate(self.events):
            if event.id == event_id:
                self.events.pop(i)
                logger.info(f"删除日历事件: {event_id}")
                return True
        return False
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict]:
        """获取即将到来的事件"""
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        return self.get_events(start_date=now, end_date=end_date)


# ==================== 邮件集成 ====================

class EmailProvider(Enum):
    """邮件提供商"""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"


class EmailMessage:
    """邮件消息"""
    
    def __init__(
        self,
        id: str,
        to: List[str],
        subject: str,
        body: str,
        cc: List[str] = None,
        bcc: List[str] = None,
        attachments: List[str] = None,
        html: bool = False
    ):
        self.id = id
        self.to = to
        self.subject = subject
        self.body = body
        self.cc = cc or []
        self.bcc = bcc or []
        self.attachments = attachments or []
        self.html = html
        self.sent_at = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "to": self.to,
            "subject": self.subject,
            "body": self.body,
            "cc": self.cc,
            "bcc": self.bcc,
            "attachments": self.attachments,
            "html": self.html,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None
        }


class EmailIntegration:
    """邮件集成服务"""
    
    def __init__(self, provider: EmailProvider = EmailProvider.SMTP):
        self.provider = provider
        self.sent_emails: List[EmailMessage] = []
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载邮件配置"""
        return {
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_user": "noreply@example.com",
            "from_email": "项目管理系统 <noreply@example.com>",
            "from_name": "项目管理系统"
        }
    
    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: List[str] = None,
        bcc: List[str] = None,
        attachments: List[str] = None,
        html: bool = False
    ) -> Dict:
        """发送邮件"""
        message = EmailMessage(
            id=f"email_{len(self.sent_emails) + 1:03d}",
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            html=html
        )
        
        # 模拟发送
        message.sent_at = datetime.now()
        self.sent_emails.append(message)
        
        logger.info(f"发送邮件: {subject} -> {', '.join(to)}")
        
        return {
            "success": True,
            "message_id": message.id,
            "sent_at": message.sent_at.isoformat()
        }
    
    def send_task_notification(
        self,
        to: List[str],
        task_title: str,
        task_status: str,
        task_url: str = ""
    ) -> Dict:
        """发送任务通知邮件"""
        subject = f"[任务通知] {task_title} - {task_status}"
        
        body = f"""
任务状态更新通知

任务: {task_title}
状态: {task_status}
{"查看详情: " + task_url if task_url else ""}

---
此邮件由项目管理系统自动发送
        """
        
        return self.send_email(
            to=to,
            subject=subject,
            body=body.strip()
        )
    
    def send_project_update(
        self,
        to: List[str],
        project_name: str,
        update_content: str
    ) -> Dict:
        """发送项目更新邮件"""
        subject = f"[项目更新] {project_name}"
        
        body = f"""
项目更新通知

项目: {project_name}

{update_content}

---
此邮件由项目管理系统自动发送
        """
        
        return self.send_email(
            to=to,
            subject=subject,
            body=body.strip()
        )
    
    def get_sent_emails(self, limit: int = 50) -> List[Dict]:
        """获取已发送邮件列表"""
        return [email.to_dict() for email in self.sent_emails[-limit:]]


# ==================== 导出单例 ====================

calendar = CalendarIntegration()
email_integration = EmailIntegration()