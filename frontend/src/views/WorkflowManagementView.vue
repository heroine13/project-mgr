<template>
  <div class="workflow-management">
    <el-tabs v-model="activeTab">
      <!-- 工作流管理 -->
      <el-tab-pane label="工作流管理" name="workflows">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📋 工作流定义</span>
              <el-button type="primary" @click="showCreateWorkflow = true">
                <el-icon><Plus /></el-icon>
                创建工作流
              </el-button>
            </div>
          </template>

          <el-table :data="workflows" v-loading="loadingWorkflows" stripe>
            <el-table-column prop="name" label="工作流名称" min-width="150" />
            <el-table-column prop="entity_type" label="适用类型" width="120">
              <template #default="{ row }">
                <el-tag>{{ row.entity_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button-group>
                  <el-button size="small" @click="editWorkflow(row)">编辑</el-button>
                  <el-button 
                    size="small" 
                    :type="row.status === 'active' ? 'danger' : 'success'"
                    @click="toggleWorkflowStatus(row)"
                  >
                    {{ row.status === 'active' ? '禁用' : '启用' }}
                  </el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 审批请求 -->
      <el-tab-pane label="审批请求" name="requests">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📝 审批请求</span>
              <el-radio-group v-model="requestFilter" size="small">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="pending">待审批</el-radio-button>
                <el-radio-button label="approved">已通过</el-radio-button>
                <el-radio-button label="rejected">已拒绝</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <el-table :data="approvalRequests" v-loading="loadingRequests" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="entity_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.entity_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="entity_id" label="关联ID" width="80" />
            <el-table-column prop="current_step" label="步骤" width="60" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="requested_by" label="申请人" width="80" />
            <el-table-column prop="created_at" label="申请时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button 
                  v-if="row.status === 'pending'" 
                  size="small" 
                  type="primary"
                  @click="openApprovalDialog(row)"
                >
                  审批
                </el-button>
                <el-button size="small" @click="viewRequestDetail(row)">
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 我的申请 -->
      <el-tab-pane label="我的申请" name="my-requests">
        <el-card>
          <template #header>
            <span>📨 我的申请</span>
          </template>

          <el-table :data="myRequests" v-loading="loadingMyRequests" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="entity_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.entity_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="result" label="审批结果" />
            <el-table-column prop="created_at" label="申请时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建/编辑工作流对话框 -->
    <el-dialog 
      v-model="showCreateWorkflow" 
      :title="editingWorkflow ? '编辑工作流' : '创建工作流'"
      width="600px"
    >
      <el-form :model="workflowForm" label-width="100px">
        <el-form-item label="工作流名称">
          <el-input v-model="workflowForm.name" placeholder="请输入工作流名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="workflowForm.description" type="textarea" rows="2" />
        </el-form-item>
        <el-form-item label="适用类型">
          <el-select v-model="workflowForm.entity_type" placeholder="选择适用类型">
            <el-option label="任务 (Task)" value="task" />
            <el-option label="项目 (Project)" value="project" />
            <el-option label="问题 (Issue)" value="issue" />
            <el-option label="文档 (Document)" value="document" />
          </el-select>
        </el-form-item>
        <el-form-item label="审批步骤">
          <div v-for="(step, index) in workflowForm.steps" :key="index" class="step-item">
            <el-card shadow="never">
              <el-row :gutter="10">
                <el-col :span="8">
                  <el-input v-model="step.name" placeholder="步骤名称" />
                </el-col>
                <el-col :span="14">
                  <el-select v-model="step.approvers" multiple placeholder="选择审批人">
                    <el-option
                      v-for="user in users"
                      :key="user.id"
                      :label="user.username"
                      :value="user.id"
                    />
                  </el-select>
                </el-col>
                <el-col :span="2">
                  <el-button type="danger" circle @click="removeStep(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-col>
              </el-row>
            </el-card>
          </div>
          <el-button type="primary" link @click="addStep">
            <el-icon><Plus /></el-icon>
            添加步骤
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateWorkflow = false">取消</el-button>
        <el-button type="primary" @click="saveWorkflow" :loading="savingWorkflow">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 审批对话框 -->
    <el-dialog v-model="showApprovalDialog" title="审批" width="500px">
      <el-alert
        :title="`审批请求 #${currentRequest?.id}`"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p>类型: {{ currentRequest?.entity_type }}</p>
        <p>关联ID: {{ currentRequest?.entity_id }}</p>
        <p>当前步骤: {{ currentRequest?.current_step + 1 }}</p>
      </el-alert>
      
      <el-form :model="approvalForm" label-width="80px">
        <el-form-item label="审批意见">
          <el-input v-model="approvalForm.comment" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showApprovalDialog = false">取消</el-button>
        <el-button type="danger" @click="submitApproval('reject')" :loading="approving">
          拒绝
        </el-button>
        <el-button type="success" @click="submitApproval('approve')" :loading="approving">
          批准
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = '/api/v1/workflows'

const activeTab = ref('workflows')
const loadingWorkflows = ref(false)
const loadingRequests = ref(false)
const loadingMyRequests = ref(false)
const savingWorkflow = ref(false)
const approving = ref(false)

const workflows = ref([])
const approvalRequests = ref([])
const myRequests = ref([])
const users = ref([])

const showCreateWorkflow = ref(false)
const showApprovalDialog = ref(false)
const editingWorkflow = ref(null)
const currentRequest = ref(null)
const requestFilter = ref('all')

const workflowForm = ref({
  name: '',
  description: '',
  entity_type: 'task',
  steps: [{ step: 1, name: '', approvers: [] }]
})

const approvalForm = ref({
  comment: ''
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger', cancelled: 'info' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { pending: '待审批', approved: '已通过', rejected: '已拒绝', cancelled: '已取消' }
  return map[status] || status
}

const fetchWorkflows = async () => {
  loadingWorkflows.value = true
  try {
    const response = await axios.get(API_BASE)
    workflows.value = response.data
  } catch (error) {
    ElMessage.error('获取工作流列表失败')
  } finally {
    loadingWorkflows.value = false
  }
}

const fetchApprovalRequests = async () => {
  loadingRequests.value = true
  try {
    const params = {}
    if (requestFilter.value !== 'all') {
      params.status = requestFilter.value
    }
    const response = await axios.get(`${API_BASE}/requests/`, { params })
    approvalRequests.value = response.data
  } catch (error) {
    ElMessage.error('获取审批请求失败')
  } finally {
    loadingRequests.value = false
  }
}

const fetchMyRequests = async () => {
  loadingMyRequests.value = true
  try {
    const response = await axios.get(`${API_BASE}/requests/`, { params: { my_requests: true } })
    myRequests.value = response.data
  } catch (error) {
    ElMessage.error('获取我的申请失败')
  } finally {
    loadingMyRequests.value = false
  }
}

const fetchUsers = async () => {
  try {
    const response = await axios.get('/api/v1/users/')
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败', error)
  }
}

const addStep = () => {
  workflowForm.value.steps.push({
    step: workflowForm.value.steps.length + 1,
    name: '',
    approvers: []
  })
}

const removeStep = (index) => {
  workflowForm.value.steps.splice(index, 1)
}

const saveWorkflow = async () => {
  savingWorkflow.value = true
  try {
    if (editingWorkflow.value) {
      await axios.put(`${API_BASE}/${editingWorkflow.value.id}`, {
        name: workflowForm.value.name,
        description: workflowForm.value.description,
        steps: workflowForm.value.steps
      })
      ElMessage.success('工作流更新成功')
    } else {
      await axios.post(API_BASE, workflowForm.value)
      ElMessage.success('工作流创建成功')
    }
    showCreateWorkflow.value = false
    fetchWorkflows()
    resetWorkflowForm()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    savingWorkflow.value = false
  }
}

const editWorkflow = (workflow) => {
  editingWorkflow.value = workflow
  workflowForm.value = {
    name: workflow.name,
    description: workflow.description,
    entity_type: workflow.entity_type,
    steps: workflow.steps_config || []
  }
  showCreateWorkflow.value = true
}

const toggleWorkflowStatus = async (workflow) => {
  const newStatus = workflow.status === 'active' ? 'draft' : 'active'
  try {
    await axios.put(`${API_BASE}/${workflow.id}`, { status: newStatus })
    ElMessage.success(`工作流已${newStatus === 'active' ? '启用' : '禁用'}`)
    fetchWorkflows()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const openApprovalDialog = (request) => {
  currentRequest.value = request
  approvalForm.value.comment = ''
  showApprovalDialog.value = true
}

const submitApproval = async (action) => {
  approving.value = true
  try {
    await axios.post(`${API_BASE}/requests/${currentRequest.value.id}/approve`, {
      action,
      comment: approvalForm.value.comment
    })
    ElMessage.success(action === 'approve' ? '审批通过' : '已拒绝')
    showApprovalDialog.value = false
    fetchApprovalRequests()
    fetchMyRequests()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '审批失败')
  } finally {
    approving.value = false
  }
}

const viewRequestDetail = (request) => {
  ElMessage.info(`请求详情: ${request.id}`)
}

const resetWorkflowForm = () => {
  editingWorkflow.value = null
  workflowForm.value = {
    name: '',
    description: '',
    entity_type: 'task',
    steps: [{ step: 1, name: '', approvers: [] }]
  }
}

watch(activeTab, (tab) => {
  if (tab === 'workflows') fetchWorkflows()
  if (tab === 'requests') fetchApprovalRequests()
  if (tab === 'my-requests') fetchMyRequests()
})

watch(requestFilter, () => {
  if (activeTab.value === 'requests') fetchApprovalRequests()
})

onMounted(() => {
  fetchWorkflows()
  fetchUsers()
})
</script>

<style scoped>
.workflow-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-item {
  margin-bottom: 10px;
}

.step-item .el-card {
  margin-bottom: 10px;
}
</style>