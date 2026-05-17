<template>
  <div class="archived-projects-container">
    <div class="page-header">
      <h1>📦 已归档项目</h1>
    </div>
    <el-card class="table-card">
      <el-table :data="projects" v-loading="loading" stripe>
        <el-table-column prop="code" label="编号" width="100" />
        <el-table-column prop="name" label="项目名称" min-width="180">
          <template #default="{ row }">
            <el-link type="primary" @click="viewProject(row.id)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="任务" width="120" align="center">
          <template #default="{ row }">
            总计 {{ row.task_count || 0 }} · 完成 {{ row.completed_tasks || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="完成率" width="140" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.completion_rate || 0" :stroke-width="14" :color="getProgressColor(row.completion_rate)" />
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="110" align="center">
          <template #default="{ row }">
            {{ row.start_date ? new Date(row.start_date).toLocaleDateString('zh-CN') : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="end_date" label="结束日期" width="110" align="center">
          <template #default="{ row }">
            {{ row.end_date ? new Date(row.end_date).toLocaleDateString('zh-CN') : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="viewProject(row.id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && projects.length === 0" description="暂无已归档项目" />
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

const getProgressColor = (rate: number) => {
  if (rate >= 80) return '#67C23A'
  if (rate >= 50) return '#409EFF'
  if (rate > 0) return '#E6A23C'
  return '#F56C6C'
}

const loadProjects = async () => {
  loading.value = true
  try {
    const res = await api.get('/projects/overview/summary', { params: { status: 'archived' } })
    projects.value = (res.projects || res.data?.projects || []) as any[]
  } catch (e) {
    console.error('加载已归档项目失败:', e)
    projects.value = []
  } finally {
    loading.value = false
  }
}

const viewProject = (id: number) => router.push(`/projects/${id}`)

onMounted(() => loadProjects())
</script>

<style scoped>
.archived-projects-container { padding: 20px; }
.page-header { display: flex; align-items: center; margin-bottom: 20px; }
.page-header h1 { margin: 0; font-size: 22px; color: #303160; }
.table-card { margin-bottom: 20px; }
</style>
