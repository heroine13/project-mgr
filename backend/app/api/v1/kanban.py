"""
Kanban API Endpoints - Drag & Drop Task Management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus

router = APIRouter(prefix="/kanban", tags=["看板视图"])


# === Schemas ===

class TaskCardResponse(BaseModel):
    """Task card for Kanban board"""
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    assignee_id: Optional[int]
    project_id: int
    due_date: Optional[datetime]
    tags: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MoveTaskRequest(BaseModel):
    """Request to move task to another column"""
    status: str
    position: Optional[int] = None


class ColumnConfig(BaseModel):
    """Kanban column configuration"""
    id: str
    title: str
    status: str
    color: str


# === Default Kanban Columns ===
DEFAULT_COLUMNS = [
    {"id": "pending", "title": "待处理", "status": "pending", "color": "#909399"},
    {"id": "in_progress", "title": "进行中", "status": "in_progress", "color": "#E6A23C"},
    {"id": "review", "title": "审核中", "status": "review", "color": "#409EFF"},
    {"id": "completed", "title": "已完成", "status": "completed", "color": "#67C23A"},
    {"id": "blocked", "title": "已阻塞", "status": "blocked", "color": "#F56C6C"},
]


@router.get("/columns")
async def get_columns(
    current_user: User = Depends(get_current_user)
):
    """Get Kanban column configuration"""
    return DEFAULT_COLUMNS


@router.get("/tasks")
async def get_kanban_tasks(
    project_id: Optional[int] = Query(None),
    assignee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tasks for Kanban board"""
    query = db.query(Task)
    
    # Filter by project
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    # Filter by assignee
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    
    # If not admin, only show assigned tasks or own created tasks
    if not current_user.is_superuser:
        query = query.filter(
            (Task.assignee_id == current_user.id) | 
            (Task.created_by == current_user.id)
        )
    
    tasks = query.order_by(Task.created_at.desc()).all()
    
    # Group by status
    result = {col["status"]: [] for col in DEFAULT_COLUMNS}
    
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value if isinstance(task.status, TaskStatus) else task.status,
            "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
            "assignee_id": task.assignee_id,
            "project_id": task.project_id,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": task.tags,
            "created_at": task.created_at.isoformat()
        }
        
        status_key = task_dict["status"]
        if status_key in result:
            result[status_key].append(task_dict)
        else:
            result["pending"].append(task_dict)
    
    return {
        "columns": DEFAULT_COLUMNS,
        "tasks": result
    }


@router.put("/tasks/{task_id}/move")
async def move_task(
    task_id: int,
    move_data: MoveTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Move task to another column (change status)"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # Verify new status is valid
    try:
        new_status = TaskStatus(move_data.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态")
    
    # Check permission
    if not current_user.is_superuser and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限移动此任务")
    
    # Update status
    old_status = task.status.value if isinstance(task.status, TaskStatus) else task.status
    task.status = new_status
    
    db.commit()
    db.refresh(task)
    
    return {
        "status": "success",
        "message": f"任务已从 '{old_status}' 移动到 '{move_data.status}'",
        "task": {
            "id": task.id,
            "title": task.title,
            "old_status": old_status,
            "new_status": move_data.status
        }
    }


@router.put("/tasks/reorder")
async def reorder_tasks(
    task_ids: List[int],
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reorder tasks within a column"""
    try:
        target_status = TaskStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态")
    
    # Update all tasks in the list
    for index, task_id in enumerate(task_ids):
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = target_status
            # Could also add a position field for ordering
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"已更新 {len(task_ids)} 个任务的位置"
    }


@router.get("/stats")
async def get_kanban_stats(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Kanban board statistics"""
    query = db.query(Task)
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    if not current_user.is_superuser:
        query = query.filter(
            (Task.assignee_id == current_user.id) | 
            (Task.created_by == current_user.id)
        )
    
    # Count by status
    stats = {}
    for col in DEFAULT_COLUMNS:
        status = col["status"]
        count = query.filter(Task.status == TaskStatus(status)).count()
        stats[status] = {
            "count": count,
            "title": col["title"],
            "color": col["color"]
        }
    
    # Total
    stats["total"] = {
        "count": query.count(),
        "title": "总计",
        "color": "#303133"
    }
    
    return stats