"""
External Contact API - Client and External User Management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/external", tags=["外部联系人"])


# === Schemas ===

class ExternalContactCreate(BaseModel):
    """Create external contact"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: str = "client"  # client, partner, contractor, vendor
    project_access: Optional[List[int]] = None
    notes: Optional[str] = None


class ExternalContactUpdate(BaseModel):
    """Update external contact"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    project_access: Optional[List[int]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ExternalContactResponse(BaseModel):
    """External contact response"""
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    role: str
    project_access: List[int]
    notes: Optional[str]
    is_active: bool
    created_by: int
    created_at: datetime
    last_access: Optional[datetime]
    
    class Config:
        from_attributes = True


# === In-memory storage ===
_contacts = {}
_contact_id_counter = 1


# === API Endpoints ===

@router.get("/contacts")
async def list_contacts(
    role: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    is_active: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List external contacts"""
    contacts = list(_contacts.values())
    
    # Filter by role
    if role:
        contacts = [c for c in contacts if c.get("role") == role]
    
    # Filter by company
    if company:
        contacts = [c for c in contacts if c.get("company") == company]
    
    # Filter by active status
    contacts = [c for c in contacts if c.get("is_active", True) == is_active]
    
    return {
        "contacts": contacts[skip:skip+limit],
        "total": len(contacts)
    }


@router.get("/contacts/{contact_id}")
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get external contact detail"""
    contact = _contacts.get(contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    return contact


@router.post("/contacts", response_model=ExternalContactResponse)
async def create_contact(
    contact_data: ExternalContactCreate,
    current_user: User = Depends(get_current_user)
):
    """Create external contact"""
    global _contact_id_counter
    
    contact = {
        "id": _contact_id_counter,
        "name": contact_data.name,
        "email": contact_data.email,
        "phone": contact_data.phone,
        "company": contact_data.company,
        "role": contact_data.role,
        "project_access": contact_data.project_access or [],
        "notes": contact_data.notes,
        "is_active": True,
        "created_by": current_user.id,
        "created_at": datetime.now().isoformat(),
        "last_access": None
    }
    
    _contacts[_contact_id_counter] = contact
    _contact_id_counter += 1
    
    return contact


@router.put("/contacts/{contact_id}", response_model=ExternalContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ExternalContactUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update external contact"""
    contact = _contacts.get(contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    # Update fields
    update_dict = contact_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        contact[key] = value
    
    contact["updated_at"] = datetime.now().isoformat()
    
    return contact


@router.delete("/contacts/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete (deactivate) external contact"""
    contact = _contacts.get(contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    # Soft delete
    contact["is_active"] = False
    contact["deleted_at"] = datetime.now().isoformat()
    
    return {"message": "联系人已停用"}


# === Access Management ===

@router.post("/contacts/{contact_id}/access")
async def grant_project_access(
    contact_id: int,
    project_ids: List[int],
    current_user: User = Depends(get_current_user)
):
    """Grant project access to external contact"""
    contact = _contacts.get(contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    # Add project access
    current_access = set(contact.get("project_access", []))
    current_access.update(project_ids)
    contact["project_access"] = list(current_access)
    
    return {
        "status": "success",
        "message": f"已授权访问 {len(project_ids)} 个项目",
        "project_access": contact["project_access"]
    }


@router.delete("/contacts/{contact_id}/access/{project_id}")
async def revoke_project_access(
    contact_id: int,
    project_id: int,
    current_user: User = Depends(get_current_user)
):
    """Revoke project access from external contact"""
    contact = _contacts.get(contact_id)
    
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    # Remove project access
    current_access = set(contact.get("project_access", []))
    current_access.discard(project_id)
    contact["project_access"] = list(current_access)
    
    return {
        "status": "success",
        "message": "已撤销项目访问权限"
    }


# === Statistics ===

@router.get("/stats")
async def get_external_stats(
    current_user: User = Depends(get_current_user)
):
    """Get external contacts statistics"""
    contacts = list(_contacts.values())
    active_contacts = [c for c in contacts if c.get("is_active", True)]
    
    # Count by role
    by_role = {}
    for c in active_contacts:
        role = c.get("role", "other")
        by_role[role] = by_role.get(role, 0) + 1
    
    # Count by company
    by_company = {}
    for c in active_contacts:
        company = c.get("company", "未知")
        by_company[company] = by_company.get(company, 0) + 1
    
    return {
        "total_contacts": len(contacts),
        "active_contacts": len(active_contacts),
        "by_role": by_role,
        "by_company": by_company
    }


# === Initialize with sample data ===
def _init_sample_contacts():
    """Initialize with sample external contacts"""
    global _contact_id_counter
    
    samples = [
        {
            "id": 1,
            "name": "客户A公司 - 张经理",
            "email": "zhang@company-a.com",
            "phone": "13800138001",
            "company": "A公司",
            "role": "client",
            "project_access": [1, 2],
            "notes": "主要客户负责人",
            "is_active": True,
            "created_by": 1,
            "created_at": "2024-01-15T10:00:00",
            "last_access": "2024-02-01T14:30:00"
        },
        {
            "id": 2,
            "name": "合作伙伴B公司 - 李总",
            "email": "li@company-b.com",
            "phone": "13800138002",
            "company": "B公司",
            "role": "partner",
            "project_access": [1],
            "notes": "战略合作伙伴",
            "is_active": True,
            "created_by": 1,
            "created_at": "2024-01-20T10:00:00",
            "last_access": "2024-01-31T09:15:00"
        },
        {
            "id": 3,
            "name": "外包团队 - 王工",
            "email": "wang@outsource.com",
            "phone": "13800138003",
            "company": "外包公司",
            "role": "contractor",
            "project_access": [2],
            "notes": "负责前端开发外包",
            "is_active": True,
            "created_by": 1,
            "created_at": "2024-02-01T10:00:00",
            "last_access": None
        }
    ]
    
    for c in samples:
        _contacts[c["id"]] = c
    
    _contact_id_counter = len(_contacts) + 1


_init_sample_contacts()