"""
User Management API Endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user, require_admin
from ...models.user import User
from ...schemas.user_mgmt import (
    RoleCreate, RoleUpdate, RoleResponse,
    UserManagementUpdate, UserListResponse,
    UserProfileUpdate, UserProfileResponse,
    AuditLogListResponse,
)
from ...crud import user_mgmt as crud_user

router = APIRouter()


# ============ User Management ============

@router.get("/users", response_model=dict)
def list_users(
    is_active: bool = None,
    search: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    skip = (page - 1) * page_size
    users, total = crud_user.get_all_users_with_roles(db, is_active, search, skip, page_size)
    return {"total": total, "items": users, "page": page, "page_size": page_size}


@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    update: UserManagementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if update.is_active is not None:
        user = crud_user.update_user_status(db, user_id, update.is_active)
    elif update.role_id is not None:
        user = crud_user.assign_role(db, user_id, update.role_id)
    else:
        return {"error": "No update provided"}
    
    if not user:
        return {"error": "User not found"}
    return {"message": "User updated successfully", "user_id": user_id}


@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = crud_user.get_or_create_profile(db, user_id)
    return profile


@router.put("/users/{user_id}/profile", response_model=UserProfileResponse)
def update_user_profile(
    user_id: int,
    profile_update: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role_id != 1:
        return {"error": "Unauthorized"}
    return crud_user.update_profile(db, user_id, profile_update)


# ============ Role Management ============

@router.get("/roles", response_model=dict)
def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    skip = (page - 1) * page_size
    roles, total = crud_user.get_roles(db, skip, page_size)
    return {"total": total, "items": roles}


@router.post("/roles", response_model=RoleResponse)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return crud_user.create_role(db, role)


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    role = crud_user.update_role(db, role_id, role_update)
    if not role:
        return {"error": "Role not found or is system role"}
    return role


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    success = crud_user.delete_role(db, role_id)
    if not success:
        return {"error": "Role not found or is system role"}
    return {"message": "Role deleted successfully"}


# ============ Audit Logs ============

@router.get("/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    user_id: int = None,
    action: str = None,
    resource: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    skip = (page - 1) * page_size
    logs, total = crud_user.get_audit_logs(db, user_id, action, resource, skip, page_size)
    return {"total": total, "items": logs, "page": page, "page_size": page_size}