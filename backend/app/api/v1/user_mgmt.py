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
    UserCreate, UserUpdate, UserResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
)
from ...crud import user_mgmt as crud_user

router = APIRouter()


# ============ User Management ============

@router.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        user = crud_user.create_user(db, user_data)
        role = crud_user.get_role(db, user.role_id) if user.role_id else None
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "role_id": user.role_id,
            "role_name": role.name if role else None,
            "created_at": user.created_at,
            "last_login": None,
        }
    except ValueError as e:
        return {"error": str(e)}


@router.get("/users", response_model=dict)
def list_users(
    is_active: bool = None,
    search: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = crud_user.update_user(db, user_id, user_update)
    if not user:
        return {"error": "User not found"}
    role = crud_user.get_role(db, user.role_id) if user.role_id else None
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "role_id": user.role_id,
        "role_name": role.name if role else None,
        "created_at": user.created_at,
        "last_login": None,
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = crud_user.delete_user(db, user_id)
    if not success:
        return {"error": "User not found or cannot be deleted"}
    return {"message": "User deleted successfully"}


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
    current_user: User = Depends(get_current_user),
):
    skip = (page - 1) * page_size
    roles, total = crud_user.get_roles(db, skip, page_size)
    return {"total": total, "items": roles}


@router.post("/roles", response_model=RoleResponse)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud_user.create_role(db, role)


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = crud_user.update_role(db, role_id, role_update)
    if not role:
        return {"error": "Role not found or is system role"}
    return role


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = crud_user.delete_role(db, role_id)
    if not success:
        return {"error": "Role not found or is system role"}
    return {"message": "Role deleted successfully"}


@router.get("/roles/{role_id}/permissions")
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    role = crud_user.get_role(db, role_id)
    if not role:
        return {"error": "Role not found"}
    import json
    permissions = json.loads(role.permissions) if role.permissions else []
    return {"permissions": permissions}


@router.put("/roles/{role_id}/permissions")
def update_role_permissions(
    role_id: int,
    permissions_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    role = crud_user.get_role(db, role_id)
    if not role:
        return {"error": "Role not found"}
    import json
    permissions_str = json.dumps(permissions_data.get("permissions", []))
    role.permissions = permissions_str
    db.commit()
    db.refresh(role)
    return {"message": "Permissions updated successfully", "permissions": permissions_data.get("permissions", [])}


# ============ Department Management ============

@router.get("/departments", response_model=dict)
def list_departments(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skip = (page - 1) * page_size
    depts, total = crud_user.get_departments(db, skip, page_size)
    return {"total": total, "items": depts, "page": page, "page_size": page_size}


@router.get("/departments/tree")
def get_department_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tree = crud_user.get_all_departments_tree(db)
    return {"items": tree}


@router.post("/departments", response_model=DepartmentResponse)
def create_department(
    dept: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud_user.create_department(db, dept)


@router.put("/departments/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    dept_update: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dept = crud_user.update_department(db, dept_id, dept_update)
    if not dept:
        return {"error": "Department not found"}
    return dept


@router.delete("/departments/{dept_id}")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        success = crud_user.delete_department(db, dept_id)
        if not success:
            return {"error": "Department not found"}
        return {"message": "Department deleted successfully"}
    except ValueError as e:
        return {"error": str(e)}


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