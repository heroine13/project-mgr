<template>
  <div class="project-list-container">
    <div class="page-header">
      <h1>项目列表</h1>
      <el-button type="primary" @click="goToNewProject">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </div>

    <!-- 搜索筛选 -->
    <el-card class="filter-card">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索项目名称/编号"
            clearable
            @clear="loadProjects"
            @keyup.enter="loadProjects"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button @click="loadProjects">搜索</el-button>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="statusFilter" placeholder="状态" clearable @change="loadProjects">
            <el-option label="进行中" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
            <el-option label="计划中" value="planning" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button @click="loadProjects" type="primary">刷新</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 项目表格 -->
    <el-card class="table-card">
      <el-table :data="projects" v-loading="loading" stripe>
        <el-table-column prop="code" label="编号" width="100" />
        <el-table-column prop="name" label="项目名称" min-width="180">
          <template #default="{ row }">
            <el-link type="primary" @click="goToDetail(row.id)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="任务" width="120" align="center">
          <template #default="{ row }">
            <div>总计 {{ row.task_count || 0 }}</div>
            <div class="small-text">
              完成 {{ row.completed_tasks || 0 }} · 进行中 {{ row.in_progress_tasks || 0 }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="问题" width="100" align="center">
          <template #default="{ row }">
            <el-link type="danger" @click="goToIssues(row.id)">
              {{ row.issue_count || 0 }} 个问题
            </el-link>
          </template>
        </el-table-column>
        <el-table-column label="完成率" width="140" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.completion_rate || 0"
              :stroke-width="14"
              :color="getProgressColor(row.completion_rate)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="budget" label="预算" width="100" align="right">
          <template #default="{ row }">
            {{ row.budget ? '¥' + row.budget.toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
      </el-table>

      <el-empty v-if="!loading && projects.length === 0" description="暂无项目">
        <el-button type="primary" @click="goToNewProject">创建第一个项目</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()
const loading = ref(false)
const projects = ref<any[]>([])
const searchKeyword = ref('')
const statusFilter = ref('')

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

const getProgressColor = (rate: number) => {
  if (rate >= 80) return '#67C23A'
  if (rate >= 50) return '#409EFF'
  if (rate > 0) return '#E6A23C'
  return '#F56C6C'
}

const loadProjects = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const res = await api.get('/projects/overview/summary', { params })
    projects.value = res.data.projects || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

const goToNewProject = () => {
  router.push('/projects/new')
}

const goToDetail = (id: number) => {
  router.push(`/projects/${id}`)
}

const goToIssues = (projectId: number) => {
  router.push(`/issues?project_id=${projectId}`)
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.project-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 22px;
  color: #303160;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.small-text {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
