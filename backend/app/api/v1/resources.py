"""
Resource Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.resource import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourceListResponse,
    ResourceAllocationCreate,
    ResourceAllocationUpdate,
    ResourceAllocationResponse,
    ResourceAllocationListResponse,
    CostRecordCreate,
    CostRecordUpdate,
    CostRecordResponse,
    CostRecordListResponse,
    ProjectCostSummary,
)
from ...crud import resource as crud_resource

router = APIRouter()


# ============ Resource Endpoints ============

@router.post("/resources", response_model=ResourceResponse, status_code=201)
def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new resource"""
    return crud_resource.create_resource(db, resource)


@router.get("/resources", response_model=ResourceListResponse)
def get_resources(
    resource_type: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get resources with filters"""
    skip = (page - 1) * page_size
    resources, total = crud_resource.get_resources(
        db, resource_type, is_available, skip, page_size
    )
    return ResourceListResponse(
        total=total,
        items=resources,
        page=page,
        page_size=page_size,
    )


@router.get("/resources/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get resource by ID"""
    resource = crud_resource.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.put("/resources/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a resource"""
    resource = crud_resource.update_resource(db, resource_id, resource_update)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.delete("/resources/{resource_id}", status_code=204)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a resource"""
    success = crud_resource.delete_resource(db, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return None


# ============ Resource Allocation Endpoints ============

@router.post("/allocations", response_model=ResourceAllocationResponse, status_code=201)
def create_allocation(
    allocation: ResourceAllocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new resource allocation"""
    return crud_resource.create_allocation(db, allocation)


@router.get("/allocations", response_model=ResourceAllocationListResponse)
def get_allocations(
    project_id: Optional[int] = Query(None),
    resource_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get allocations with filters"""
    skip = (page - 1) * page_size
    allocations, total = crud_resource.get_allocations(
        db, project_id, resource_id, status, skip, page_size
    )
    return ResourceAllocationListResponse(
        total=total,
        items=allocations,
    )


@router.get("/allocations/{allocation_id}", response_model=ResourceAllocationResponse)
def get_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get allocation by ID"""
    allocation = crud_resource.get_allocation(db, allocation_id)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation


@router.put("/allocations/{allocation_id}", response_model=ResourceAllocationResponse)
def update_allocation(
    allocation_id: int,
    allocation_update: ResourceAllocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an allocation"""
    allocation = crud_resource.update_allocation(db, allocation_id, allocation_update)
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation


@router.delete("/allocations/{allocation_id}", status_code=204)
def delete_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an allocation"""
    success = crud_resource.delete_allocation(db, allocation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return None


# ============ Cost Record Endpoints ============

@router.post("/costs", response_model=CostRecordResponse, status_code=201)
def create_cost_record(
    cost_record: CostRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new cost record"""
    return crud_resource.create_cost_record(db, cost_record, current_user.id)


@router.get("/costs", response_model=CostRecordListResponse)
def get_cost_records(
    project_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    is_approved: Optional[bool] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get cost records with filters"""
    from datetime import datetime
    
    skip = (page - 1) * page_size
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    
    costs, total = crud_resource.get_cost_records(
        db, project_id, category, is_approved, start_dt, end_dt, skip, page_size
    )
    return CostRecordListResponse(
        total=total,
        items=costs,
    )


@router.get("/costs/{cost_id}", response_model=CostRecordResponse)
def get_cost_record(
    cost_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get cost record by ID"""
    cost = crud_resource.get_cost_record(db, cost_id)
    if not cost:
        raise HTTPException(status_code=404, detail="Cost record not found")
    return cost


@router.put("/costs/{cost_id}", response_model=CostRecordResponse)
def update_cost_record(
    cost_id: int,
    cost_update: CostRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a cost record"""
    cost = crud_resource.update_cost_record(db, cost_id, cost_update, current_user.id)
    if not cost:
        raise HTTPException(status_code=404, detail="Cost record not found")
    return cost


@router.delete("/costs/{cost_id}", status_code=204)
def delete_cost_record(
    cost_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a cost record"""
    success = crud_resource.delete_cost_record(db, cost_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cost record not found")
    return None


# ============ Cost Summary Endpoints ============

@router.get("/projects/{project_id}/cost-summary", response_model=ProjectCostSummary)
def get_project_cost_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project cost summary"""
    summary = crud_resource.get_project_cost_summary(db, project_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectCostSummary(**summary)