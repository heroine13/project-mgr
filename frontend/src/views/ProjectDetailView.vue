<template>
  <div class="project-detail">
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
    <div class="project-content">
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { 
  Edit, Download, More, Plus, Search, 
  Clock, Setting, UserFilled, Upload, 
  View, Delete 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// Mock data - TODO: Replace with API calls
const project = ref({
  id: 1,
  name: 'Website Redesign',
  code: 'WEB-001',
  description: 'Redesign company website with modern UI/UX',
  status: 'active',
  start_date: '2026-04-01',
  end_date: '2026-06-30',
  budget: 50000,
  actual_cost: 12000,
  owner_id: 1
})

const tasks = ref([
  { id: 1, title: 'Homepage Layout Design', status: 'in_progress', priority: 'high', assignee_name: 'John Doe', due_date: '2026-04-10', completed: false },
  { id: 2, title: 'API Integration', status: 'pending', priority: 'urgent', assignee_name: 'Jane Smith', due_date: '2026-04-05', completed: false },
  { id: 3, title: 'Content Strategy', status: 'completed', priority: 'medium', assignee_name: 'Mike Johnson', due_date: '2026-04-15', completed: true }
])

const teamMembers = ref([
  { id: 1, name: 'John Doe', role: 'Frontend Developer', avatar: '', initials: 'JD', taskCount: 5 },
  { id: 2, name: 'Jane Smith', role: 'Backend Developer', avatar: '', initials: 'JS', taskCount: 3 },
  { id: 3, name: 'Mike Johnson', role: 'Project Manager', avatar: '', initials: 'MJ', taskCount: 2 }
])

const attachments = ref([
  { id: 1, name: 'Design Specifications.pdf', type: 'pdf', size: 2048000, uploaded_at: '2026-04-04T10:30:00Z' },
  { id: 2, name: 'Wireframe.sketch', type: 'sketch', size: 5120000, uploaded_at: '2026-04-04T14:15:00Z' },
  { id: 3, name: 'Project Timeline.xlsx', type: 'excel', size: 1024000, uploaded_at: '2026-04-04T16:45:00Z' }
])

const timelineEvents = ref([
  { id: 1, user_name: 'John Doe', user_initials: 'JD', content: 'Created the project', created_at: '2026-04-01T09:00:00Z' },
  { id: 2, user_name: 'Jane Smith', user_initials: 'JS', content: 'Added API integration task', created_at: '2026-04-02T14:30:00Z' },
  { id: 3, user_name: 'Mike Johnson', user_initials: 'MJ', content: 'Updated project timeline', created_at: '2026-04-03T11:15:00Z' }
])

const stats = ref({
  totalTasks: 15,
  overdueTasks: 3,
  completionRate: 65,
  budget: 50000,
  actualCost: 12000
})

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

// Event Handlers
const editProject = () => {
  editDialogVisible.value = true
}

const saveProject = () => {
  editDialogVisible.value = false
  // TODO: Save project data
}

const exportProject = () => {
  // TODO: Export project data
  console.log('Export project')
}

const handleProjectCommand = (command: string) => {
  if (command === 'archive') {
    // TODO: Archive project
  } else if (command === 'delete') {
    // TODO: Delete project with confirmation
  }
}

const createTask = () => {
  router.push(`/projects/${project.value.id}/tasks/new`)
}

const viewTask = (task: any) => {
  router.push(`/tasks/${task.id}`)
}

const editTask = (task: any) => {
  router.push(`/tasks/${task.id}/edit`)
}

const updateTaskStatus = (task: any) => {
  // TODO: Update task status via API
  console.log('Update task status:', task.id, task.completed)
}

const manageTeam = () => {
  router.push(`/projects/${project.value.id}/team`)
}

const addTeamMember = () => {
  // TODO: Add team member dialog
  console.log('Add team member')
}

const beforeUpload = (file: File) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('File size cannot exceed 10MB')
    return false
  }
  return true
}

const handleUpload = () => {
  // TODO: Handle file upload
  console.log('Upload file')
}

const downloadFile = (file: any) => {
  // TODO: Download file
  console.log('Download file:', file.name)
}

const previewFile = (file: any) => {
  // TODO: Preview file
  console.log('Preview file:', file.name)
}

const deleteFile = (file: any) => {
  // TODO: Delete file with confirmation
  console.log('Delete file:', file.name)
}

// Lifecycle
onMounted(() => {
  // TODO: Load project data from API
  const projectId = route.params.id
  console.log('Loading project:', projectId)
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
</style>