"""
Project Model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .user import Base

class Project(Base):
    """Project model for project management"""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    code = Column(String(50), unique=True, index=True)  # Project code like "PRJ-001"
    status = Column(String(50), default="active")  # active, completed, archived
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    budget = Column(Integer, default=0)
    actual_cost = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    tasks = relationship("Task", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', code='{self.code}')>"