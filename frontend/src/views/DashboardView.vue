<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div>
        <h1>👋 欢迎回来，{{ user?.full_name || user?.username }}</h1>
        <p class="subtitle">这里是项目进度管理系统概览</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="goToNewProject">
          <el-icon><Plus /></el-icon>
          新建项目
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #4CAF50;">
            <el-icon><Folder /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.activeProjects }}</h3>
            <p>进行中项目</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #2196F3;">
            <el-icon><DocumentChecked /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.totalTasks }}</h3>
            <p>总任务数</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #FF5722;">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.overdueTasks }}</h3>
            <p>逾期任务</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #9C27B0;">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.teamMembers }}</h3>
            <p>团队成员</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-content">
      <!-- 左侧：项目列表 -->
      <el-col :xs="24" :md="16">
        <el-card class="dashboard-section">
          <template #header>
            <div class="section-header">
              <h3>项目列表</h3>
              <el-button type="primary" link @click="goToProjects">查看全部</el-button>
            </div>
          </template>
          
          <el-table :data="projectList" stripe style="width: 100%">
            <el-table-column prop="code" label="编号" width="100" />
            <el-table-column prop="name" label="项目名称" min-width="180" />
            <el-table-column prop="status" label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="任务" width="80" align="center">
              <template #default="{ row }">
                <span>{{ row.task_count || 0 }}</span>
              </template>
            </el-table-column>
            <el-table-column label="完成率" width="100" align="center">
              <template #default="{ row }">
                <el-progress :percentage="row.completion_rate || 0" :stroke-width="12" :format="() => (row.completion_rate || 0) + '%'" />
              </template>
            </el-table-column>
          </el-table>
          
          <el-empty v-if="projectList.length === 0" description="暂无项目" />
          <el-button type="primary" @click="goToNewProject" v-if="projectList.length === 0">
            创建第一个项目
          </el-button>
        </el-card>

        <!-- 最近活动 -->
        <el-card class="dashboard-section" style="margin-top: 20px;">
          <template #header>
            <h3>最近活动</h3>
          </template>
          <div v-for="item in recentActivities" :key="item.id" class="activity-item">
            <el-tag size="small" type="info">{{ item.entity_type }}</el-tag>
            <span class="activity-text">{{ item.action }} {{ item.entity_name }}</span>
            <span class="activity-time">{{ formatTime(item.created_at) }}</span>
          </div>
          <el-empty v-if="recentActivities.length === 0" description="暂无活动" />
        </el-card>
      </el-col>

      <!-- 右侧：任务统计 + 趋势 -->
      <el-col :xs="24" :md="8">
        <!-- 任务状态分布 -->
        <el-card class="dashboard-section">
          <template #header>
            <h3>任务状态分布</h3>
          </template>
          <div class="task-status-list">
            <div v-for="item in taskStatusBreakdown" :key="item.label" class="status-item">
              <span class="status-label">{{ item.label }}</span>
              <el-progress :percentage="item.percentage" :stroke-width="16" :color="item.color" />
              <span class="status-count">{{ item.value }}</span>
            </div>
          </div>
        </el-card>

        <!-- 项目完成率 -->
        <el-card class="dashboard-section" style="margin-top: 20px;">
          <template #header>
            <h3>项目完成率</h3>
          </template>
          <div class="project-completion-list">
            <div v-for="p in projectList.slice(0, 5)" :key="p.id" class="project-completion-item">
              <span class="project-name">{{ p.name }}</span>
              <el-progress :percentage="p.completion_rate || 0" :stroke-width="10" :color="getCompletionColor(p.completion_rate)" />
            </div>
          </div>
          <el-empty v-if="projectList.length === 0" description="暂无项目" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/utils/api'

// 用户信息
const user = ref({
  id: 1,
  username: 'admin',
  email: 'admin@projectmgr.local',
  full_name: 'Administrator'
})

// 统计数据
const stats = ref({
  activeProjects: 0,
  totalTasks: 0,
  overdueTasks: 0,
  teamMembers: 0
})

// 项目列表
const projectList = ref<any[]>([])

// 最近活动
const recentActivities = ref<any[]>([])

// 任务状态分布
const taskStatusBreakdown = ref<any[]>([])

// 加载仪表盘数据
const loadDashboardData = async () => {
  try {
    const response = await api.get('/reports/dashboard')
    const data = response.data.data
    
    // 统计数据
    stats.value = {
      activeProjects: data.projects?.active || 0,
      totalTasks: data.summary?.total_tasks || 0,
      overdueTasks: data.overdue_tasks || 0,
      teamMembers: data.team?.total || 0
    }
    
    // 项目列表
    projectList.value = data.project_list || []
    
    // 最近活动
    recentActivities.value = (data.recent_activities || []).map((a: any, i: number) => ({
      id: i,
      ...a
    }))
    
    // 任务状态分布
    const summary = data.summary || {}
    taskStatusBreakdown.value = [
      { label: '已完成', value: summary.completed || 0, percentage: summary.completion_rate || 0, color: '#67C23A' },
      { label: '进行中', value: summary.in_progress || 0, percentage: 0, color: '#409EFF' },
      { label: '待处理', value: summary.pending || 0, percentage: 0, color: '#E6A23C' },
    ]
    
    // 计算各状态的百分比
    const total = summary.total_tasks || 0
    if (total > 0) {
      taskStatusBreakdown.value[1].percentage = Math.round((summary.in_progress || 0) / total * 100)
      taskStatusBreakdown.value[2].percentage = Math.round((summary.pending || 0) / total * 100)
    }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
  }
}

const refreshData = () => {
  loadDashboardData()
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    active: 'success',
    planning: 'info',
    completed: '',
    archived: 'info'
  }
  return map[status] || ''
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    active: '进行中',
    planning: '计划中',
    completed: '已完成',
    archived: '已归档'
  }
  return map[status] || status
}

const getCompletionColor = (rate: number) => {
  if (rate >= 80) return '#67C23A'
  if (rate >= 50) return '#409EFF'
  if (rate > 0) return '#E6A23C'
  return '#F56C6C'
}

const formatTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  if (hours < 1) return '刚刚'
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

const goToNewProject = () => {
  window.location.href = '/projects/new'
}

const goToProjects = () => {
  window.location.href = '/projects'
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-header h1 {
  margin: 0 0 4px 0;
  font-size: 22px;
  color: #303160;
}

.dashboard-header .subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  width: 100%;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  margin-right: 16px;
}

.stat-info h3 {
  margin: 0 0 4px 0;
  font-size: 24px;
  color: #303030303;
}

.stat-info p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.dashboard-content {
  margin-bottom: 30px;
}

.dashboard-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303030;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-text {
  margin: 0 10px;
  flex: 1;
  font-size: 14px;
  color: #606266;
}

.activity-time {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

.task-status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-label {
  width: 60px;
  font-size: 13px;
  color: #606266;
}

.status-count {
  font-size: 13px;
  color: #909399;
  min-width: 30px;
  text-align: right;
}

.project-completion-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.project-completion-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.project-name {
  width: 100px;
  font-size: 13px;
  color: #606266;
}
</style>
