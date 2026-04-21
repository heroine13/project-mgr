"""
Enhanced Reports API - Advanced Analytics and Visualizations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.project import Project
from app.models.issue import Issue, IssueStatus, IssuePriority

router = APIRouter(prefix="/reports", tags=["报表增强"])


# === Dashboard Reports ===

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard summary statistics"""
    # Base query conditions
    task_query = db.query(Task)
    project_query = db.query(Project)
    issue_query = db.query(Issue)
    
    if project_id:
        task_query = task_query.filter(Task.project_id == project_id)
        issue_query = issue_query.filter(Issue.project_id == project_id)
    
    # Task stats
    total_tasks = task_query.count()
    pending_tasks = task_query.filter(Task.status == TaskStatus.PENDING).count()
    in_progress_tasks = task_query.filter(Task.status == TaskStatus.IN_PROGRESS).count()
    completed_tasks = task_query.filter(Task.status == TaskStatus.COMPLETED).count()
    blocked_tasks = task_query.filter(Task.status == TaskStatus.BLOCKED).count()
    
    # Project stats
    total_projects = project_query.count()
    active_projects = project_query.filter(Project.status == "active").count()
    completed_projects = project_query.filter(Project.status == "completed").count()
    
    # Issue stats
    total_issues = issue_query.count()
    open_issues = issue_query.filter(Issue.status == IssueStatus.OPEN).count()
    resolved_issues = issue_query.filter(Issue.status == IssueStatus.RESOLVED).count()
    
    # Calculate completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        "tasks": {
            "total": total_tasks,
            "pending": pending_tasks,
            "in_progress": in_progress_tasks,
            "completed": completed_tasks,
            "blocked": blocked_tasks,
            "completion_rate": round(completion_rate, 1)
        },
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "completed": completed_projects
        },
        "issues": {
            "total": total_issues,
            "open": open_issues,
            "resolved": resolved_issues,
            "resolution_rate": round(resolved_issues / total_issues * 100, 1) if total_issues > 0 else 0
        }
    }


@router.get("/dashboard/trends")
async def get_dashboard_trends(
    days: int = Query(30, ge=7, le=90),
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trend data for the specified number of days"""
    start_date = datetime.now() - timedelta(days=days)
    
    # Task creation trend
    task_created = (
        db.query(
            func.date(Task.created_at).label('date'),
            func.count(Task.id).label('count')
        )
        .filter(Task.created_at >= start_date)
        .group_by(func.date(Task.created_at))
        .all()
    )
    
    # Task completion trend
    task_completed = (
        db.query(
            func.date(Task.updated_at).label('date'),
            func.count(Task.id).label('count')
        )
        .filter(Task.updated_at >= start_date, Task.status == TaskStatus.COMPLETED)
        .group_by(func.date(Task.updated_at))
        .all()
    )
    
    # Issue creation trend
    issue_created = (
        db.query(
            func.date(Issue.created_at).label('date'),
            func.count(Issue.id).label('count')
        )
        .filter(Issue.created_at >= start_date)
        .group_by(func.date(Issue.created_at))
        .all()
    )
    
    # Fill in missing dates with zero
    date_range = [(start_date + timedelta(days=i)).date() for i in range(days)]
    
    task_created_dict = {str(row.date): row.count for row in task_created}
    task_completed_dict = {str(row.date): row.count for row in task_completed}
    issue_created_dict = {str(row.date): row.count for row in issue_created}
    
    trends = []
    for date in date_range:
        date_str = str(date)
        trends.append({
            "date": date_str,
            "tasks_created": task_created_dict.get(date_str, 0),
            "tasks_completed": task_completed_dict.get(date_str, 0),
            "issues_created": issue_created_dict.get(date_str, 0)
        })
    
    return {
        "period_days": days,
        "trends": trends
    }


# === Task Reports ===

@router.get("/tasks/by-priority")
async def get_tasks_by_priority(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task count by priority"""
    query = db.query(Task.priority, func.count(Task.id)).group_by(Task.priority)
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    results = query.all()
    
    # Convert enum to string
    return {
        "priorities": [
            {"priority": row[0].value if hasattr(row[0], 'value') else str(row[0]), "count": row[1]}
            for row in results
        ]
    }


@router.get("/tasks/by-assignee")
async def get_tasks_by_assignee(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task distribution by assignee"""
    query = (
        db.query(
            Task.assignee_id,
            func.count(Task.id).label('total'),
            func.sum(func.cast(Task.estimated_hours, db.bind.dialect.type_descriptor(db.bind.dialect, 'INTEGER'))).label('estimated_hours')
        )
        .filter(Task.assignee_id.isnot(None))
        .group_by(Task.assignee_id)
    )
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    results = query.all()
    
    return {
        "assignees": [
            {
                "assignee_id": row[0],
                "task_count": row[1],
                "estimated_hours": row[2] or 0
            }
            for row in results
        ]
    }


@router.get("/tasks/overdue")
async def get_overdue_tasks(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overdue tasks"""
    query = (
        db.query(Task)
        .filter(
            Task.due_date < datetime.now(),
            Task.status.notin_([TaskStatus.COMPLETED])
        )
    )
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    tasks = query.order_by(Task.due_date).limit(50).all()
    
    return {
        "count": len(tasks),
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status.value if isinstance(task.status, TaskStatus) else task.status,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "assignee_id": task.assignee_id,
                "project_id": task.project_id
            }
            for task in tasks
        ]
    }


# === Project Reports ===

@router.get("/projects/progress")
async def get_project_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for all projects"""
    projects = db.query(Project).all()
    
    result = []
    for project in projects:
        total_tasks = db.query(Task).filter(Task.project_id == project.id).count()
        completed_tasks = db.query(Task).filter(
            Task.project_id == project.id,
            Task.status == TaskStatus.COMPLETED
        ).count()
        
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        result.append({
            "id": project.id,
            "name": project.name,
            "code": project.code,
            "status": project.status,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "progress": round(progress, 1)
        })
    
    return {"projects": result}


@router.get("/projects/budget")
async def get_project_budget(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get budget analysis for projects"""
    projects = db.query(Project).filter(Project.budget > 0).all()
    
    result = []
    for project in projects:
        # Calculate actual cost from tasks
        actual_cost = db.query(
            func.sum(Task.actual_hours * 50)  # Assuming $50/hour
        ).filter(Task.project_id == project.id).scalar() or 0
        
        result.append({
            "id": project.id,
            "name": project.name,
            "code": project.code,
            "budget": project.budget,
            "actual_cost": actual_cost,
            "remaining": project.budget - actual_cost,
            "utilization_rate": round(actual_cost / project.budget * 100, 1) if project.budget > 0 else 0
        })
    
    return {"projects": result}


# === Team Performance ===

@router.get("/team/performance")
async def get_team_performance(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team member performance metrics"""
    # Get all users who have tasks
    users_with_tasks = (
        db.query(
            Task.assignee_id,
            func.count(Task.id).label('total_tasks'),
            func.sum(
                db.case(
                    (Task.status == TaskStatus.COMPLETED, 1),
                    else_=0
                )
            ).label('completed_tasks'),
            func.avg(Task.actual_hours).label('avg_hours')
        )
        .filter(Task.assignee_id.isnot(None))
        .group_by(Task.assignee_id)
    )
    
    if project_id:
        users_with_tasks = users_with_tasks.filter(Task.project_id == project_id)
    
    results = users_with_tasks.all()
    
    team_performance = []
    for row in results:
        user_id = row[0]
        total = row[1]
        completed = row[2] or 0
        avg_hours = float(row[3] or 0)
        
        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        
        team_performance.append({
            "user_id": user_id,
            "username": user.username if user else "Unknown",
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
            "avg_hours_per_task": round(avg_hours, 1)
        })
    
    return {"team": team_performance}


# === Export Reports ===

@router.get("/export/summary")
async def export_summary_report(
    project_id: Optional[int] = Query(None),
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export comprehensive summary report"""
    summary = await get_dashboard_summary(project_id, db, current_user)
    trends = await get_dashboard_trends(30, project_id, db, current_user)
    
    if format == "json":
        return {
            "generated_at": datetime.now().isoformat(),
            "project_id": project_id,
            "summary": summary,
            "trends": trends
        }
    
    # CSV format
    csv_lines = ["Metric,Value"]
    csv_lines.append(f"Total Tasks,{summary['tasks']['total']}")
    csv_lines.append(f"Completed Tasks,{summary['tasks']['completed']}")
    csv_lines.append(f"Completion Rate,{summary['tasks']['completion_rate']}%")
    csv_lines.append(f"Total Projects,{summary['projects']['total']}")
    csv_lines.append(f"Active Projects,{summary['projects']['active']}")
    csv_lines.append(f"Total Issues,{summary['issues']['total']}")
    csv_lines.append(f"Resolved Issues,{summary['issues']['resolved']}")
    
    return "\n".join(csv_lines)