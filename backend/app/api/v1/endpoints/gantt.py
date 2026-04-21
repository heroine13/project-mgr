"""
甘特图API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Project
from app.models.gantt import GanttTask, GanttDependency, GanttView, GanttBaseline
from app.schemas.gantt import (
    GanttTaskCreate, GanttTaskUpdate, GanttTaskResponse,
    GanttDependencyCreate, GanttDependencyResponse,
    GanttViewCreate, GanttViewUpdate, GanttViewResponse,
    GanttBaselineCreate, GanttBaselineUpdate, GanttBaselineResponse,
    GanttProjectData, GanttTaskMove, GanttBatchUpdate
)
from app.crud import crud_gantt
from app.crud import crud_project


router = APIRouter()


# ==================== 甘特图任务相关API ====================

@router.post("/tasks", response_model=GanttTaskResponse)
def create_gantt_task(
    task_in: GanttTaskCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """创建甘特图任务"""
    # 检查项目访问权限
    project = crud_project.get_project(db, project_id=task_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查用户是否有项目访问权限（这里简化处理，实际需要实现权限检查）
    # 暂时允许创建者访问
    
    # 创建任务
    try:
        task = crud_gantt.create_gantt_task(db, task_in=task_in, user_id=current_user.id)
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks", response_model=List[GanttTaskResponse])
def get_gantt_tasks(
    project_id: int = Query(..., description="项目ID"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    status_filter: str = Query(None, description="状态过滤器"),
    priority_filter: str = Query(None, description="优先级过滤器"),
    resource_filter: str = Query(None, description="资源过滤器"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """获取项目的甘特图任务列表"""
    # 检查项目访问权限
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    tasks = crud_gantt.get_gantt_tasks_by_project(
        db,
        project_id=project_id,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        priority_filter=priority_filter,
        resource_filter=resource_filter
    )
    return tasks


@router.get("/tasks/{task_id}", response_model=GanttTaskResponse)
def get_gantt_task(
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """获取甘特图任务详情"""
    task = crud_gantt.get_gantt_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 检查权限（简化：只允许任务所在项目的用户访问）
    # 实际需要更详细的权限检查
    
    return task


@router.put("/tasks/{task_id}", response_model=GanttTaskResponse)
def update_gantt_task(
    task_id: int,
    task_in: GanttTaskUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """更新甘特图任务"""
    task = crud_gantt.get_gantt_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 权限检查（简化）
    
    try:
        updated_task = crud_gantt.update_gantt_task(db, db_task=task, task_in=task_in)
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tasks/{task_id}")
def delete_gantt_task(
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """删除甘特图任务"""
    task = crud_gantt.get_gantt_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 权限检查
    
    success = crud_gantt.delete_gantt_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=400, detail="删除失败")
    
    return {"message": "任务删除成功"}


@router.post("/tasks/{task_id}/move", response_model=GanttTaskResponse)
def move_gantt_task(
    task_id: int,
    move_data: GanttTaskMove,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """移动甘特图任务（更新时间和位置）"""
    try:
        task = crud_gantt.move_gantt_task(db, task_id=task_id, move_data=move_data)
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tasks/batch-move", response_model=List[GanttTaskResponse])
def batch_move_gantt_tasks(
    batch_update: GanttBatchUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """批量移动甘特图任务"""
    try:
        tasks = crud_gantt.batch_move_gantt_tasks(db, batch_update=batch_update)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 甘特图依赖关系相关API ====================

@router.post("/dependencies", response_model=GanttDependencyResponse)
def create_gantt_dependency(
    dependency_in: GanttDependencyCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """创建甘特图依赖关系"""
    # 检查任务是否存在
    predecessor = crud_gantt.get_gantt_task(db, task_id=dependency_in.predecessor_id)
    successor = crud_gantt.get_gantt_task(db, task_id=dependency_in.successor_id)
    
    if not predecessor or not successor:
        raise HTTPException(status_code=404, detail="前置或后置任务不存在")
    
    # 检查是否在同一项目中
    if predecessor.project_id != successor.project_id:
        raise HTTPException(status_code=400, detail="任务不在同一项目中")
    
    try:
        dependency = crud_gantt.create_gantt_dependency(
            db, dependency_in=dependency_in, user_id=current_user.id
        )
        return dependency
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dependencies", response_model=List[GanttDependencyResponse])
def get_gantt_dependencies(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """获取项目的甘特图依赖关系列表"""
    # 检查项目访问权限
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    dependencies = crud_gantt.get_gantt_dependencies_by_project(db, project_id=project_id)
    return dependencies


@router.delete("/dependencies/{dependency_id}")
def delete_gantt_dependency(
    dependency_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """删除甘特图依赖关系"""
    dependency = crud_gantt.get_gantt_dependency(db, dependency_id=dependency_id)
    if not dependency:
        raise HTTPException(status_code=404, detail="依赖关系不存在")
    
    # 权限检查
    
    success = crud_gantt.delete_gantt_dependency(db, dependency_id=dependency_id)
    if not success:
        raise HTTPException(status_code=400, detail="删除失败")
    
    return {"message": "依赖关系删除成功"}


# ==================== 甘特图视图相关API ====================

@router.post("/views", response_model=GanttViewResponse)
def create_gantt_view(
    view_in: GanttViewCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """创建甘特图视图"""
    # 检查项目访问权限
    project = crud_project.get_project(db, project_id=view_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        view = crud_gantt.create_gantt_view(db, view_in=view_in, user_id=current_user.id)
        return view
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/views", response_model=List[GanttViewResponse])
def get_gantt_views(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """获取用户对项目的甘特图视图列表"""
    # 检查项目访问权限
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    views = crud_gantt.get_gantt_views_by_project_and_user(
        db, project_id=project_id, user_id=current_user.id
    )
    return views


@router.get("/views/default", response_model=GanttViewResponse)
def get_default_gantt_view(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """获取用户的默认甘特图视图"""
    # 检查项目访问权限
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    view = crud_gantt.get_default_gantt_view(
        db, project_id=project_id, user_id=current_user.id
    )
    
    if not view:
        # 如果没有默认视图，返回第一个视图或创建默认视图
        views = crud_gantt.get_gantt_views_by_project_and_user(
            db, project_id=project_id, user_id=current_user.id
        )
        if views:
            return views[0]
        else:
            # 创建默认视图
            default_view_in = GanttViewCreate(
                project_id=project_id,
                name="默认视图",
                description="自动创建的默认甘特图视图",
                is_default=1
            )
            view = crud_gantt.create_gantt_view(
                db, view_in=default_view_in, user_id=current_user.id
            )
            return view
    
    return view


@router.get("/views/{view_id}", response_model=GanttViewResponse)
def get_gantt_view(
    view_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """获取甘特图视图详情"""
    view = crud_gantt.get_gantt_view(db, view_id=view_id)
    if not view:
        raise HTTPException(status_code=404, detail="视图不存在")
    
    # 权限检查：只能访问自己的视图或公开视图
    if view.user_id != current_user.id and not view.is_public:
        raise HTTPException(status_code=403, detail="无权限访问此视图")
    
    return view


@router.put("/views/{view_id}", response_model=GanttViewResponse)
def update_gantt_view(
    view_id: int,
    view_in: GanttViewUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """更新甘特图视图"""
    view = crud_gantt.get_gantt_view(db, view_id=view_id)
    if not view:
        raise HTTPException(status_code=404, detail="视图不存在")
    
    # 权限检查：只能更新自己的视图
    if view.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限更新此视图")
    
    try:
        updated_view = crud_gantt.update_gantt_view(db, db_view=view, view_in=view_in)
        return updated_view
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/views/{view_id}")
def delete_gantt_view(
    view_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """删除甘特图视图"""
    view = crud_gantt.get_gantt_view(db, view_id=view_id)
    if not view:
        raise HTTPException(status_code=404, detail="视图不存在")
    
    # 权限检查：只能删除自己的视图
    if view.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此视图")
    
    success = crud_gantt.delete_gantt_view(db, view_id=view_id)
    if not success:
        raise HTTPException(status_code=400, detail="删除失败")
    
    return {"message": "视图删除成功"}


# ==================== 甘特图基线相关API ====================

@router.post("/baselines", response_model=GanttBaselineResponse)
def create_gantt_baseline(
    baseline_in: GanttBaselineCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """创建甘特图基线"""
    # 检查项目和任务是否存在
    project = crud_project.get_project(db, project_id=baseline_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    task = crud_gantt.get_gantt_task(db, task_id=baseline_in.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    try:
        baseline = crud_gantt.create_gantt_baseline(
            db, baseline_in=baseline_in, user_id=current_user.id
        )
        return baseline
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/baselines", response_model=List[GanttBaselineResponse])
def get_gantt_baselines(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """获取项目的甘特图基线列表"""
    # 检查项目访问权限
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    baselines = crud_gantt.get_gantt_baselines_by_project(db, project_id=project_id)
    return baselines


@router.put("/baselines/{baseline_id}", response_model=GanttBaselineResponse)
def update_gantt_baseline(
    baseline_id: int,
    baseline_in: GanttBaselineUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """更新甘特图基线（主要更新实际值）"""
    baseline = crud_gantt.get_gantt_baseline(db, baseline_id=baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="基线不存在")
    
    # 权限检查
    
    try:
        updated_baseline = crud_gantt.update_gantt_baseline(
            db, db_baseline=baseline, baseline_in=baseline_in
        )
        return updated_baseline
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/baselines/{baseline_id}")
def delete_gantt_baseline(
    baseline_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """删除甘特图基线"""
    baseline = crud_gantt.get_gantt_baseline(db, baseline_id=baseline_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="基线不存在")
    
    success = crud_gantt.delete_gantt_baseline(db, baseline_id=baseline_id)
    if not success:
        raise HTTPException(status_code=400, detail="删除失败")
    
    return {"message": "基线删除成功"}


# ==================== 综合数据API ====================

@router.get("/project/{project_id}/full-data", response_model=GanttProjectData)
def get_gantt_project_full_data(
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """获取项目的完整甘特图数据"""
    # 检查项目访问权限
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取所有任务
    tasks = crud_gantt.get_gantt_tasks_by_project(db, project_id=project_id, limit=1000)
    
    # 获取所有依赖关系
    dependencies = crud_gantt.get_gantt_dependencies_by_project(db, project_id=project_id)
    
    # 获取用户的所有视图
    views = crud_gantt.get_gantt_views_by_project_and_user(
        db, project_id=project_id, user_id=current_user.id
    )
    
    # 获取所有基线
    baselines = crud_gantt.get_gantt_baselines_by_project(db, project_id=project_id)
    
    # 获取项目资源（用户）信息（简化处理）
    # 实际应该从用户表获取项目成员
    
    return GanttProjectData(
        tasks=tasks,
        dependencies=dependencies,
        views=views,
        baselines=baselines,
        resources=[]  # 这里留空，实际应该填充资源数据
    )