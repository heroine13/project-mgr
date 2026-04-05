<template>
  <div class="gantt-task-list">
    <div class="list-header">
      <div class="header-title">
        <h3>任务列表</h3>
        <span class="task-count">{{ filteredTasks.length }} 个任务</span>
      </div>
      <div class="header-actions">
        <el-button
          size="small"
          icon="el-icon-plus"
          type="primary"
          @click="handleAddTask"
        >
          添加
        </el-button>
        <el-button
          size="small"
          icon="el-icon-sort"
          @click="toggleSortOrder"
        >
          {{ sortAscending ? '升序' : '降序' }}
        </el-button>
      </div>
    </div>
    
    <div class="list-filters">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索任务..."
        size="small"
        clearable
        prefix-icon="el-icon-search"
      />
      
      <div class="filter-controls">
        <el-select
          v-model="filterPriority"
          placeholder="优先级"
          size="small"
          clearable
        >
          <el-option label="普通" value="0" />
          <el-option label="重要" value="1" />
          <el-option label="紧急" value="2" />
        </el-select>
        
        <el-select
          v-model="filterResource"
          placeholder="资源"
          size="small"
          clearable
        >
          <el-option
            v-for="resource in resources"
            :key="resource.id"
            :label="resource.name"
            :value="resource.id"
          />
        </el-select>
      </div>
    </div>
    
    <div class="list-content">
      <el-scrollbar>
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="task-item"
          :class="{ 
            'task-selected': task.id === selectedTaskId,
            'task-milestone': task.is_milestone,
            [`priority-${task.priority}`]: true 
          }"
          @click="handleTaskClick(task)"
          @contextmenu.prevent="handleTaskContextMenu(task, $event)"
        >
          <div class="task-info">
            <div class="task-name">
              <el-tag
                v-if="task.is_milestone"
                size="small"
                type="warning"
                class="milestone-tag"
              >
                里程碑
              </el-tag>
              <span class="name-text">{{ task.name }}</span>
            </div>
            <div class="task-meta">
              <span class="task-duration">
                {{ formatDuration(task) }}
              </span>
              <span class="task-progress">
                {{ (task.progress * 100).toFixed(0) }}%
              </span>
            </div>
          </div>
          
          <div class="task-resource" v-if="task.resource_name">
            <el-avatar size="small" :style="{ backgroundColor: getResourceColor(task.resource_id) }">
              {{ task.resource_name.charAt(0) }}
            </el-avatar>
            <span class="resource-name">{{ task.resource_name }}</span>
          </div>
          
          <div class="task-actions">
            <el-button
              size="small"
              icon="el-icon-edit"
              circle
              @click.stop="handleEditTask(task)"
            />
            <el-button
              size="small"
              icon="el-icon-delete"
              circle
              @click.stop="handleDeleteTask(task)"
            />
          </div>
        </div>
        
        <div v-if="filteredTasks.length === 0" class="empty-state">
          <el-empty description="暂无任务" />
          <el-button type="primary" @click="handleAddTask">
            创建第一个任务
          </el-button>
        </div>
      </el-scrollbar>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { GanttTask } from '@/types/gantt'

interface Resource {
  id: number
  name: string
}

interface Props {
  tasks: GanttTask[]
  selectedTaskId?: number | null
}

interface Emits {
  (e: 'task-click', task: GanttTask): void
  (e: 'task-context-menu', task: GanttTask, event: MouseEvent): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 搜索和过滤
const searchKeyword = ref('')
const filterPriority = ref<string>('')
const filterResource = ref<string>('')
const sortAscending = ref(true)

// 资源列表（简化，实际应该从API获取）
const resources = ref<Resource[]>([
  { id: 1, name: '张工' },
  { id: 2, name: '李工' },
  { id: 3, name: '王经理' },
  { id: 4, name: '赵总监' }
])

// 计算属性
const filteredTasks = computed(() => {
  let filtered = [...props.tasks]
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(task => 
      task.name.toLowerCase().includes(keyword) ||
      (task.description && task.description.toLowerCase().includes(keyword))
    )
  }
  
  // 优先级过滤
  if (filterPriority.value !== '') {
    filtered = filtered.filter(task => task.priority.toString() === filterPriority.value)
  }
  
  // 资源过滤
  if (filterResource.value !== '') {
    filtered = filtered.filter(task => task.resource_id?.toString() === filterResource.value)
  }
  
  // 排序
  filtered.sort((a, b) => {
    const comparison = new Date(a.start_date).getTime() - new Date(b.start_date).getTime()
    return sortAscending.value ? comparison : -comparison
  })
  
  return filtered
})

// 事件处理
const handleTaskClick = (task: GanttTask) => {
  emit('task-click', task)
}

const handleTaskContextMenu = (task: GanttTask, event: MouseEvent) => {
  emit('task-context-menu', task, event)
}

const handleAddTask = () => {
  // TODO: 实现添加任务对话框
  console.log('添加任务')
}

const handleEditTask = (task: GanttTask) => {
  // 点击编辑时也选中任务
  emit('task-click', task)
}

const handleDeleteTask = async (task: GanttTask) => {
  const confirmed = confirm(`确定要删除任务 "${task.name}" 吗？`)
  if (confirmed) {
    // TODO: 调用API删除任务
    console.log('删除任务:', task.id)
  }
}

const toggleSortOrder = () => {
  sortAscending.value = !sortAscending.value
}

// 辅助函数
const formatDuration = (task: GanttTask): string => {
  const startDate = new Date(task.start_date)
  const endDate = new Date(task.end_date)
  
  const durationMs = endDate.getTime() - startDate.getTime()
  const days = Math.ceil(durationMs / (1000 * 60 * 60 * 24))
  
  if (days === 1) {
    return '1天'
  } else if (days < 30) {
    return `${days}天`
  } else if (days < 365) {
    const months = Math.floor(days / 30)
    return `${months}个月`
  } else {
    const years = Math.floor(days / 365)
    return `${years}年`
  }
}

const getResourceColor = (resourceId?: number): string => {
  if (!resourceId) return '#9E9E9E'
  
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
  const index = resourceId % colors.length
  return colors[index]
}
</script>

<style scoped>
.gantt-task-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #ffffff;
}

.list-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fafafa;
}

.header-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.task-count {
  font-size: 12px;
  color: #666;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.list-filters {
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-controls {
  display: flex;
  gap: 8px;
}

.list-content {
  flex: 1;
  overflow: hidden;
  padding: 8px 0;
}

.task-item {
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-item:hover {
  background-color: #f5f5f5;
}

.task-selected {
  background-color: #e3f2fd !important;
  border-left: 4px solid #2196f3;
}

.task-milestone {
  border-left: 4px solid #ff9800;
}

.task-item.priority-1 {
  border-left-color: #ff9800;
}

.task-item.priority-2 {
  border-left-color: #f44336;
}

.task-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.milestone-tag {
  height: 20px;
  line-height: 18px;
}

.name-text {
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #666;
}

.task-resource {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 100px;
}

.resource-name {
  font-size: 12px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.task-item:hover .task-actions {
  opacity: 1;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
</style>