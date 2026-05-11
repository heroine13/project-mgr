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

def get_tasks_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get tasks created by or assigned to a user"""
    return db.query(Task).filter(
        (Task.created_by == user_id) | (Task.assignee_id == user_id)
    ).offset(skip).limit(limit).all()

def is_project_member(db: Session, project_id: int, user_id: int) -> bool:
    """Check if user is a member of the project"""
    from app.models.project import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    return member is not None

def create_task(db: Session, task_data: TaskCreate, created_by: int) -> Task:
    """Create new task"""
    # 将 Pydantic 枚举转换为字符串
    status_value = task_data.status.value if hasattr(task_data.status, 'value') else task_data.status
    priority_value = task_data.priority.value if hasattr(task_data.priority, 'value') else task_data.priority
    
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        status=status_value,
        priority=priority_value,
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
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            # 将 Pydantic 枚举转换为字符串
            if hasattr(value, 'value'):
                value = value.value
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