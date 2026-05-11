"""
Resource Management CRUD Operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional, List
from datetime import datetime

from ..models.resource import Resource, ResourceAllocation, CostRecord, ResourceType, AllocationStatus
from ..models.project import Project
from ..schemas.resource import ResourceCreate, ResourceUpdate, ResourceAllocationCreate, ResourceAllocationUpdate, CostRecordCreate, CostRecordUpdate


# ============ Resource CRUD ============

def create_resource(db: Session, resource: ResourceCreate) -> Resource:
    """Create a new resource"""
    db_resource = Resource(
        name=resource.name,
        resource_type=ResourceType(resource.resource_type.value),
        description=resource.description,
        user_id=resource.user_id,
        unit_cost=resource.unit_cost,
        currency=resource.currency,
        is_available=resource.is_available,
        max_capacity=resource.max_capacity,
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource


def get_resource(db: Session, resource_id: int) -> Optional[Resource]:
    """Get resource by ID"""
    return db.query(Resource).filter(Resource.id == resource_id).first()


def get_resources(
    db: Session,
    resource_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[Resource], int]:
    """Get resources with filters"""
    query = db.query(Resource)
    
    if resource_type:
        query = query.filter(Resource.resource_type == ResourceType(resource_type))
    if is_available is not None:
        query = query.filter(Resource.is_available == is_available)
    
    total = query.count()
    resources = query.order_by(Resource.created_at.desc()).offset(skip).limit(limit).all()
    return resources, total


def update_resource(db: Session, resource_id: int, resource_update: ResourceUpdate) -> Optional[Resource]:
    """Update a resource"""
    db_resource = get_resource(db, resource_id)
    if not db_resource:
        return None
    
    update_data = resource_update.model_dump(exclude_unset=True)
    if "resource_type" in update_data and update_data["resource_type"]:
        update_data["resource_type"] = ResourceType(update_data["resource_type"].value)
    
    for field, value in update_data.items():
        setattr(db_resource, field, value)
    
    db.commit()
    db.refresh(db_resource)
    return db_resource


def delete_resource(db: Session, resource_id: int) -> bool:
    """Delete a resource"""
    db_resource = get_resource(db, resource_id)
    if not db_resource:
        return False
    
    db.delete(db_resource)
    db.commit()
    return True


# ============ Resource Allocation CRUD ============

def create_allocation(db: Session, allocation: ResourceAllocationCreate) -> ResourceAllocation:
    """Create a new resource allocation"""
    db_allocation = ResourceAllocation(
        resource_id=allocation.resource_id,
        project_id=allocation.project_id,
        task_id=allocation.task_id,
        allocation_type=allocation.allocation_type,
        allocated_value=allocation.allocated_value,
        start_date=allocation.start_date,
        end_date=allocation.end_date,
        actual_usage=allocation.actual_usage,
        actual_cost=allocation.actual_cost,
        budgeted_cost=allocation.budgeted_cost,
        status=AllocationStatus(allocation.status.value),
        notes=allocation.notes,
    )
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return db_allocation


def get_allocation(db: Session, allocation_id: int) -> Optional[ResourceAllocation]:
    """Get allocation by ID"""
    return db.query(ResourceAllocation).filter(ResourceAllocation.id == allocation_id).first()


def get_allocations(
    db: Session,
    project_id: Optional[int] = None,
    resource_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[ResourceAllocation], int]:
    """Get allocations with filters"""
    query = db.query(ResourceAllocation)
    
    if project_id:
        query = query.filter(ResourceAllocation.project_id == project_id)
    if resource_id:
        query = query.filter(ResourceAllocation.resource_id == resource_id)
    if status:
        query = query.filter(ResourceAllocation.status == AllocationStatus(status))
    
    total = query.count()
    allocations = query.order_by(ResourceAllocation.created_at.desc()).offset(skip).limit(limit).all()
    return allocations, total


def update_allocation(db: Session, allocation_id: int, allocation_update: ResourceAllocationUpdate) -> Optional[ResourceAllocation]:
    """Update an allocation"""
    db_allocation = get_allocation(db, allocation_id)
    if not db_allocation:
        return None
    
    update_data = allocation_update.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"]:
        update_data["status"] = AllocationStatus(update_data["status"].value)
    
    for field, value in update_data.items():
        setattr(db_allocation, field, value)
    
    db.commit()
    db.refresh(db_allocation)
    return db_allocation


def delete_allocation(db: Session, allocation_id: int) -> bool:
    """Delete an allocation"""
    db_allocation = get_allocation(db, allocation_id)
    if not db_allocation:
        return False
    
    db.delete(db_allocation)
    db.commit()
    return True


# ============ Cost Record CRUD ============

def create_cost_record(db: Session, cost_record: CostRecordCreate, user_id: int) -> CostRecord:
    """Create a new cost record"""
    db_cost = CostRecord(
        project_id=cost_record.project_id,
        task_id=cost_record.task_id,
        category=cost_record.category,
        description=cost_record.description,
        amount=cost_record.amount,
        currency=cost_record.currency,
        cost_date=cost_record.cost_date or datetime.utcnow(),
        is_approved=cost_record.is_approved,
    )
    if cost_record.is_approved:
        db_cost.approved_by = user_id
        db_cost.approved_at = datetime.utcnow()
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost


def get_cost_record(db: Session, cost_id: int) -> Optional[CostRecord]:
    """Get cost record by ID"""
    return db.query(CostRecord).filter(CostRecord.id == cost_id).first()


def get_cost_records(
    db: Session,
    project_id: Optional[int] = None,
    category: Optional[str] = None,
    is_approved: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[CostRecord], int]:
    """Get cost records with filters"""
    query = db.query(CostRecord)
    
    if project_id:
        query = query.filter(CostRecord.project_id == project_id)
    if category:
        query = query.filter(CostRecord.category == category)
    if is_approved is not None:
        query = query.filter(CostRecord.is_approved == is_approved)
    if start_date:
        query = query.filter(CostRecord.cost_date >= start_date)
    if end_date:
        query = query.filter(CostRecord.cost_date <= end_date)
    
    total = query.count()
    costs = query.order_by(CostRecord.cost_date.desc()).offset(skip).limit(limit).all()
    return costs, total


def update_cost_record(db: Session, cost_id: int, cost_update: CostRecordUpdate, user_id: int) -> Optional[CostRecord]:
    """Update a cost record"""
    db_cost = get_cost_record(db, cost_id)
    if not db_cost:
        return None
    
    update_data = cost_update.model_dump(exclude_unset=True)
    
    # Handle approval
    if "is_approved" in update_data:
        if update_data["is_approved"] and not db_cost.is_approved:
            update_data["approved_by"] = user_id
            update_data["approved_at"] = datetime.utcnow()
        elif not update_data["is_approved"]:
            update_data["approved_by"] = None
            update_data["approved_at"] = None
    
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    db.commit()
    db.refresh(db_cost)
    return db_cost


def delete_cost_record(db: Session, cost_id: int) -> bool:
    """Delete a cost record"""
    db_cost = get_cost_record(db, cost_id)
    if not db_cost:
        return False
    
    db.delete(db_cost)
    db.commit()
    return True


# ============ Cost Summary ============

def get_project_cost_summary(db: Session, project_id: int) -> Optional[dict]:
    """Get project cost summary"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    
    # Get cost by category
    cost_by_category = {}
    categories = ["labor", "material", "equipment", "other"]
    for cat in categories:
        total = db.query(func.sum(CostRecord.amount)).filter(
            CostRecord.project_id == project_id,
            CostRecord.category == cat
        ).scalar() or 0
        cost_by_category[cat] = float(total)
    
    # Get total actual cost from allocations
    total_actual_cost = db.query(func.sum(ResourceAllocation.actual_cost)).filter(
        ResourceAllocation.project_id == project_id,
        ResourceAllocation.status == AllocationStatus.COMPLETED
    ).scalar() or 0
    
    # Get planned and actual hours
    planned_hours = db.query(func.sum(ResourceAllocation.allocated_value)).filter(
        ResourceAllocation.project_id == project_id,
        ResourceAllocation.allocation_type == "hours"
    ).scalar() or 0
    
    actual_hours = db.query(func.sum(ResourceAllocation.actual_usage)).filter(
        ResourceAllocation.project_id == project_id
    ).scalar() or 0
    
    budget = float(project.budget or 0)
    actual_cost = max(float(project.actual_cost or 0), sum(cost_by_category.values()))
    
    return {
        "project_id": project.id,
        "project_name": project.name,
        "budget": budget,
        "actual_cost": actual_cost,
        "remaining_budget": budget - actual_cost,
        "cost_percentage": (actual_cost / budget * 100) if budget > 0 else 0,
        "labor_cost": cost_by_category.get("labor", 0),
        "material_cost": cost_by_category.get("material", 0),
        "equipment_cost": cost_by_category.get("equipment", 0),
        "other_cost": cost_by_category.get("other", 0),
        "planned_hours": float(planned_hours),
        "actual_hours": float(actual_hours),
        "utilization_rate": (float(actual_hours) / float(planned_hours) * 100) if planned_hours > 0 else 0,
    }