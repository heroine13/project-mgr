<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()

const issueId = computed(() => Number(route.params.id))

const loading = ref(false)
const issue = ref<any>(null)
const comments = ref<any[]>([])
const submitting = ref(false)
const newComment = ref('')
const showEditDialog = ref(false)
const editing = ref(false)
const editForm = ref({
  title: '',
  description: '',
  issue_type: '',
  priority: '',
  status: ''
})

const issueTypes = [
  { label: 'Bug', value: 'bug' },
  { label: 'Feature Request', value: 'feature' },
  { label: 'Improvement', value: 'improvement' },
  { label: 'Question', value: 'question' }
]

const priorities = [
  { label: 'Low', value: 'low', color: '#909399' },
  { label: 'Medium', value: 'medium', color: '#E6A23C' },
  { label: 'High', value: 'high', color: '#F56C6C' },
  { label: 'Critical', value: 'critical', color: '#DC2626' }
]

const statuses = [
  { label: 'Open', value: 'open', color: '#409EFF' },
  { label: 'In Progress', value: 'in_progress', color: '#E6A23C' },
  { label: 'Resolved', value: 'resolved', color: '#67C23A' },
  { label: 'Closed', value: 'closed', color: '#909399' },
  { label: 'Reopened', value: 'reopened', color: '#F56C6C' }
]

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

const loadIssue = async () => {
  loading.value = true
  try {
    const res = await api.get(`/issues/${issueId.value}`)
    issue.value = res.data
  } catch (error) {
    ElMessage.error('Failed to load issue')
  } finally {
    loading.value = false
  }
}

const loadComments = async () => {
  try {
    const res = await api.get(`/issues/${issueId.value}/comments`)
    comments.value = res.data || []
  } catch (error) {
    console.error(error)
  }
}

const addComment = async () => {
  if (!newComment.value.trim()) return
  submitting.value = true
  try {
    await api.post(`/issues/${issueId.value}/comments`, {
      content: newComment.value
    })
    newComment.value = ''
    loadComments()
    ElMessage.success('Comment added')
  } catch (error) {
    ElMessage.error('Failed to add comment')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadIssue()
  loadComments()
})
</script>

<template>
  <div class="issue-detail">
    <el-card v-if="issue">
      <h1>{{ issue.title }}</h1>
      <el-tag :color="getStatusColor(issue.status)">
        {{ getStatusLabel(issue.status) }}
      </el-tag>
      <p>{{ issue.description }}</p>
    </el-card>
    <div v-else>Loading...</div>
  </div>
</template>

<style scoped>
.issue-detail { padding: 20px; }
</style>
