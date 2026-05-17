"""
CRUD operations for Project model
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Get project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()

def get_project_by_code(db: Session, code: str) -> Optional[Project]:
    """Get project by code"""
    return db.query(Project).filter(Project.code == code).first()

def get_projects_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
    """Get projects by owner ID"""
    return db.query(Project).filter(Project.owner_id == owner_id).offset(skip).limit(limit).all()

def get_all_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """Get all projects"""
    return db.query(Project).offset(skip).limit(limit).all()

def create_project(db: Session, project_data: ProjectCreate, owner_id: int) -> Project:
    """Create new project"""
    db_project = Project(
        name=project_data.name,
        description=project_data.description,
        code=project_data.code,
        status=project_data.status,
        owner_id=owner_id,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        budget=project_data.budget,
        actual_cost=project_data.actual_cost
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
    """Update project"""
    db_project = get_project(db, project_id)
    if db_project:
        update_data = project_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int) -> bool:
    """Delete project"""
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

def _audit_log(db, user_id, action, resource, resource_id, details=None):
    """Helper to create audit log"""
    try:
        from app.models.audit_log import AuditLog
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Audit log error: {e}")
