# Day 4上午开发进度报告 (2026-04-06)

## ✅ 当前状态
- **时间**: 开始实施Day 4上午计划
- **开发阶段**: 高级功能开发 (Day 4)
- **上午目标**: 甘特图和时间线功能开发

## 🎯 今日开发计划执行

### 第一阶段：甘特图组件集成 (09:00-11:30)

#### **1. 甘特图库选择和技术评估**
经过技术评估，决定使用以下方案：

**方案选择**：
- **ECharts甘特图扩展**: 基于已有的ECharts库扩展甘特图功能
- **优势**: 
  - 无需额外库依赖
  - 与现有技术栈(ECharts)保持一致
  - 开源且高度可定制
  - 中文文档和社区支持完善

**技术规格**：
- 使用ECharts自定义系列扩展实现甘特图
- 支持时间轴、任务条、依赖关系
- 支持拖拽交互
- 响应式设计，支持移动端

#### **2. 甘特图数据模型设计**
**后端API扩展**：
```python
# 新增甘特图相关API端点
POST   /api/v1/gantt/tasks          # 创建甘特图任务
GET    /api/v1/gantt/tasks          # 获取甘特图任务列表
GET    /api/v1/gantt/tasks/{id}     # 获取单个甘特图任务
PUT    /api/v1/gantt/tasks/{id}     # 更新甘特图任务
DELETE /api/v1/gantt/tasks/{id}     # 删除甘特图任务
POST   /api/v1/gantt/dependencies   # 创建任务依赖关系
GET    /api/v1/gantt/dependencies   # 获取依赖关系列表
```

**数据模型扩展**：
- **GanttTask**: 甘特图任务，包含开始时间、结束时间、进度等
- **GanttDependency**: 任务依赖关系，前置任务、后置任务
- **GanttResource**: 资源分配，人员、设备等

#### **3. 前端甘特图组件架构设计**
**组件结构**：
```
frontend/src/components/gantt/
├── GanttChart.vue          # 主甘特图组件
├── GanttTaskBar.vue        # 单个任务条组件
├── GanttDependency.vue     # 依赖关系线组件
├── GanttToolbar.vue        # 甘特图工具栏
├── GanttConfigPanel.vue    # 配置面板
└── index.ts               # 组件导出
```

**技术实现要点**：
1. ECharts自定义系列实现
2. Canvas渲染优化
3. 拖拽交互事件处理
4. 时间轴缩放和导航
5. 依赖关系可视化

## 🚀 立即开始实施

### **步骤1：扩展后端数据模型**
首先需要扩展后端的甘特图相关数据模型：

```python
# backend/app/models/gantt.py
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class GanttTask(Base):
    __tablename__ = "gantt_tasks"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    progress = Column(Float, default=0.0)  # 0.0-1.0
    priority = Column(Integer, default=0)
    color = Column(String(20), default="#4CAF50")
    
    # 关系
    project = relationship("Project", backref="gantt_tasks")
    dependencies = relationship("GanttDependency", 
                               foreign_keys="GanttDependency.predecessor_id",
                               backref="predecessor")
    dependents = relationship("GanttDependency", 
                              foreign_keys="GanttDependency.successor_id",
                              backref="successor")

class GanttDependency(Base):
    __tablename__ = "gantt_dependencies"
    
    id = Column(Integer, primary_key=True)
    predecessor_id = Column(Integer, ForeignKey("gantt_tasks.id"), nullable=False)
    successor_id = Column(Integer, ForeignKey("gantt_tasks.id"), nullable=False)
    type = Column(String(20), default="FS")  # FS(完成-开始), SS(开始-开始), FF(完成-完成), SF(开始-完成)
    
    # 添加唯一约束
    __table_args__ = (
        UniqueConstraint('predecessor_id', 'successor_id', name='uq_dependency'),
    )

class GanttResource(Base):
    __tablename__ = "gantt_resources"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("gantt_tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_name = Column(String(255))
    allocation = Column(Float, default=1.0)  # 资源分配比例 0.0-1.0
    
    task = relationship("GanttTask", backref="resources")
    user = relationship("User", backref="gantt_assignments")
```

### **步骤2：创建甘特图API端点**
创建甘特图相关的CRUD API端点：

```python
# backend/app/api/v1/endpoints/gantt.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.models.gantt import GanttTask, GanttDependency, GanttResource
from app.schemas.gantt import GanttTaskCreate, GanttTaskUpdate, GanttTaskResponse
from app.crud import crud_gantt

router = APIRouter()

@router.post("/tasks", response_model=GanttTaskResponse)
def create_gantt_task(
    task_in: GanttTaskCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """创建甘特图任务"""
    # 检查项目权限
    project = db.query(models.Project).filter(models.Project.id == task_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 检查用户是否有项目访问权限
    if not project.is_accessible_by(current_user.id, db):
        raise HTTPException(status_code=403, detail="No permission to access this project")
    
    # 创建任务
    task = crud_gantt.create_task(db=db, task_in=task_in)
    return task

@router.get("/tasks", response_model=List[GanttTaskResponse])
def get_gantt_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """获取项目的甘特图任务列表"""
    # 检查项目权限
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.is_accessible_by(current_user.id, db):
        raise HTTPException(status_code=403, detail="No permission to access this project")
    
    tasks = crud_gantt.get_tasks_by_project(db, project_id=project_id, skip=skip, limit=limit)
    return tasks

# 更多API端点...
```

### **步骤3：创建前端甘特图组件**
开始创建Vue 3甘特图组件：

```vue
<!-- frontend/src/components/gantt/GanttChart.vue -->
<template>
  <div class="gantt-chart">
    <div class="gantt-header">
      <GanttToolbar 
        :scale="timeScale"
        @scale-change="handleScaleChange"
        @today="jumpToToday"
        @fit="fitToView"
      />
    </div>
    
    <div class="gantt-content">
      <!-- 左侧任务列表 -->
      <div class="gantt-task-list">
        <GanttTaskList 
          :tasks="tasks"
          @task-click="handleTaskClick"
          @task-drag-start="handleTaskDragStart"
        />
      </div>
      
      <!-- 右侧时间轴区域 -->
      <div class="gantt-timeline">
        <div class="gantt-time-header">
          <div 
            v-for="timeUnit in timeUnits"
            :key="timeUnit.label"
            class="time-header-cell"
          >
            {{ timeUnit.label }}
          </div>
        </div>
        
        <div class="gantt-chart-area">
          <!-- ECharts甘特图渲染区域 -->
          <div ref="chartRef" class="gantt-chart-canvas"></div>
          
          <!-- 任务条拖拽交互层 -->
          <div 
            v-if="draggingTask"
            class="gantt-drag-layer"
            @mousemove="handleDragMove"
            @mouseup="handleDragEnd"
          >
            <GanttTaskBar 
              :task="draggingTask"
              :style="dragStyle"
              class="dragging"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 任务详情配置面板 -->
    <GanttConfigPanel 
      v-if="selectedTask"
      :task="selectedTask"
      @update="handleTaskUpdate"
      @close="selectedTask = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useChart } from './useChart'
import { useGanttStore } from '@/stores/gantt'
import GanttToolbar from './GanttToolbar.vue'
import GanttTaskList from './GanttTaskList.vue'
import GanttTaskBar from './GanttTaskBar.vue'
import GanttConfigPanel from './GanttConfigPanel.vue'

// 状态管理
const ganttStore = useGanttStore()
const chartRef = ref<HTMLElement>()
const selectedTask = ref<any>(null)
const draggingTask = ref<any>(null)
const dragStartX = ref(0)
const dragStartY = ref(0)

// 计算属性
const tasks = computed(() => ganttStore.tasks)
const timeScale = computed(() => ganttStore.timeScale)
const timeUnits = computed(() => ganttStore.timeUnits)

// 拖拽样式
const dragStyle = computed(() => ({
  transform: `translate(${dragStartX.value}px, ${dragStartY.value}px)`
}))

// 图表初始化
const { initChart, updateChart, setTimeScale } = useChart()

onMounted(() => {
  initChart(chartRef.value!)
  
  // 加载甘特图数据
  loadGanttData()
})

onUnmounted(() => {
  // 清理图表实例
})

// 事件处理
const handleScaleChange = (scale: string) => {
  setTimeScale(scale)
  ganttStore.setTimeScale(scale)
}

const handleTaskClick = (task: any) => {
  selectedTask.value = task
}

const handleTaskDragStart = (task: any, event: MouseEvent) => {
  draggingTask.value = task
  dragStartX.value = event.clientX
  dragStartY.value = event.clientY
}

const handleDragMove = (event: MouseEvent) => {
  if (!draggingTask.value) return
  
  dragStartX.value = event.clientX
  dragStartY.value = event.clientY
}

const handleDragEnd = () => {
  if (draggingTask.value) {
    // 更新任务位置到后端
    updateTaskPosition(draggingTask.value, dragStartX.value, dragStartY.value)
    draggingTask.value = null
  }
}

// API调用
const loadGanttData = async () => {
  try {
    await ganttStore.fetchGanttTasks()
    updateChart(ganttStore.tasks)
  } catch (error) {
    console.error('Failed to load gantt data:', error)
  }
}

const updateTaskPosition = async (task: any, x: number, y: number) => {
  try {
    // 将像素位置转换为时间
    const newStartDate = ganttStore.pixelToDate(x)
    const newEndDate = ganttStore.pixelToDate(x + task.durationInPixels)
    
    await ganttStore.updateTask({
      id: task.id,
      start_date: newStartDate,
      end_date: newEndDate
    })
    
    updateChart(ganttStore.tasks)
  } catch (error) {
    console.error('Failed to update task position:', error)
  }
}

const handleTaskUpdate = async (updatedTask: any) => {
  try {
    await ganttStore.updateTask(updatedTask)
    updateChart(ganttStore.tasks)
    selectedTask.value = null
  } catch (error) {
    console.error('Failed to update task:', error)
  }
}
</script>

<style scoped>
.gantt-chart {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.gantt-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
}

.gantt-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.gantt-task-list {
  width: 300px;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
}

.gantt-timeline {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.gantt-time-header {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f5f5f5;
}

.time-header-cell {
  padding: 8px 12px;
  border-right: 1px solid #e0e0e0;
  text-align: center;
  min-width: 80px;
}

.gantt-chart-area {
  flex: 1;
  position: relative;
  overflow: auto;
}

.gantt-chart-canvas {
  width: 100%;
  height: 100%;
}

.gantt-drag-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1000;
}

.dragging {
  opacity: 0.7;
  pointer-events: none;
}
</style>
```

## 📊 甘特图功能规格

### **核心功能**
1. **时间轴显示**: 支持天、周、月、季度、年不同时间尺度
2. **任务条**: 显示任务名称、时间范围、进度百分比
3. **拖拽调整**: 拖拽任务条调整开始/结束时间
4. **依赖关系**: 任务间的依赖关系连线显示
5. **资源分配**: 显示任务分配的人员或资源
6. **里程碑**: 特殊标记的重要时间点

### **交互功能**
1. **缩放**: 鼠标滚轮缩放时间轴
2. **平移**: 拖动时间轴进行平移
3. **任务选择**: 点击任务条选中任务
4. **右键菜单**: 任务条右键操作菜单
5. **快捷键**: 支持常用操作的键盘快捷键

### **数据可视化**
1. **进度显示**: 通过颜色和填充表示任务进度
2. **状态标记**: 不同状态的任务使用不同颜色
3. **关键路径**: 高亮显示项目的关键路径
4. **基线对比**: 显示计划与实际的对比
5. **资源负荷**: 显示资源的负荷情况

## 🔄 下一步计划

### **上午剩余时间安排**
1. **10:30-11:30**: 完成甘特图数据模型的API端点实现
2. **11:30-12:00**: 创建前端甘特图Store状态管理
3. **12:00-12:30**: 集成测试甘特图基础功能

### **上午提交计划**
预计在12:30前完成以下内容：
1. 后端甘特图数据模型完整实现
2. 甘特图API端点全部完成
3. 前端甘特图基础组件结构
4. 上午代码提交到GitHub

## 📈 风险评估

### **技术风险**
1. **ECharts甘特图性能**: 任务数量较多时的渲染性能
2. **拖拽交互复杂性**: 时间计算的准确性
3. **依赖关系可视化**: 复杂的依赖关系可能难以清晰显示

### **应对措施**
1. **性能优化**: 使用虚拟滚动、任务分组、懒加载
2. **交互简化**: 提供简单模式和高级模式切换
3. **可视化优化**: 使用颜色编码、动画效果提升可读性

## ✅ 质量保证
- **单元测试**: 编写甘特图相关组件的单元测试
- **集成测试**: 测试API端点和前端组件的集成
- **用户测试**: 甘特图交互的易用性测试
- **性能测试**: 大数据量下的渲染和交互性能测试

**严格按照"按顺序实施"的要求，立即开始甘特图组件的代码实现！**