"""Project Detail API - 项目详情页完整数据接口"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.issue import Issue, IssueStatus
from app.models.comment import Comment
from app.models.document import Document

router = APIRouter()


@router.get("/{project_id}/detail")
async def get_project_detail(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目详情页完整数据（含任务、成员、评论/时间线、文档附件、统计）
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 获取项目所有任务
    tasks = db.query(Task).filter(Task.project_id == project_id).all()

    # 任务统计
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "completed")
    in_progress_tasks = sum(1 for t in tasks if t.status == "in_progress")
    pending_tasks = sum(1 for t in tasks if t.status == "pending")
    blocked_tasks = sum(1 for t in tasks if t.status == "blocked")
    overdue_tasks = sum(1 for t in tasks if t.due_date and datetime.now(tz=t.due_date.tzinfo or datetime.now().tzinfo) < datetime.now(tz=t.due_date.tzinfo or datetime.now().tzinfo) and t.status != "completed")

    completion_rate = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0

    # 获取项目所有问题
    issues = db.query(Issue).filter(Issue.project_id == project_id).all()

    # 获取项目成员（去重）
    member_ids = set()
    member_task_counts = {}
    for task in tasks:
        if task.assignee_id:
            member_ids.add(task.assignee_id)
            member_task_counts[task.assignee_id] = member_task_counts.get(task.assignee_id, 0) + 1
        if task.created_by:
            member_ids.add(task.created_by)
            member_task_counts[task.created_by] = member_task_counts.get(task.created_by, 0) + 1

    # 获取团队成员详情
    members = []
    for uid in member_ids:
        user = db.query(User).filter(User.id == uid).first()
        if user:
            members.append({
                "id": user.id,
                "name": user.username,
                "role": "member",
                "avatar": None,
                "initials": (user.username[:2]).upper() if user.username else "??",
                "taskCount": member_task_counts.get(uid, 0),
            })

    # 获取项目相关评论/时间线
    comments = db.query(Comment).filter(
        Comment.project_id == project_id
    ).order_by(Comment.created_at.desc()).limit(50).all()

    timeline_events = []
    for c in comments:
        timeline_events.append({
            "id": c.id,
            "type": "comment",
            "user_name": c.user.username if c.user else "Unknown",
            "user_initials": (c.user.username[:2]).upper() if c.user else "?",
            "content": c.content,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    # 项目事件（任务创建/更新等）
    for t in tasks:
        timeline_events.append({
            "id": f"task_{t.id}",
            "type": "task",
            "user_name": t.creator.username if t.creator else "Unknown",
            "user_initials": (t.creator.username[:2]).upper() if t.creator else "?",
            "content": f"任务 '{t.title}' 状态已改为 {t.status}",
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })

    # 按时间排序
    timeline_events.sort(key=lambda x: x["created_at"] or "", reverse=True)

    # 获取项目相关文档/附件
    documents = db.query(Document).filter(Document.project_id == project_id).all()
    attachments = []
    for doc in documents:
        extensions = {
            "pdf": "pdf", "doc": "doc", "docx": "docx",
            "xls": "xls", "xlsx": "xlsx", "png": "png", "jpg": "jpg", "jpeg": "jpeg",
            "sketch": "sketch", "zip": "zip", "md": "markdown",
        }
        ext = ""
        if doc.name:
            parts = doc.name.rsplit(".", 1)
            if len(parts) == 2:
                ext = parts[1].lower()
        attachments.append({
            "id": doc.id,
            "name": doc.name or "未命名文件",
            "type": extensions.get(ext, "other"),
            "size": 0,  # Document model 没有 size 字段
            "uploaded_at": doc.created_at.isoformat() if doc.created_at else None,
        })

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "code": project.code,
            "description": project.description,
            "status": project.status,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "budget": project.budget or 0,
            "actual_cost": project.actual_cost or 0,
            "owner_id": project.owner_id,
        },
        "tasks": [{
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "assignee_name": t.assignee.username if t.assignee else "",
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "completed": t.status == "completed",
            "estimated_hours": t.estimated_hours or 0,
            "actual_hours": t.actual_hours or 0,
        } for t in tasks],
        "stats": {
            "totalTasks": total_tasks,
            "overdueTasks": overdue_tasks,
            "completionRate": completion_rate,
            "completedTasks": completed_tasks,
            "inProgressTasks": in_progress_tasks,
            "pendingTasks": pending_tasks,
            "blockedTasks": blocked_tasks,
        },
        "teamMembers": members,
        "timelineEvents": timeline_events,
        "attachments": attachments,
    }


@router.put("/{project_id}/detail")
async def update_project_detail(
    project_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新项目基本信息
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    allowed_fields = {"name", "description", "code", "status", "start_date", "end_date", "budget", "actual_cost"}
    for field in allowed_fields:
        if field in update_data and update_data[field] is not None:
            setattr(project, field, update_data[field])

    db.commit()
    db.refresh(project)

    return {
        "id": project.id,
        "name": project.name,
        "code": project.code,
        "description": project.description,
        "status": project.status,
        "start_date": project.start_date.isoformat() if project.start_date else None,
        "end_date": project.end_date.isoformat() if project.end_date else None,
        "budget": project.budget or 0,
        "actual_cost": project.actual_cost or 0,
    }
