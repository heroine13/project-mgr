<template>
  <div class="team-view">
    <el-tabs v-model="activeTab">
      <!-- 团队成员 -->
      <el-tab-pane label="👥 团队成员" name="members">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>团队成员</span>
              <el-button type="primary" @click="showInviteDialog = true">
                <el-icon><Plus /></el-icon>
                邀请成员
              </el-button>
            </div>
          </template>

          <el-table :data="members" v-loading="loading" stripe>
            <el-table-column label="成员" min-width="200">
              <template #default="{ row }">
                <div class="member-info">
                  <el-avatar :size="40">{{ row.username?.charAt(0).toUpperCase() }}</el-avatar>
                  <div class="member-detail">
                    <span class="member-name">{{ row.username }}</span>
                    <span class="member-title">{{ row.title }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="department" label="部门" width="120" />
            <el-table-column prop="role" label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
                  {{ row.role === 'admin' ? '管理员' : '成员' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column label="最后活跃" width="180">
              <template #default="{ row }">
                {{ formatTime(row.last_active) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="viewMember(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 活动动态 -->
      <el-tab-pane label="📝 活动动态" name="activity">
        <el-card>
          <template #header>
            <span>团队活动</span>
          </template>

          <div class="activity-feed">
            <div v-for="activity in activities" :key="activity.id" class="activity-item">
              <div class="activity-icon">
                <span>{{ getActivityIcon(activity.type) }}</span>
              </div>
              <div class="activity-content">
                <div class="activity-user">{{ activity.username }}</div>
                <div class="activity-desc">{{ activity.description }}</div>
                <div class="activity-time">{{ formatTime(activity.created_at) }}</div>
              </div>
            </div>

            <el-empty v-if="activities.length === 0" description="暂无活动" />
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 工作负载 -->
      <el-tab-pane label="📊 工作负载" name="workload">
        <el-card>
          <template #header>
            <span>团队工作负载</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="8" v-for="item in workload" :key="item.user_id">
              <el-card class="workload-card">
                <div class="workload-header">
                  <el-avatar>{{ item.username?.charAt(0).toUpperCase() }}</el-avatar>
                  <span class="workload-name">{{ item.username }}</span>
                </div>
                <div class="workload-stats">
                  <div class="stat-item">
                    <span class="stat-label">已分配</span>
                    <span class="stat-value">{{ item.assigned }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">进行中</span>
                    <span class="stat-value" style="color: #E6A23C">{{ item.in_progress }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">已完成</span>
                    <span class="stat-value" style="color: #67C23A">{{ item.completed }}</span>
                  </div>
                </div>
                <el-progress 
                  :percentage="parseInt(item.capacity)" 
                  :color="getCapacityColor(item.capacity)"
                />
                <div class="capacity-text">容量: {{ item.capacity }}</div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>

      <!-- 统计 -->
      <el-tab-pane label="📈 团队统计" name="stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="团队成员" :value="teamStats.total_members" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="活跃成员" :value="teamStats.active_members" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="进行中任务" :value="teamStats.tasks_assigned" />
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <el-statistic title="已完成任务" :value="teamStats.tasks_completed" />
            </el-card>
          </el-col>
        </el-row>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>部门分布</span>
          </template>
          <el-table :data="departmentStats" stripe>
            <el-table-column prop="department" label="部门" />
            <el-table-column prop="members" label="成员数" />
            <el-table-column prop="completed_tasks" label="完成任务" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 邀请成员对话框 -->
    <el-dialog v-model="showInviteDialog" title="邀请团队成员" width="400px">
      <el-form :model="inviteForm" label-width="80px">
        <el-form-item label="邮箱">
          <el-input v-model="inviteForm.email" placeholder="请输入成员邮箱" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="inviteForm.name" placeholder="请输入成员姓名" />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="inviteForm.department" placeholder="选择部门" clearable>
            <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInviteDialog = false">取消</el-button>
        <el-button type="primary" @click="inviteMember" :loading="inviting">发送邀请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = '/api/v1/team'

const activeTab = ref('members')
const loading = ref(false)
const inviting = ref(false)

const members = ref([])
const activities = ref([])
const workload = ref([])
const teamStats = ref({})
const departmentStats = ref([])
const showInviteDialog = ref(false)
const inviteForm = ref({ email: '', name: '', department: '' })
const departments = ref([])

const formatTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN')
}

const getActivityIcon = (type) => {
  const icons = {
    task_completed: '✅',
    comment: '💬',
    task_assigned: '📌',
    status_change: '🔄',
    project_created: '📁'
  }
  return icons[type] || '📝'
}

const getCapacityColor = (capacity) => {
  const pct = parseInt(capacity)
  if (pct >= 90) return '#F56C6C'
  if (pct >= 70) return '#E6A23C'
  return '#67C23A'
}

const fetchMembers = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/members`)
    members.value = response.data.members || []
  } catch (error) {
    console.error('获取成员列表失败', error)
  } finally {
    loading.value = false
  }
}

const fetchActivities = async () => {
  try {
    const response = await axios.get(`${API_BASE}/activity`)
    activities.value = response.data.activities || []
  } catch (error) {
    console.error('获取活动失败', error)
  }
}

const fetchWorkload = async () => {
  try {
    const response = await axios.get(`${API_BASE}/workload`)
    workload.value = response.data.workload || []
  } catch (error) {
    console.error('获取工作负载失败', error)
  }
}

const fetchStats = async () => {
  try {
    const response = await axios.get(`${API_BASE}/stats`)
    teamStats.value = response.data
    
    // Format department stats
    const byDept = response.data.by_department || {}
    departmentStats.value = Object.entries(byDept).map(([dept, data]) => ({
      department: dept,
      members: data.members,
      completed_tasks: data.completed_tasks
    }))
  } catch (error) {
    console.error('获取统计失败', error)
  }
}

const viewMember = (member) => {
  ElMessage.info(`查看成员: ${member.username}`)
}

const inviteMember = async () => {
  if (!inviteForm.value.email || !inviteForm.value.name) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  inviting.value = true
  try {
    await axios.post(`${API_BASE}/invite`, null, {
      params: inviteForm.value
    })
    ElMessage.success('邀请已发送')
    showInviteDialog.value = false
    inviteForm.value = { email: '', name: '', department: '' }
    fetchMembers()
  } catch (error: any) {
    console.error('邀请成员失败', error)
    ElMessage.error(error?.response?.data?.detail || error?.message || '邀请失败，请确保已登录')
  } finally {
    inviting.value = false
  }
}

const loadDepartments = async () => {
  try {
    const res = await axios.get('/api/v1/users/departments', { params: { page_size: 100 } })
    departments.value = res.data.items || []
  } catch (e) {
    console.error('加载部门失败', e)
  }
}

onMounted(() => {
  fetchMembers()
  fetchActivities()
  fetchWorkload()
  fetchStats()
  loadDepartments()
})
</script>

<style scoped>
.team-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.member-detail {
  display: flex;
  flex-direction: column;
}

.member-name {
  font-weight: 500;
}

.member-title {
  font-size: 12px;
  color: #909399;
}

.activity-feed {
  max-height: 500px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 50%;
}

.activity-content {
  flex: 1;
}

.activity-user {
  font-weight: 500;
  margin-bottom: 5px;
}

.activity-desc {
  color: #606266;
  margin-bottom: 5px;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

.workload-card {
  text-align: center;
}

.workload-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
}

.workload-name {
  font-weight: 500;
}

.workload-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 15px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #909399;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
}

.capacity-text {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.stat-card {
  text-align: center;
}
</style>