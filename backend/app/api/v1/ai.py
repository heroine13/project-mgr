"""
AI API Endpoints - 智能项目管理功能 (增强版)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

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


class MeetingNotesRequest(BaseModel):
    """Meeting notes request"""
    project_id: int
    recent_updates: list[str]


# === API Endpoints ===

@router.get("/suggestions/tasks")
async def get_task_suggestions(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🤖 AI智能任务建议
    
    基于项目上下文，AI分析并提供：
    - 任务优先级调整建议
    - 资源分配建议
    - 风险识别
    - 综合改进建议
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取项目任务
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    # 调用AI服务生成建议
    suggestions = await AIService.generate_task_suggestions(db, project_id, current_user.id)
    
    return {
        "success": True,
        "project_id": project_id,
        "project_name": project.name,
        "suggestions": suggestions,
        "generated_at": datetime.now().isoformat()
    }


@router.post("/chat")
async def ai_chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    💬 AI对话助手
    
    智能回答项目管理相关问题
    - 项目管理咨询
    - 任务管理建议
    - 进度分析
    - 团队协作指导
    """
    # 构建项目上下文
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
    
    # 获取AI回复
    response = await AIChatService.chat(chat_request.message, project_context)
    
    return {
        "success": True,
        "message": response,
        "conversation_id": f"conv_{current_user.id}_{int(datetime.now().timestamp())}"
    }


@router.post("/summarize/project")
async def summarize_project(
    request: ProjectSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📊 AI项目状态总结
    
    自动生成项目进度总结报告
    - 项目完成情况
    - 问题汇总
    - 改进建议
    """
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取项目数据
    tasks = db.query(Task).filter(Task.project_id == request.project_id).all()
    issues = db.query(Issue).filter(Issue.project_id == request.project_id).all()
    
    tasks_data = [
        {
            "id": t.id,
            "title": t.title,
            "status": str(t.status),
            "priority": str(t.priority),
            "due_date": str(t.due_date) if t.due_date else None
        }
        for t in tasks
    ]
    
    issues_data = [
        {
            "id": i.id,
            "title": i.title,
            "status": str(i.status),
            "priority": str(i.priority)
        }
        for i in issues
    ]
    
    # 生成AI总结
    summary = await AIService.summarize_project_status(project.name, tasks_data, issues_data)
    
    return {
        "success": True,
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
    project_id: Optional[int] = Query(None, description="项目ID（可选）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    👥 AI团队绩效分析
    
    分析团队成员表现
    - 个人绩效统计
    - 最佳表现者识别
    - 需要改进的成员
    - 团队提升建议
    """
    # 获取团队成员
    if project_id:
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        user_ids = set(t.assignee_id for t in tasks if t.assignee_id)
    else:
        tasks = db.query(Task).all()
        user_ids = set(t.assignee_id for t in tasks if t.assignee_id)
    
    # 获取用户详情
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
    
    # 获取任务数据用于分析
    tasks_query = db.query(Task)
    if project_id:
        tasks_query = tasks_query.filter(Task.project_id == project_id)
    all_tasks = tasks_query.all()
    
    tasks_data = [
        {
            "assignee_id": t.assignee_id,
            "status": str(t.status),
            "actual_hours": t.actual_hours or 0
        }
        for t in all_tasks if t.assignee_id
    ]
    
    # AI分析
    analysis = await AIService.analyze_team_performance(team_members, tasks_data)
    
    return {
        "success": True,
        "project_id": project_id,
        "team_size": len(team_members),
        "analysis": analysis
    }


@router.get("/dependencies/suggest")
async def suggest_dependencies(
    task_id: int = Query(..., description="任务ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🔗 AI任务依赖建议
    
    智能分析任务间的依赖关系
    - 推荐前置任务
    - 分析依赖置信度
    - 依赖原因说明
    """
    # 获取任务
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 获取同项目其他任务
    other_tasks = db.query(Task).filter(
        Task.project_id == task.project_id,
        Task.id != task_id
    ).all()
    
    tasks_data = [
        {
            "id": t.id,
            "title": t.title,
            "status": str(t.status)
        }
        for t in other_tasks
    ]
    
    # 获取AI建议
    suggestions = await AIService.suggest_task_dependencies(task.title, tasks_data)
    
    return {
        "success": True,
        "task_id": task_id,
        "task_title": task.title,
        "suggestions": suggestions
    }


@router.post("/meeting/notes")
async def generate_meeting_notes(
    request: MeetingNotesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📝 AI会议纪要生成
    
    根据项目更新自动生成会议纪要
    - 最近进展汇总
    - 待讨论事项
    - 下一步计划
    """
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 生成会议纪要
    notes = await AIService.generate_meeting_notes(project.name, request.recent_updates)
    
    return {
        "success": True,
        "project_name": project.name,
        "notes": notes,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/smart/reply")
async def smart_reply(
    message: str = Query(..., description="用户消息"),
    project_id: Optional[int] = Query(None, description="项目ID（可选）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    💡 AI智能回复
    
    快速获取项目管理相关问题的答案
    """
    # 构建上下文
    context = None
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            context = {
                "project_name": project.name,
                "project_id": project.id
            }
    
    # 获取智能回复
    response = await AIService.smart_reply(message, context)
    
    return {
        "success": True,
        "message": response
    }


@router.get("/status")
async def get_ai_status():
    """
    🔧 AI服务状态查询
    
    返回当前AI服务配置状态
    """
    from app.services.ai import AI_PROVIDER, AI_MODEL, AI_API_KEY
    
    return {
        "provider": AI_PROVIDER,
        "model": AI_MODEL,
        "configured": bool(AI_API_KEY),
        "status": "active" if AI_API_KEY else "demo_mode",
        "message": "AI服务已就绪" if AI_API_KEY else "演示模式，请配置API密钥"
    }

