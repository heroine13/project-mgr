<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>{{ $t('dashboard.welcome') }}, {{ user?.full_name || user?.username }}</h1>
      <div class="header-actions">
        <el-button type="primary" @click="createNewProject">
          <el-icon><Plus /></el-icon>
          {{ $t('dashboard.newProject') }}
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          {{ $t('dashboard.refresh') }}
        </el-button>
      </div>
    </div>
    
    <!-- Stats Overview -->
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #4CAF50;">
                <el-icon><Folder /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.projects }}</h3>
                <p>{{ $t('dashboard.activeProjects') }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #2196F3;">
                <el-icon><Tickets /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.tasks }}</h3>
                <p>{{ $t('dashboard.totalTasks') }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #FF9800;">
                <el-icon><AlarmClock /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.overdue }}</h3>
                <p>{{ $t('dashboard.overdueTasks') }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #9C27B0;">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.teamMembers }}</h3>
                <p>{{ $t('dashboard.teamMembers') }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- Main Content -->
    <div class="dashboard-content">
      <el-row :gutter="20">
        <!-- Recent Projects -->
        <el-col :xs="24" :md="12">
          <el-card class="dashboard-section">
            <template #header>
              <div class="section-header">
                <h3>{{ $t('dashboard.recentProjects') }}</h3>
                <el-link type="primary" @click="goToProjects">
                  {{ $t('dashboard.viewAll') }}
                </el-link>
              </div>
            </template>
            
            <div v-if="recentProjects.length > 0">
              <div 
                v-for="project in recentProjects" 
                :key="project.id" 
                class="project-item"
              >
                <div class="project-info">
                  <h4>{{ project.name }}</h4>
                  <p class="project-code">{{ project.code }}</p>
                  <p class="project-description">{{ project.description }}</p>
                </div>
                <div class="project-status">
                  <el-tag :type="getStatusType(project.status)" size="small">
                    {{ project.status }}
                  </el-tag>
                  <div class="project-actions">
                    <el-button size="small" @click="viewProject(project)">
                      {{ $t('dashboard.view') }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <el-empty :description="$t('dashboard.noProjects')" />
              <el-button type="primary" @click="createNewProject">
                {{ $t('dashboard.createProject') }}
              </el-button>
            </div>
          </el-card>
        </el-col>
        
        <!-- Recent Tasks -->
        <el-col :xs="24" :md="12">
          <el-card class="dashboard-section">
            <template #header>
              <div class="section-header">
                <h3>{{ $t('dashboard.recentTasks') }}</h3>
                <el-link type="primary" @click="goToTasks">
                  {{ $t('dashboard.viewAll') }}
                </el-link>
              </div>
            </template>
            
            <div v-if="recentTasks.length > 0">
              <div 
                v-for="task in recentTasks" 
                :key="task.id" 
                class="task-item"
              >
                <div class="task-info">
                  <h4>{{ task.title }}</h4>
                  <div class="task-meta">
                    <span class="project-name">{{ task.project_name }}</span>
                    <span class="due-date" :class="{ overdue: isOverdue(task.due_date) }">
                      <el-icon><Clock /></el-icon>
                      {{ formatDate(task.due_date) }}
                    </span>
                  </div>
                </div>
                <div class="task-status">
                  <el-tag :type="getPriorityType(task.priority)" size="small">
                    {{ task.priority }}
                  </el-tag>
                  <el-progress 
                    :percentage="getTaskProgress(task)" 
                    :show-text="false"
                    :stroke-width="4"
                    :width="80"
                  />
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <el-empty :description="$t('dashboard.noTasks')" />
              <el-button type="primary" @click="createNewTask">
                {{ $t('dashboard.createTask') }}
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- Activity Timeline -->
      <el-card class="dashboard-section activity-timeline">
        <template #header>
          <h3>{{ $t('dashboard.recentActivity') }}</h3>
        </template>
        
        <el-timeline>
          <el-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :timestamp="formatDate(activity.created_at)"
            placement="top"
          >
            <el-card shadow="hover" size="small">
              <div class="activity-content">
                <div class="activity-user">
                  <el-avatar size="small">{{ activity.user_initials }}</el-avatar>
                  <span>{{ activity.user_name }}</span>
                </div>
                <div class="activity-text">
                  {{ activity.action }}
                </div>
                <div class="activity-target">
                  <el-tag size="small">{{ activity.entity_type }}</el-tag>
                  <span>{{ activity.entity_name }}</span>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { 
  Plus, Refresh, Folder, Tickets, 
  AlarmClock, User, Clock 
} from '@element-plus/icons-vue'

const router = useRouter()
const { t } = useI18n()

// Mock data - TODO: Replace with API calls
const user = ref({
  id: 1,
  username: 'admin',
  email: 'admin@projectmgr.local',
  full_name: 'Administrator'
})

const stats = ref({
  projects: 5,
  tasks: 42,
  overdue: 3,
  teamMembers: 8
})

const recentProjects = ref([
  { id: 1, name: 'Website Redesign', code: 'WEB-001', description: 'Redesign company website', status: 'active' },
  { id: 2, name: 'Mobile App Development', code: 'MOB-001', description: 'New mobile application', status: 'active' },
  { id: 3, name: 'Marketing Campaign', code: 'MRK-001', description: 'Q4 marketing campaign', status: 'planning' }
])

const recentTasks = ref([
  { id: 1, title: 'Homepage Layout Design', project_name: 'Website Redesign', due_date: '2026-04-10', priority: 'high', status: 'in_progress' },
  { id: 2, title: 'API Integration', project_name: 'Mobile App Development', due_date: '2026-04-05', priority: 'urgent', status: 'pending' },
  { id: 3, title: 'Content Strategy', project_name: 'Marketing Campaign', due_date: '2026-04-15', priority: 'medium', status: 'completed' }
])

const recentActivities = ref([
  { id: 1, user_name: 'John Doe', user_initials: 'JD', action: 'created a new task', entity_type: 'Task', entity_name: 'API Integration', created_at: '2026-04-04T14:30:00Z' },
  { id: 2, user_name: 'Jane Smith', user_initials: 'JS', action: 'updated project status', entity_type: 'Project', entity_name: 'Website Redesign', created_at: '2026-04-04T12:15:00Z' },
  { id: 3, user_name: 'Admin', user_initials: 'A', action: 'added new team member', entity_type: 'User', entity_name: 'Mike Johnson', created_at: '2026-04-04T10:45:00Z' }
])

onMounted(() => {
  loadDashboardData()
})

const loadDashboardData = async () => {
  // TODO: Load data from API
  console.log('Loading dashboard data...')
}

const refreshData = () => {
  loadDashboardData()
}

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

const getTaskProgress = (task: any) => {
  const progressMap: Record<string, number> = {
    pending: 0,
    in_progress: 50,
    review: 75,
    completed: 100,
    blocked: 10
  }
  return progressMap[task.status] || 0
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const isOverdue = (dueDate: string) => {
  if (!dueDate) return false
  const due = new Date(dueDate)
  const now = new Date()
  return due < now
}

const createNewProject = () => {
  router.push('/projects/new')
}

const createNewTask = () => {
  router.push('/tasks/new')
}

const viewProject = (project: any) => {
  router.push(`/projects/${project.id}`)
}

const goToProjects = () => {
  router.push('/projects')
}

const goToTasks = () => {
  router.push('/tasks')
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-overview {
  margin-bottom: 30px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon .el-icon {
  font-size: 24px;
}

.stat-info h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.stat-info p {
  margin: 5px 0 0 0;
  color: #666;
  font-size: 14px;
}

.dashboard-content {
  margin-top: 30px;
}

.dashboard-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-item, .task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.project-item:last-child, .task-item:last-child {
  border-bottom: none;
}

.project-info h4, .task-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
}

.project-code {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.project-description {
  margin: 5px 0 0 0;
  color: #999;
  font-size: 13px;
}

.project-status, .task-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.project-actions {
  display: flex;
  gap: 5px;
}

.task-meta {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-top: 5px;
}

.project-name, .due-date {
  font-size: 13px;
  color: #666;
}

.due-date {
  display: flex;
  align-items: center;
  gap: 3px;
}

.due-date.overdue {
  color: #f56c6c;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 20px 0;
}

.activity-timeline {
  margin-top: 30px;
}

.activity-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-user {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.activity-text {
  color: #333;
}

.activity-target {
  display: flex;
  align-items: center;
  gap: 10px;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .project-item, .task-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .project-status, .task-status {
    align-items: flex-start;
    width: 100%;
  }
}
</style>