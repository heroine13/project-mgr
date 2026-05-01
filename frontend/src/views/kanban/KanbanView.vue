<template>
  <div class="kanban-view">
    <!-- 头部 -->
    <div class="kanban-header">
      <h2>📋 看板视图</h2>
      <div class="header-actions">
        <el-select v-model="selectedProject" placeholder="选择项目" clearable @change="fetchTasks">
          <el-option label="全部项目" :value="null" />
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-button type="primary" @click="fetchTasks">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 统计栏 -->
    <div class="kanban-stats" v-if="stats">
      <div 
        v-for="col in columns" 
        :key="col.id" 
        class="stat-item"
        :style="{ borderLeftColor: col.color }"
      >
        <span class="stat-title">{{ col.title }}</span>
        <span class="stat-count" :style="{ backgroundColor: col.color }">
          {{ stats[col.status]?.count || 0 }}
        </span>
      </div>
    </div>

    <!-- 看板列 -->
    <div class="kanban-board" v-loading="loading">
      <div 
        v-for="column in columns" 
        :key="column.id" 
        class="kanban-column"
        @dragover.prevent
        @drop="handleDrop($event, column.status)"
      >
        <div class="column-header" :style="{ backgroundColor: column.color }">
          <span class="column-title">{{ column.title }}</span>
          <span class="column-count">{{ getColumnTasks(column.status).length }}</span>
        </div>
        
        <div class="column-content">
          <div 
            v-for="task in getColumnTasks(column.status)" 
            :key="task.id"
            class="task-card"
            draggable="true"
            @dragstart="handleDragStart($event, task)"
            @click="viewTaskDetail(task)"
          >
            <div class="task-header">
              <el-tag size="small" :type="getPriorityType(task.priority)">
                {{ getPriorityText(task.priority) }}
              </el-tag>
              <span class="task-id">#{{ task.id }}</span>
            </div>
            <h4 class="task-title">{{ task.title }}</h4>
            <p class="task-desc" v-if="task.description">
              {{ truncate(task.description, 60) }}
            </p>
            <div class="task-footer">
              <el-avatar v-if="task.assignee_id" :size="24" class="task-assignee">
                {{ task.assignee_id }}
              </el-avatar>
              <span class="task-due" v-if="task.due_date" :class="{ overdue: isOverdue(task.due_date) }">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(task.due_date) }}
              </span>
            </div>
          </div>
          
          <div v-if="getColumnTasks(column.status).length === 0" class="column-empty">
            暂无任务
          </div>
        </div>
      </div>
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog v-model="showTaskDetail" :title="`任务 #${selectedTask?.id}`" width="600px">
      <div v-if="selectedTask" class="task-detail">
        <h3>{{ selectedTask.title }}</h3>
        <p><strong>状态：</strong>{{ getStatusText(selectedTask.status) }}</p>
        <p><strong>优先级：</strong>{{ getPriorityText(selectedTask.priority) }}</p>
        <p><strong>描述：</strong>{{ selectedTask.description || '无' }}</p>
        <p><strong>截止日期：</strong>{{ selectedTask.due_date ? formatDate(selectedTask.due_date) : '未设置' }}</p>
      </div>
      <template #footer>
        <el-button @click="showTaskDetail = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Calendar } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = '/api/v1'

const loading = ref(false)
const tasks = ref({})
const columns = ref([])
const projects = ref([])
const selectedProject = ref(null)
const stats = ref(null)
const showTaskDetail = ref(false)
const selectedTask = ref(null)
const draggedTask = ref(null)

const getColumnTasks = (status) => {
  return tasks.value[status] || []
}

const fetchColumns = async () => {
  try {
    const response = await axios.get(`${API_BASE}/kanban/columns`)
    columns.value = response.data
  } catch (error) {
    console.error('获取列配置失败', error)
    columns.value = [
      { id: 'pending', title: '待处理', status: 'pending', color: '#909399' },
      { id: 'in_progress', title: '进行中', status: 'in_progress', color: '#E6A23C' },
      { id: 'review', title: '审核中', status: 'review', color: '#409EFF' },
      { id: 'completed', title: '已完成', status: 'completed', color: '#67C23A' },
      { id: 'blocked', title: '已阻塞', status: 'blocked', color: '#F56C6C' },
    ]
  }
}

const fetchTasks = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    const response = await axios.get(`${API_BASE}/kanban/tasks`, { params })
    tasks.value = response.data.tasks
    
    // Also fetch stats
    const statsResponse = await axios.get(`${API_BASE}/kanban/stats`, { params })
    stats.value = statsResponse.data
  } catch (error) {
    console.warn('获取任务失败', error)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await axios.get(`${API_BASE}/projects/`)
    projects.value = response.data
  } catch (error) {
    console.warn('获取项目失败', error)
    projects.value = []
  }
}

const handleDragStart = (event, task) => {
  draggedTask.value = task
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', task.id.toString())
}

const handleDrop = async (event, targetStatus) => {
  event.preventDefault()
  
  if (!draggedTask.value) return
  
  const taskId = draggedTask.value.id
  const oldStatus = draggedTask.value.status
  
  // Optimistic update
  if (oldStatus !== targetStatus) {
    // Remove from old column
    if (tasks.value[oldStatus]) {
      tasks.value[oldStatus] = tasks.value[oldStatus].filter(t => t.id !== taskId)
    }
    // Add to new column
    if (!tasks.value[targetStatus]) {
      tasks.value[targetStatus] = []
    }
    draggedTask.value.status = targetStatus
    tasks.value[targetStatus].push(draggedTask.value)
  }
  
  // API call to update status
  try {
    await axios.put(`${API_BASE}/kanban/tasks/${taskId}/move`, {
      status: targetStatus
    })
    ElMessage.success(`已移动到 ${getStatusText(targetStatus)}`)
  } catch (error) {
    // Revert on error
    fetchTasks()
    ElMessage.error('移动失败')
  }
  
  draggedTask.value = null
}

const viewTaskDetail = (task) => {
  selectedTask.value = task
  showTaskDetail.value = true
}

const getPriorityType = (priority) => {
  const map = { urgent: 'danger', high: 'warning', medium: 'primary', low: 'info' }
  return map[priority] || 'info'
}

const getPriorityText = (priority) => {
  const map = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    in_progress: '进行中',
    review: '审核中',
    completed: '已完成',
    blocked: '已阻塞'
  }
  return map[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const isOverdue = (dateStr) => {
  return new Date(dateStr) < new Date()
}

const truncate = (str, len) => {
  if (!str) return ''
  return str.length > len ? str.substring(0, len) + '...' : str
}

onMounted(() => {
  fetchColumns()
  fetchProjects()
  fetchTasks()
})
</script>

<style scoped>
.kanban-view {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.kanban-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.kanban-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.kanban-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: white;
  border-radius: 6px;
  border-left: 4px solid;
}

.stat-title {
  font-weight: 500;
}

.stat-count {
  padding: 2px 10px;
  border-radius: 12px;
  color: white;
  font-weight: bold;
}

.kanban-board {
  display: flex;
  gap: 15px;
  flex: 1;
  overflow-x: auto;
  padding-bottom: 10px;
}

.kanban-column {
  min-width: 280px;
  max-width: 280px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.column-header {
  padding: 15px;
  border-radius: 8px 8px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.column-title {
  font-weight: bold;
}

.column-count {
  background: rgba(255,255,255,0.3);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.column-content {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  min-height: 200px;
}

.column-empty {
  text-align: center;
  color: #909399;
  padding: 30px 0;
}

.task-card {
  background: white;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s;
}

.task-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.task-card:active {
  cursor: grabbing;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-id {
  font-size: 12px;
  color: #909399;
}

.task-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
}

.task-desc {
  margin: 0 0 10px 0;
  font-size: 12px;
  color: #606266;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.task-due {
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-due.overdue {
  color: #F56C6C;
}

.task-detail h3 {
  margin-top: 0;
}

.task-detail p {
  margin: 10px 0;
}
</style>