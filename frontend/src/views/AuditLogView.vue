<template>
  <div class="audit-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📊 审计日志</span>
          <div class="header-actions">
            <el-button type="primary" @click="fetchLogs">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="success" @click="exportLogs('json')">
              导出JSON
            </el-button>
            <el-button type="info" @click="exportLogs('csv')">
              导出CSV
            </el-button>
          </div>
        </div>
      </template>

      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-statistic title="总记录数" :value="stats.total" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="今日" :value="stats.today" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="本周" :value="stats.this_week" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="本月" :value="stats.this_month" />
        </el-col>
      </el-row>

      <!-- 筛选条件 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="操作类型">
          <el-select v-model="filters.action" placeholder="全部" clearable>
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="filters.resource_type" placeholder="全部" clearable>
            <el-option label="任务" value="task" />
            <el-option label="项目" value="project" />
            <el-option label="用户" value="user" />
            <el-option label="Issue" value="issue" />
            <el-option label="认证" value="auth" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchLogs">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 日志表格 -->
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="action" label="操作" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)">
              {{ getActionText(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="100">
          <template #default="{ row }">
            <el-tag type="info">{{ row.resource_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_id" label="资源ID" width="80" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="ip_address" label="IP地址" width="130" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.limit"
          :total="pagination.total"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchLogs"
          @current-change="fetchLogs"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetail" title="日志详情" width="600px">
      <div v-if="selectedLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedLog.id }}</el-descriptions-item>
          <el-descriptions-item label="用户">{{ selectedLog.username }}</el-descriptions-item>
          <el-descriptions-item label="操作">{{ getActionText(selectedLog.action) }}</el-descriptions-item>
          <el-descriptions-item label="资源类型">{{ selectedLog.resource_type }}</el-descriptions-item>
          <el-descriptions-item label="资源ID">{{ selectedLog.resource_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedLog.status === 'success' ? 'success' : 'danger'">
              {{ selectedLog.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="IP地址">{{ selectedLog.ip_address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ formatDate(selectedLog.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedLog.description || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="selectedLog.old_value || selectedLog.new_value" class="value-comparison">
          <h4>变更对比</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <h5>修改前</h5>
              <pre>{{ JSON.stringify(selectedLog.old_value, null, 2) }}</pre>
            </el-col>
            <el-col :span="12">
              <h5>修改后</h5>
              <pre>{{ JSON.stringify(selectedLog.new_value, null, 2) }}</pre>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '@/utils/api'

const API_BASE = '/audit'

const loading = ref(false)
const logs = ref([])
const stats = ref({ total: 0, today: 0, this_week: 0, this_month: 0 })
const showDetail = ref(false)
const selectedLog = ref(null)

const filters = ref({
  action: '',
  resource_type: '',
  status: ''
})

const dateRange = ref(null)

const pagination = ref({
  page: 1,
  limit: 50,
  total: 0
})

const getActionType = (action) => {
  const map = {
    login: 'success',
    logout: 'info',
    create: 'primary',
    update: 'warning',
    delete: 'danger'
  }
  return map[action] || 'info'
}

const getActionText = (action) => {
  const map = {
    login: '登录',
    logout: '登出',
    create: '创建',
    update: '更新',
    delete: '删除'
  }
  return map[action] || action
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.value.page - 1) * pagination.value.limit,
      limit: pagination.value.limit
    }
    
    if (filters.value.action) params.action = filters.value.action
    if (filters.value.resource_type) params.resource_type = filters.value.resource_type
    if (filters.value.status) params.status = filters.value.status
    if (dateRange.value && dateRange.value[0]) {
      params.start_date = dateRange.value[0].toISOString()
      params.end_date = dateRange.value[1].toISOString()
    }
    
    const response = await api.get(`${API_BASE}/logs`, { params })
    logs.value = response.data
    
    // Fetch stats
    const statsResponse = await api.get(`${API_BASE}/stats`)
    stats.value = statsResponse.data
    
    pagination.value.total = stats.value.total
  } catch (error) {
    ElMessage.error('获取审计日志失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = { action: '', resource_type: '', status: '' }
  dateRange.value = null
  pagination.value.page = 1
  fetchLogs()
}

const exportLogs = async (format) => {
  try {
    const params = { format }
    if (dateRange.value && dateRange.value[0]) {
      params.start_date = dateRange.value[0].toISOString()
      params.end_date = dateRange.value[1].toISOString()
    }
    
    const response = await api.get(`${API_BASE}/export`, { params })
    
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      downloadFile(blob, `audit_logs_${Date.now()}.json`)
    } else {
      const blob = new Blob([response.data], { type: 'text/csv' })
      downloadFile(blob, `audit_logs_${Date.now()}.csv`)
    }
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.audit-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-row {
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.filter-form {
  margin-bottom: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.log-detail pre {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow: auto;
}

.value-comparison {
  margin-top: 20px;
}

.value-comparison h4 {
  margin-bottom: 10px;
}

.value-comparison h5 {
  margin-bottom: 5px;
  color: #606266;
}
</style>