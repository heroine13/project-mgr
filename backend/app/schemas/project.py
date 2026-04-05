"""
Project schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    code: str = Field(..., min_length=1, max_length=50)
    status: str = Field("active", min_length=1, max_length=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[int] = Field(0, ge=0)
    actual_cost: Optional[int] = Field(0, ge=0)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[int] = Field(None, ge=0)
    actual_cost: Optional[int] = Field(None, ge=0)

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True