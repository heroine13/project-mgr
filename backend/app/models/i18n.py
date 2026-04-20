"""
Internationalization (i18n) Management Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .user import Base


class Language(Base):
    """Supported languages"""
    
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)  # e.g., 'en', 'zh-CN'
    name = Column(String(100), nullable=False)  # e.g., 'English', '简体中文'
    native_name = Column(String(100))  # e.g., 'English', '中文'
    is_default = Column(Boolean, default=False)  # Default language
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    translations = relationship("Translation", back_populates="language")
    
    def __repr__(self):
        return f"<Language(code='{self.code}', name='{self.name}')>"


class TranslationKey(Base):
    """Translation keys (like 'dashboard.welcome')"""
    
    __tablename__ = "translation_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)  # Description for translators
    module = Column(String(100))  # e.g., 'common', 'dashboard', 'tasks'
    is_approved = Column(Boolean, default=False)  # Approved by admin
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    translations = relationship("Translation", back_populates="key_obj")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<TranslationKey(key='{self.key}')>"


class Translation(Base):
    """Translation values for each language"""
    
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(Integer, ForeignKey("translation_keys.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    
    value = Column(Text, nullable=False)  # The translated text
    is_machine_translated = Column(Boolean, default=False)  # From AI/机器翻译
    is_reviewed = Column(Boolean, default=False)  # Reviewed by human
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    key_obj = relationship("TranslationKey", back_populates="translations")
    language = relationship("Language", back_populates="translations")
    creator = relationship("User", foreign_keys=[created_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<Translation(key_id={self.key_id}, lang_id={self.language_id})>"