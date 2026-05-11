<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()

// 状态
const loading = ref(false)
const issues = ref<any[]>([])
const stats = ref<any>(null)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

// 筛选条件
const searchText = ref('')
const filterStatus = ref('')
const filterPriority = ref('')
const filterType = ref('')
const filterProject = ref<number | null>(null)

// 项目列表
const projects = ref<any[]>([])

// 弹窗
const showCreateDialog = ref(false)
const creating = ref(false)
const newIssue = ref({
  title: '',
  description: '',
  issue_type: 'bug',
  priority: 'medium',
  project_id: null as number | null,
  labels: ''
})

// Issue类型选项
const issueTypes = [
  { label: 'Bug', value: 'bug' },
  { label: '功能请求', value: 'feature' },
  { label: '改进', value: 'improvement' },
  { label: '问题', value: 'question' }
]

// 优先级选项
const priorities = [
  { label: '低', value: 'low', color: '#909399' },
  { label: '中', value: 'medium', color: '#E6A23C' },
  { label: '高', value: 'high', color: '#F56C6C' },
  { label: '紧急', value: 'critical', color: '#DC2626' }
]

// 状态选项
const statuses = [
  { label: '开放', value: 'open', color: '#409EFF' },
  { label: '处理中', value: 'in_progress', color: '#E6A23C' },
  { label: '已解决', value: 'resolved', color: '#67C23A' },
  { label: '已关闭', value: 'closed', color: '#909399' },
  { label: '重新打开', value: 'reopened', color: '#F56C6C' }
]

// 获取颜色
const getPriorityColor = (priority: string) => {
  const p = priorities.find(p => p.value === priority)
  return p?.color || '#909399'
}

const getStatusColor = (status: string) => {
  const s = statuses.find(s => s.value === status)
  return s?.color || '#909399'
}

const getStatusLabel = (status: string) => {
  const s = statuses.find(s => s.value === status)
  return s?.label || status
}

const getTypeLabel = (type: string) => {
  const t = issueTypes.find(t => t.value === type)
  return t?.label || type
}

// 加载数据
const loadIssues = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (searchText.value) params.search = searchText.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPriority.value) params.priority = filterPriority.value
    if (filterType.value) params.issue_type = filterType.value
    if (filterProject.value) params.project_id = filterProject.value
    
    const res = await api.get('/issues/', { params })
    const data = res.data || res
    issues.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.warn('加载Issue失败', error)
    issues.value = []
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await api.get('/issues/stats', { 
      params: filterProject.value ? { project_id: filterProject.value } : {} 
    })
    stats.value = res.data || res
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const loadProjects = async () => {
  try {
    const res = await api.get('/projects/', { params: { page_size: 100 } })
    const data = res.data || res
    projects.value = data.items || data || []
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

// 创建Issue
const createIssue = async () => {
  if (!newIssue.value.title || !newIssue.value.project_id) {
    ElMessage.warning('请填写标题和选择项目')
    return
  }
  
  creating.value = true
  try {
    await api.post('/issues/', newIssue.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    newIssue.value = { title: '', description: '', issue_type: 'bug', priority: 'medium', project_id: null, labels: '' }
    loadIssues()
    loadStats()
  } catch (error) {
    ElMessage.error(error?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

// 查看详情
const viewIssue = (issueId: number) => {
  router.push(`/issues/${issueId}`)
}

// 更新状态
const updateStatus = async (issue: any, newStatus: string) => {
  try {
    await api.patch(`/issues/${issue.id}/status`, { status: newStatus })
    ElMessage.success('状态更新成功')
    loadIssues()
    loadStats()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

// 搜索
const handleSearch = () => {
  page.value = 1
  loadIssues()
}

// 重置筛选
const resetFilters = () => {
  searchText.value = ''
  filterStatus.value = ''
  filterPriority.value = ''
  filterType.value = ''
  filterProject.value = null
  page.value = 1
  loadIssues()
}

// 分页变化
const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadIssues()
}

onMounted(() => {
  loadIssues()
  loadStats()
  loadProjects()
})
</script>

<template>
  <div class="issues-view">
    <!-- 头部统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats?.total || 0 }}</div>
          <div class="stat-label">总计</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color: #409EFF">{{ stats?.open || 0 }}</div>
          <div class="stat-label">开放</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color: #E6A23C">{{ stats?.in_progress || 0 }}</div>
          <div class="stat-label">处理中</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color: #67C23A">{{ stats?.resolved || 0 }}</div>
          <div class="stat-label">已解决</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color: #909399">{{ stats?.closed || 0 }}</div>
          <div class="stat-label">已关闭</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-button type="primary" size="large" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建Issue
        </el-button>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="4">
          <el-input 
            v-model="searchText" 
            placeholder="搜索标题/描述" 
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="3">
          <el-select v-model="filterProject" placeholder="选择项目" clearable @change="handleSearch">
            <el-option 
              v-for="p in projects" 
              :key="p.id" 
              :label="p.name" 
              :value="p.id" 
            />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-select v-model="filterStatus" placeholder="状态" clearable @change="handleSearch">
            <el-option v-for="s in statuses" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-select v-model="filterPriority" placeholder="优先级" clearable @change="handleSearch">
            <el-option v-for="p in priorities" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <el-select v-model="filterType" placeholder="类型" clearable @change="handleSearch">
            <el-option v-for="t in issueTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Issue列表 -->
    <el-card class="list-card">
      <el-table :data="issues" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.issue_type === 'bug' ? 'danger' : row.issue_type === 'feature' ? 'success' : 'warning'">
              {{ getTypeLabel(row.issue_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewIssue(row.id)">{{ row.title }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :color="getStatusColor(row.status)" effect="dark">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :color="getPriorityColor(row.priority)" effect="dark" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="project_id" label="项目ID" width="80" />
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewIssue(row.id)">查看</el-button>
            <el-dropdown @command="(cmd: string) => updateStatus(row, cmd)">
              <el-button type="primary" link size="small">
                状态 <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="s in statuses" :key="s.value" :command="s.value">
                    {{ s.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 创建Issue弹窗 -->
    <el-dialog v-model="showCreateDialog" title="新建Issue" width="600px">
      <el-form :model="newIssue" label-width="80px">
        <el-form-item label="项目" required>
          <el-select v-model="newIssue.project_id" placeholder="选择项目" style="width: 100%">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题" required>
          <el-input v-model="newIssue.title" placeholder="输入Issue标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newIssue.description" type="textarea" :rows="4" placeholder="详细描述问题" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="类型">
              <el-select v-model="newIssue.issue_type" style="width: 100%">
                <el-option v-for="t in issueTypes" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="newIssue.priority" style="width: 100%">
                <el-option v-for="p in priorities" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标签">
          <el-input v-model="newIssue.labels" placeholder="用逗号分隔多个标签" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="createIssue">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.issues-view {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.filter-card {
  margin-bottom: 20px;
}

.list-card {
  min-height: 400px;
}

.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>