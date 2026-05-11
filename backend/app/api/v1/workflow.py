"""
Workflow API Endpoints - Approval Workflow System
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workflow import Workflow, ApprovalRequest, ApprovalAction, WorkflowTemplate
from app.models.workflow import WorkflowStatus, ApprovalStatus

router = APIRouter(prefix="/workflows", tags=["审批流管理"])


# === Pydantic Schemas ===

class WorkflowStep(BaseModel):
    """Workflow step configuration"""
    step: int
    name: str
    approvers: List[int]  # User IDs who can approve this step
    required_approvers: int = 1


class WorkflowCreate(BaseModel):
    """Create workflow request"""
    name: str
    description: Optional[str] = None
    entity_type: str  # task, project, issue, etc.
    steps: List[WorkflowStep]


class WorkflowUpdate(BaseModel):
    """Update workflow request"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    steps: Optional[List[WorkflowStep]] = None


class WorkflowResponse(BaseModel):
    """Workflow response"""
    id: int
    name: str
    description: Optional[str]
    entity_type: str
    status: str
    steps_config: Optional[List[dict]]
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApprovalRequestCreate(BaseModel):
    """Create approval request"""
    workflow_id: int
    entity_type: str
    entity_id: int
    request_data: Optional[dict] = None


class ApprovalRequestResponse(BaseModel):
    """Approval request response"""
    id: int
    workflow_id: int
    entity_type: str
    entity_id: int
    current_step: int
    status: str
    requested_by: int
    request_data: Optional[dict]
    result: Optional[str]
    decided_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApprovalActionCreate(BaseModel):
    """Create approval action"""
    action: str  # approve, reject
    comment: Optional[str] = None


# === Workflow CRUD ===

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    entity_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all workflows"""
    query = db.query(Workflow)
    
    if entity_type:
        query = query.filter(Workflow.entity_type == entity_type)
    if status:
        query = query.filter(Workflow.status == status)
    
    workflows = query.order_by(Workflow.created_at.desc()).offset(skip).limit(limit).all()
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow by ID"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    return workflow


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workflow"""
    # Convert steps to JSON
    steps_config = [step.model_dump() for step in workflow_data.steps]
    
    workflow = Workflow(
        name=workflow_data.name,
        description=workflow_data.description,
        entity_type=workflow_data.entity_type,
        status=WorkflowStatus.DRAFT,
        steps_config=steps_config,
        created_by=current_user.id
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # Update fields
    if workflow_data.name is not None:
        workflow.name = workflow_data.name
    if workflow_data.description is not None:
        workflow.description = workflow_data.description
    if workflow_data.status is not None:
        workflow.status = WorkflowStatus(workflow_data.status)
    if workflow_data.steps is not None:
        workflow.steps_config = [step.model_dump() for step in workflow_data.steps]
    
    db.commit()
    db.refresh(workflow)
    
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # Check if there are pending requests
    pending_count = db.query(ApprovalRequest).filter(
        ApprovalRequest.workflow_id == workflow_id,
        ApprovalRequest.status == ApprovalStatus.PENDING
    ).count()
    
    if pending_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该工作流有 {pending_count} 个待审批的请求，无法删除"
        )
    
    db.delete(workflow)
    db.commit()
    
    return {"message": "工作流已删除"}


# === Approval Request ===

@router.get("/requests/", response_model=List[ApprovalRequestResponse])
async def list_approval_requests(
    workflow_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    my_requests: bool = Query(False),  # Requests I submitted
    my_approvals: bool = Query(False),  # Requests waiting for my approval
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List approval requests"""
    query = db.query(ApprovalRequest)
    
    if workflow_id:
        query = query.filter(ApprovalRequest.workflow_id == workflow_id)
    if entity_type:
        query = query.filter(ApprovalRequest.entity_type == entity_type)
    if status:
        query = query.filter(ApprovalRequest.status == ApprovalStatus(status))
    
    if my_requests:
        query = query.filter(ApprovalRequest.requested_by == current_user.id)
    
    requests = query.order_by(ApprovalRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@router.post("/requests/", response_model=ApprovalRequestResponse)
async def create_approval_request(
    request_data: ApprovalRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an approval request"""
    # Verify workflow exists and is active
    workflow = db.query(Workflow).filter(
        Workflow.id == request_data.workflow_id,
        Workflow.status == WorkflowStatus.ACTIVE
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在或未激活")
    
    # Check if there's already a pending request for this entity
    existing = db.query(ApprovalRequest).filter(
        ApprovalRequest.workflow_id == request_data.workflow_id,
        ApprovalRequest.entity_type == request_data.entity_type,
        ApprovalRequest.entity_id == request_data.entity_id,
        ApprovalRequest.status == ApprovalStatus.PENDING
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该实体已有待审批的请求")
    
    # Create request
    approval_request = ApprovalRequest(
        workflow_id=request_data.workflow_id,
        entity_type=request_data.entity_type,
        entity_id=request_data.entity_id,
        current_step=0,
        status=ApprovalStatus.PENDING,
        requested_by=current_user.id,
        request_data=request_data.request_data
    )
    
    db.add(approval_request)
    db.commit()
    db.refresh(approval_request)
    
    return approval_request


@router.get("/requests/{request_id}", response_model=ApprovalRequestResponse)
async def get_approval_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval request details"""
    approval_request = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == request_id
    ).first()
    
    if not approval_request:
        raise HTTPException(status_code=404, detail="审批请求不存在")
    
    return approval_request


@router.post("/requests/{request_id}/approve")
async def approve_request(
    request_id: int,
    action_data: ApprovalActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject an approval request"""
    approval_request = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == request_id
    ).first()
    
    if not approval_request:
        raise HTTPException(status_code=404, detail="审批请求不存在")
    
    if approval_request.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail="该请求已处理")
    
    # Get workflow and current step config
    workflow = db.query(Workflow).filter(Workflow.id == approval_request.workflow_id).first()
    steps = workflow.steps_config or []
    
    if approval_request.current_step >= len(steps):
        raise HTTPException(status_code=400, detail="审批流程已完成")
    
    current_step_config = steps[approval_request.current_step]
    
    # Check if current user is an approver for this step
    approvers = current_step_config.get("approvers", [])
    if current_user.id not in approvers and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您不是该审批步骤的审批人")
    
    # Record approval action
    approval_action = ApprovalAction(
        request_id=request_id,
        step=approval_request.current_step,
        approver_id=current_user.id,
        action=action_data.action,
        comment=action_data.comment
    )
    db.add(approval_action)
    
    # Process action
    if action_data.action == "approve":
        # Move to next step
        approval_request.current_step += 1
        
        # Check if all steps completed
        if approval_request.current_step >= len(steps):
            approval_request.status = ApprovalStatus.APPROVED
            approval_request.decided_at = datetime.now()
            approval_request.result = "审批通过"
    
    elif action_data.action == "reject":
        approval_request.status = ApprovalStatus.REJECTED
        approval_request.decided_at = datetime.now()
        approval_request.result = action_data.comment or "审批拒绝"
    
    else:
        raise HTTPException(status_code=400, detail="无效的操作类型")
    
    db.commit()
    db.refresh(approval_request)
    
    return {
        "status": "success",
        "message": f"已{action_data.action}",
        "request": approval_request
    }


@router.post("/requests/{request_id}/cancel")
async def cancel_approval_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an approval request"""
    approval_request = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == request_id
    ).first()
    
    if not approval_request:
        raise HTTPException(status_code=404, detail="审批请求不存在")
    
    if approval_request.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能取消待审批的请求")
    
    # Only requester or admin can cancel
    if approval_request.requested_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权限取消此请求")
    
    approval_request.status = ApprovalStatus.CANCELLED
    db.commit()
    
    return {"message": "审批请求已取消"}


# === Workflow Templates ===

@router.get("/templates/")
async def list_workflow_templates(
    entity_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflow templates"""
    query = db.query(WorkflowTemplate)
    
    if entity_type:
        query = query.filter(WorkflowTemplate.entity_type == entity_type)
    
    templates = query.order_by(WorkflowTemplate.is_system.desc(), WorkflowTemplate.name).all()
    return templates


@router.post("/templates/")
async def create_workflow_template(
    name: str,
    description: Optional[str],
    entity_type: str,
    steps: List[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a workflow template"""
    template = WorkflowTemplate(
        name=name,
        description=description,
        entity_type=entity_type,
        steps=steps,
        created_by=current_user.id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template