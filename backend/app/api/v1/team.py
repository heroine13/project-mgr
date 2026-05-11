"""
Team Collaboration API - Enhanced Team Features
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/team", tags=["团队协作"])


# === Schemas ===

class TeamMemberUpdate(BaseModel):
    """Update team member role/permissions"""
    role: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None


class TeamStatsResponse(BaseModel):
    """Team statistics"""
    total_members: int
    active_members: int
    tasks_assigned: int
    tasks_completed: int
    average_completion_time: float


class CollaborationEvent(BaseModel):
    """Real-time collaboration event"""
    id: int
    type: str  # task_update, comment, status_change, etc.
    user_id: int
    username: str
    resource_type: str
    resource_id: int
    description: str
    created_at: datetime


# === Team Management ===

@router.get("/members")
async def get_team_members(
    project_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all team members"""
    # In production, this would query from database
    # For now, return mock data
    
    members = [
        {
            "id": 1,
            "username": "zhangsan",
            "email": "zhangsan@example.com",
            "role": "admin",
            "department": "技术部",
            "title": "技术总监",
            "avatar": None,
            "is_active": True,
            "last_active": datetime.now().isoformat()
        },
        {
            "id": 2,
            "username": "lisi",
            "email": "lisi@example.com",
            "role": "member",
            "department": "技术部",
            "title": "高级工程师",
            "avatar": None,
            "is_active": True,
            "last_active": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            "id": 3,
            "username": "wangwu",
            "email": "wangwu@example.com",
            "role": "member",
            "department": "产品部",
            "title": "产品经理",
            "avatar": None,
            "is_active": True,
            "last_active": (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]
    
    # Filter by department
    if department:
        members = [m for m in members if m.get("department") == department]
    
    return {"members": members, "total": len(members)}


@router.get("/members/{user_id}")
async def get_member_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team member detail"""
    # Mock data
    member = {
        "id": user_id,
        "username": f"user_{user_id}",
        "email": f"user{user_id}@example.com",
        "role": "member",
        "department": "技术部",
        "title": "工程师",
        "phone": "13800138000",
        "avatar": None,
        "skills": ["Python", "Vue.js", "FastAPI"],
        "bio": "热爱技术和产品开发",
        "joined_at": "2024-01-01T00:00:00",
        "last_active": datetime.now().isoformat(),
        "statistics": {
            "total_tasks": 50,
            "completed_tasks": 35,
            "avg_completion_days": 3.5
        }
    }
    
    return member


@router.put("/members/{user_id}")
async def update_team_member(
    user_id: int,
    update_data: TeamMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update team member information"""
    # Only admin can update
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以更新成员信息")
    
    return {
        "status": "success",
        "message": "成员信息已更新",
        "user_id": user_id
    }


@router.get("/stats")
async def get_team_stats(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team statistics"""
    
    # Mock statistics
    return {
        "total_members": 12,
        "active_members": 10,
        "tasks_assigned": 45,
        "tasks_completed": 28,
        "average_completion_time": 3.5,  # days
        "by_department": {
            "技术部": {"members": 6, "completed_tasks": 18},
            "产品部": {"members": 3, "completed_tasks": 6},
            "设计部": {"members": 2, "completed_tasks": 4},
            "市场部": {"members": 1, "completed_tasks": 0}
        }
    }


# === Activity Feed ===

@router.get("/activity")
async def get_team_activity(
    project_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team activity feed"""
    
    # Mock activity data
    activities = [
        {
            "id": 1,
            "type": "task_completed",
            "user_id": 2,
            "username": "lisi",
            "resource_type": "task",
            "resource_id": 15,
            "description": "完成了任务 '用户登录功能开发'",
            "created_at": (datetime.now() - timedelta(minutes=30)).isoformat()
        },
        {
            "id": 2,
            "type": "comment",
            "user_id": 3,
            "username": "wangwu",
            "resource_type": "issue",
            "resource_id": 8,
            "description": "在Issue #8 中评论: '建议优先处理这个问题'",
            "created_at": (datetime.now() - timedelta(hours=1)).isoformat()
        },
        {
            "id": 3,
            "type": "task_assigned",
            "user_id": 1,
            "username": "zhangsan",
            "resource_type": "task",
            "resource_id": 20,
            "description": "将任务 'API文档编写' 分配给 lisi",
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            "id": 4,
            "type": "status_change",
            "user_id": 2,
            "username": "lisi",
            "resource_type": "project",
            "resource_id": 3,
            "description": "将项目 'App开发' 状态改为 '进行中'",
            "created_at": (datetime.now() - timedelta(hours=3)).isoformat()
        }
    ]
    
    return {"activities": activities[:limit]}


# === Quick Actions ===

@router.post("/invite")
async def invite_team_member(
    email: str,
    name: str,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Invite a new team member"""
    # In production, this would send an invitation email
    
    return {
        "status": "success",
        "message": f"已向 {email} 发送邀请",
        "invitation_expires": (datetime.now() + timedelta(days=7)).isoformat()
    }


@router.get("/online")
async def get_online_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get currently online team members"""
    
    # Mock online users (active in last 5 minutes)
    online = [
        {"id": 1, "username": "zhangsan", "last_active": datetime.now().isoformat()},
        {"id": 2, "username": "lisi", "last_active": (datetime.now() - timedelta(minutes=3)).isoformat()}
    ]
    
    return {"online": online, "count": len(online)}


@router.get("/workload")
async def get_team_workload(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team member workload distribution"""
    
    workload = [
        {"user_id": 1, "username": "zhangsan", "assigned": 5, "completed": 3, "in_progress": 2, "capacity": "80%"},
        {"user_id": 2, "username": "lisi", "assigned": 8, "completed": 5, "in_progress": 3, "capacity": "100%"},
        {"user_id": 3, "username": "wangwu", "assigned": 3, "completed": 1, "in_progress": 2, "capacity": "40%"}
    ]
    
    return {"workload": workload}


# === Mentions ===

@router.get("/search-users")
async def search_users(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search users for mentions"""
    
    # Mock search results
    results = [
        {"id": 1, "username": "zhangsan", "display_name": "张三"},
        {"id": 2, "username": "lisi", "display_name": "李四"},
        {"id": 3, "username": "wangwu", "display_name": "王五"}
    ]
    
    # Filter by query
    results = [u for u in results if q.lower() in u["username"].lower() or q in u.get("display_name", "")]
    
    return {"results": results}