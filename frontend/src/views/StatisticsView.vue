<template>
  <div class="statistics-view">
    <!-- Header -->
    <div class="statistics-header">
      <h1>{{ $t('navigation.reports') }}</h1>
      <div class="header-actions">
        <el-button-group>
          <el-button type="primary" @click="exportReport">
            <el-icon><Download /></el-icon>
            {{ $t('common.export') }}
          </el-button>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            {{ $t('dashboard.refresh') }}
          </el-button>
          <el-dropdown @command="handleReportCommand">
            <el-button>
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pdf">{{ $t('common.exportPDF') }}</el-dropdown-item>
                <el-dropdown-item command="excel">{{ $t('common.exportExcel') }}</el-dropdown-item>
                <el-dropdown-item command="print" divided>{{ $t('common.print') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-button-group>
      </div>
    </div>
    
    <!-- Date Range Selector -->
    <el-card class="filter-card">
      <div class="filter-content">
        <div class="date-range-selector">
          <span class="filter-label">{{ $t('common.dateRange') }}:</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="-"
            :start-placeholder="$t('common.startDate')"
            :end-placeholder="$t('common.endDate')"
            size="small"
          />
          <el-button type="primary" size="small" @click="applyFilters">
            {{ $t('common.apply') }}
          </el-button>
          <el-button size="small" @click="resetFilters">
            {{ $t('common.reset') }}
          </el-button>
        </div>
        
        <div class="additional-filters">
          <el-select
            v-model="selectedProject"
            :placeholder="$t('project.name')"
            size="small"
            clearable
          >
            <el-option
              v-for="project in availableProjects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
          
          <el-select
            v-model="selectedUser"
            :placeholder="$t('task.assignee')"
            size="small"
            clearable
          >
            <el-option
              v-for="user in availableUsers"
              :key="user.id"
              :label="user.name"
              :value="user.id"
            />
          </el-select>
          
          <el-select
            v-model="selectedStatus"
            :placeholder="$t('task.status')"
            size="small"
            clearable
            multiple
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
    </el-card>
    
    <!-- Stats Overview -->
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6" v-for="stat in overviewStats" :key="stat.id">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon" :style="{ background: stat.color }">
                <el-icon>
                  <component :is="stat.icon" />
                </el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stat.value }}</h3>
                <p>{{ stat.label }}</p>
                <div class="stat-trend" :class="stat.trendClass">
                  <el-icon v-if="stat.trendIcon"><component :is="stat.trendIcon" /></el-icon>
                  <span>{{ stat.trendValue }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- Charts Section -->
    <div class="charts-section">
      <el-row :gutter="20">
        <!-- Task Status Distribution -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <template #header>
              <h3>{{ $t('statistics.taskStatusDistribution') }}</h3>
            </template>
            <div class="chart-container">
              <div ref="statusChartRef" style="width: 100%; height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
        
        <!-- Project Progress -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <template #header>
              <h3>{{ $t('statistics.projectProgress') }}</h3>
            </template>
            <div class="chart-container">
              <div ref="progressChartRef" style="width: 100%; height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <!-- Task Completion Trend -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <template #header>
              <h3>{{ $t('statistics.taskCompletionTrend') }}</h3>
            </template>
            <div class="chart-container">
              <div ref="trendChartRef" style="width: 100%; height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
        
        <!-- Team Performance -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <template #header>
              <h3>{{ $t('statistics.teamPerformance') }}</h3>
            </template>
            <div class="chart-container">
              <div ref="performanceChartRef" style="width: 100%; height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- Detailed Reports -->
    <div class="reports-section">
      <el-card class="reports-card">
        <template #header>
          <div class="reports-header">
            <h3>{{ $t('statistics.detailedReports') }}</h3>
            <div class="reports-actions">
              <el-radio-group v-model="activeReportTab" size="small">
                <el-radio-button label="projects">{{ $t('navigation.projects') }}</el-radio-button>
                <el-radio-button label="tasks">{{ $t('navigation.tasks') }}</el-radio-button>
                <el-radio-button label="users">{{ $t('navigation.team') }}</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        
        <!-- Projects Report -->
        <div v-show="activeReportTab === 'projects'" class="report-table">
          <el-table :data="projectsReport" stripe style="width: 100%">
            <el-table-column prop="name" :label="$t('project.name')" min-width="150">
              <template #default="{ row }">
                <router-link :to="`/projects/${row.id}`" class="project-link">
                  {{ row.name }}
                </router-link>
              </template>
            </el-table-column>
            <el-table-column prop="code" :label="$t('project.code')" width="100" />
            <el-table-column prop="status" :label="$t('project.status')" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ $t(`status.${row.status}`) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_tasks" :label="$t('dashboard.totalTasks')" width="100" />
            <el-table-column prop="completed_tasks" :label="$t('common.completed')" width="100" />
            <el-table-column prop="completion_rate" :label="$t('common.completionRate')" width="120">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.completion_rate" 
                  :show-text="false"
                  :stroke-width="6"
                />
                <span class="percentage">{{ row.completion_rate }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="budget_utilization" :label="$t('statistics.budgetUtilization')" width="120">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.budget_utilization" 
                  :show-text="false"
                  :stroke-width="6"
                  :color="getBudgetColor(row.budget_utilization)"
                />
                <span class="percentage">{{ row.budget_utilization }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="owner" :label="$t('project.owner')" width="120" />
          </el-table>
        </div>
        
        <!-- Tasks Report -->
        <div v-show="activeReportTab === 'tasks'" class="report-table">
          <el-table :data="tasksReport" stripe style="width: 100%">
            <el-table-column prop="title" :label="$t('task.title')" min-width="200" />
            <el-table-column prop="project_name" :label="$t('project.name')" width="150" />
            <el-table-column prop="status" :label="$t('task.status')" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ $t(`status.${row.status}`) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" :label="$t('task.priority')" width="100">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" size="small">
                  {{ $t(`priority.${row.priority}`) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="assignee" :label="$t('task.assignee')" width="120" />
            <el-table-column prop="due_date" :label="$t('task.dueDate')" width="120">
              <template #default="{ row }">
                <span :class="{ overdue: isOverdue(row.due_date) }">
                  {{ formatDate(row.due_date) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="estimated_hours" :label="$t('task.estimatedHours')" width="120" />
            <el-table-column prop="actual_hours" :label="$t('task.actualHours')" width="120" />
            <el-table-column prop="time_variance" :label="$t('statistics.timeVariance')" width="120">
              <template #default="{ row }">
                <span :class="{ over: row.time_variance > 0, under: row.time_variance < 0 }">
                  {{ row.time_variance > 0 ? '+' : '' }}{{ row.time_variance }}h
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- Users Report -->
        <div v-show="activeReportTab === 'users'" class="report-table">
          <el-table :data="usersReport" stripe style="width: 100%">
            <el-table-column prop="name" :label="$t('common.name')" width="150" />
            <el-table-column prop="role" :label="$t('common.role')" width="120" />
            <el-table-column prop="total_tasks" :label="$t('dashboard.totalTasks')" width="100" />
            <el-table-column prop="completed_tasks" :label="$t('common.completed')" width="100" />
            <el-table-column prop="completion_rate" :label="$t('common.completionRate')" width="120">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.completion_rate" 
                  :show-text="false"
                  :stroke-width="6"
                />
                <span class="percentage">{{ row.completion_rate }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="overdue_tasks" :label="$t('dashboard.overdueTasks')" width="120">
              <template #default="{ row }">
                <span class="overdue-count">{{ row.overdue_tasks }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="avg_completion_time" :label="$t('statistics.avgCompletionTime')" width="150">
              <template #default="{ row }">
                {{ row.avg_completion_time }}h
              </template>
            </el-table-column>
            <el-table-column prop="productivity_score" :label="$t('statistics.productivityScore')" width="150">
              <template #default="{ row }">
                <el-rate 
                  v-model="row.productivity_score" 
                  disabled
                  :max="5"
                  :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>
    
    <!-- Export Dialog -->
    <el-dialog
      v-model="exportDialogVisible"
      :title="$t('common.exportReport')"
      width="400px"
    >
      <div class="export-options">
        <el-form :model="exportForm" label-width="100px">
          <el-form-item :label="$t('common.format')">
            <el-radio-group v-model="exportForm.format">
              <el-radio label="pdf">PDF</el-radio>
              <el-radio label="excel">Excel</el-radio>
              <el-radio label="csv">CSV</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item :label="$t('common.dateRange')">
            <el-date-picker
              v-model="exportForm.dateRange"
              type="daterange"
              range-separator="-"
              :start-placeholder="$t('common.startDate')"
              :end-placeholder="$t('common.endDate')"
              size="small"
              style="width: 100%;"
            />
          </el-form-item>
          
          <el-form-item :label="$t('common.includeCharts')">
            <el-switch v-model="exportForm.includeCharts" :active-value="true" :inactive-value="false" />
          </el-form-item>
          
          <el-form-item :label="$t('common.includeDetails')">
            <el-switch v-model="exportForm.includeDetails" :active-value="true" :inactive-value="false" />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="exportDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="executeExport" :loading="exporting">
          {{ $t('common.export') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import {
  Download, Refresh, More,
  Folder, Tickets, User, Timer,
  TrendCharts, ArrowUp, ArrowDown
} from '@element-plus/icons-vue'

const { t } = useI18n()

// Mock data
const overviewStats = ref([
  { id: 1, label: t('dashboard.activeProjects'), value: '8', icon: 'Folder', color: '#4CAF50', trendIcon: 'ArrowUp', trendValue: '+12%', trendClass: 'positive' },
  { id: 2, label: t('dashboard.totalTasks'), value: '156', icon: 'Tickets', color: '#2196F3', trendIcon: 'ArrowUp', trendValue: '+8%', trendClass: 'positive' },
  { id: 3, label: t('dashboard.overdueTasks'), value: '14', icon: 'AlarmClock', color: '#FF9800', trendIcon: 'ArrowDown', trendValue: '-3%', trendClass: 'negative' },
  { id: 4, label: t('statistics.completionRate'), value: '78%', icon: 'TrendCharts', color: '#9C27B0', trendIcon: 'ArrowUp', trendValue: '+5%', trendClass: 'positive' }
])

const projectsReport = ref([
  { id: 1, name: 'Website Redesign', code: 'WEB-001', status: 'active', total_tasks: 25, completed_tasks: 18, completion_rate: 72, budget_utilization: 65, owner: 'John Doe' },
  { id: 2, name: 'Mobile App Development', code: 'MOB-001', status: 'active', total_tasks: 42, completed_tasks: 32, completion_rate: 76, budget_utilization: 45, owner: 'Jane Smith' },
  { id: 3, name: 'Marketing Campaign', code: 'MRK-001', status: 'planning', total_tasks: 15, completed_tasks: 3, completion_rate: 20, budget_utilization: 30, owner: 'Mike Johnson' }
])

const tasksReport = ref([
  { id: 1, title: 'Homepage Layout Design', project_name: 'Website Redesign', status: 'completed', priority: 'high', assignee: 'John Doe', due_date: '2026-04-10', estimated_hours: 20, actual_hours: 18, time_variance: -2 },
  { id: 2, title: 'API Integration', project_name: 'Mobile App Development', status: 'in_progress', priority: 'urgent', assignee: 'Jane Smith', due_date: '2026-04-05', estimated_hours: 15, actual_hours: 20, time_variance: 5 },
  { id: 3, title: 'Content Strategy', project_name: 'Marketing Campaign', status: 'pending', priority: 'medium', assignee: 'Mike Johnson', due_date: '2026-04-15', estimated_hours: 10, actual_hours: 0, time_variance: -10 }
])

const usersReport = ref([
  { id: 1, name: 'John Doe', role: 'Frontend Developer', total_tasks: 25, completed_tasks: 20, completion_rate: 80, overdue_tasks: 2, avg_completion_time: 12.5, productivity_score: 4 },
  { id: 2, name: 'Jane Smith', role: 'Backend Developer', total_tasks: 18, completed_tasks: 15, completion_rate: 83, overdue_tasks: 1, avg_completion_time: 14.2, productivity_score: 5 },
  { id: 3, name: 'Mike Johnson', role: 'Project Manager', total_tasks: 12, completed_tasks: 8, completion_rate: 67, overdue_tasks: 0, avg_completion_time: 18.7, productivity_score: 3 }
])

const availableProjects = ref([
  { id: 1, name: 'Website Redesign' },
  { id: 2, name: 'Mobile App Development' },
  { id: 3, name: 'Marketing Campaign' }
])

const availableUsers = ref([
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Smith' },
  { id: 3, name: 'Mike Johnson' }
])

const taskStatuses = ref([
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'review', label: 'Review' },
  { value: 'completed', label: 'Completed' },
  { value: 'blocked', label: 'Blocked' }
])

// State
const dateRange = ref(['2026-04-01', '2026-04-05'])
const selectedProject = ref(null)
const selectedUser = ref(null)
const selectedStatus = ref([])
const activeReportTab = ref('projects')
const exportDialogVisible = ref(false)
const exporting = ref(false)

const exportForm = ref({
  format: 'pdf',
  dateRange: ['2026-04-01', '2026-04-05'],
  includeCharts: true,
  includeDetails: true
})

// Chart refs
const statusChartRef = ref<HTMLElement>()
const progressChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const performanceChartRef = ref<HTMLElement>()

let statusChart: ECharts | null = null
let progressChart: ECharts | null = null
let trendChart: ECharts | null = null
let performanceChart: ECharts | null = null

// Methods
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    planning: 'info',
    completed: '',
    archived: 'info',
    pending: 'info',
    in_progress: 'warning',
    review: '',
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

const getBudgetColor = (percentage: number) => {
  if (percentage <= 50) return '#67C23A'
  if (percentage <= 80) return '#E6A23C'
  return '#F56C6C'
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const isOverdue = (dueDate: string) => {
  if (!dueDate) return false
  const due = new Date(dueDate)
  const now = new Date()
  return due < now
}

// Event Handlers
const refreshData = () => {
  // TODO: Refresh data from API
  console.log('Refreshing data...')
}

const exportReport = () => {
  exportDialogVisible.value = true
}

const executeExport = () => {
  exporting.value = true
  // TODO: Export report
  setTimeout(() => {
    exporting.value = false
    exportDialogVisible.value = false
    ElMessage.success(t('common.exportSuccess'))
  }, 1000)
}

const handleReportCommand = (command: string) => {
  if (command === 'pdf' || command === 'excel') {
    exportForm.value.format = command
    exportDialogVisible.value = true
  } else if (command === 'print') {
    window.print()
  }
}

const applyFilters = () => {
  // TODO: Apply filters and reload data
  console.log('Applying filters:', { dateRange: dateRange.value, selectedProject: selectedProject.value, selectedUser: selectedUser.value, selectedStatus: selectedStatus.value })
}

const resetFilters = () => {
  dateRange.value = ['2026-04-01', '2026-04-05']
  selectedProject.value = null
  selectedUser.value = null
  selectedStatus.value = []
  // TODO: Reset data
}

// Chart initialization
const initCharts = () => {
  // Task Status Distribution Chart
  if (statusChartRef.value) {
    statusChart = echarts.init(statusChartRef.value)
    const statusOption = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        data: ['Pending', 'In Progress', 'Review', 'Completed', 'Blocked']
      },
      series: [
        {
          name: 'Task Status',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: 25, name: 'Pending', itemStyle: { color: '#909399' } },
            { value: 42, name: 'In Progress', itemStyle: { color: '#E6A23C' } },
            { value: 18, name: 'Review', itemStyle: { color: '#409EFF' } },
            { value: 65, name: 'Completed', itemStyle: { color: '#67C23A' } },
            { value: 6, name: 'Blocked', itemStyle: { color: '#F56C6C' } }
          ]
        }
      ]
    }
    statusChart.setOption(statusOption)
  }

  // Project Progress Chart
  if (progressChartRef.value) {
    progressChart = echarts.init(progressChartRef.value)
    const progressOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['Website Redesign', 'Mobile App', 'Marketing', 'Internal Tools', 'Customer Portal']
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: 'Progress',
          type: 'bar',
          data: [72, 84, 35, 92, 68],
          itemStyle: {
            color: function(params: any) {
              const colorList = ['#67C23A', '#E6A23C', '#F56C6C', '#409EFF', '#909399']
              return colorList[params.dataIndex % colorList.length]
            }
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}%'
          }
        }
      ]
    }
    progressChart.setOption(progressOption)
  }

  // Task Completion Trend Chart
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    const trendOption = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['Completed Tasks', 'Created Tasks']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Current Week']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: 'Completed Tasks',
          type: 'line',
          smooth: true,
          data: [12, 15, 18, 22, 25],
          itemStyle: {
            color: '#67C23A'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(103, 194, 58, 0.6)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
            ])
          }
        },
        {
          name: 'Created Tasks',
          type: 'line',
          smooth: true,
          data: [15, 18, 20, 25, 28],
          itemStyle: {
            color: '#409EFF'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.6)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ])
          }
        }
      ]
    }
    trendChart.setOption(trendOption)
  }

  // Team Performance Chart
  if (performanceChartRef.value) {
    performanceChart = echarts.init(performanceChartRef.value)
    const performanceOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['Completed', 'In Progress', 'Pending']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'value'
      },
      yAxis: {
        type: 'category',
        data: ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'David Brown']
      },
      series: [
        {
          name: 'Completed',
          type: 'bar',
          stack: 'total',
          label: {
            show: true
          },
          emphasis: {
            focus: 'series'
          },
          data: [20, 15, 8, 12, 10],
          itemStyle: {
            color: '#67C23A'
          }
        },
        {
          name: 'In Progress',
          type: 'bar',
          stack: 'total',
          label: {
            show: true
          },
          emphasis: {
            focus: 'series'
          },
          data: [5, 3, 4, 8, 6],
          itemStyle: {
            color: '#E6A23C'
          }
        },
        {
          name: 'Pending',
          type: 'bar',
          stack: 'total',
          label: {
            show: true
          },
          emphasis: {
            focus: 'series'
          },
          data: [0, 0, 0, 0, 2],
          itemStyle: {
            color: '#F56C6C'
          }
        }
      ]
    }
    performanceChart.setOption(performanceOption)
  }
}

// Responsive chart resize
const handleResize = () => {
  if (statusChart) statusChart.resize()
  if (progressChart) progressChart.resize()
  if (trendChart) trendChart.resize()
  if (performanceChart) performanceChart.resize()
}

// Lifecycle
onMounted(() => {
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
})

// Cleanup
onUnmounted(() => {
  if (statusChart) statusChart.dispose()
  if (progressChart) progressChart.dispose()
  if (trendChart) trendChart.dispose()
  if (performanceChart) performanceChart.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.statistics-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.statistics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.statistics-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.filter-card {
  margin-bottom: 20px;
}

.filter-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.date-range-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-weight: 500;
  color: var(--el-text-color-primary);
  min-width: 80px;
}

.additional-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stats-overview {
  margin: 20px 0;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon .el-icon {
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-info h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.stat-info p {
  margin: 4px 0 0 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 4px;
}

.stat-trend.positive {
  color: var(--el-color-success);
}

.stat-trend.negative {
  color: var(--el-color-error);
}

.charts-section {
  margin: 30px 0;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
}

.reports-section {
  margin-top: 30px;
}

.reports-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-table {
  margin-top: 20px;
}

.project-link {
  color: var(--el-color-primary);
  text-decoration: none;
}

.project-link:hover {
  text-decoration: underline;
}

.percentage {
  display: inline-block;
  margin-left: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  min-width: 30px;
}

.overdue-count {
  color: var(--el-color-error);
  font-weight: 500;
}

.overdue {
  color: var(--el-color-error);
}

.over {
  color: var(--el-color-error);
}

.under {
  color: var(--el-color-success);
}

.export-options {
  padding: 10px 0;
}

@media (max-width: 768px) {
  .statistics-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .date-range-selector {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .additional-filters {
    flex-direction: column;
  }
  
  .reports-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .reports-actions {
    width: 100%;
    overflow-x: auto;
  }
}
</style>