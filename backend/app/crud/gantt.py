"""
甘特图相关CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, timedelta
from app.models.gantt import GanttTask, GanttDependency, GanttView, GanttBaseline
from app.schemas.gantt import (
    GanttTaskCreate, GanttTaskUpdate,
    GanttDependencyCreate,
    GanttViewCreate, GanttViewUpdate,
    GanttBaselineCreate, GanttBaselineUpdate,
    GanttTaskMove, GanttBatchUpdate
)


# ==================== GanttTask CRUD ====================

def create_gantt_task(db: Session, task_in: GanttTaskCreate, user_id: int) -> GanttTask:
    """创建甘特图任务"""
    db_task = GanttTask(
        **task_in.dict(exclude_unset=True),
        created_by=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_gantt_task(db: Session, task_id: int) -> Optional[GanttTask]:
    """获取甘特图任务"""
    return db.query(GanttTask).filter(GanttTask.id == task_id).first()


def get_gantt_tasks_by_project(
    db: Session, 
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    resource_filter: Optional[str] = None
) -> List[GanttTask]:
    """获取项目的甘特图任务列表"""
    query = db.query(GanttTask).filter(GanttTask.project_id == project_id)
    
    # 应用过滤器
    if status_filter:
        # 这里的状态过滤需要根据实际需求实现
        pass
    
    if priority_filter:
        priorities = priority_filter.split(',')
        query = query.filter(GanttTask.priority.in_(priorities))
    
    if resource_filter:
        resources = resource_filter.split(',')
        query = query.filter(GanttTask.resource_id.in_(resources))
    
    # 排序：按行位置和开始时间排序
    query = query.order_by(GanttTask.row.asc(), GanttTask.start_date.asc())
    
    return query.offset(skip).limit(limit).all()


def update_gantt_task(
    db: Session,
    db_task: GanttTask,
    task_in: GanttTaskUpdate
) -> GanttTask:
    """更新甘特图任务"""
    update_data = task_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.utcnow()
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_gantt_task(db: Session, task_id: int) -> bool:
    """删除甘特图任务"""
    db_task = get_gantt_task(db, task_id)
    if not db_task:
        return False
    
    # 删除相关依赖关系
    db.query(GanttDependency).filter(
        or_(
            GanttDependency.predecessor_id == task_id,
            GanttDependency.successor_id == task_id
        )
    ).delete()
    
    # 删除相关基线
    db.query(GanttBaseline).filter(GanttBaseline.task_id == task_id).delete()
    
    # 删除任务
    db.delete(db_task)
    db.commit()
    return True


def move_gantt_task(
    db: Session,
    task_id: int,
    move_data: GanttTaskMove
) -> GanttTask:
    """移动甘特图任务（更新时间和位置）"""
    db_task = get_gantt_task(db, task_id)
    if not db_task:
        raise ValueError(f"任务 {task_id} 不存在")
    
    # 更新任务信息
    db_task.start_date = move_data.new_start_date
    db_task.end_date = move_data.new_end_date
    if move_data.new_row is not None:
        db_task.row = move_data.new_row
    
    db_task.updated_at = datetime.utcnow()
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task


def batch_move_gantt_tasks(
    db: Session,
    batch_update: GanttBatchUpdate
) -> List[GanttTask]:
    """批量移动甘特图任务"""
    updated_tasks = []
    
    for task_move in batch_update.task_updates:
        db_task = get_gantt_task(db, task_move.task_id)
        if db_task:
            db_task.start_date = task_move.new_start_date
            db_task.end_date = task_move.new_end_date
            if task_move.new_row is not None:
                db_task.row = task_move.new_row
            db_task.updated_at = datetime.utcnow()
            updated_tasks.append(db_task)
    
    db.commit()
    
    # 如果启用了依赖关系更新，更新相关依赖任务的时间
    if batch_update.update_dependencies:
        for task in updated_tasks:
            update_dependent_tasks(db, task)
    
    return updated_tasks


def update_dependent_tasks(db: Session, task: GanttTask):
    """更新依赖于该任务的任务时间"""
    # 获取所有以后置任务依赖于当前任务的任务
    dependencies = db.query(GanttDependency).filter(
        GanttDependency.predecessor_id == task.id
    ).all()
    
    for dependency in dependencies:
        successor_task = get_gantt_task(db, dependency.successor_id)
        if successor_task:
            # 根据依赖类型调整后置任务的时间
            if dependency.dependency_type == "FS":  # 完成-开始
                new_start_date = task.end_date + timedelta(days=dependency.lag_days)
                if successor_task.start_date < new_start_date:
                    successor_task.start_date = new_start_date
                    if successor_task.end_date < successor_task.start_date + timedelta(days=successor_task.duration_days):
                        successor_task.end_date = successor_task.start_date + timedelta(days=successor_task.duration_days)
            
            elif dependency.dependency_type == "SS":  # 开始-开始
                new_start_date = task.start_date + timedelta(days=dependency.lag_days)
                if successor_task.start_date < new_start_date:
                    successor_task.start_date = new_start_date
                    
            elif dependency.dependency_type == "FF":  # 完成-完成
                new_end_date = task.end_date + timedelta(days=dependency.lag_days)
                if successor_task.end_date < new_end_date:
                    successor_task.end_date = new_end_date
                    if successor_task.start_date > successor_task.end_date - timedelta(days=successor_task.duration_days):
                        successor_task.start_date = successor_task.end_date - timedelta(days=successor_task.duration_days)
            
            elif dependency.dependency_type == "SF":  # 开始-完成
                new_end_date = task.start_date + timedelta(days=dependency.lag_days)
                if successor_task.end_date < new_end_date:
                    successor_task.end_date = new_end_date
                    if successor_task.start_date > successor_task.end_date - timedelta(days=successor_task.duration_days):
                        successor_task.start_date = successor_task.end_date - timedelta(days=successor_task.duration_days)
            
            successor_task.updated_at = datetime.utcnow()
            db.add(successor_task)
    
    db.commit()


# ==================== GanttDependency CRUD ====================

def create_gantt_dependency(
    db: Session, 
    dependency_in: GanttDependencyCreate,
    user_id: int
) -> GanttDependency:
    """创建甘特图依赖关系"""
    # 检查是否创建了循环依赖
    if has_circular_dependency(db, dependency_in.predecessor_id, dependency_in.successor_id):
        raise ValueError("创建依赖关系会导致循环依赖")
    
    db_dependency = GanttDependency(
        **dependency_in.dict(),
        created_by=user_id
    )
    db.add(db_dependency)
    db.commit()
    db.refresh(db_dependency)
    
    # 更新后置任务的时间
    update_dependent_tasks(db, get_gantt_task(db, dependency_in.predecessor_id))
    
    return db_dependency


def get_gantt_dependency(db: Session, dependency_id: int) -> Optional[GanttDependency]:
    """获取甘特图依赖关系"""
    return db.query(GanttDependency).filter(GanttDependency.id == dependency_id).first()


def get_gantt_dependencies_by_project(
    db: Session,
    project_id: int
) -> List[GanttDependency]:
    """获取项目的甘特图依赖关系列表"""
    return db.query(GanttDependency).join(
        GanttTask, 
        or_(
            GanttDependency.predecessor_id == GanttTask.id,
            GanttDependency.successor_id == GanttTask.id
        )
    ).filter(GanttTask.project_id == project_id).all()


def delete_gantt_dependency(db: Session, dependency_id: int) -> bool:
    """删除甘特图依赖关系"""
    db_dependency = get_gantt_dependency(db, dependency_id)
    if not db_dependency:
        return False
    
    db.delete(db_dependency)
    db.commit()
    return True


def has_circular_dependency(db: Session, start_task_id: int, end_task_id: int) -> bool:
    """检查是否创建了循环依赖"""
    visited = set()
    stack = [start_task_id]
    
    while stack:
        current_task_id = stack.pop()
        
        if current_task_id == end_task_id:
            return True  # 找到循环依赖
        
        if current_task_id in visited:
            continue
        
        visited.add(current_task_id)
        
        # 获取当前任务的所有前置任务
        predecessors = db.query(GanttDependency).filter(
            GanttDependency.successor_id == current_task_id
        ).all()
        
        for dep in predecessors:
            stack.append(dep.predecessor_id)
    
    return False


# ==================== GanttView CRUD ====================

def create_gantt_view(
    db: Session, 
    view_in: GanttViewCreate,
    user_id: int
) -> GanttView:
    """创建甘特图视图"""
    # 如果设置为默认视图，取消其他默认视图
    if view_in.is_default:
        db.query(GanttView).filter(
            and_(
                GanttView.project_id == view_in.project_id,
                GanttView.user_id == user_id,
                GanttView.is_default == 1
            )
        ).update({"is_default": 0})
    
    db_view = GanttView(
        **view_in.dict(exclude_unset=True),
        user_id=user_id
    )
    db.add(db_view)
    db.commit()
    db.refresh(db_view)
    return db_view


def get_gantt_view(db: Session, view_id: int) -> Optional[GanttView]:
    """获取甘特图视图"""
    return db.query(GanttView).filter(GanttView.id == view_id).first()


def get_gantt_views_by_project_and_user(
    db: Session,
    project_id: int,
    user_id: int
) -> List[GanttView]:
    """获取用户对项目的甘特图视图列表"""
    return db.query(GanttView).filter(
        and_(
            GanttView.project_id == project_id,
            GanttView.user_id == user_id
        )
    ).order_by(
        GanttView.is_default.desc(),
        GanttView.updated_at.desc()
    ).all()


def get_default_gantt_view(
    db: Session,
    project_id: int,
    user_id: int
) -> Optional[GanttView]:
    """获取用户的默认甘特图视图"""
    return db.query(GanttView).filter(
        and_(
            GanttView.project_id == project_id,
            GanttView.user_id == user_id,
            GanttView.is_default == 1
        )
    ).first()


def update_gantt_view(
    db: Session,
    db_view: GanttView,
    view_in: GanttViewUpdate
) -> GanttView:
    """更新甘特图视图"""
    # 如果设置为默认视图，取消其他默认视图
    if view_in.is_default and not db_view.is_default:
        db.query(GanttView).filter(
            and_(
                GanttView.project_id == db_view.project_id,
                GanttView.user_id == db_view.user_id,
                GanttView.is_default == 1
            )
        ).update({"is_default": 0})
    
    update_data = view_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_view, field, value)
    
    db_view.updated_at = datetime.utcnow()
    db.add(db_view)
    db.commit()
    db.refresh(db_view)
    return db_view


def delete_gantt_view(db: Session, view_id: int) -> bool:
    """删除甘特图视图"""
    db_view = get_gantt_view(db, view_id)
    if not db_view:
        return False
    
    db.delete(db_view)
    db.commit()
    return True


# ==================== GanttBaseline CRUD ====================

def create_gantt_baseline(
    db: Session, 
    baseline_in: GanttBaselineCreate,
    user_id: int
) -> GanttBaseline:
    """创建甘特图基线"""
    # 计算计划持续时间
    if baseline_in.planned_duration_days is None and baseline_in.planned_start_date and baseline_in.planned_end_date:
        duration_days = (baseline_in.planned_end_date - baseline_in.planned_start_date).days
        baseline_in.planned_duration_days = duration_days
    
    db_baseline = GanttBaseline(
        **baseline_in.dict(exclude_unset=True),
        created_by=user_id
    )
    db.add(db_baseline)
    db.commit()
    db.refresh(db_baseline)
    return db_baseline


def get_gantt_baseline(db: Session, baseline_id: int) -> Optional[GanttBaseline]:
    """获取甘特图基线"""
    return db.query(GanttBaseline).filter(GanttBaseline.id == baseline_id).first()


def get_gantt_baselines_by_project(
    db: Session,
    project_id: int
) -> List[GanttBaseline]:
    """获取项目的甘特图基线列表"""
    return db.query(GanttBaseline).filter(
        GanttBaseline.project_id == project_id
    ).order_by(
        GanttBaseline.baseline_number.asc(),
        GanttBaseline.created_at.desc()
    ).all()


def update_gantt_baseline(
    db: Session,
    db_baseline: GanttBaseline,
    baseline_in: GanttBaselineUpdate
) -> GanttBaseline:
    """更新甘特图基线（主要更新实际值）"""
    update_data = baseline_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_baseline, field, value)
    
    # 如果更新了实际值，重新计算偏差
    if baseline_in.actual_start_date or baseline_in.actual_end_date or baseline_in.actual_progress:
        # 计算持续时间
        if baseline_in.actual_start_date and baseline_in.actual_end_date:
            actual_duration = (db_baseline.actual_end_date - db_baseline.actual_start_date).days
            db_baseline.actual_duration_days = actual_duration
        
        # 计算偏差
        if db_baseline.planned_start_date and db_baseline.actual_start_date:
            db_baseline.start_variance_days = (
                db_baseline.actual_start_date - db_baseline.planned_start_date
            ).days
        
        if db_baseline.planned_end_date and db_baseline.actual_end_date:
            db_baseline.end_variance_days = (
                db_baseline.actual_end_date - db_baseline.planned_end_date
            ).days
        
        if db_baseline.planned_duration_days and db_baseline.actual_duration_days:
            db_baseline.duration_variance_days = (
                db_baseline.actual_duration_days - db_baseline.planned_duration_days
            )
        
        if db_baseline.planned_progress and db_baseline.actual_progress:
            db_baseline.progress_variance = (
                db_baseline.actual_progress - db_baseline.planned_progress
            )
    
    db.add(db_baseline)
    db.commit()
    db.refresh(db_baseline)
    return db_baseline


def delete_gantt_baseline(db: Session, baseline_id: int) -> bool:
    """删除甘特图基线"""
    db_baseline = get_gantt_baseline(db, baseline_id)
    if not db_baseline:
        return False
    
    db.delete(db_baseline)
    db.commit()
    return True