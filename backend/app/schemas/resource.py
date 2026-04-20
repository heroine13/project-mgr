"""
Resource Management Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ResourceTypeEnum(str, Enum):
    HUMAN = "human"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    OTHER = "other"


class AllocationStatusEnum(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ============ Resource Schemas ============

class ResourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    resource_type: ResourceTypeEnum = ResourceTypeEnum.HUMAN
    description: Optional[str] = None
    user_id: Optional[int] = None
    unit_cost: float = 0
    currency: str = "CNY"
    is_available: bool = True
    max_capacity: float = 0


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    resource_type: Optional[ResourceTypeEnum] = None
    description: Optional[str] = None
    user_id: Optional[int] = None
    unit_cost: Optional[float] = None
    currency: Optional[str] = None
    is_available: Optional[bool] = None
    max_capacity: Optional[float] = None


class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ResourceListResponse(BaseModel):
    total: int
    items: List[ResourceResponse]


# ============ Resource Allocation Schemas ============

class ResourceAllocationBase(BaseModel):
    resource_id: int
    project_id: int
    task_id: Optional[int] = None
    allocation_type: str = "percentage"  # percentage, hours, units
    allocated_value: float = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    actual_usage: float = 0
    actual_cost: float = 0
    budgeted_cost: float = 0
    status: AllocationStatusEnum = AllocationStatusEnum.PENDING
    notes: Optional[str] = None


class ResourceAllocationCreate(ResourceAllocationBase):
    pass


class ResourceAllocationUpdate(BaseModel):
    resource_id: Optional[int] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    allocation_type: Optional[str] = None
    allocated_value: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    actual_usage: Optional[float] = None
    actual_cost: Optional[float] = None
    budgeted_cost: Optional[float] = None
    status: Optional[AllocationStatusEnum] = None
    notes: Optional[str] = None


class ResourceAllocationResponse(ResourceAllocationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ResourceAllocationListResponse(BaseModel):
    total: int
    items: List[ResourceAllocationResponse]


# ============ Cost Record Schemas ============

class CostRecordBase(BaseModel):
    project_id: int
    task_id: Optional[int] = None
    category: str
    description: Optional[str] = None
    amount: float = Field(..., gt=0)
    currency: str = "CNY"
    cost_date: Optional[datetime] = None
    is_approved: bool = False


class CostRecordCreate(CostRecordBase):
    pass


class CostRecordUpdate(BaseModel):
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    cost_date: Optional[datetime] = None
    is_approved: Optional[bool] = None


class CostRecordResponse(CostRecordBase):
    id: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CostRecordListResponse(BaseModel):
    total: int
    items: List[CostRecordResponse]


# ============ Project Cost Summary ============

class ProjectCostSummary(BaseModel):
    """Project cost summary"""
    project_id: int
    project_name: str
    budget: float
    actual_cost: float
    remaining_budget: float
    cost_percentage: float
    labor_cost: float
    material_cost: float
    equipment_cost: float
    other_cost: float
    planned_hours: float
    actual_hours: float
    utilization_rate: float