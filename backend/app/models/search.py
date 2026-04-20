"""
Document Category and Search Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .user import Base
from pydantic import BaseModel  # For reference only, using SQLAlchemy models


class DocumentCategory(Base):
    """Document category for classification"""
    
    __tablename__ = "document_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("document_categories.id"), nullable=True)
    color = Column(String(20))  # Color code for UI
    icon = Column(String(50))  # Icon name
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    parent = relationship("DocumentCategory", remote_side=[id], back_populates="children")
    children = relationship("DocumentCategory", back_populates="parent")
    documents = relationship("Document", back_populates="category")
    
    def __repr__(self):
        return f"<DocumentCategory(name='{self.name}')>"


class SearchHistory(Base):
    """User search history"""
    
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(String(500), nullable=False)
    filters = Column(Text)  # JSON string of filters used
    result_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<SearchHistory(user_id={self.user_id}, query='{self.query}')>"


class SavedSearch(Base):
    """Saved search queries"""
    
    __tablename__ = "saved_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    query = Column(String(500), nullable=False)
    filters = Column(Text)  # JSON string
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<SavedSearch(name='{self.name}', user_id={self.user_id})>"