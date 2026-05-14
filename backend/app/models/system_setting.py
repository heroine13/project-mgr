"""System settings model - 系统配置存储"""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class SystemSetting(Base):
    """系统设置表"""
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True, comment="配置键名")
    value = Column(Text, nullable=True, comment="配置值")
    description = Column(String(255), nullable=True, comment="描述")
    category = Column(String(50), nullable=True, comment="分类")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
