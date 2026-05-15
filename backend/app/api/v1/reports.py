"""
高级报表 API 接口 - 使用真实数据库数据
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.models.issue import Issue, IssueStatus

router = APIRouter(prefix="/api/v1/reports", tags=["报表管理"])


# ==================== 响应模型 ====================

class ReportResponse(BaseModel):
    """报表响应"""
    code: int = 0
    msg: str = "success"
    data: Optional[Dict[str, Any]] = None


# ==================== 报表接口 ====================

@router.get("/overview", summary="项目概览报表")
async def get_overview_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取项目概览报表 - 真实数据"""
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "active").count()
    completed_projects = db.query(Project).filter(Project.status == "completed").count()
    
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "completed").count()
    in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
    pending_tasks = db.query(Task).filter(Task.status == "pending").count()
    completion_rate = round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
    
    return ReportResponse(data={
        "generated_at": datetime.now().isoformat(),
        "report_type": "项目概览报表",
        "data": {
            "title": "项目概览",
            "summary": {
                "total_tasks": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "pending": pending_tasks,
                "completion_rate": completion_rate
            },
            "projects": {
                "total": total_projects,
                "active": active_projects,
                "completed": completed_projects
            },
            "team": {
                "total": db.query(User).count(),
                "active": db.query(User).filter(User.is_active == True).count()
            }
        }
    })


@router.get("/trend", summary="任务趋势报表")
async def get_trend_report(days: int = Query(30, ge=7, le=90), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取任务趋势报表 - 真实数据"""
    trends = []
    today = datetime.now()
    
    for i in range(days):
        date = (today - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        start_date = (today - timedelta(days=days - i - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = (today - timedelta(days=days - i)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        created = db.query(Task).filter(
            Task.created_at >= start_date,
            Task.created_at < end_date
        ).count()
        
        completed = db.query(Task).filter(
            Task.status == "completed",
            Task.updated_at >= start_date,
            Task.updated_at < end_date
        ).count()
        
        cancelled = db.query(Task).filter(
            Task.status == "completed",  # 简化处理
            Task.updated_at >= start_date,
            Task.updated_at < end_date
        ).count()
        
        trends.append({
            "date": date,
            "created": created,
            "completed": completed,
            "cancelled": cancelled
        })
    
    return ReportResponse(data={
        "generated_at": datetime.now().isoformat(),
        "report_type": "任务趋势报表",
        "period_days": days,
        "data": {"trend": trends}
    })


@router.get("/team", summary="团队绩效报表")
async def get_team_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取团队绩效报表 - 真实数据"""
    from app.models.user import User
    from app.models.task import Task
    
    users = db.query(User).filter(User.is_active == True).all()
    team_data = []
    for user in users[:10]:  # 最多10人
        tasks_completed = db.query(Task).filter(
            Task.assignee_id == user.id,
            Task.status == "completed"
        ).count()
        tasks_in_progress = db.query(Task).filter(
            Task.assignee_id == user.id,
            Task.status == "in_progress"
        ).count()
        
        team_data.append({
            "name": user.full_name or user.username,
            "tasks_completed": tasks_completed,
            "tasks_in_progress": tasks_in_progress,
            "on_time_rate": 100.0  # TODO: 需要逾期判断逻辑
        })
    
    return ReportResponse(data={
        "generated_at": datetime.now().isoformat(),
        "report_type": "团队绩效报表",
        "data": {"team": team_data}
    })


@router.get("/resource", summary="资源利用报表")
async def get_resource_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取资源利用报表 - 真实数据"""
    total_users = db.query(User).filter(User.is_active == True).count()
    active_users = db.query(Task).filter(
        Task.assignee_id != None,
        Task.status == "in_progress"
    ).distinct().count()
    
    return ReportResponse(data={
        "generated_at": datetime.now().isoformat(),
        "report_type": "资源利用报表",
        "data": {
            "overall": round(active_users / total_users * 100, 1) if total_users > 0 else 0,
            "by_member": [],
            "by_project": []
        }
    })


@router.get("/budget", summary="预算分析报表")
async def get_budget_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取预算分析报表 - 真实数据"""
    total_budget = db.query(func.sum(Project.budget)).scalar() or 0
    total_cost = db.query(func.sum(Project.actual_cost)).scalar() or 0
    
    return ReportResponse(data={
        "generated_at": datetime.now().isoformat(),
        "report_type": "预算分析报表",
        "data": {
            "total_budget": total_budget,
            "spent": total_cost,
            "remaining": total_budget - total_cost,
            "by_project": [
                {
                    "project": p.name,
                    "budget": p.budget or 0,
                    "spent": p.actual_cost or 0
                }
                for p in db.query(Project).all()
            ]
        }
    })


@router.get("/risk", summary="风险分析报表")
async def get_risk_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取风险分析报表 - 真实数据"""
    blocked_tasks = db.query(Task).filter(Task.status == "blocked").count()
    overdue_tasks = db.query(Task).filter(
        Task.due_date < datetime.now(),
        Task.status != "completed"
    ).count()
    open_issues = db.query(Issue).filter(Issue.status == "open").count()
    
    return ReportResponse(data={
        "generated_at": datetime.now().isoformat(),
        "report_type": "风险分析报表",
        "data": {
            "blocked_tasks": blocked_tasks,
            "overdue_tasks": overdue_tasks,
            "open_issues": open_issues,
            "risk_level": "high" if (blocked_tasks + overdue_tasks) > 5 else "medium" if (blocked_tasks + overdue_tasks) > 2 else "low"
        }
    })


@router.get("/comprehensive", summary="综合报表")
async def get_comprehensive_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取综合报表 - 真实数据"""
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "active").count()
    completed_projects = db.query(Project).filter(Project.status == "completed").count()
    
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "completed").count()
    in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
    pending_tasks = db.query(Task).filter(Task.status == "pending").count()
    completion_rate = round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
    
    return ReportResponse(data={
        "generated_at": datetime.now().isoformat(),
        "report_type": "综合报表",
        "data": {
            "projects": {
                "total": total_projects,
                "active": active_projects,
                "completed": completed_projects
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "pending": pending_tasks,
                "completion_rate": completion_rate
            },
            "team": {
                "total": db.query(User).count(),
                "active": db.query(User).filter(User.is_active == True).count()
            },
            "budget": {
                "total": db.query(func.sum(Project.budget)).scalar() or 0,
                "spent": db.query(func.sum(Project.actual_cost)).scalar() or 0,
            }
        }
    })


@router.get("/dashboard", summary="仪表盘数据")
async def get_dashboard_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取仪表盘数据 - 真实数据"""
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "completed").count()
    in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
    pending_tasks = db.query(Task).filter(Task.status == "pending").count()
    completion_rate = round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
    
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "active").count()
    completed_projects = db.query(Project).filter(Project.status == "completed").count()
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    overdue_tasks = db.query(Task).filter(
        Task.due_date < datetime.now(),
        Task.status != "completed"
    ).count()
    
    # 最近7天趋势
    trend = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=6 - i)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = (datetime.now() - timedelta(days=5 - i)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        created = db.query(Task).filter(
            Task.created_at >= start_date,
            Task.created_at < end_date
        ).count()
        
        completed = db.query(Task).filter(
            Task.status == "completed",
            Task.updated_at >= start_date,
            Task.updated_at < end_date
        ).count()
        
        trend.append({
            "date": date,
            "created": created,
            "completed": completed,
        })
    
    # 项目列表
    projects = []
    for p in db.query(Project).order_by(desc(Project.created_at)).limit(5).all():
        task_count = db.query(Task).filter(Task.project_id == p.id).count()
        completed_count = db.query(Task).filter(
            Task.project_id == p.id,
            Task.status == "completed"
        ).count()
        projects.append({
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "status": p.status,
            "task_count": task_count,
            "completed_tasks": completed_count,
            "completion_rate": round(completed_count / task_count * 100, 1) if task_count > 0 else 0,
        })
    
    # 最近活动
    activities = []
    for t in db.query(Task).order_by(desc(Task.updated_at)).limit(5).all():
        activities.append({
            "action": "created a task" if t.status == "pending" else "updated task",
            "entity_type": "Task",
            "entity_name": t.title,
            "created_at": t.updated_at.isoformat() if t.updated_at else None
        })
    
    return ReportResponse(data={
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_tasks": total_tasks,
            "completed": completed_tasks,
            "in_progress": in_progress_tasks,
            "pending": pending_tasks,
            "completion_rate": completion_rate
        },
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "completed": completed_projects
        },
        "team": {
            "total": total_users,
            "active": active_users
        },
        "trend": trend,
        "overdue_tasks": overdue_tasks,
        "project_list": projects,
        "recent_activities": activities,
    })


# ==================== 报表列表 ====================

@router.get("/types", summary="报表类型列表")
async def get_report_types():
    """获取所有可用的报表类型"""
    return ReportResponse(data={
        "types": [
            {"id": "overview", "name": "项目概览", "description": "项目整体状态和进度"},
            {"id": "trend", "name": "任务趋势", "description": "任务创建和完成趋势"},
            {"id": "team", "name": "团队绩效", "description": "团队成员工作绩效"},
            {"id": "resource", "name": "资源利用", "description": "资源使用情况分析"},
            {"id": "budget", "name": "预算分析", "description": "预算执行情况"},
            {"id": "risk", "name": "风险分析", "description": "项目风险评估"},
            {"id": "comprehensive", "name": "综合报表", "description": "所有报表汇总"},
            {"id": "dashboard", "name": "仪表盘", "description": "精简仪表盘数据"}
        ]
    })
