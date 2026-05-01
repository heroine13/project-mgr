"""
User Management CRUD Operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from datetime import datetime

from ..models.user_mgmt import Role, UserProfile, AuditLog, Department
from ..models.user import User
from ..schemas.user_mgmt import RoleCreate, RoleUpdate, UserProfileUpdate, UserCreate, UserUpdate, DepartmentCreate, DepartmentUpdate
from ..core.security import get_password_hash


# ============ Role CRUD ============

def create_role(db: Session, role: RoleCreate) -> Role:
    db_role = Role(
        name=role.name,
        description=role.description,
        permissions=role.permissions,
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 50) -> tuple[List[Role], int]:
    query = db.query(Role)
    total = query.count()
    roles = query.offset(skip).limit(limit).all()
    return roles, total


def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
    db_role = get_role(db, role_id)
    if not db_role or db_role.is_system:
        return None
    for field, value in role_update.model_dump(exclude_unset=True).items():
        setattr(db_role, field, value)
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int) -> bool:
    db_role = get_role(db, role_id)
    if not db_role or db_role.is_system:
        return False
    db.delete(db_role)
    db.commit()
    return True


# ============ User Profile CRUD ============

def get_or_create_profile(db: Session, user_id: int) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_profile(db: Session, user_id: int, profile_update: UserProfileUpdate) -> Optional[UserProfile]:
    profile = get_or_create_profile(db, user_id)
    for field, value in profile_update.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


def update_last_login(db: Session, user_id: int):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        profile.last_login_at = datetime.utcnow()
        profile.login_count = (profile.login_count or 0) + 1
        db.commit()


# ============ User Management ============

def get_all_users_with_roles(
    db: Session,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[dict], int]:
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
        )
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    result = []
    for u in users:
        role_name = None
        if u.role_id:
            role = get_role(db, u.role_id)
            role_name = role.name if role else None
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "role_id": u.role_id,
            "role_name": role_name,
            "created_at": u.created_at,
            "last_login": None,
        })
    return result, total


def update_user_status(db: Session, user_id: int, is_active: bool) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def assign_role(db: Session, user_id: int, role_id: int) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    role = get_role(db, role_id)
    if not role:
        return None
    user.role_id = role_id
    db.commit()
    db.refresh(user)
    return user


# ============ User CRUD ============

def create_user(db: Session, user_data: UserCreate) -> User:
    # Check if username or email exists
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise ValueError("Username or email already exists")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role_id=user_data.role_id,
        is_active=user_data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Create empty profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    return user


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    user = get_user(db, user_id)
    if not user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user or user.is_superuser:
        return False
    db.delete(user)
    db.commit()
    return True


# ============ Department CRUD ============

def create_department(db: Session, dept: DepartmentCreate) -> Department:
    db_dept = Department(
        name=dept.name,
        code=dept.code,
        parent_id=dept.parent_id,
        description=dept.description,
        sort_order=dept.sort_order,
    )
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept


def get_department(db: Session, dept_id: int) -> Optional[Department]:
    return db.query(Department).filter(Department.id == dept_id).first()


def get_departments(db: Session, skip: int = 0, limit: int = 100) -> tuple[List[Department], int]:
    query = db.query(Department).filter(Department.is_active == True).order_by(Department.sort_order, Department.name)
    total = query.count()
    depts = query.offset(skip).limit(limit).all()
    return depts, total


def get_all_departments_tree(db: Session) -> List[dict]:
    """Get all departments as tree structure"""
    all_depts = db.query(Department).filter(Department.is_active == True).order_by(Department.sort_order).all()
    
    def build_tree(parent_id: Optional[int]) -> List[dict]:
        children = []
        for d in all_depts:
            if d.parent_id == parent_id:
                children.append({
                    "id": d.id,
                    "name": d.name,
                    "code": d.code,
                    "description": d.description,
                    "children": build_tree(d.id)
                })
        return children
    
    return build_tree(None)


def update_department(db: Session, dept_id: int, dept_update: DepartmentUpdate) -> Optional[Department]:
    dept = get_department(db, dept_id)
    if not dept:
        return None
    for field, value in dept_update.model_dump(exclude_unset=True).items():
        setattr(dept, field, value)
    db.commit()
    db.refresh(dept)
    return dept


def delete_department(db: Session, dept_id: int) -> bool:
    dept = get_department(db, dept_id)
    if not dept:
        return False
    # Check if has children
    children = db.query(Department).filter(Department.parent_id == dept_id).count()
    if children > 0:
        raise ValueError("Cannot delete department with sub-departments")
    dept.is_active = False
    db.commit()
    return True


# ============ Audit Log ============

def create_audit_log(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_audit_logs(
    db: Session,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[AuditLog], int]:
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource:
        query = query.filter(AuditLog.resource == resource)
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs, total