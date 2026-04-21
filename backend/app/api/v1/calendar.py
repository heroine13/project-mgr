"""
Calendar API - Project and Task Calendar View
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.project import Project
from app.models.issue import Issue

router = APIRouter(prefix="/calendar", tags=["日历视图"])


# === Schemas ===

class CalendarEvent(BaseModel):
    """Calendar event"""
    id: int
    title: str
    start: str  # ISO datetime
    end: Optional[str]
    allDay: bool = False
    color: str
    type: str  # task, project, issue
    resource_id: int
    description: Optional[str] = None
    status: Optional[str] = None


class CalendarEventsResponse(BaseModel):
    """Response for calendar events"""
    events: List[CalendarEvent]
    start: str
    end: str


# === Color Scheme ===
TYPE_COLORS = {
    "task": "#409EFF",      # Blue
    "project": "#67C23A",  # Green
    "issue": "#E6A23C",    # Orange
    "milestone": "#909399" # Gray
}

STATUS_COLORS = {
    "pending": "#909399",
    "in_progress": "#E6A23C",
    "review": "#409EFF",
    "completed": "#67C23A",
    "blocked": "#F56C6C"
}


@router.get("/events")
async def get_calendar_events(
    start: str = Query(..., description="Start date (ISO format)"),
    end: str = Query(..., description="End date (ISO format)"),
    project_id: Optional[int] = Query(None),
    event_type: Optional[str] = Query(None, description="Filter by type: task, project, issue"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get calendar events for specified date range"""
    
    try:
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format.")
    
    events = []
    
    # Get tasks with due dates
    task_query = db.query(Task).filter(
        Task.due_date >= start_date,
        Task.due_date <= end_date
    )
    
    if project_id:
        task_query = task_query.filter(Task.project_id == project_id)
    
    # Filter by user if not admin
    if not current_user.is_superuser:
        task_query = task_query.filter(
            (Task.assignee_id == current_user.id) |
            (Task.created_by == current_user.id)
        )
    
    tasks = task_query.all()
    
    for task in tasks:
        status_color = STATUS_COLORS.get(
            task.status.value if hasattr(task.status, 'value') else str(task.status),
            TYPE_COLORS["task"]
        )
        
        events.append(CalendarEvent(
            id=task.id,
            title=f"[任务] {task.title}",
            start=task.due_date.isoformat(),
            allDay=True,
            color=status_color,
            type="task",
            resource_id=task.id,
            description=task.description,
            status=task.status.value if hasattr(task.status, 'value') else str(task.status)
        ))
    
    # Get projects with start/end dates
    project_query = db.query(Project).filter(
        or_(
            Project.start_date >= start_date,
            Project.end_date <= end_date,
            and_(
                Project.start_date <= end_date,
                Project.end_date >= start_date
            )
        )
    )
    
    projects = project_query.all()
    
    for project in projects:
        if project.start_date:
            events.append(CalendarEvent(
                id=project.id + 100000,  # Offset to avoid ID conflicts
                title=f"[项目开始] {project.name}",
                start=project.start_date.isoformat(),
                allDay=True,
                color=TYPE_COLORS["project"],
                type="project",
                resource_id=project.id,
                description=project.description,
                status=project.status
            ))
        
        if project.end_date:
            events.append(CalendarEvent(
                id=project.id + 200000,
                title=f"[项目截止] {project.name}",
                start=project.end_date.isoformat(),
                allDay=True,
                color=TYPE_COLORS["project"],
                type="project",
                resource_id=project.id,
                description=project.description,
                status=project.status
            ))
    
    # Get issues with due dates
    if event_type is None or event_type == "issue":
        issue_query = db.query(Issue).filter(
            Issue.created_at >= start_date,
            Issue.created_at <= end_date
        )
        
        if project_id:
            issue_query = issue_query.filter(Issue.project_id == project_id)
        
        issues = issue_query.all()
        
        for issue in issues:
            events.append(CalendarEvent(
                id=issue.id + 500000,
                title=f"[Issue] {issue.title}",
                start=issue.created_at.isoformat(),
                allDay=True,
                color=TYPE_COLORS["issue"],
                type="issue",
                resource_id=issue.id,
                description=issue.description,
                status=issue.status.value if hasattr(issue.status, 'value') else str(issue.status)
            ))
    
    return {
        "events": events,
        "start": start,
        "end": end
    }


@router.get("/month-view")
async def get_month_view(
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month (1-12)"),
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get calendar events for a specific month"""
    
    # Calculate start and end of month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    # Get events
    return await get_calendar_events(
        start=start_date.isoformat(),
        end=end_date.isoformat(),
        project_id=project_id,
        db=db,
        current_user=current_user
    )


@router.get("/upcoming")
async def get_upcoming_events(
    days: int = Query(7, ge=1, le=30),
    project_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming events for the next N days"""
    
    now = datetime.now()
    end_date = now + timedelta(days=days)
    
    # Get upcoming tasks
    query = db.query(Task).filter(
        Task.due_date >= now,
        Task.due_date <= end_date,
        Task.status.notin_([TaskStatus.COMPLETED])
    )
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    if not current_user.is_superuser:
        query = query.filter(
            (Task.assignee_id == current_user.id) |
            (Task.created_by == current_user.id)
        )
    
    tasks = query.order_by(Task.due_date).limit(limit).all()
    
    upcoming = []
    for task in tasks:
        days_until = (task.due_date - now).days
        upcoming.append({
            "id": task.id,
            "type": "task",
            "title": task.title,
            "due_date": task.due_date.isoformat(),
            "days_until": days_until,
            "status": task.status.value if hasattr(task.status, 'value') else str(task.status),
            "priority": task.priority.value if hasattr(task.priority, 'value') else str(task.priority)
        })
    
    return {
        "upcoming": upcoming,
        "days": days
    }


# Import needed for the query
from sqlalchemy import or_, and_