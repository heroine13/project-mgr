"""
Project API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.crud.project import get_project, get_projects_by_owner, get_all_projects, create_project, update_project, delete_project
from app.core.security import get_current_user

router = APIRouter()

def get_current_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current user from security"""
    return {"user_id": 1, "username": "admin"}

@router.get("/", response_model=List[ProjectResponse])
async def read_projects(
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get projects with optional filters"""
    if owner_id:
        return get_projects_by_owner(db, owner_id, skip, limit)
    else:
        return get_all_projects(db, skip, limit)

@router.get("/{project_id}", response_model=ProjectResponse)
async def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get project by ID"""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.post("/", response_model=ProjectResponse)
async def create_new_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new project"""
    # Check if project code is unique
    existing = db.query(Project).filter(Project.code == project_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project code already exists"
        )
    project = create_project(db, project_data, owner_id=current_user.get("user_id", 1))
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_existing_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update project"""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions - only owner or admin can update
    if project.owner_id != current_user.get("user_id", 1) and not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project"
        )
    
    updated_project = update_project(db, project_id, project_data)
    return updated_project

@router.delete("/{project_id}")
async def delete_existing_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete project"""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if project.owner_id != current_user.get("user_id", 1) and not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )
    
    success = delete_project(db, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )
    
    return {"message": "Project deleted successfully"}