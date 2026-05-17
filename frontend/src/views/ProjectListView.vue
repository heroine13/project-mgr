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
            <el-link type="primary" @click="showProjectDetail(row)">{{ row.name }}</el-link>
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
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="editProject(row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              :disabled="row.status !== 'planning'"
              @click="deleteProject(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && projects.length === 0" description="暂无项目">
        <el-button type="primary" @click="goToNewProject">创建第一个项目</el-button>
      </el-empty>
    </el-card>

    <!-- 项目详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="项目详情" width="700px">
      <el-descriptions v-if="currentProject" :column="2" border>
        <el-descriptions-item label="项目编号">{{ currentProject.code }}</el-descriptions-item>
        <el-descriptions-item label="项目名称">{{ currentProject.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentProject.status)">
            {{ getStatusLabel(currentProject.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="预算">¥{{ currentProject.budget || 0 }}</el-descriptions-item>
        <el-descriptions-item label="开始日期">{{ currentProject.start_date ? new Date(currentProject.start_date).toLocaleDateString('zh-CN') : '-' }}</el-descriptions-item>
        <el-descriptions-item label="结束日期">{{ currentProject.end_date ? new Date(currentProject.end_date).toLocaleDateString('zh-CN') : '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentProject.created_at }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentProject.description || '暂无描述' }}</el-descriptions-item>
        <el-descriptions-item label="任务统计">
          总计 {{ currentProject.task_count || 0 }} · 完成 {{ currentProject.completed_tasks || 0 }} · 进行中 {{ currentProject.in_progress_tasks || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="问题统计">
          总计 {{ currentProject.issue_count || 0 }} · 开放 {{ currentProject.open_issues || 0 }} · 已解决 {{ currentProject.resolved_issues || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="完成率">
          {{ currentProject.completion_rate || 0 }}%
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 编辑项目弹窗 -->
    <el-dialog v-model="editDialogVisible" :title="editDialogTitle" width="600px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="项目编号">
          <el-input v-model="editForm.code" />
        </el-form-item>
        <el-form-item label="项目名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="进行中" value="active" />
            <el-option label="计划中" value="planning" />
            <el-option label="已完成" value="completed" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="editForm.start_date" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="editForm.end_date" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="预算">
          <el-input-number v-model="editForm.budget" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProject">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()
const loading = ref(false)
const projects = ref<any[]>([])
const searchKeyword = ref('')
const statusFilter = ref('')

// 详情弹窗
const detailDialogVisible = ref(false)
const currentProject = ref<any>(null)

// 编辑弹窗
const editDialogVisible = ref(false)
const editDialogTitle = ref('')
const editForm = ref<any>({
  id: null,
  code: '',
  name: '',
  status: 'active',
  budget: 0,
  description: '',
  start_date: '',
  end_date: ''
})

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
    projects.value = res.projects || []
  } catch (error) {
    console.error('加载项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

const goToNewProject = () => {
  router.push('/projects/new')
}

// 显示项目详情
const showProjectDetail = (project: any) => {
  currentProject.value = project
  detailDialogVisible.value = true
}

// 编辑项目
const editProject = (project: any) => {
  editDialogTitle.value = '编辑项目'
  editForm.value = {
    id: project.id,
    code: project.code,
    name: project.name,
    status: project.status,
    budget: project.budget || 0,
    description: project.description || '',
    start_date: project.start_date ? new Date(project.start_date).toISOString().split('T')[0] : '',
    end_date: project.end_date ? new Date(project.end_date).toISOString().split('T')[0] : ''
  }
  editDialogVisible.value = true
}

// 保存项目
const saveProject = async () => {
  try {
    const data = { ...editForm.value }
    // 转换日期格式
    if (data.start_date) {
      data.start_date = new Date(data.start_date).toISOString()
    }
    if (data.end_date) {
      data.end_date = new Date(data.end_date).toISOString()
    }
    await api.put(`/projects/${data.id}`, data)
    ElMessage.success('项目更新成功')
    editDialogVisible.value = false
    loadProjects()
  } catch (error) {
    console.error('更新项目失败:', error)
    ElMessage.error('更新项目失败')
  }
}

// 删除项目
const deleteProject = async (project: any) => {
  if (project.status !== 'planning') {
    ElMessage.warning('只有计划中的项目才能删除')
    return
  }

  try {
    await ElMessageBox.confirm(`确定要删除项目"${project.name}"吗？此操作不可恢复。`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/projects/${project.id}`)
    ElMessage.success('项目删除成功')
    loadProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除项目失败:', error)
      ElMessage.error('删除项目失败')
    }
  }
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
  color: #90999;
  margin-top: 2px;
}
</style>