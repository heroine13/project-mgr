"""
甘特图相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.core.database import Base


class GanttTask(Base):
    """甘特图任务模型"""
    __tablename__ = "gantt_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # 关联到现有任务
    
    # 基本信息
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    progress = Column(Float, default=0.0)  # 0.0-1.0
    priority = Column(Integer, default=0)  # 0:普通, 1:重要, 2:紧急
    
    # 显示属性
    color = Column(String(20), default="#4CAF50")
    text_color = Column(String(20), default="#FFFFFF")
    row = Column(Integer, default=0)  # 甘特图行位置
    
    # 资源分配
    resource_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resource_name = Column(String(255))
    allocation = Column(Float, default=1.0)  # 资源分配比例 0.0-1.0
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_milestone = Column(Integer, default=0)  # 0:普通任务, 1:里程碑
    
    # 关系
    project = relationship("Project", backref="gantt_tasks")
    task = relationship("Task", backref="gantt_representation")
    resource = relationship("User", foreign_keys=[resource_id], backref="gantt_assignments")
    creator = relationship("User", foreign_keys=[created_by])
    
    # 依赖关系
    predecessor_links = relationship(
        "GanttDependency",
        foreign_keys="GanttDependency.successor_id",
        backref="successor_task",
        cascade="all, delete-orphan"
    )
    successor_links = relationship(
        "GanttDependency",
        foreign_keys="GanttDependency.predecessor_id",
        backref="predecessor_task",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<GanttTask(id={self.id}, name='{self.name}', project_id={self.project_id})>"
    
    @property
    def duration_days(self):
        """计算任务持续时间（天）"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0


class GanttDependency(Base):
    """甘特图任务依赖关系模型"""
    __tablename__ = "gantt_dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    predecessor_id = Column(Integer, ForeignKey("gantt_tasks.id"), nullable=False)
    successor_id = Column(Integer, ForeignKey("gantt_tasks.id"), nullable=False)
    dependency_type = Column(String(20), default="FS")  # FS(完成-开始), SS(开始-开始), FF(完成-完成), SF(开始-完成)
    lag_days = Column(Integer, default=0)  # 延迟天数
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # 添加唯一约束，防止重复依赖
    __table_args__ = (
        UniqueConstraint('predecessor_id', 'successor_id', name='uq_dependency'),
    )
    
    def __repr__(self):
        return f"<GanttDependency(id={self.id}, predecessor={self.predecessor_id}, successor={self.successor_id}, type='{self.dependency_type}')>"


class GanttView(Base):
    """甘特图视图配置模型"""
    __tablename__ = "gantt_views"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 视图配置
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    time_scale = Column(String(20), default="week")  # day, week, month, quarter, year
    show_resources = Column(Integer, default=1)  # 0:不显示, 1:显示
    show_dependencies = Column(Integer, default=1)  # 0:不显示, 1:显示
    show_progress = Column(Integer, default=1)  # 0:不显示, 1:显示
    show_milestones = Column(Integer, default=1)  # 0:不显示, 1:显示
    show_critical_path = Column(Integer, default=0)  # 0:不显示, 1:显示
    color_scheme = Column(String(50), default="default")
    
    # 时间范围
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # 排序和分组
    sort_by = Column(String(50), default="start_date")
    sort_order = Column(String(10), default="asc")  # asc, desc
    group_by = Column(String(50))  # resource, priority, status
    
    # 过滤条件
    filter_status = Column(String(100))  # 逗号分隔的状态列表
    filter_priority = Column(String(100))  # 逗号分隔的优先级列表
    filter_resource = Column(String(100))  # 逗号分隔的资源ID列表
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_default = Column(Integer, default=0)  # 0:不是默认视图, 1:默认视图
    is_public = Column(Integer, default=0)  # 0:私有, 1:公开
    
    # 关系
    project = relationship("Project", backref="gantt_views")
    user = relationship("User", backref="gantt_view_configs")
    
    def __repr__(self):
        return f"<GanttView(id={self.id}, name='{self.name}', project_id={self.project_id})>"


class GanttBaseline(Base):
    """甘特图基线（计划与实际的对比）"""
    __tablename__ = "gantt_baselines"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("gantt_tasks.id"), nullable=False)
    baseline_number = Column(Integer, default=1)  # 基线编号
    
    # 计划值
    planned_start_date = Column(DateTime, nullable=False)
    planned_end_date = Column(DateTime, nullable=False)
    planned_progress = Column(Float, default=0.0)
    planned_duration_days = Column(Integer)
    
    # 实际值（当任务完成时填写）
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    actual_progress = Column(Float)
    actual_duration_days = Column(Integer)
    
    # 偏差计算
    start_variance_days = Column(Integer)  # 开始时间偏差（天）
    end_variance_days = Column(Integer)    # 结束时间偏差（天）
    duration_variance_days = Column(Integer)  # 持续时间偏差（天）
    progress_variance = Column(Float)      # 进度偏差
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    def __repr__(self):
        return f"<GanttBaseline(id={self.id}, task_id={self.task_id}, baseline_number={self.baseline_number})>"
    
    @property
    def is_completed(self):
        """任务是否已完成"""
        return self.actual_end_date is not None
    
    @property
    def variance_color(self):
        """根据偏差程度返回颜色"""
        if not self.is_completed:
            return "gray"
        
        max_variance = max(
            abs(self.start_variance_days or 0),
            abs(self.end_variance_days or 0),
            abs(self.duration_variance_days or 0)
        )
        
        if max_variance <= 2:
            return "green"
        elif max_variance <= 5:
            return "yellow"
        else:
            return "red"