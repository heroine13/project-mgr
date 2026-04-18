"""
通知数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Notification(Base):
    """通知模型"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 通知类型: task_created, task_updated, task_assigned, task_completed, 
    #           project_created, project_updated, comment_mentioned, comment_replied
    type = Column(String(50), nullable=False, index=True)
    
    # 通知标题和内容
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    
    # 关联数据 (JSON格式存储关联的ID和类型)
    # 例如: {"task_id": 1, "project_id": 2}
    related_data = Column(JSON, nullable=True)
    
    # 链接 (点击通知跳转的URL)
    link = Column(String(500), nullable=True)
    
    # 状态
    is_read = Column(Boolean, default=False, index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关联关系
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"


class NotificationPreference(Base):
    """用户通知偏好设置"""
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # 邮件通知开关
    email_task_created = Column(Boolean, default=True)
    email_task_updated = Column(Boolean, default=True)
    email_task_assigned = Column(Boolean, default=True)
    email_task_completed = Column(Boolean, default=False)
    email_comment_mentioned = Column(Boolean, default=True)
    email_comment_replied = Column(Boolean, default=True)
    email_project_updated = Column(Boolean, default=True)
    
    # 站内通知开关
    site_task_created = Column(Boolean, default=True)
    site_task_updated = Column(Boolean, default=True)
    site_task_assigned = Column(Boolean, default=True)
    site_task_completed = Column(Boolean, default=True)
    site_comment_mentioned = Column(Boolean, default=True)
    site_comment_replied = Column(Boolean, default=True)
    site_project_updated = Column(Boolean, default=True)
    
    # 通知频率: instant, daily, weekly
    email_frequency = Column(String(20), default="instant")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="notification_preference")
    
    def __repr__(self):
        return f"<NotificationPreference user_id={self.user_id}>"


class EmailQueue(Base):
    """邮件发送队列"""
    __tablename__ = "email_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 邮件类型
    email_type = Column(String(50), nullable=False)
    
    # 收件人信息
    to_email = Column(String(200), nullable=False)
    to_name = Column(String(100), nullable=True)
    
    # 邮件内容
    subject = Column(String(200), nullable=False)
    html_content = Column(Text, nullable=True)
    plain_content = Column(Text, nullable=True)
    
    # 发送状态: pending, sent, failed
    status = Column(String(20), default="pending", index=True)
    
    # 重试次数
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # 错误信息
    error_message = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<EmailQueue {self.id}: {self.email_type} -> {self.to_email}>"