"""
Project Template API - Reusable Project Templates
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/project-templates", tags=["项目模板"])


# === Schemas ===

class TaskTemplate(BaseModel):
    """Task template"""
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    estimated_hours: int = 0
    tags: Optional[str] = None


class ProjectTemplateCreate(BaseModel):
    """Create project template"""
    name: str
    description: Optional[str] = None
    category: str = "general"
    tasks: List[TaskTemplate] = []


class ProjectTemplateUpdate(BaseModel):
    """Update project template"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tasks: Optional[List[TaskTemplate]] = None
    is_active: Optional[bool] = None


class ProjectTemplateResponse(BaseModel):
    """Project template response"""
    id: int
    name: str
    description: Optional[str]
    category: str
    tasks: List[dict]
    is_active: bool
    usage_count: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# === In-memory storage for demo ===
# In production, this would be a database model
_templates = {}


# === API Endpoints ===

@router.get("/", response_model=List[ProjectTemplateResponse])
async def list_templates(
    category: Optional[str] = Query(None),
    include_inactive: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List all project templates"""
    templates = list(_templates.values())
    
    # Filter by category
    if category:
        templates = [t for t in templates if t.get("category") == category]
    
    # Filter by active status
    if not include_inactive:
        templates = [t for t in templates if t.get("is_active", True)]
    
    # Sort by usage count
    templates.sort(key=lambda x: x.get("usage_count", 0), reverse=True)
    
    return templates[skip:skip+limit]


@router.get("/{template_id}", response_model=ProjectTemplateResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific template"""
    template = _templates.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return template


@router.post("/", response_model=ProjectTemplateResponse)
async def create_template(
    template_data: ProjectTemplateCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new project template"""
    # Generate ID
    template_id = len(_templates) + 1
    
    template = {
        "id": template_id,
        "name": template_data.name,
        "description": template_data.description,
        "category": template_data.category,
        "tasks": [t.model_dump() for t in template_data.tasks],
        "is_active": True,
        "usage_count": 0,
        "created_by": current_user.id,
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }
    
    _templates[template_id] = template
    
    return template


@router.put("/{template_id}", response_model=ProjectTemplateResponse)
async def update_template(
    template_id: int,
    template_data: ProjectTemplateUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a template"""
    template = _templates.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # Update fields
    if template_data.name is not None:
        template["name"] = template_data.name
    if template_data.description is not None:
        template["description"] = template_data.description
    if template_data.category is not None:
        template["category"] = template_data.category
    if template_data.tasks is not None:
        template["tasks"] = [t.model_dump() for t in template_data.tasks]
    if template_data.is_active is not None:
        template["is_active"] = template_data.is_active
    
    template["updated_at"] = datetime.now().isoformat()
    
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a template"""
    if template_id not in _templates:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # Only creator or admin can delete
    template = _templates[template_id]
    if template["created_by"] != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权限删除此模板")
    
    del _templates[template_id]
    
    return {"message": "模板已删除"}


@router.post("/{template_id}/use")
async def use_template(
    template_id: int,
    project_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Use a template to create a new project"""
    template = _templates.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    if not template.get("is_active", True):
        raise HTTPException(status_code=400, detail="模板已停用")
    
    # Increment usage count
    template["usage_count"] = template.get("usage_count", 0) + 1
    
    # In production, this would:
    # 1. Create a new project
    # 2. Create tasks from template
    
    return {
        "status": "success",
        "message": f"已使用模板 '{template['name']}' 创建项目 '{project_name}'",
        "project_name": project_name,
        "tasks_created": len(template.get("tasks", []))
    }


@router.get("/categories/list")
async def list_categories(
    current_user: User = Depends(get_current_user)
):
    """List all template categories"""
    categories = [
        {"id": "general", "name": "通用", "icon": "Folder"},
        {"id": "software", "name": "软件开发", "icon": "Monitor"},
        {"id": "marketing", "name": "市场营销", "icon": "TrendCharts"},
        {"id": "event", "name": "活动策划", "icon": "Calendar"},
        {"id": "research", "name": "研究开发", "icon": "Search"},
        {"id": "hr", "name": "人力资源", "icon": "User"},
    ]
    return {"categories": categories}


# Initialize with some default templates
def _init_default_templates():
    """Initialize with default templates"""
    defaults = [
        {
            "id": 1,
            "name": "软件开发项目",
            "description": "标准的软件敏捷开发项目模板",
            "category": "software",
            "tasks": [
                {"title": "需求分析", "description": "收集和分析用户需求", "priority": "high", "estimated_hours": 16},
                {"title": "系统设计", "description": "架构设计和详细设计", "priority": "high", "estimated_hours": 24},
                {"title": "前端开发", "description": "用户界面开发", "priority": "medium", "estimated_hours": 40},
                {"title": "后端开发", "description": "服务接口和业务逻辑", "priority": "medium", "estimated_hours": 40},
                {"title": "测试", "description": "单元测试和集成测试", "priority": "medium", "estimated_hours": 24},
                {"title": "部署上线", "description": "部署到生产环境", "priority": "high", "estimated_hours": 8},
            ],
            "is_active": True,
            "usage_count": 15,
            "created_by": 1,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": None
        },
        {
            "id": 2,
            "name": "市场营销活动",
            "description": "营销活动策划和执行模板",
            "category": "marketing",
            "tasks": [
                {"title": "市场调研", "description": "分析目标市场和竞争对手", "priority": "high", "estimated_hours": 8},
                {"title": "活动策划", "description": "制定活动方案和预算", "priority": "high", "estimated_hours": 12},
                {"title": "物料准备", "description": "制作宣传物料", "priority": "medium", "estimated_hours": 16},
                {"title": "推广执行", "description": "执行推广计划", "priority": "high", "estimated_hours": 24},
                {"title": "效果评估", "description": "分析活动效果", "priority": "medium", "estimated_hours": 8},
            ],
            "is_active": True,
            "usage_count": 8,
            "created_by": 1,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": None
        },
        {
            "id": 3,
            "name": "新员工入职",
            "description": "新员工入职流程模板",
            "category": "hr",
            "tasks": [
                {"title": "准备入职材料", "description": "合同、办公用品等", "priority": "high", "estimated_hours": 2},
                {"title": "系统账号开通", "description": "邮箱、钉钉、代码仓库等", "priority": "high", "estimated_hours": 4},
                {"title": "入职培训", "description": "公司制度、流程培训", "priority": "medium", "estimated_hours": 8},
                {"title": "部门介绍", "description": "团队成员和工作内容介绍", "priority": "medium", "estimated_hours": 4},
                {"title": "导师对接", "description": "分配导师并进行指导", "priority": "high", "estimated_hours": 2},
            ],
            "is_active": True,
            "usage_count": 12,
            "created_by": 1,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": None
        }
    ]
    
    for t in defaults:
        _templates[t["id"]] = t


# Initialize on module load
_init_default_templates()