<template>
  <div class="reports-view">
    <el-tabs v-model="activeTab">
      <!-- 仪表盘概览 -->
      <el-tab-pane label="📊 数据概览" name="summary">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="总任务数" :value="summary.tasks.total">
                <template #prefix>📋</template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="已完成" :value="summary.tasks.completed">
                <template #prefix>✅</template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="进行中" :value="summary.tasks.in_progress">
                <template #prefix>🔄</template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="完成率" :value="summary.tasks.completion_rate" suffix="%">
                <template #prefix>📈</template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="8">
            <el-card>
              <h4>项目统计</h4>
              <p>总项目: {{ summary.projects.total }}</p>
              <p>进行中: {{ summary.projects.active }}</p>
              <p>已完成: {{ summary.projects.completed }}</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <h4>Issue统计</h4>
              <p>总Issue: {{ summary.issues.total }}</p>
              <p>开放: {{ summary.issues.open }}</p>
              <p>已解决: {{ summary.issues.resolved }}</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <h4>团队负载</h4>
              <p>成员任务分配情况</p>
              <el-button type="primary" size="small" @click="activeTab = 'team'">
                查看详情
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 趋势分析 -->
      <el-tab-pane label="📈 趋势分析" name="trends">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务与Issue趋势 (最近30天)</span>
              <el-select v-model="trendDays" @change="fetchTrends">
                <el-option label="7天" :value="7" />
                <el-option label="14天" :value="14" />
                <el-option label="30天" :value="30" />
                <el-option label="90天" :value="90" />
              </el-select>
            </div>
          </template>
          <div v-if="trendChartData" class="chart-container">
            <div class="chart-placeholder">
              <p>趋势数据:</p>
              <ul>
                <li v-for="day in trendChartData.slice(-7)" :key="day.date">
                  {{ day.date }}: 创建 {{ day.tasks_created }}, 完成 {{ day.tasks_completed }}, Issue {{ day.issues_created }}
                </li>
              </ul>
            </div>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 团队绩效 -->
      <el-tab-pane label="👥 团队绩效" name="team">
        <el-card>
          <template #header>
            <span>团队成员绩效</span>
          </template>
          <el-table :data="teamPerformance" v-loading="loading">
            <el-table-column prop="username" label="成员" />
            <el-table-column prop="total_tasks" label="总任务" />
            <el-table-column prop="completed_tasks" label="已完成" />
            <el-table-column prop="completion_rate" label="完成率" suffix="%">
              <template #default="{ row }">
                <el-progress :percentage="row.completion_rate" :color="getProgressColor(row.completion_rate)" />
              </template>
            </el-table-column>
            <el-table-column prop="avg_hours_per_task" label="平均耗时" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 项目进度 -->
      <el-tab-pane label="📁 项目进度" name="projects">
        <el-card>
          <template #header>
            <span>所有项目进度</span>
          </template>
          <el-table :data="projectProgress" v-loading="loading">
            <el-table-column prop="name" label="项目名称" />
            <el-table-column prop="code" label="项目代码" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_tasks" label="总任务" width="100" />
            <el-table-column prop="completed_tasks" label="已完成" width="100" />
            <el-table-column label="进度" width="200">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :color="getProgressColor(row.progress)" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 逾期任务 -->
      <el-tab-pane label="⚠️ 逾期任务" name="overdue">
        <el-card>
          <template #header>
            <span>逾期任务列表</span>
          </template>
          <el-table :data="overdueTasks" v-loading="loading">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="title" label="任务标题" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="截止日期" width="120">
              <template #default="{ row }">
                <span style="color: #F56C6C">{{ formatDate(row.due_date) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="assignee_id" label="负责人" width="80" />
          </el-table>
          <el-empty v-if="!loading && overdueTasks.length === 0" description="没有逾期任务" />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const API_BASE = '/reports'

const activeTab = ref('summary')
const loading = ref(false)
const trendDays = ref(30)

const summary = ref({
  tasks: { total: 0, completed: 0, in_progress: 0, completion_rate: 0 },
  projects: { total: 0, active: 0, completed: 0 },
  issues: { total: 0, open: 0, resolved: 0 }
})

const trendChartData = ref(null)
const teamPerformance = ref([])
const projectProgress = ref([])
const overdueTasks = ref([])

const fetchSummary = async () => {
  try {
    const response = await api.get(`${API_BASE}/overview`)
    const data = response.data || response
    summary.value = data.data || data
  } catch (error) {
    console.error('获取摘要失败', error)
  }
}

const fetchTrends = async () => {
  try {
    const response = await api.get(`${API_BASE}/trend`, {
      params: { days: trendDays.value }
    })
    const data = response.data || response
    trendChartData.value = data.trends || data.data?.trends || null
  } catch (error) {
    console.error('获取趋势失败', error)
  }
}

const fetchTeamPerformance = async () => {
  loading.value = true
  try {
    const response = await api.get(`${API_BASE}/team`)
    const data = response.data || response
    teamPerformance.value = data.team || data.data?.team || []
  } catch (error) {
    console.error('获取团队绩效失败', error)
  } finally {
    loading.value = false
  }
}

const fetchProjectProgress = async () => {
  loading.value = true
  try {
    const response = await api.get(`${API_BASE}/overview`)
    const data = response.data || response
    // 使用 overview 数据作为项目进度
    projectProgress.value = data.projects || data.data?.projects || []
  } catch (error) {
    console.error('获取项目进度失败', error)
  } finally {
    loading.value = false
  }
}

const fetchOverdueTasks = async () => {
  loading.value = true
  try {
    const response = await api.get('/tasks/', {
      params: { status: 'overdue', page_size: 50 }
    })
    const data = response.data || response
    overdueTasks.value = data.items || []
  } catch (error) {
    console.error('获取逾期任务失败', error)
    overdueTasks.value = []
  } finally {
    loading.value = false
  }
}

const getProgressColor = (percentage) => {
  if (percentage >= 80) return '#67C23A'
  if (percentage >= 50) return '#E6A23C'
  return '#F56C6C'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchSummary()
  fetchTrends()
  fetchTeamPerformance()
  fetchProjectProgress()
  fetchOverdueTasks()
})
</script>

<style scoped>
.reports-view {
  padding: 20px;
}

.stat-card {
  text-align: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  min-height: 300px;
}

.chart-placeholder {
  padding: 20px;
}

.chart-placeholder ul {
  list-style: none;
  padding: 0;
}

.chart-placeholder li {
  padding: 8px;
  border-bottom: 1px solid #eee;
}
</style>