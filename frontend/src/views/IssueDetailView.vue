<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()

const issueId = computed(() => Number(route.params.id))

// 状态
const loading = ref(false)
const issue = ref<any>(null)
const comments = ref<any[]>([])
const submitting = ref(false)

// 新评论
const newComment = ref('')

// 弹窗
const showEditDialog = ref(false)
const editing = ref(false)
const editForm = ref({
  title: '',
  description: '',
  issue_type: '',
  priority: '',
  status: ''
})

// 选项
const issueTypes = [
  { label: 'Bug', value: 'bug' },
  { label: '功能请求', value: 'feature' },
  { label: '改进', value: 'improvement' },
  { label: '问题', value: 'question' }
]

const priorities = [
  { label: '低', value: 'low', color: '#909399' },
  { label: '中', value: 'medium', color: '#E6A23C' },
  { label: '高', value: 'high', color: '#F56C6C' },
  { label: '紧急', value: 'critical', color: '#DC2626' }
]

const statuses = [
  { label: '开放', value: 'open', color: '#409EFF' },
  { label: '处理中', value: 'in_progress', color: '#E6A23C' },
  { label: '已解决', value: 'resolved', color: '#67C23A' },
  { label: '已关闭', value: 'closed', color: '#909399' },
  { label: '重新打开', value: 'reopened', color: '#F56C6C' ]
]

// 颜色方法
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

// 加载Issue详情
const loadIssue = async () => {
  loading.value = true
  try {
    const res = await api.get(`/issues/${issueId.value}`)
    issue.value = res
  } catch (error: any) {
    ElMessage.error('加载Issue失败')
    router.push('/issues')
  } finally {
    loading.value = false
  }
}

// 加载评论
const loadComments = async () => {
  try {
    const res = await api.get(`/issues/${issueId.value}/comments`)
    comments.value = res.items
  } catch (error) {
    console.error('加载评论失败', error)
  }
}

// 更新Issue
const updateIssue = async () => {
  editing.value = true
  try {
    await api.put(`/issues/${issueId.value}`, editForm.value)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    loadIssue()
  } catch (error: any) {
    ElMessage.error(error?.detail || '更新失败')
  } finally {
    editing.value = false
  }
}

// 更新状态
const updateStatus = async (newStatus: string) => {
  try {
    await api.patch(`/issues/${issueId.value}/status`, { status: newStatus })
    ElMessage.success('状态更新成功')
    loadIssue()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

// 删除Issue
const deleteIssue = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这个Issue吗？', '提示', { type: 'warning' })
    await api.delete(`/issues/${issueId.value}`)
    ElMessage.success('删除成功')
    router.push('/issues')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 添加评论
const addComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  
  submitting.value = true
  try {
    await api.post(`/issues/${issueId.value}/comments`, { content: newComment.value })
    ElMessage.success('评论成功')
    newComment.value = ''
    loadComments()
  } catch (error: any) {
    ElMessage.error(error?.detail || '评论失败')
  } finally {
    submitting.value = false
  }
}

// 删除评论
const deleteComment = async (commentId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', { type: 'warning' })
    await api.delete(`/issues/comments/${commentId}`)
    ElMessage.success('删除成功')
    loadComments()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 打开编辑弹窗
const openEditDialog = () => {
  editForm.value = {
    title: issue.value.title,
    description: issue.value.description || '',
    issue_type: issue.value.issue_type,
    priority: issue.value.priority,
    status: issue.value.status
  }
  showEditDialog.value = true
}

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString()
}

// 返回列表
const goBack = () => {
  router.push('/issues')
}

onMounted(() => {
  loadIssue()
  loadComments()
})
</script>

<template>
  <div class="issue-detail-view" v-loading="loading">
    <!-- 返回按钮 -->
    <el-button @click="goBack" class="back-btn">
      <el-icon><ArrowLeft /></el-icon>
      返回列表
    </el-button>

    <div v-if="issue" class="issue-content">
      <!-- Issue头部信息 -->
      <el-card class="issue-header-card">
        <template #header>
          <div class="header-actions">
            <div class="header-left">
              <el-tag :type="issue.issue_type === 'bug' ? 'danger' : 'success'" style="margin-right: 10px">
                {{ getTypeLabel(issue.issue_type) }}
              </el-tag>
              <span class="issue-id">#{{ issue.id }}</span>
            </div>
            <div class="header-right">
              <el-button type="primary" @click="openEditDialog">编辑</el-button>
              <el-button type="danger" @click="deleteIssue">删除</el-button>
            </div>
          </div>
        </template>
        
        <h1 class="issue-title">{{ issue.title }}</h1>
        
        <div class="issue-meta">
          <el-tag :color="getStatusColor(issue.status)" effect="dark">
            {{ getStatusLabel(issue.status) }}
          </el-tag>
          <el-tag :color="getPriorityColor(issue.priority)" effect="dark" style="margin-left: 10px">
            {{ issue.priority }}
          </el-tag>
          <span class="meta-item">
            项目ID: {{ issue.project_id }}
          </span>
          <span class="meta-item">
            报告人ID: {{ issue.reporter_id }}
          </span>
          <span class="meta-item">
            创建时间: {{ formatDate(issue.created_at) }}
          </span>
        </div>

        <el-divider />

        <!-- Issue描述 -->
        <div class="issue-description">
          <h3>描述</h3>
          <p v-if="issue.description">{{ issue.description }}</p>
          <p v-else class="no-content">暂无描述</p>
        </div>

        <!-- 标签 -->
        <div v-if="issue.labels" class="issue-labels">
          <el-tag v-for="label in issue.labels.split(',')" :key="label" style="margin-right: 5px">
            {{ label.trim() }}
          </el-tag>
        </div>

        <!-- 状态更新 -->
        <div class="status-update">
          <h3>更新状态</h3>
          <el-select :model-value="issue.status" @change="updateStatus" style="width: 200px">
            <el-option v-for="s in statuses" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </div>
      </el-card>

      <!-- 评论区域 -->
      <el-card class="comments-card">
        <template #header>
          <div class="comments-header">
            <span>评论 ({{ comments.length }})</span>
          </div>
        </template>

        <!-- 评论列表 -->
        <div v-if="comments.length > 0" class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <span class="comment-user">用户 {{ comment.user_id }}</span>
              <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
              <el-button type="danger" link size="small" @click="deleteComment(comment.id)">
                删除
              </el-button>
            </div>
            <div class="comment-content">{{ comment.content }}</div>
          </div>
        </div>
        <div v-else class="no-comments">
          暂无评论
        </div>

        <!-- 添加评论 -->
        <el-divider />
        <div class="add-comment">
          <el-input
            v-model="newComment"
            type="textarea"
            :rows="3"
            placeholder="添加评论..."
          />
          <el-button 
            type="primary" 
            :loading="submitting" 
            @click="addComment"
            style="margin-top: 10px"
          >
            提交评论
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑Issue" width="600px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="4" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="类型">
              <el-select v-model="editForm.issue_type" style="width: 100%">
                <el-option v-for="t in issueTypes" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级">
              <el-select v-model="editForm.priority" style="width: 100%">
                <el-option v-for="p in priorities" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="editForm.status" style="width: 100%">
                <el-option v-for="s in statuses" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="editing" @click="updateIssue">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.issue-detail-view {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.back-btn {
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.issue-id {
  font-size: 18px;
  font-weight: bold;
  color: #606266;
}

.header-right {
  display: flex;
  gap: 10px;
}

.issue-title {
  font-size: 24px;
  margin: 10px 0;
}

.issue-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.meta-item {
  color: #909399;
  font-size: 14px;
}

.issue-description {
  margin: 20px 0;
}

.issue-description h3 {
  margin-bottom: 10px;
}

.issue-description p {
  line-height: 1.6;
  white-space: pre-wrap;
}

.no-content {
  color: #909399;
  font-style: italic;
}

.issue-labels {
  margin: 15px 0;
}

.status-update {
  margin-top: 20px;
}

.status-update h3 {
  margin-bottom: 10px;
}

.comments-card {
  margin-top: 20px;
}

.comments-header {
  font-weight: bold;
}

.comments-list {
  max-height: 500px;
  overflow-y: auto;
}

.comment-item {
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.comment-user {
  font-weight: bold;
  color: #409EFF;
}

.comment-time {
  color: #909399;
  font-size: 12px;
  flex: 1;
}

.comment-content {
  line-height: 1.6;
  white-space: pre-wrap;
}

.no-comments {
  text-align: center;
  color: #909399;
  padding: 30px;
}

.add-comment {
  margin-top: 10px;
}
</style>