<template>
  <div class="my-tasks-container">
    <div class="page-header">
      <h1>📋 我的任务</h1>
    </div>
    <el-card class="table-card">
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="title" label="任务标题" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewTask(row.id)">{{ row.title }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="项目" width="150" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">{{ getPriorityLabel(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="110" align="center">
          <template #default="{ row }">
            <span :class="{ overdue: isOverdue(row.due_date) }">{{ formatDate(row.due_date) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="viewTask(row.id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && tasks.length === 0" description="暂无任务" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()
const loading = ref(false)
const tasks = ref<any[]>([])

const getStatusType = (status: string) => ({
  pending: 'info', in_progress: 'warning', completed: 'success', blocked: 'danger'
}[status] || '')
const getStatusLabel = (status: string) => ({
  pending: '待处理', in_progress: '进行中', completed: '已完成', blocked: '已阻塞'
}[status] || status)
const getPriorityType = (p: string) => ({
  low: 'info', medium: '', high: 'warning', urgent: 'danger'
}[p] || '')
const getPriorityLabel = (p: string) => ({
  low: '低', medium: '中', high: '高', urgent: '紧急'
}[p] || p)
const formatDate = (d: string) => d ? new Date(d).toLocaleDateString('zh-CN') : '-'
const isOverdue = (d: string) => d && new Date(d) < new Date()

const loadTasks = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await api.get('/tasks/', {
      params: { assignee_id: 1 }
    })
    tasks.value = Array.isArray(res) ? res : (res.data || res.items || [])
  } catch (e) {
    console.error('加载我的任务失败:', e)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const viewTask = (id: number) => {
  router.push(`/tasks/${id}`)
}

onMounted(() => loadTasks())
</script>

<style scoped>
.my-tasks-container { padding: 20px; }
.page-header { display: flex; align-items: center; margin-bottom: 20px; }
.page-header h1 { margin: 0; font-size: 22px; color: #303160; }
.table-card { margin-bottom: 20px; }
.overdue { color: #F56C6C; font-weight: bold; }
</style>
