"""
CRUD operations for Task model
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Get task by ID"""
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get tasks by project ID"""
    return db.query(Task).filter(Task.project_id == project_id).offset(skip).limit(limit).all()

def get_tasks_by_assignee(db: Session, assignee_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get tasks by assignee ID"""
    return db.query(Task).filter(Task.assignee_id == assignee_id).offset(skip).limit(limit).all()

def create_task(db: Session, task_data: TaskCreate, created_by: int) -> Task:
    """Create new task"""
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        assignee_id=task_data.assignee_id,
        project_id=task_data.project_id,
        due_date=task_data.due_date,
        estimated_hours=task_data.estimated_hours,
        actual_hours=task_data.actual_hours,
        tags=task_data.tags,
        created_by=created_by
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
    """Update task"""
    db_task = get_task(db, task_id)
    if db_task:
        update_data = task_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int) -> bool:
    """Delete task"""
    db_task = get_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False