"""
数据导出 API 端点
支持 Excel、CSV、PDF 格式导出
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.utils.exporter import (
    export_to_excel,
    export_to_csv,
    export_to_pdf,
    format_task_for_export,
    format_project_for_export,
    format_user_for_export
)

router = APIRouter(prefix="/export", tags=["数据导出"])


# === 任务导出 ===

@router.get("/tasks")
async def export_tasks(
    format: str = Query("excel", enum=["excel", "csv", "pdf"]),
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出任务数据
    
    Args:
        format: 导出格式 (excel, csv, pdf)
        project_id: 项目ID筛选
        status: 任务状态筛选
    """
    # 构建查询
    query = db.query(Task).filter(Task.is_deleted == False)
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    if status:
        query = query.filter(Task.status == status)
    
    # 获取任务列表
    tasks = query.all()
    
    # 转换为导出格式
    task_data = []
    for task in tasks:
        project = db.query(Project).filter(Project.id == task.project_id).first()
        task_data.append({
            'id': task.id,
            'title': task.title,
            'project_name': project.name if project else '',
            'assignee_name': task.assignee_id,  # 简化处理
            'status': task.status,
            'priority': task.priority,
            'start_date': str(task.start_date) if task.start_date else '',
            'due_date': str(task.due_date) if task.due_date else '',
            'progress': task.progress or 0,
            'description': task.description or ''
        })
    
    headers, rows = format_task_for_export(task_data)
    
    # 根据格式导出
    filename = f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if format == "excel":
        content = export_to_excel(headers, rows, f"{filename}.xlsx")
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == "csv":
        content = export_to_csv(headers, rows, f"{filename}.csv")
        media_type = "text/csv; charset=utf-8"
    elif format == "pdf":
        content = export_to_pdf(headers, rows, f"{filename}.pdf")
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="不支持的导出格式")
    
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}.{format}"
        }
    )


# === 项目导出 ===

@router.get("/projects")
async def export_projects(
    format: str = Query("excel", enum=["excel", "csv", "pdf"]),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出项目数据
    """
    # 构建查询
    query = db.query(Project).filter(Project.is_deleted == False)
    
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.all()
    
    # 转换为导出格式
    project_data = []
    for project in projects:
        project_data.append({
            'id': project.id,
            'name': project.name,
            'owner_name': project.owner_id,  # 简化处理
            'status': project.status,
            'start_date': str(project.start_date) if project.start_date else '',
            'end_date': str(project.end_date) if project.end_date else '',
            'budget': project.budget or 0,
            'progress': project.progress or 0,
            'description': project.description or ''
        })
    
    headers, rows = format_project_for_export(project_data)
    
    filename = f"projects_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if format == "excel":
        content = export_to_excel(headers, rows, f"{filename}.xlsx")
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == "csv":
        content = export_to_csv(headers, rows, f"{filename}.csv")
        media_type = "text/csv; charset=utf-8"
    elif format == "pdf":
        content = export_to_pdf(headers, rows, f"{filename}.pdf")
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="不支持的导出格式")
    
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}.{format}"
        }
    )


# === 用户导出 (仅管理员) ===

@router.get("/users")
async def export_users(
    format: str = Query("excel", enum=["excel", "csv", "pdf"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出用户数据 (仅管理员)
    """
    # 检查管理员权限
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="仅管理员可导出用户数据")
    
    users = db.query(User).all()
    
    # 转换为导出格式
    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name or '',
            'is_active': user.is_active,
            'created_at': str(user.created_at) if user.created_at else ''
        })
    
    headers, rows = format_user_for_export(user_data)
    
    filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if format == "excel":
        content = export_to_excel(headers, rows, f"{filename}.xlsx")
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == "csv":
        content = export_to_csv(headers, rows, f"{filename}.csv")
        media_type = "text/csv; charset=utf-8"
    elif format == "pdf":
        content = export_to_pdf(headers, rows, f"{filename}.pdf")
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="不支持的导出格式")
    
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}.{format}"
        }
    )


# === 统计报表导出 ===

@router.get("/statistics")
async def export_statistics(
    format: str = Query("excel", enum=["excel", "csv", "pdf"]),
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出统计数据报表
    """
    # 获取统计数据
    stats = {
        '总项目数': 0,
        '进行中项目': 0,
        '已完成项目': 0,
        '总任务数': 0,
        '进行中任务': 0,
        '已完成任务': 0,
        '团队成员数': 0
    }
    
    # 项目统计
    project_query = db.query(Project).filter(Project.is_deleted == False)
    if project_id:
        project_query = project_query.filter(Project.id == project_id)
    
    projects = project_query.all()
    stats['总项目数'] = len(projects)
    stats['进行中项目'] = sum(1 for p in projects if p.status == 'active')
    stats['已完成项目'] = sum(1 for p in projects if p.status == 'completed')
    
    # 任务统计
    task_query = db.query(Task).filter(Task.is_deleted == False)
    if project_id:
        task_query = task_query.filter(Task.project_id == project_id)
    
    tasks = task_query.all()
    stats['总任务数'] = len(tasks)
    stats['进行中任务'] = sum(1 for t in tasks if t.status == 'in_progress')
    stats['已完成任务'] = sum(1 for t in tasks if t.status == 'completed')
    
    # 用户统计
    stats['团队成员数'] = db.query(User).filter(User.is_active == True).count()
    
    # 格式化数据
    headers = ['统计项', '数值']
    rows = [[k, v] for k, v in stats.items()]
    
    filename = f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if format == "excel":
        content = export_to_excel(headers, rows, f"{filename}.xlsx")
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == "csv":
        content = export_to_csv(headers, rows, f"{filename}.csv")
        media_type = "text/csv; charset=utf-8"
    elif format == "pdf":
        content = export_to_pdf(headers, rows, f"{filename}.pdf")
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="不支持的导出格式")
    
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}.{format}"
        }
    )


# 导入 datetime
from datetime import datetime