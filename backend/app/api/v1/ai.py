"""
AI API Endpoints - Intelligent Features
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.models.issue import Issue
from app.services.ai import AIService, AIChatService

router = APIRouter(prefix="/ai", tags=["AI智能助手"])


# === Schemas ===

class TaskSuggestionRequest(BaseModel):
    """Request for task suggestions"""
    project_id: int


class ChatRequest(BaseModel):
    """AI chat request"""
    message: str
    project_id: Optional[int] = None


class ProjectSummaryRequest(BaseModel):
    """Project summary request"""
    project_id: int


# === API Endpoints ===

@router.get("/suggestions/tasks")
async def get_task_suggestions(
    project_id: int = Query(..., description="Project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered task suggestions"""
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # Get project tasks
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    tasks_data = [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
            "priority": t.priority.value if hasattr(t.priority, 'value') else str(t.priority),
            "assignee_id": t.assignee_id,
            "due_date": t.due_date.isoformat() if t.due_date else None
        }
        for t in tasks
    ]
    
    # Get AI suggestions
    suggestions = AIService.generate_task_suggestions(db, project_id, current_user.id)
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "suggestions": suggestions,
        "generated_at": "now"
    }


@router.post("/chat")
async def ai_chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI chat endpoint for project management assistance"""
    
    # Build project context if project_id provided
    project_context = None
    if chat_request.project_id:
        project = db.query(Project).filter(Project.id == chat_request.project_id).first()
        if project:
            tasks = db.query(Task).filter(Task.project_id == project.id).all()
            completed = sum(1 for t in tasks if str(t.status) == "completed")
            
            project_context = {
                "name": project.name,
                "task_count": len(tasks),
                "completion_rate": round(completed / len(tasks) * 100, 1) if tasks else 0
            }
    
    # Get AI response
    response = await AIChatService.chat(chat_request.message, project_context)
    
    return {
        "message": response,
        "conversation_id": "conv_123"  # Would be generated in production
    }


@router.post("/summarize/project")
async def summarize_project(
    request: ProjectSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered project status summary"""
    
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # Get project data
    tasks = db.query(Task).filter(Task.project_id == request.project_id).all()
    issues = db.query(Issue).filter(Issue.project_id == request.project_id).all()
    
    tasks_data = [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
            "priority": t.priority.value if hasattr(t.priority, 'value') else str(t.priority),
            "due_date": t.due_date.isoformat() if t.due_date else None
        }
        for t in tasks
    ]
    
    issues_data = [
        {
            "id": i.id,
            "title": i.title,
            "status": i.status.value if hasattr(i.status, 'value') else str(i.status),
            "priority": i.priority.value if hasattr(i.priority, 'value') else str(i.priority)
        }
        for i in issues
    ]
    
    # Generate summary
    summary = AIService.summarize_project_status(project.name, tasks_data, issues_data)
    
    return {
        "project_id": request.project_id,
        "project_name": project.name,
        "summary": summary,
        "metrics": {
            "total_tasks": len(tasks),
            "completed_tasks": sum(1 for t in tasks if str(t.status) == "completed"),
            "total_issues": len(issues),
            "open_issues": sum(1 for i in issues if str(i.status) == "open")
        }
    }


@router.get("/team/analysis")
async def analyze_team_performance(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered team performance analysis"""
    
    # Get team members
    if project_id:
        # Get users who have tasks in this project
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        user_ids = set(t.assignee_id for t in tasks if t.assignee_id)
    else:
        # Get all users with tasks
        tasks = db.query(Task).all()
        user_ids = set(t.assignee_id for t in tasks if t.assignee_id)
    
    # Get user details
    from app.models.user import User as UserModel
    team_members = []
    for user_id in user_ids:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            team_members.append({
                "id": user.id,
                "username": user.username,
                "email": user.email
            })
    
    # Get all tasks for analysis
    tasks_query = db.query(Task)
    if project_id:
        tasks_query = tasks_query.filter(Task.project_id == project_id)
    all_tasks = tasks_query.all()
    
    tasks_data = [
        {
            "assignee_id": t.assignee_id,
            "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
            "actual_hours": t.actual_hours or 0
        }
        for t in all_tasks if t.assignee_id
    ]
    
    # Get AI analysis
    analysis = AIService.analyze_team_performance(team_members, tasks_data)
    
    return {
        "project_id": project_id,
        "team_size": len(team_members),
        "analysis": analysis
    }


@router.get("/dependencies/suggest")
async def suggest_dependencies(
    task_id: int = Query(..., description="Task ID to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Suggest task dependencies based on AI analysis"""
    
    # Get the task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # Get other tasks in the same project
    other_tasks = db.query(Task).filter(
        Task.project_id == task.project_id,
        Task.id != task_id
    ).all()
    
    tasks_data = [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status.value if hasattr(t.status, 'value') else str(t.status)
        }
        for t in other_tasks
    ]
    
    # Get AI suggestions
    suggestions = AIService.suggest_task_dependencies(task.title, tasks_data)
    
    return {
        "task_id": task_id,
        "task_title": task.title,
        "suggestions": suggestions
    }