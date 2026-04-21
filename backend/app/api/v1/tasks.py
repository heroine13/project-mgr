"""
Task API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud.task import get_task, get_tasks_by_project, get_tasks_by_assignee, get_tasks_by_user, create_task, update_task, delete_task
from app.models.project import Project
from app.auth.jwt_handler import verify_token

router = APIRouter()

def get_current_user(token: str = Depends(verify_token)) -> dict:
    """Get current user from JWT token"""
    return token

@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get tasks with optional filters"""
    # Implement proper filtering logic
    if project_id:
        return get_tasks_by_project(db, project_id, skip, limit)
    elif assignee_id:
        return get_tasks_by_assignee(db, assignee_id, skip, limit)
    else:
        # Return all tasks for the user
        return get_tasks_by_user(db, current_user["user_id"], skip, limit)

@router.get("/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get task by ID"""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.post("/", response_model=TaskResponse)
async def create_new_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new task"""
    # Check if project exists and user has permission
    project = db.query(Project).filter(Project.id == task_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    # Check if user is project member or owner
    if project.owner_id != current_user["user_id"] and not is_project_member(db, task_data.project_id, current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create task in this project"
        )
    task = create_task(db, task_data, created_by=current_user["user_id"])
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_existing_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update task"""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    # Check permissions - only owner, assignee or project member can update
    if task.created_by != current_user["user_id"] and task.assignee_id != current_user["user_id"] and project.owner_id != current_user["user_id"] and not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    updated_task = update_task(db, task_id, task_data)
    return updated_task

@router.delete("/{task_id}")
async def delete_existing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete task"""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    # Check permissions - only owner or project owner can delete
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if task.created_by != current_user["user_id"] and project.owner_id != current_user["user_id"] and not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    success = delete_task(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
    
    return {"message": "Task deleted successfully"}