<template>
  <div class="task-detail">
    <!-- Task Header -->
    <div class="task-header">
      <div class="header-left">
        <div class="task-title-section">
          <el-checkbox v-model="task.completed" @change="updateTaskCompletion">
            <h1 class="task-title">{{ task.title }}</h1>
          </el-checkbox>
          <div class="task-actions">
            <el-button type="text" size="small" @click="editTask">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button type="text" size="small" @click="deleteTask">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
        
        <div class="task-meta">
          <div class="meta-item">
            <el-icon><Folder /></el-icon>
            <span class="project-link" @click="goToProject">{{ task.project_name }}</span>
          </div>
          <div class="meta-item">
            <el-icon><User /></el-icon>
            <span>{{ task.assignee_name || $t('common.unassigned') }}</span>
          </div>
          <div class="meta-item" :class="{ overdue: isOverdue(task.due_date) }">
            <el-icon><Clock /></el-icon>
            <span>{{ formatDate(task.due_date) }}</span>
          </div>
        </div>
        
        <div class="task-tags">
          <el-tag :type="getStatusType(task.status)" size="small" class="status-tag">
            {{ $t(`status.${task.status}`) }}
          </el-tag>
          <el-tag :type="getPriorityType(task.priority)" size="small" class="priority-tag">
            {{ $t(`priority.${task.priority}`) }}
          </el-tag>
          <el-tag v-for="tag in task.tagsArray" :key="tag" size="small" class="custom-tag">
            {{ tag }}
          </el-tag>
        </div>
      </div>
      
      <div class="header-right">
        <el-button-group>
          <el-button type="primary" @click="editTask">
            <el-icon><Edit /></el-icon>
            {{ $t('common.edit') }}
          </el-button>
          <el-button @click="addComment">
            <el-icon><ChatDotRound /></el-icon>
            {{ $t('common.comment') }}
          </el-button>
          <el-dropdown @command="handleTaskCommand">
            <el-button>
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="move">{{ $t('common.move') }}</el-dropdown-item>
                <el-dropdown-item command="copy">{{ $t('common.copy') }}</el-dropdown-item>
                <el-dropdown-item command="archive" divided>{{ $t('status.archived') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-button-group>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="task-content">
      <el-row :gutter="20">
        <!-- Left Column -->
        <el-col :xs="24" :md="16">
          <!-- Task Description -->
          <el-card class="section-card">
            <template #header>
              <h3>{{ $t('task.description') }}</h3>
            </template>
            <div class="description-content">
              <div v-if="task.description" class="description-text">
                <vue-markdown :source="task.description" />
              </div>
              <div v-else class="empty-description">
                <el-empty :description="$t('common.noDescription')" />
                <el-button type="text" @click="editTask">
                  {{ $t('common.addDescription') }}
                </el-button>
              </div>
            </div>
          </el-card>
          
          <!-- Comments Section -->
          <el-card class="section-card">
            <template #header>
              <h3>{{ $t('common.comments') }}</h3>
            </template>
            
            <div class="comments-section">
              <!-- Comment Input -->
              <div class="comment-input">
                <el-input
                  v-model="newComment"
                  type="textarea"
                  :rows="3"
                  :placeholder="$t('common.addComment')"
                  resize="none"
                />
                <div class="comment-actions">
                  <el-button-group>
                    <el-button @click="cancelComment">
                      {{ $t('common.cancel') }}
                    </el-button>
                    <el-button type="primary" @click="submitComment" :disabled="!newComment.trim()">
                      {{ $t('common.comment') }}
                    </el-button>
                  </el-button-group>
                </div>
              </div>
              
              <!-- Comments List -->
              <div class="comments-list">
                <div v-for="comment in comments" :key="comment.id" class="comment-item">
                  <div class="comment-header">
                    <div class="comment-user">
                      <el-avatar :size="32" :src="comment.user_avatar">
                        {{ comment.user_initials }}
                      </el-avatar>
                      <div class="user-info">
                        <div class="user-name">{{ comment.user_name }}</div>
                        <div class="comment-time">{{ formatRelativeTime(comment.created_at) }}</div>
                      </div>
                    </div>
                    <div class="comment-actions" v-if="comment.can_edit">
                      <el-button type="text" size="small" @click="editComment(comment)">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                      <el-button type="text" size="small" @click="deleteComment(comment)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                  <div class="comment-content">
                    <vue-markdown :source="comment.content" />
                  </div>
                  <div class="comment-attachments" v-if="comment.attachments && comment.attachments.length > 0">
                    <div class="attachment-list">
                      <div v-for="attachment in comment.attachments" :key="attachment.id" class="attachment-preview">
                        <div class="attachment-icon">
                          <el-icon>
                            <component :is="getFileIcon(attachment.type)" />
                          </el-icon>
                        </div>
                        <div class="attachment-info">
                          <div class="attachment-name">{{ attachment.name }}</div>
                          <div class="attachment-size">{{ formatFileSize(attachment.size) }}</div>
                        </div>
                        <div class="attachment-actions">
                          <el-button type="text" size="small" @click="downloadAttachment(attachment)">
                            <el-icon><Download /></el-icon>
                          </el-button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Empty State -->
              <div v-if="comments.length === 0" class="empty-comments">
                <el-empty :description="$t('common.noComments')" />
              </div>
            </div>
          </el-card>
          
          <!-- Subtasks Section -->
          <el-card class="section-card" v-if="subtasks.length > 0">
            <template #header>
              <div class="section-header">
                <h3>{{ $t('common.subtasks') }}</h3>
                <el-button type="primary" size="small" @click="addSubtask">
                  <el-icon><Plus /></el-icon>
                  {{ $t('common.addSubtask') }}
                </el-button>
              </div>
            </template>
            
            <div class="subtasks-list">
              <div v-for="subtask in subtasks" :key="subtask.id" class="subtask-item">
                <div class="subtask-checkbox">
                  <el-checkbox v-model="subtask.completed" @change="updateSubtaskStatus(subtask)" />
                </div>
                <div class="subtask-info" @click="viewSubtask(subtask)">
                  <div class="subtask-title">{{ subtask.title }}</div>
                  <div class="subtask-meta">
                    <el-tag size="small" :type="getPriorityType(subtask.priority)">
                      {{ $t(`priority.${subtask.priority}`) }}
                    </el-tag>
                    <span class="due-date" :class="{ overdue: isOverdue(subtask.due_date) }">
                      <el-icon><Clock /></el-icon>
                      {{ formatDate(subtask.due_date) }}
                    </span>
                  </div>
                </div>
                <div class="subtask-actions">
                  <el-button type="text" size="small" @click="editSubtask(subtask)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button type="text" size="small" @click="deleteSubtask(subtask)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- Right Column -->
        <el-col :xs="24" :md="8">
          <!-- Task Details -->
          <el-card class="section-card details-card">
            <template #header>
              <h3>{{ $t('common.details') }}</h3>
            </template>
            
            <div class="details-content">
              <div class="detail-item">
                <div class="detail-label">{{ $t('task.assignee') }}</div>
                <div class="detail-value">
                  <el-select
                    v-model="task.assignee_id"
                    :placeholder="$t('common.selectAssignee')"
                    size="small"
                    style="width: 100%;"
                    @change="updateAssignee"
                  >
                    <el-option
                      v-for="user in availableUsers"
                      :key="user.id"
                      :label="user.name"
                      :value="user.id"
                    />
                  </el-select>
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-label">{{ $t('task.status') }}</div>
                <div class="detail-value">
                  <el-select
                    v-model="task.status"
                    size="small"
                    style="width: 100%;"
                    @change="updateStatus"
                  >
                    <el-option
                      v-for="status in taskStatuses"
                      :key="status.value"
                      :label="$t(`status.${status.value}`)"
                      :value="status.value"
                    />
                  </el-select>
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-label">{{ $t('task.priority') }}</div>
                <div class="detail-value">
                  <el-select
                    v-model="task.priority"
                    size="small"
                    style="width: 100%;"
                    @change="updatePriority"
                  >
                    <el-option
                      v-for="priority in taskPriorities"
                      :key="priority.value"
                      :label="$t(`priority.${priority.value}`)"
                      :value="priority.value"
                    />
                  </el-select>
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-label">{{ $t('task.dueDate') }}</div>
                <div class="detail-value">
                  <el-date-picker
                    v-model="task.due_date"
                    type="datetime"
                    size="small"
                    style="width: 100%;"
                    :placeholder="$t('common.selectDate')"
                    @change="updateDueDate"
                  />
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-label">{{ $t('task.estimatedHours') }}</div>
                <div class="detail-value">
                  <el-input-number
                    v-model="task.estimated_hours"
                    :min="0"
                    :max="1000"
                    size="small"
                    style="width: 100%;"
                    @change="updateEstimatedHours"
                  />
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-label">{{ $t('task.actualHours') }}</div>
                <div class="detail-value">
                  <el-input-number
                    v-model="task.actual_hours"
                    :min="0"
                    :max="1000"
                    size="small"
                    style="width: 100%;"
                    @change="updateActualHours"
                  />
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-label">{{ $t('task.tags') }}</div>
                <div class="detail-value">
                  <el-select
                    v-model="task.tagsArray"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    size="small"
                    style="width: 100%;"
                    :placeholder="$t('common.addTags')"
                    @change="updateTags"
                  >
                    <el-option
                      v-for="tag in availableTags"
                      :key="tag"
                      :label="tag"
                      :value="tag"
                    />
                  </el-select>
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-label">{{ $t('task.createdBy') }}</div>
                <div class="detail-value">
                  <div class="creator-info">
                    <el-avatar :size="24" :src="creatorAvatar">
                      {{ creatorInitials }}
                    </el-avatar>
                    <span>{{ creatorName }}</span>
                  </div>
                </div>
              </div>
              
              <div class="detail-item">
                <div class="detail-label">{{ $t('common.createdAt') }}</div>
                <div class="detail-value">{{ formatFullDate(task.created_at) }}</div>
              </div>
              
              <div class="detail-item">
                <div class="detail-label">{{ $t('common.updatedAt') }}</div>
                <div class="detail-value">{{ formatFullDate(task.updated_at) }}</div>
              </div>
            </div>
          </el-card>
          
          <!-- Time Tracking -->
          <el-card class="section-card time-card">
            <template #header>
              <div class="section-header">
                <h3>{{ $t('common.timeTracking') }}</h3>
                <el-button type="text" size="small" @click="startTimer">
                  <el-icon><Timer /></el-icon>
                </el-button>
              </div>
            </template>
            
            <div class="time-content">
              <div class="time-stats">
                <div class="time-stat">
                  <div class="stat-label">{{ $t('task.estimatedHours') }}</div>
                  <div class="stat-value">{{ task.estimated_hours }}h</div>
                </div>
                <div class="time-stat">
                  <div class="stat-label">{{ $t('task.actualHours') }}</div>
                  <div class="stat-value" :class="{ over: task.actual_hours > task.estimated_hours }">
                    {{ task.actual_hours }}h
                  </div>
                </div>
                <div class="time-stat">
                  <div class="stat-label">{{ $t('common.remaining') }}</div>
                  <div class="stat-value">
                    {{ Math.max(0, task.estimated_hours - task.actual_hours) }}h
                  </div>
                </div>
              </div>
              
              <div class="time-entries">
                <div v-for="entry in timeEntries" :key="entry.id" class="time-entry">
                  <div class="entry-user">
                    <el-avatar :size="24">{{ entry.user_initials }}</el-avatar>
                  </div>
                  <div class="entry-info">
                    <div class="entry-duration">{{ entry.duration }}h</div>
                    <div class="entry-date">{{ formatRelativeTime(entry.started_at) }}</div>
                  </div>
                  <div class="entry-actions">
                    <el-button type="text" size="small" @click="editTimeEntry(entry)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
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
                    <span>{{ formatRelativeTime(file.uploaded_at) }}</span>
                  </div>
                </div>
                <div class="attachment-actions">
                  <el-button type="text" size="small" @click="previewFile(file)">
                    <el-icon><View /></el-icon>
                  </el-button>
                  <el-button type="text" size="small" @click="downloadFile(file)">
                    <el-icon><Download /></el-icon>
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
    
    <!-- Edit Task Dialog -->
    <el-dialog
      v-model="editDialogVisible"
      :title="$t('common.edit')"
      width="600px"
    >
      <!-- Edit form would go here -->
      <span>Edit task form</span>
      <template #footer>
        <el-button @click="editDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="saveTask">
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
import VueMarkdown from 'vue-markdown'
import { 
  Edit, Delete, Folder, User, Clock,
  ChatDotRound, More, Plus, Upload,
  View, Download, Timer
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// Mock data - TODO: Replace with API calls
const task = ref({
  id: 1,
  title: 'Homepage Layout Design',
  description: 'Design modern homepage layout with responsive design principles.\n\n## Requirements\n- Mobile-first design\n- Dark mode support\n- Accessibility compliance\n- Performance optimization',
  status: 'in_progress',
  priority: 'high',
  assignee_id: 1,
  assignee_name: 'John Doe',
  project_id: 1,
  project_name: 'Website Redesign',
  due_date: '2026-04-10T18:00:00Z',
  estimated_hours: 20,
  actual_hours: 12,
  tags: 'design,ui,responsive',
  tagsArray: ['design', 'ui', 'responsive'],
  completed: false,
  created_by: 1,
  created_at: '2026-04-01T09:00:00Z',
  updated_at: '2026-04-04T14:30:00Z'
})

const comments = ref([
  { 
    id: 1, 
    user_id: 1, 
    user_name: 'John Doe', 
    user_initials: 'JD', 
    user_avatar: '',
    content: 'Initial design mockup completed. Please review.',
    created_at: '2026-04-02T10:30:00Z',
    can_edit: true,
    attachments: []
  },
  { 
    id: 2, 
    user_id: 2, 
    user_name: 'Jane Smith', 
    user_initials: 'JS', 
    user_avatar: '',
    content: 'Looks good! Can we add more contrast for accessibility?',
    created_at: '2026-04-03T14:15:00Z',
    can_edit: false,
    attachments: [
      { id: 1, name: 'accessibility-guidelines.pdf', type: 'pdf', size: 2048000 }
    ]
  }
])

const subtasks = ref([
  { id: 1, title: 'Mobile layout design', status: 'completed', priority: 'medium', due_date: '2026-04-05T18:00:00Z', completed: true },
  { id: 2, title: 'Dark mode implementation', status: 'in_progress', priority: 'high', due_date: '2026-04-08T18:00:00Z', completed: false },
  { id: 3, title: 'Accessibility testing', status: 'pending', priority: 'medium', due_date: '2026-04-12T18:00:00Z', completed: false }
])

const attachments = ref([
  { id: 1, name: 'design-mockup.fig', type: 'figma', size: 5120000, uploaded_at: '2026-04-02T10:30:00Z' },
  { id: 2, name: 'color-palette.pdf', type: 'pdf', size: 1024000, uploaded_at: '2026-04-03T14:15:00Z' }
])

const timeEntries = ref([
  { id: 1, user_id: 1, user_initials: 'JD', duration: 4, started_at: '2026-04-02T09:00:00Z', ended_at: '2026-04-02T13:00:00Z' },
  { id: 2, user_id: 1, user_initials: 'JD', duration: 3, started_at: '2026-04-03T10:00:00Z', ended_at: '2026-04-03T13:00:00Z' },
  { id: 3, user_id: 1, user_initials: 'JD', duration: 5, started_at: '2026-04-04T09:00:00Z', ended_at: '2026-04-04T14:00:00Z' }
])

const availableUsers = ref([
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Smith' },
  { id: 3, name: 'Mike Johnson' }
])

const availableTags = ref(['design', 'ui', 'responsive', 'frontend', 'backend', 'bug', 'feature'])

// State
const editDialogVisible = ref(false)
const newComment = ref('')

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
const creatorName = computed(() => 'John Doe') // TODO: Get from API
const creatorInitials = computed(() => 'JD')
const creatorAvatar = computed(() => '')

// Methods
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'info',
    in_progress: 'warning',
    review: '',
    completed: 'success',
    blocked: 'danger'
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

const formatFullDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}

const formatRelativeTime = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) { // Less than 1 minute
    return '刚刚'
  } else if (diff < 3600000) { // Less than 1 hour
    const minutes = Math.floor(diff / 60000)
    return `${minutes}分钟前`
  } else if (diff < 86400000) { // Less than 1 day
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  } else if (diff < 604800000) { // Less than 1 week
    const days = Math.floor(diff / 86400000)
    return `${days}天前`
  } else {
    return date.toLocaleDateString()
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileIcon = (fileType: string) => {
  const iconMap: Record<string, string> = {
    pdf: 'Document',
    doc: 'Document',
    docx: 'Document',
    xls: 'Document',
    xlsx: 'Document',
    figma: 'Picture',
    sketch: 'Picture',
    png: 'Picture',
    jpg: 'Picture',
    jpeg: 'Picture'
  }
  return iconMap[fileType] || 'Document'
}

const isOverdue = (dueDate: string) => {
  if (!dueDate) return false
  const due = new Date(dueDate)
  const now = new Date()
  return due < now
}

// Event Handlers
const goToProject = () => {
  router.push(`/projects/${task.value.project_id}`)
}

const editTask = () => {
  editDialogVisible.value = true
}

const saveTask = () => {
  editDialogVisible.value = false
  // TODO: Save task data
}

const deleteTask = () => {
  // TODO: Delete task with confirmation
  ElMessageBox.confirm(
    '确定要删除这个任务吗？',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    router.push('/tasks')
  })
}

const addComment = () => {
  // Focus on comment input
  const commentInput = document.querySelector('.comment-input textarea')
  if (commentInput) {
    commentInput.focus()
  }
}

const submitComment = () => {
  if (!newComment.value.trim()) return
  
  const newCommentObj = {
    id: Date.now(),
    user_id: 1,
    user_name: 'Current User',
    user_initials: 'CU',
    user_avatar: '',
    content: newComment.value,
    created_at: new Date().toISOString(),
    can_edit: true,
    attachments: []
  }
  
  comments.value.unshift(newCommentObj)
  newComment.value = ''
}

const cancelComment = () => {
  newComment.value = ''
}

const editComment = (comment: any) => {
  // TODO: Edit comment
  console.log('Edit comment:', comment.id)
}

const deleteComment = (comment: any) => {
  // TODO: Delete comment with confirmation
  console.log('Delete comment:', comment.id)
}

const downloadAttachment = (attachment: any) => {
  // TODO: Download attachment
  console.log('Download attachment:', attachment.name)
}

const addSubtask = () => {
  // TODO: Add subtask dialog
  console.log('Add subtask')
}

const viewSubtask = (subtask: any) => {
  // TODO: View subtask details
  console.log('View subtask:', subtask.id)
}

const editSubtask = (subtask: any) => {
  // TODO: Edit subtask
  console.log('Edit subtask:', subtask.id)
}

const deleteSubtask = (subtask: any) => {
  // TODO: Delete subtask with confirmation
  console.log('Delete subtask:', subtask.id)
}

const updateSubtaskStatus = (subtask: any) => {
  // TODO: Update subtask status via API
  console.log('Update subtask status:', subtask.id, subtask.completed)
}

const updateTaskCompletion = () => {
  // TODO: Update task completion status via API
  console.log('Update task completion:', task.value.completed)
}

const updateAssignee = () => {
  // TODO: Update assignee via API
  console.log('Update assignee:', task.value.assignee_id)
}

const updateStatus = () => {
  // TODO: Update status via API
  console.log('Update status:', task.value.status)
}

const updatePriority = () => {
  // TODO: Update priority via API
  console.log('Update priority:', task.value.priority)
}

const updateDueDate = () => {
  // TODO: Update due date via API
  console.log('Update due date:', task.value.due_date)
}

const updateEstimatedHours = () => {
  // TODO: Update estimated hours via API
  console.log('Update estimated hours:', task.value.estimated_hours)
}

const updateActualHours = () => {
  // TODO: Update actual hours via API
  console.log('Update actual hours:', task.value.actual_hours)
}

const updateTags = () => {
  // TODO: Update tags via API
  console.log('Update tags:', task.value.tagsArray)
}

const handleTaskCommand = (command: string) => {
  if (command === 'move') {
    // TODO: Move task dialog
  } else if (command === 'copy') {
    // TODO: Copy task dialog
  } else if (command === 'archive') {
    // TODO: Archive task
  }
}

const startTimer = () => {
  // TODO: Start time tracking
  console.log('Start timer')
}

const editTimeEntry = (entry: any) => {
  // TODO: Edit time entry
  console.log('Edit time entry:', entry.id)
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

const previewFile = (file: any) => {
  // TODO: Preview file
  console.log('Preview file:', file.name)
}

const downloadFile = (file: any) => {
  // TODO: Download file
  console.log('Download file:', file.name)
}

// Lifecycle
onMounted(() => {
  // TODO: Load task data from API
  const taskId = route.params.id
  console.log('Loading task:', taskId)
})
</script>

<style scoped>
.task-detail {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.task-header {
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

.task-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.task-title {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.task-actions {
  display: flex;
  gap: 4px;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.project-link {
  color: var(--el-color-primary);
  cursor: pointer;
  text-decoration: underline;
}

.meta-item.overdue {
  color: var(--el-color-danger);
}

.task-tags {
  display: flex;
  gap: 8px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.task-content {
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

/* Description Section */
.description-content {
  min-height: 100px;
}

.description-text {
  line-height: 1.8;
}

.description-text :deep(p) {
  margin-bottom: 1em;
}

.description-text :deep(h1),
.description-text :deep(h2),
.description-text :deep(h3) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
}

.description-text :deep(ul),
.description-text :deep(ol) {
  margin-left: 2em;
  margin-bottom: 1em;
}

.description-text :deep(code) {
  background: var(--el-fill-color-light);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.empty-description {
  text-align: center;
  padding: 40px 0;
}

/* Comments Section */
.comment-input {
  margin-bottom: 30px;
}

.comment-actions {
  margin-top: 12px;
  text-align: right;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  padding: 20px;
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.comment-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.comment-content {
  line-height: 1.6;
  color: var(--el-text-color-regular);
  margin-bottom: 16px;
}

.comment-content :deep(p) {
  margin-bottom: 0.5em;
}

.comment-attachments {
  margin-top: 16px;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.attachment-icon {
  font-size: 24px;
  color: var(--el-color-primary);
}

.attachment-info {
  flex: 1;
}

.attachment-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.attachment-size {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* Responsive styles */
@media (max-width: 768px) {
  .task-detail {
    padding: 12px;
  }
  
  .task-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .task-title {
    font-size: 22px;
  }
  
  .task-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>