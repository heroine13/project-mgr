<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

// 状态
const activeTab = ref('resources')
const loading = ref(false)

// 资源列表
const resources = ref<any[]>([])
const resourceTotal = ref(0)

// 分配列表
const allocations = ref<any[]>([])
const allocationTotal = ref(0)

// 成本记录
const costs = ref<any[]>([])
const costTotal = ref(0)

// 项目列表（用于筛选）
const projects = ref<any[]>([])

// 分页
const page = ref(1)
const pageSize = ref(20)

// 弹窗
const showResourceDialog = ref(false)
const showAllocationDialog = ref(false)
const showCostDialog = ref(false)
const editing = ref(false)

// 表单数据
const resourceForm = ref({
  name: '',
  resource_type: 'human',
  description: '',
  user_id: null as number | null,
  unit_cost: 0,
  currency: 'CNY',
  is_available: true,
  max_capacity: 0
})

const allocationForm = ref({
  resource_id: null as number | null,
  project_id: null as number | null,
  task_id: null as number | null,
  allocation_type: 'percentage',
  allocated_value: 0,
  start_date: '',
  end_date: '',
  budgeted_cost: 0,
  status: 'pending'
})

const costForm = ref({
  project_id: null as number | null,
  task_id: null as number | null,
  category: 'labor',
  description: '',
  amount: 0,
  currency: 'CNY',
  cost_date: '',
  is_approved: false
})

// 选项
const resourceTypes = [
  { label: '人力', value: 'human' },
  { label: '物料', value: 'material' },
  { label: '设备', value: 'equipment' },
  { label: '其他', value: 'other' }
]

const categories = [
  { label: '人工', value: 'labor' },
  { label: '物料', value: 'material' },
  { label: '设备', value: 'equipment' },
  { label: '其他', value: 'other' }
]

const allocationStatuses = [
  { label: '待处理', value: 'pending' },
  { label: '进行中', value: 'active' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
]

// 加载数据
const loadResources = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    const res = await api.get('/resources/resources', { params })
    const data = res.data || res
    [a-z_]+.value = data.items
    resourceTotal.value = (res.data || res).total || 0
  } catch (error) {
    console.warn('加载资源失败', error)
    resources.value = []
  } finally {
    loading.value = false
  }
}

const loadAllocations = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    const res = await api.get('/resources/allocations', { params })
    const data = res.data || res
    [a-z_]+.value = data.items
    allocationTotal.value = (res.data || res).total || 0
  } catch (error) {
    console.warn('加载分配记录失败', error)
    allocations.value = []
  } finally {
    loading.value = false
  }
}

const loadCosts = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    const res = await api.get('/resources/costs', { params })
    const data = res.data || res
    [a-z_]+.value = data.items
    costTotal.value = (res.data || res).total || 0
  } catch (error) {
    console.warn('加载成本记录失败', error)
    costRecords.value = []
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  try {
    const res = await api.get('/projects/', { params: { page_size: 100 } })
    const data = res.data || res
    [a-z_]+.value = data.items
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

// 创建资源
const createResource = async () => {
  if (!resourceForm.value.name) {
    ElMessage.warning('请填写资源名称')
    return
  }
  try {
    await api.post('/resources/resources', resourceForm.value)
    ElMessage.success('创建成功')
    showResourceDialog.value = false
    resetResourceForm()
    loadResources()
  } catch (error: any) {
    ElMessage.error(error?.detail || '创建失败')
  }
}

// 创建分配
const createAllocation = async () => {
  if (!allocationForm.value.resource_id || !allocationForm.value.project_id) {
    ElMessage.warning('请选择资源和项目')
    return
  }
  try {
    const data = { ...allocationForm.value }
    if (data.start_date) data.start_date = new Date(data.start_date)
    if (data.end_date) data.end_date = new Date(data.end_date)
    await api.post('/resources/allocations', data)
    ElMessage.success('创建成功')
    showAllocationDialog.value = false
    resetAllocationForm()
    loadAllocations()
  } catch (error: any) {
    ElMessage.error(error?.detail || '创建失败')
  }
}

// 创建成本记录
const createCost = async () => {
  if (!costForm.value.project_id || !costForm.value.amount) {
    ElMessage.warning('请填写必要信息')
    return
  }
  try {
    const data = { ...costForm.value }
    if (data.cost_date) data.cost_date = new Date(data.cost_date)
    await api.post('/resources/costs', data)
    ElMessage.success('创建成功')
    showCostDialog.value = false
    resetCostForm()
    loadCosts()
  } catch (error: any) {
    ElMessage.error(error?.detail || '创建失败')
  }
}

// 重置表单
const resetResourceForm = () => {
  resourceForm.value = {
    name: '', resource_type: 'human', description: '',
    user_id: null, unit_cost: 0, currency: 'CNY', is_available: true, max_capacity: 0
  }
}

const resetAllocationForm = () => {
  allocationForm.value = {
    resource_id: null, project_id: null, task_id: null,
    allocation_type: 'percentage', allocated_value: 0,
    start_date: '', end_date: '', budgeted_cost: 0, status: 'pending'
  }
}

const resetCostForm = () => {
  costForm.value = {
    project_id: null, task_id: null, category: 'labor',
    description: '', amount: 0, currency: 'CNY', cost_date: '', is_approved: false
  }
}

// 标签切换
const handleTabChange = (tab: string) => {
  page.value = 1
  if (tab === 'resources') loadResources()
  else if (tab === 'allocations') loadAllocations()
  else if (tab === 'costs') loadCosts()
}

// 格式化
const formatDate = (date: string) => date ? new Date(date).toLocaleDateString() : '-'
const formatMoney = (amount: number, currency: string = 'CNY') => {
  return new Intl.NumberFormat('zh-CN', { style: 'currency', currency }).format(amount)
}

onMounted(() => {
  loadResources()
  loadProjects()
})
</script>

<template>
  <div class="resource-view">
    <h2>资源与成本管理</h2>
    
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <!-- 资源管理 -->
      <el-tab-pane label="资源管理" name="resources">
        <div class="toolbar">
          <el-button type="primary" @click="showResourceDialog = true">
            <el-icon><Plus /></el-icon> 添加资源
          </el-button>
        </div>
        
        <el-table :data="resources" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="资源名称" />
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag>{{ row.resource_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
          <el-table-column label="单位成本" width="120">
            <template #default="{ row }">
              {{ formatMoney(row.unit_cost, row.currency) }}
            </template>
          </el-table-column>
          <el-table-column label="可用" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_available ? 'success' : 'info'">
                {{ row.is_available ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="120">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 资源分配 -->
      <el-tab-pane label="资源分配" name="allocations">
        <div class="toolbar">
          <el-button type="primary" @click="showAllocationDialog = true">
            <el-icon><Plus /></el-icon> 添加分配
          </el-button>
        </div>
        
        <el-table :data="allocations" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="resource_id" label="资源ID" width="80" />
          <el-table-column prop="project_id" label="项目ID" width="80" />
          <el-table-column label="分配类型" width="100">
            <template #default="{ row }">
              {{ row.allocation_type === 'percentage' ? '百分比' : row.allocation_type === 'hours' ? '工时' : '单位' }}
            </template>
          </el-table-column>
          <el-table-column prop="allocated_value" label="分配值" width="100" />
          <el-table-column label="预算成本" width="120">
            <template #default="{ row }">
              {{ formatMoney(row.budgeted_cost) }}
            </template>
          </el-table-column>
          <el-table-column label="实际成本" width="120">
            <template #default="{ row }">
              {{ formatMoney(row.actual_cost) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : row.status === 'completed' ? 'info' : 'warning'">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 成本记录 -->
      <el-tab-pane label="成本记录" name="costs">
        <div class="toolbar">
          <el-button type="primary" @click="showCostDialog = true">
            <el-icon><Plus /></el-icon> 添加成本
          </el-button>
        </div>
        
        <el-table :data="costs" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="project_id" label="项目ID" width="80" />
          <el-table-column label="类别" width="100">
            <template #default="{ row }">
              <el-tag>{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
          <el-table-column label="金额" width="120">
            <template #default="{ row }">
              {{ formatMoney(row.amount, row.currency) }}
            </template>
          </el-table-column>
          <el-table-column label="日期" width="120">
            <template #default="{ row }">
              {{ formatDate(row.cost_date) }}
            </template>
          </el-table-column>
          <el-table-column label="审批" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_approved ? 'success' : 'warning'">
                {{ row.is_approved ? '已审批' : '待审批' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加资源弹窗 -->
    <el-dialog v-model="showResourceDialog" title="添加资源" width="500px">
      <el-form :model="resourceForm" label-width="100px">
        <el-form-item label="资源名称" required>
          <el-input v-model="resourceForm.name" />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="resourceForm.resource_type" style="width: 100%">
            <el-option v-for="t in resourceTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="resourceForm.description" type="textarea" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="单位成本">
              <el-input-number v-model="resourceForm.unit_cost" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大产能">
              <el-input-number v-model="resourceForm.max_capacity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="是否可用">
          <el-switch v-model="resourceForm.is_available" :active-value="true" :inactive-value="false" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showResourceDialog = false">取消</el-button>
        <el-button type="primary" @click="createResource">创建</el-button>
      </template>
    </el-dialog>

    <!-- 添加分配弹窗 -->
    <el-dialog v-model="showAllocationDialog" title="添加资源分配" width="500px">
      <el-form :model="allocationForm" label-width="100px">
        <el-form-item label="选择资源" required>
          <el-select v-model="allocationForm.resource_id" placeholder="选择资源" style="width: 100%">
            <el-option v-for="r in resources" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择项目" required>
          <el-select v-model="allocationForm.project_id" placeholder="选择项目" style="width: 100%">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分配类型">
          <el-select v-model="allocationForm.allocation_type" style="width: 100%">
            <el-option label="百分比" value="percentage" />
            <el-option label="工时" value="hours" />
            <el-option label="单位" value="units" />
          </el-select>
        </el-form-item>
        <el-form-item label="分配值">
          <el-input-number v-model="allocationForm.allocated_value" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="预算成本">
          <el-input-number v-model="allocationForm.budgeted_cost" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="allocationForm.status" style="width: 100%">
            <el-option v-for="s in allocationStatuses" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAllocationDialog = false">取消</el-button>
        <el-button type="primary" @click="createAllocation">创建</el-button>
      </template>
    </el-dialog>

    <!-- 添加成本弹窗 -->
    <el-dialog v-model="showCostDialog" title="添加成本记录" width="500px">
      <el-form :model="costForm" label-width="100px">
        <el-form-item label="选择项目" required>
          <el-select v-model="costForm.project_id" placeholder="选择项目" style="width: 100%">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="成本类别">
          <el-select v-model="costForm.category" style="width: 100%">
            <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="costForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number v-model="costForm.amount" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="costForm.cost_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCostDialog = false">取消</el-button>
        <el-button type="primary" @click="createCost">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.resource-view {
  padding: 20px;
}

.resource-view h2 {
  margin-bottom: 20px;
}

.toolbar {
  margin-bottom: 15px;
}
</style>