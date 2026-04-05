"""
甘特图相关数据模式
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class GanttTaskBase(BaseModel):
    """甘特图任务基础模式"""
    project_id: int = Field(..., description="项目ID")
    task_id: Optional[int] = Field(None, description="关联的任务ID")
    name: str = Field(..., max_length=255, description="任务名称")
    description: Optional[str] = Field(None, max_length=1000, description="任务描述")
    start_date: datetime = Field(..., description="开始时间")
    end_date: datetime = Field(..., description="结束时间")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="进度 (0.0-1.0)")
    priority: int = Field(0, description="优先级 (0:普通, 1:重要, 2:紧急)")
    color: Optional[str] = Field("#4CAF50", max_length=20, description="颜色代码")
    text_color: Optional[str] = Field("#FFFFFF", max_length=20, description="文字颜色")
    row: int = Field(0, description="甘特图行位置")
    resource_id: Optional[int] = Field(None, description="资源ID（用户ID）")
    resource_name: Optional[str] = Field(None, max_length=255, description="资源名称")
    allocation: float = Field(1.0, ge=0.0, le=1.0, description="资源分配比例 (0.0-1.0)")
    is_milestone: int = Field(0, description="是否里程碑 (0:普通任务, 1:里程碑)")


class GanttTaskCreate(GanttTaskBase):
    """创建甘特图任务模式"""
    pass


class GanttTaskUpdate(BaseModel):
    """更新甘特图任务模式"""
    name: Optional[str] = Field(None, max_length=255, description="任务名称")
    description: Optional[str] = Field(None, max_length=1000, description="任务描述")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    progress: Optional[float] = Field(None, ge=0.0, le=1.0, description="进度")
    priority: Optional[int] = Field(None, description="优先级")
    color: Optional[str] = Field(None, max_length=20, description="颜色代码")
    text_color: Optional[str] = Field(None, max_length=20, description="文字颜色")
    row: Optional[int] = Field(None, description="行位置")
    resource_id: Optional[int] = Field(None, description="资源ID")
    resource_name: Optional[str] = Field(None, max_length=255, description="资源名称")
    allocation: Optional[float] = Field(None, ge=0.0, le=1.0, description="资源分配比例")
    is_milestone: Optional[int] = Field(None, description="是否里程碑")


class GanttTaskResponse(GanttTaskBase):
    """甘特图任务响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    duration_days: Optional[int] = Field(None, description="持续时间（天）")
    
    class Config:
        from_attributes = True


class GanttDependencyBase(BaseModel):
    """甘特图依赖关系基础模式"""
    predecessor_id: int = Field(..., description="前置任务ID")
    successor_id: int = Field(..., description="后置任务ID")
    dependency_type: str = Field("FS", description="依赖类型 (FS, SS, FF, SF)")
    lag_days: int = Field(0, description="延迟天数")


class GanttDependencyCreate(GanttDependencyBase):
    """创建甘特图依赖关系模式"""
    pass


class GanttDependencyResponse(GanttDependencyBase):
    """甘特图依赖关系响应模式"""
    id: int
    created_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class GanttViewBase(BaseModel):
    """甘特图视图基础模式"""
    project_id: int = Field(..., description="项目ID")
    name: str = Field(..., max_length=255, description="视图名称")
    description: Optional[str] = Field(None, max_length=500, description="视图描述")
    time_scale: str = Field("week", description="时间尺度 (day, week, month, quarter, year)")
    show_resources: int = Field(1, description="是否显示资源")
    show_dependencies: int = Field(1, description="是否显示依赖关系")
    show_progress: int = Field(1, description="是否显示进度")
    show_milestones: int = Field(1, description="是否显示里程碑")
    show_critical_path: int = Field(0, description="是否显示关键路径")
    color_scheme: str = Field("default", description="颜色方案")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    sort_by: Optional[str] = Field("start_date", description="排序字段")
    sort_order: Optional[str] = Field("asc", description="排序顺序 (asc, desc)")
    group_by: Optional[str] = Field(None, description="分组字段")
    filter_status: Optional[str] = Field(None, description="状态过滤")
    filter_priority: Optional[str] = Field(None, description="优先级过滤")
    filter_resource: Optional[str] = Field(None, description="资源过滤")
    is_default: int = Field(0, description="是否默认视图")
    is_public: int = Field(0, description="是否公开")


class GanttViewCreate(GanttViewBase):
    """创建甘特图视图模式"""
    pass


class GanttViewUpdate(BaseModel):
    """更新甘特图视图模式"""
    name: Optional[str] = Field(None, max_length=255, description="视图名称")
    description: Optional[str] = Field(None, max_length=500, description="视图描述")
    time_scale: Optional[str] = Field(None, description="时间尺度")
    show_resources: Optional[int] = Field(None, description="是否显示资源")
    show_dependencies: Optional[int] = Field(None, description="是否显示依赖关系")
    show_progress: Optional[int] = Field(None, description="是否显示进度")
    show_milestones: Optional[int] = Field(None, description="是否显示里程碑")
    show_critical_path: Optional[int] = Field(None, description="是否显示关键路径")
    color_scheme: Optional[str] = Field(None, description="颜色方案")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: Optional[str] = Field(None, description="排序顺序")
    group_by: Optional[str] = Field(None, description="分组字段")
    filter_status: Optional[str] = Field(None, description="状态过滤")
    filter_priority: Optional[str] = Field(None, description="优先级过滤")
    filter_resource: Optional[str] = Field(None, description="资源过滤")
    is_default: Optional[int] = Field(None, description="是否默认视图")
    is_public: Optional[int] = Field(None, description="是否公开")


class GanttViewResponse(GanttViewBase):
    """甘特图视图响应模式"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GanttBaselineBase(BaseModel):
    """甘特图基线基础模式"""
    project_id: int = Field(..., description="项目ID")
    task_id: int = Field(..., description="任务ID")
    baseline_number: int = Field(1, description="基线编号")
    planned_start_date: datetime = Field(..., description="计划开始时间")
    planned_end_date: datetime = Field(..., description="计划结束时间")
    planned_progress: float = Field(0.0, ge=0.0, le=1.0, description="计划进度")
    planned_duration_days: Optional[int] = Field(None, description="计划持续时间")


class GanttBaselineCreate(GanttBaselineBase):
    """创建甘特图基线模式"""
    pass


class GanttBaselineUpdate(BaseModel):
    """更新甘特图基线模式"""
    actual_start_date: Optional[datetime] = Field(None, description="实际开始时间")
    actual_end_date: Optional[datetime] = Field(None, description="实际结束时间")
    actual_progress: Optional[float] = Field(None, ge=0.0, le=1.0, description="实际进度")
    actual_duration_days: Optional[int] = Field(None, description="实际持续时间")
    start_variance_days: Optional[int] = Field(None, description="开始时间偏差")
    end_variance_days: Optional[int] = Field(None, description="结束时间偏差")
    duration_variance_days: Optional[int] = Field(None, description="持续时间偏差")
    progress_variance: Optional[float] = Field(None, description="进度偏差")


class GanttBaselineResponse(GanttBaselineBase):
    """甘特图基线响应模式"""
    id: int
    actual_start_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    actual_progress: Optional[float]
    actual_duration_days: Optional[int]
    start_variance_days: Optional[int]
    end_variance_days: Optional[int]
    duration_variance_days: Optional[int]
    progress_variance: Optional[float]
    created_at: datetime
    created_by: Optional[int]
    is_completed: bool
    variance_color: str
    
    class Config:
        from_attributes = True


class GanttProjectData(BaseModel):
    """项目甘特图完整数据结构"""
    tasks: List[GanttTaskResponse]
    dependencies: List[GanttDependencyResponse]
    views: List[GanttViewResponse]
    baselines: List[GanttBaselineResponse]
    resources: List[dict]  # 简化资源信息


class GanttTaskMove(BaseModel):
    """甘特图任务移动模式"""
    task_id: int = Field(..., description="任务ID")
    new_start_date: datetime = Field(..., description="新的开始时间")
    new_end_date: datetime = Field(..., description="新的结束时间")
    new_row: Optional[int] = Field(None, description="新的行位置")


class GanttBatchUpdate(BaseModel):
    """甘特图批量更新模式"""
    task_updates: List[GanttTaskMove] = Field(..., description="任务更新列表")
    update_dependencies: bool = Field(True, description="是否更新依赖关系")