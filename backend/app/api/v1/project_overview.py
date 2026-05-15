"""Project Overview API - 项目总览接口"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.models.issue import Issue, IssueStatus

router = APIRouter(tags=["项目总览"])


@router.get("/summary")
async def get_projects_summary(
    status: Optional[str] = Query(None, description="项目状态过滤: active/completed/archived"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有项目的汇总统计
    包含每个项目的任务数、问题数、完成率等
    """
    query = db.query(
        Project.id,
        Project.name,
        Project.code,
        Project.description,
        Project.status,
        Project.budget,
        Project.actual_cost,
        Project.start_date,
        Project.end_date,
        Project.owner_id,
        Project.created_at,
        func.count(Task.id).label("task_count"),
        func.sum(case((Task.status == "completed", 1), else_=0)).label("completed_tasks"),
        func.sum(case((Task.status == "in_progress", 1), else_=0)).label("in_progress_tasks"),
        func.sum(case((Task.status == "pending", 1), else_=0)).label("pending_tasks"),
        func.sum(case((Task.status == "blocked", 1), else_=0)).label("blocked_tasks"),
        func.count(Issue.id).label("issue_count"),
        func.sum(case((Issue.status == "open", 1), else_=0)).label("open_issues"),
        func.sum(case((Issue.status == "resolved", 1), else_=0)).label("resolved_issues"),
    ).outerjoin(Task, Task.project_id == Project.id).outerjoin(Issue, Issue.project_id == Project.id).group_by(Project.id)

    if status:
        query = query.filter(Project.status == status)

    query = query.order_by(Project.created_at.desc())

    projects_data = []
    for row in query.all():
        task_count = row.task_count or 0
        completed = row.completed_tasks or 0
        in_progress = row.in_progress_tasks or 0
        pending = row.pending_tasks or 0
        blocked = row.blocked_tasks or 0
        completion_rate = round(completed / task_count * 100, 1) if task_count > 0 else 0

        projects_data.append({
            "id": row.id,
            "name": row.name,
            "code": row.code,
            "description": row.description,
            "status": row.status,
            "budget": row.budget or 0,
            "actual_cost": row.actual_cost or 0,
            "start_date": row.start_date.isoformat() if row.start_date else None,
            "end_date": row.end_date.isoformat() if row.end_date else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "task_count": task_count,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "pending_tasks": pending,
            "blocked_tasks": blocked,
            "completion_rate": completion_rate,
            "issue_count": row.issue_count or 0,
            "open_issues": row.open_issues or 0,
            "resolved_issues": row.resolved_issues or 0,
        })

    total_projects = len(projects_data)
    active_projects = len([p for p in projects_data if p["status"] == "active"])
    completed_projects = len([p for p in projects_data if p["status"] == "completed"])
    total_tasks = sum(p["task_count"] for p in projects_data)
    total_completed_tasks = sum(p["completed_tasks"] for p in projects_data)
    total_issues = sum(p["issue_count"] for p in projects_data)
    total_open_issues = sum(p["open_issues"] for p in projects_data)

    return {
        "stats": {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "total_tasks": total_tasks,
            "completed_tasks": total_completed_tasks,
            "total_issues": total_issues,
            "open_issues": total_open_issues,
        },
        "projects": projects_data,
    }


@router.get("/project/{project_id}")
async def get_project_detail(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个项目的详细信息（含任务和问题统计）
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    issues = db.query(Issue).filter(Issue.project_id == project_id).all()

    task_stats = {
        "total": len(tasks),
        "pending": sum(1 for t in tasks if t.status == "pending"),
        "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
        "completed": sum(1 for t in tasks if t.status == "completed"),
        "blocked": sum(1 for t in tasks if t.status == "blocked"),
    }

    issue_total = len(issues)
    open_issues = sum(1 for i in issues if i.status == "open")
    resolved_issues = sum(1 for i in issues if i.status == "resolved")
    completion_rate = round((task_stats["completed"] / task_stats["total"]) * 100, 1) if task_stats["total"] > 0 else 0

    return {
        "id": project.id,
        "name": project.name,
        "code": project.code,
        "description": project.description,
        "status": project.status,
        "budget": project.budget or 0,
        "actual_cost": project.actual_cost or 0,
        "start_date": project.start_date.isoformat() if project.start_date else None,
        "end_date": project.end_date.isoformat() if project.end_date else None,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "stats": {
            "tasks": task_stats,
            "issues": {
                "total": issue_total,
                "open": open_issues,
                "resolved": resolved_issues,
            },
            "completion_rate": completion_rate,
        },
    }
