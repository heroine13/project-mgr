"""System settings service - 系统设置读写服务"""

import json
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.system_setting import SystemSetting


class SystemSettingsService:
    """系统设置服务"""

    @staticmethod
    def get_all(db: Session) -> Dict[str, str]:
        """获取所有设置"""
        settings = db.query(SystemSetting).all()
        return {s.key: s.value or "" for s in settings}

    @staticmethod
    def get_by_category(db: Session, category: str) -> Dict[str, str]:
        """按分类获取设置"""
        settings = db.query(SystemSetting).filter(SystemSetting.category == category).all()
        return {s.key: s.value or "" for s in settings}

    @staticmethod
    def get_ai_settings(db: Session) -> Dict[str, str]:
        """获取AI配置"""
        return SystemSettingsService.get_by_category(db, "ai")

    @staticmethod
    def save(db: Session, key: str, value: str, description: str = "", category: str = "general") -> SystemSetting:
        """保存单个设置（upsert）"""
        existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if existing:
            existing.value = value
            existing.description = description
            existing.category = category
        else:
            existing = SystemSetting(key=key, value=value, description=description, category=category)
            db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    @staticmethod
    def save_batch(db: Session, settings_data: Dict[str, str], category: str = "ai") -> None:
        """批量保存设置（先删后插）"""
        db.query(SystemSetting).filter(
            SystemSetting.category == category
        ).delete()
        for key, value in settings_data.items():
            db.add(SystemSetting(key=key, value=str(value), category=category))
        db.commit()

    @staticmethod
    def delete(db: Session, key: str) -> bool:
        """删除设置"""
        existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if existing:
            db.delete(existing)
            db.commit()
            return True
        return False
