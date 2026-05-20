<template>
  <div class="project-detail">
    <!-- Loading -->
    <el-skeleton v-if="loading" :rows="10" animated />

    <!-- Project Header -->
    <div class="project-header">
      <div class="header-left">
        <h1 class="project-title">{{ project.name }}</h1>
        <div class="project-meta">
          <el-tag :type="getStatusType(project.status)" size="small">
            {{ $t(`status.${project.status}`) }}
          </el-tag>
          <span class="project-code">{{ project.code }}</span>
          <span class="project-dates">
            {{ formatDate(project.start_date) }} - {{ formatDate(project.end_date) }}
          </span>
        </div>
      </div>

      <div class="header-right">
        <el-button-group>
          <el-button type="primary" @click="editProject">
            <el-icon><Edit /></el-icon>
            {{ $t('common.edit') }}
          </el-button>
          <el-button @click="exportProject">
            <el-icon><Download /></el-icon>
            {{ $t('common.export') }}
          </el-button>
          <el-dropdown @command="handleProjectCommand">
            <el-button>
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="archive">{{ $t('status.archived') }}</el-dropdown-item>
                <el-dropdown-item command="delete" divided>{{ $t('common.delete') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-button-group>
      </div>
    </div>

    <!-- Main Content -->
    <el-tabs v-model="activeTab" class="project-tabs">
      <!-- 甘特图标签页（新增） -->
      <el-tab-pane :label="$t('gantt')" name="gantt">
        <el-card v-loading="ganttLoading" class="gantt-card">
          <div class="gantt-container" style="height: 600px;">
            <GanttChart v-if="ganttStore.tasks.length > 0" />
            <el-empty v-else description="暂无甘特图数据，请先添加任务" />
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 描述标签页（原有） -->
      <el-tab-pane :label="$t('project.description')" name="description">
        <el-row :gutter="20">
        <!-- Left Column -->
        <el-col :xs="24" :md="16">
          <!-- Project Description -->
          <el-card class="section-card">
            <template #header>
              <h3>{{ $t('project.description') }}</h3>
            </template>
            <div class="description-content">
              <p>{{ project.description || $t('common.noDescription') }}</p>
            </div>
          </el-card>

          <!-- Project Tasks -->
          <el-card class="section-card">
            <template #header>
              <div class="section-header">
                <h3>{{ $t('navigation.tasks') }}</h3>
                <el-button type="primary" size="small" @click="createTask">
                  <el-icon><Plus /></el-icon>
                  {{ $t('dashboard.createTask') }}
                </el-button>
              </div>
            </template>

            <div class="tasks-section">
              <!-- Task Filters -->
              <div class="task-filters">
                <el-input
                  v-model="taskSearch"
                  :placeholder="$t('common.search')"
                  :prefix-icon="Search"
                  size="small"
                  class="task-search"
                />
                <el-select
                  v-model="taskStatusFilter"
                  :placeholder="$t('task.status')"
                  size="small"
                  class="status-filter"
                >
                  <el-option
                    v-for="status in taskStatuses"
                    :key="status.value"
                    :label="$t(`status.${status.value}`)"
                    :value="status.value"
                  />
                </el-select>
                <el-select
                  v-model="taskPriorityFilter"
                  :placeholder="$t('task.priority')"
                  size="small"
                  class="priority-filter"
                >
                  <el-option
                    v-for="priority in taskPriorities"
                    :key="priority.value"
                    :label="$t(`priority.${priority.value}`)"
                    :value="priority.value"
                  />
                </el-select>
              </div>

              <!-- Task List -->
              <div class="task-list">
                <div v-for="task in filteredTasks" :key="task.id" class="task-item">
                  <div class="task-checkbox">
                    <el-checkbox v-model="task.completed" @change="updateTaskStatus(task)" />
                  </div>
                  <div class="task-info" @click="viewTask(task)">
                    <div class="task-title">{{ task.title }}</div>
                    <div class="task-meta">
                      <el-tag size="small" :type="getPriorityType(task.priority)">
                        {{ $t(`priority.${task.priority}`) }}
                      </el-tag>
                      <span class="assignee">{{ task.assignee_name }}</span>
                      <span class="due-date" :class="{ overdue: isOverdue(task.due_date) }">
                        <el-icon><Clock /></el-icon>
                        {{ formatDate(task.due_date) }}
                      </span>
                    </div>
                  </div>
                  <div class="task-actions">
                    <el-button type="text" size="small" @click="editTask(task)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-popconfirm
                      title="确定要删除这个任务吗？"
                      confirm-button-text="确定"
                      cancel-button-text="取消"
                      @confirm="deleteTask(task)"
                    >
                      <template #reference>
                        <el-button type="text" size="small" @click>
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </template>
                    </el-popconfirm>
                  </div>
                </div>
              </div>

              <!-- Empty State -->
              <div v-if="filteredTasks.length === 0" class="empty-tasks">
                <el-empty :description="$t('dashboard.noTasks')" />
                <el-button type="primary" @click="createTask">
                  {{ $t('dashboard.createTask') }}
                </el-button>
              </div>
            </div>
          </el-card>

          <!-- Project Timeline -->
          <el-card class="section-card">
            <template #header>
              <h3>{{ $t('common.timeline') }}</h3>
            </template>
            <div class="timeline-section">
              <el-timeline>
                <el-timeline-item
                  v-for="event in timelineEvents"
                  :key="event.id"
                  :timestamp="formatDate(event.created_at)"
                  placement="top"
                >
                  <div class="timeline-event">
                    <div class="event-user">
                      <el-avatar size="small">{{ event.user_initials }}</el-avatar>
                      <span>{{ event.user_name }}</span>
                    </div>
                    <div class="event-content">
                      {{ event.content }}
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-card>
        </el-col>

        <!-- Right Column -->
        <el-col :xs="24" :md="8">
          <!-- Project Stats -->
          <el-card class="section-card stats-card">
            <template #header>
              <h3>{{ $t('common.stats') }}</h3>
            </template>
            <div class="stats-content">
              <div class="stat-item">
                <div class="stat-label">{{ $t('dashboard.totalTasks') }}</div>
                <div class="stat-value">{{ stats.totalTasks }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">{{ $t('dashboard.overdueTasks') }}</div>
                <div class="stat-value" style="color: #f56c6c;">{{ stats.overdueTasks }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">{{ $t('common.completionRate') }}</div>
                <div class="stat-value">{{ stats.completionRate }}%</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">{{ $t('project.budget') }}</div>
                <div class="stat-value">¥{{ formatNumber(project.budget) }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">{{ $t('project.actualCost') }}</div>
                <div class="stat-value">¥{{ formatNumber(project.actual_cost) }}</div>
              </div>
            </div>
          </el-card>

          <!-- Team Members -->
          <el-card class="section-card team-card">
            <template #header>
              <div class="section-header">
                <h3>{{ $t('navigation.team') }}</h3>
                <el-button type="text" size="small" @click="manageTeam">
                  <el-icon><Setting /></el-icon>
                </el-button>
              </div>
            </template>
            <div class="team-members">
              <div v-for="member in teamMembers" :key="member.id" class="team-member">
                <el-avatar :size="40" :src="member.avatar">
                  {{ member.initials }}
                </el-avatar>
                <div class="member-info">
                  <div class="member-name">{{ member.name }}</div>
                  <div class="member-role">{{ member.role }}</div>
                </div>
                <div class="member-stats">
                  <div class="member-tasks">{{ member.taskCount }} {{ $t('navigation.tasks') }}</div>
                </div>
              </div>
            </div>
            <div class="team-actions">
              <el-button type="primary" size="small" @click="addTeamMember" plain>
                <el-icon><UserFilled /></el-icon>
                {{ $t('common.addMember') }}
              </el-button>
            </div>
          </el-card>

          <!-- Attachments -->
          <el-card class="section-card attachments-card">
            <template #header>
              <div class="section-header">
                <h3>{{ $t('common.attachments') }}</h3>
              <el-upload
                  action="#"
                  :show-file-list="false"
                  :before-upload="beforeUpload"
                  :http-request="handleUpload"
                >
                  <el-button type="text" size="small">
                    <el-icon><Upload /></el-icon>
                  </el-button>
                </el-upload>
              </div>
            </template>
            <div class="attachments-list">
              <div v-for="file in attachments" :key="file.id" class="attachment-item">
                <div class="attachment-icon">
                  <el-icon>
                    <component :is="getFileIcon(file.type)" />
                  </el-icon>
                </div>
                <div class="attachment-info">
                  <div class="attachment-name">{{ file.name }}</div>
                  <div class="attachment-meta">
                    <span>{{ formatFileSize(file.size) }}</span>
                    <span>{{ formatDate(file.uploaded_at) }}</span>
                  </div>
                </div>
                <div class="attachment-actions">
                  <el-button type="text" size="small" @click="downloadFile(file)">
                    <el-icon><Download /></el-icon>
                  </el-button>
                  <el-button type="text" size="small" @click="previewFile(file)">
                    <el-icon><View /></el-icon>
                  </el-button>
                  <el-button type="text" size="small" @click="deleteFile(file)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
            <div v-if="attachments.length === 0" class="empty-attachments">
              <el-empty :description="$t('common.noAttachments')" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    </el-tab-pane>

    <!-- Edit Project Dialog -->
    <el-dialog
      v-model="editDialogVisible"
      :title="$t('common.edit')"
      width="600px"
    >
      <!-- Edit form would go here -->
      <span>Edit project form</span>
            <template #footer>
        <el-button @click="editDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="saveProject">
          {{ $t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
  </el-tabs>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit, Download, More, Plus, Search,
  Clock, Setting, UserFilled, Upload,
  View, Delete, Document, Picture, Folder
} from '@element-plus/icons-vue'
import GanttChart from '@/components/gantt/GanttChart.vue'
import { useGanttStore } from '@/stores/gantt'
import request from '@/services/request'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const ganttStore = useGanttStore()

const projectId = computed(() => Number(route.params.id))

// 标签页
const activeTab = ref('description')

// 加载状态
const loading = ref(false)
const project = ref<any>(null)
const tasks = ref<any[]>([])
const stats = ref<any>({})
const teamMembers = ref<any[]>([])
const timelineEvents = ref<any[]>([])
const attachments = ref<any[]>([])

// State
const editDialogVisible = ref(false)
const taskSearch = ref('')
const taskStatusFilter = ref('')
const taskPriorityFilter = ref('')

// Constants
const taskStatuses = [
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'review', label: 'Review' },
  { value: 'completed', label: 'Completed' },
  { value: 'blocked', label: 'Blocked' }
]

const taskPriorities = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' }
]

// Computed
const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    const matchesSearch = !taskSearch.value ||
      task.title.toLowerCase().includes(taskSearch.value.toLowerCase())
    const matchesStatus = !taskStatusFilter.value ||
      task.status === taskStatusFilter.value
    const matchesPriority = !taskPriorityFilter.value ||
      task.priority === taskPriorityFilter.value

    return matchesSearch && matchesStatus && matchesPriority
  })
})

// Methods
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    planning: 'info',
    completed: '',
    archived: 'info'
  }
  return statusMap[status] || ''
}

const getPriorityType = (priority: string) => {
  const priorityMap: Record<string, string> = {
    low: 'info',
    medium: '',
    high: 'warning',
    urgent: 'danger'
  }
  return priorityMap[priority] || ''
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const isOverdue = (dueDate: string) => {
  if (!dueDate) return false
  const due = new Date(dueDate)
  const now = new Date()
  return due < now
}

const getFileIcon = (fileType: string) => {
  const iconMap: Record<string, string> = {
    pdf: 'Document',
    doc: 'Document',
    docx: 'Document',
    xls: 'Document',
    xlsx: 'Document',
    sketch: 'Picture',
    png: 'Picture',
    jpg: 'Picture',
    jpeg: 'Picture',
    zip: 'Folder'
  }
  return iconMap[fileType] || 'Document'
}

// API 加载
async function loadProjectDetail() {
  loading.value = true
  ganttLoading.value = true
  try {
    const res: any = await request.get(`/projects/${projectId.value}/detail`)
    project.value = res.project
    tasks.value = res.tasks
    stats.value = res.stats
    teamMembers.value = res.teamMembers
    timelineEvents.value = res.timelineEvents
    attachments.value = res.attachments
    // 加载甘特图数据
    await ganttStore.fetchGanttTasks()
  } catch (err: any) {
    console.error('加载项目详情失败:', err)
    ElMessage.error(err?.response?.data?.detail || '加载项目详情失败')
  } finally {
    loading.value = false
    ganttLoading.value = false
  }
}

// 甘特图加载状态
const ganttLoading = ref(false)

// 更新任务状态
async function updateTaskStatus(task: any) {
  const newStatus = task.completed ? 'completed' : 'pending'
  try {
    await request.put(`/tasks/${task.id}`, { status: newStatus })
    task.status = newStatus
    ElMessage.success('任务状态已更新')
    await loadProjectDetail()
  } catch (err: any) {
    console.error('更新任务状态失败:', err)
    ElMessage.error(err?.response?.data?.detail || '更新失败')
    task.completed = !task.completed // 回滚
  }
}

// 编辑项目
async function saveProject() {
  try {
    await request.put(`/projects/${project.value.id}`, project.value)
    ElMessage.success('项目已更新')
    editDialogVisible.value = false
    await loadProjectDetail()
  } catch (err: any) {
    console.error('保存项目失败:', err)
    ElMessage.error(err?.response?.data?.detail || '保存失败')
  }
}

// 删除项目
const handleProjectCommand = async (command: string) => {
  if (command === 'archive') {
    try {
      await request.put(`/projects/${project.value.id}`, { status: 'archived' })
      ElMessage.success('项目已归档')
      await loadProjectDetail()
    } catch (err: any) {
      ElMessage.error(err?.response?.data?.detail || '归档失败')
    }
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除此项目吗？此操作不可恢复。', '删除项目', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      })
      await request.delete(`/projects/${project.value.id}`)
      ElMessage.success('项目已删除')
      router.push('/projects')
    } catch (e: any) {
      if (e !== 'cancel') {
        console.error('删除项目失败', e)
        ElMessage.error(e?.response?.data?.detail || '删除失败')
      }
    }
  }
}

// 文件操作
async function handleUpload(file: any) {
  const formData = new FormData()
  formData.append('file', file.file)
  try {
    await request.post(`/projects/${projectId.value}/attachments`, formData)
    ElMessage.success('文件上传成功')
    await loadProjectDetail()
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '上传失败')
  }
}

async function downloadFile(file: any) {
  window.open(`/projects/${projectId.value}/attachments/${file.id}/download`, '_blank')
}

async function previewFile(file: any) {
  window.open(`/projects/${projectId.value}/attachments/${file.id}/preview`, '_blank')
}

async function deleteFile(file: any) {
  try {
    await ElMessageBox.confirm('确定要删除此文件吗？', '删除文件', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await request.delete(`/projects/${projectId.value}/attachments/${file.id}`)
    ElMessage.success('文件已删除')
    await loadProjectDetail()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 查看任务
function viewTask(task: any) {
  router.push({ name: 'task-detail', params: { id: task.id } })
}

// 创建任务
function createTask() {
  router.push({ name: 'create-task-page', query: { projectId: projectId.value } })
}

// 编辑任务
function editTask(task: any) {
  router.push({ name: 'task-detail', params: { id: task.id } })
}

// 删除任务
async function deleteTask(task: any) {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务"${task.title}"吗？此操作不可恢复。`,
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await request.delete(`/tasks/${task.id}`)
    ElMessage.success('任务已删除')
    await loadProjectDetail()
  } catch (err: any) {
    if (err !== 'cancel') {
      ElMessage.error('删除任务失败')
    }
  }
}

// Lifecycle
onMounted(() => {
  loadProjectDetail()
})
</script>

<style scoped>
.project-detail {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.header-left {
  flex: 1;
}

.project-title {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.project-code {
  color: var(--el-text-color-secondary);
  font-family: monospace;
  font-size: 14px;
}

.project-dates {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.project-content {
  margin-top: 20px;
}

.section-card {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Tasks Section */
.task-filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.task-search {
  flex: 1;
}

.status-filter, .priority-filter {
  width: 120px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
  cursor: pointer;
  transition: all 0.3s ease;
}

.task-item:hover {
  border-color: var(--el-color-primary-light-7);
  background: var(--el-color-primary-light-9);
}

.task-checkbox {
  flex-shrink: 0;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.assignee {
  color: var(--el-text-color-regular);
}

.due-date {
  display: flex;
  align-items: center;
  gap: 4px;
}

.due-date.overdue {
  color: var(--el-color-danger);
  font-weight: 500;
}

.task-actions {
  flex-shrink: 0;
}

.empty-tasks {
  text-align: center;
  padding: 40px 0;
}

/* Timeline Section */
.timeline-event {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.event-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
}

.event-content {
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

/* Stats Section */
.stats-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.stat-label {
  color: var(--el-text-color-secondary);
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* Team Section */
.team-members {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
}

.member-info {
  flex: 1;
}

.member-name {
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--el-text-color-primary);
}

.member-role {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.member-stats {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.team-actions {
  text-align: center;
}

/* Attachments Section */
.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
}

.attachment-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-color-primary-light-9);
  border-radius: 6px;
  color: var(--el-color-primary);
}

.attachment-icon .el-icon {
  font-size: 20px;
}

.attachment-info {
  flex: 1;
  min-width: 0;
}

.attachment-name {
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--el-text-color-primary);
  word-break: break-all;
}

.attachment-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.attachment-actions {
  flex-shrink: 0;
  display: flex;
  gap: 4px;
}

.empty-attachments {
  text-align: center;
  padding: 40px 0;
}

@media (max-width: 768px) {
  .project-header {
    flex-direction: column;
    gap: 20px;
  }

  .header-right {
    width: 100%;
    justify-content: flex-start;
  }

  .task-filters {
    flex-direction: column;
  }

  .task-search, .status-filter, .priority-filter {
    width: 100%;
  }

  .team-member {
    flex-direction: column;
    text-align: center;
  }

  .attachment-item {
    flex-direction: column;
    text-align: center;
  }

  .attachment-actions {
    margin-top: 10px;
  }
}

/* 甘特图样式 */
.project-tabs {
  margin-top: 20px;
}

.project-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.project-tabs :deep(.el-tabs__content) {
  padding: 20px 0;
}

.gantt-card {
  min-height: 650px;
}

.gantt-container {
  width: 100%;
  overflow: hidden;
}

</style>
