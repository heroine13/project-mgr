<template>
  <div class="notifications-view">
    <div class="header">
      <h1>通知中心</h1>
      <div class="actions">
        <el-button @click="handleMarkAllRead" :disabled="unreadCount === 0">
          全部已读
        </el-button>
        <el-button type="primary" @click="settingsVisible = true">
          通知设置
        </el-button>
      </div>
    </div>
    
    <!-- 筛选 -->
    <div class="filter-bar">
      <el-radio-group v-model="filterType" @change="handleFilterChange">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="unread">未读</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 通知列表 -->
    <div class="notification-list" v-loading="isLoading">
      <template v-if="notifications && notifications.length > 0">
        <el-card
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-card"
          :class="{ unread: !notification.is_read }"
          @click="handleItemClick(notification)"
        >
          <div class="card-content">
            <div class="icon">{{ getIcon(notification.type) }}</div>
            <div class="info">
              <div class="title">{{ notification.title }}</div>
              <div class="content" v-if="notification.content">
                {{ notification.content }}
              </div>
              <div class="time">{{ formatTime(notification.created_at) }}</div>
            </div>
            <div class="actions">
              <el-button
                v-if="!notification.is_read"
                size="small"
                @click.stop="handleMarkAsRead(notification.id)"
              >
                标记已读
              </el-button>
              <el-button
                size="small"
                type="danger"
                plain
                @click.stop="handleDelete(notification.id)"
              >
                删除
              </el-button>
            </div>
          </div>
        </el-card>
      </template>
      <el-empty v-else description="暂无通知" />
    </div>
    
    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 设置抽屉 -->
    <el-drawer
      v-model="settingsVisible"
      title="通知设置"
      direction="rtl"
      size="400px"
    >
      <div class="settings-content">
        <el-form label-width="120px">
          <el-form-item label="邮件通知">
            <div class="preference-group">
              <el-checkbox v-model="prefs.email_task_created">任务创建</el-checkbox>
              <el-checkbox v-model="prefs.email_task_updated">任务更新</el-checkbox>
              <el-checkbox v-model="prefs.email_task_assigned">任务分配</el-checkbox>
              <el-checkbox v-model="prefs.email_task_completed">任务完成</el-checkbox>
              <el-checkbox v-model="prefs.email_comment_mentioned">@提及</el-checkbox>
              <el-checkbox v-model="prefs.email_comment_replied">回复</el-checkbox>
            </div>
          </el-form-item>
          
          <el-form-item label="站内通知">
            <div class="preference-group">
              <el-checkbox v-model="prefs.site_task_created">任务创建</el-checkbox>
              <el-checkbox v-model="prefs.site_task_updated">任务更新</el-checkbox>
              <el-checkbox v-model="prefs.site_task_assigned">任务分配</el-checkbox>
              <el-checkbox v-model="prefs.site_task_completed">任务完成</el-checkbox>
              <el-checkbox v-model="prefs.site_comment_mentioned">@提及</el-checkbox>
              <el-checkbox v-model="prefs.site_comment_replied">回复</el-checkbox>
            </div>
          </el-form-item>
          
          <el-form-item label="邮件接收频率">
            <el-select v-model="prefs.email_frequency" style="width: 100%">
              <el-option label="即时通知" value="instant" />
              <el-option label="每日汇总" value="daily" />
              <el-option label="每周汇总" value="weekly" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleSaveSettings" :loading="saving">
              保存设置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useNotificationStore, type Notification } from '@/stores/notification'

const router = useRouter()
const notificationStore = useNotificationStore()

const notifications = computed(() => notificationStore.notifications)
const unreadCount = computed(() => notificationStore.unreadCount)
const isLoading = computed(() => notificationStore.isLoading)

const filterType = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const settingsVisible = ref(false)
const saving = ref(false)
const prefs = ref({
  email_task_created: true,
  email_task_updated: true,
  email_task_assigned: true,
  email_task_completed: false,
  email_comment_mentioned: true,
  email_comment_replied: true,
  site_task_created: true,
  site_task_updated: true,
  site_task_assigned: true,
  site_task_completed: true,
  site_comment_mentioned: true,
  site_comment_replied: true,
  email_frequency: 'instant'
})

// 初始化
onMounted(async () => {
  await loadNotifications()
})

// 加载通知
async function loadNotifications() {
  const unreadOnly = filterType.value === 'unread'
  const data = await notificationStore.fetchNotifications(unreadOnly)
  total.value = data?.length || 0
}

// 筛选变化
function handleFilterChange() {
  currentPage.value = 1
  loadNotifications()
}

// 分页变化
function handlePageChange() {
  loadNotifications()
}

function handleSizeChange() {
  loadNotifications()
}

// 点击通知项
function handleItemClick(notification: Notification) {
  if (!notification.is_read) {
    notificationStore.markAsRead(notification.id)
  }
  if (notification.link) {
    router.push(notification.link)
  }
}

// 标记已读
async function handleMarkAsRead(id: number) {
  await notificationStore.markAsRead(id)
}

// 标记全部已读
async function handleMarkAllRead() {
  await notificationStore.markAllAsRead()
  ElMessage.success('已全部标记为已读')
}

// 删除通知
async function handleDelete(id: number) {
  await notificationStore.deleteNotification(id)
  ElMessage.success('删除成功')
}

// 获取图标
function getIcon(type: string): string {
  const iconMap: Record<string, string> = {
    'task_created': '📋',
    'task_updated': '✏️',
    'task_assigned': '👤',
    'task_completed': '✅',
    'project_created': '📁',
    'project_updated': '📝',
    'comment_mentioned': '💬',
    'comment_replied': '💭'
  }
  return iconMap[type] || '🔔'
}

// 格式化时间
function formatTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString('zh-CN')
}

// 打开设置
async function handleOpenSettings() {
  settingsVisible.value = true
  const preference = await notificationStore.fetchPreferences()
  if (preference) {
    prefs.value = { ...preference }
  }
}

// 保存设置
async function handleSaveSettings() {
  saving.value = true
  try {
    await notificationStore.updatePreferences(prefs.value)
    ElMessage.success('设置保存成功')
    settingsVisible.value = false
  } catch (error) {
    ElMessage.error('设置保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.notifications-view {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
}

.filter-bar {
  margin-bottom: 20px;
}

.notification-list {
  min-height: 400px;
}

.notification-card {
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.notification-card:hover {
  transform: translateX(4px);
}

.notification-card.unread {
  border-left: 4px solid #409eff;
  background: #f0f7ff;
}

.card-content {
  display: flex;
  align-items: flex-start;
}

.icon {
  font-size: 24px;
  margin-right: 16px;
  flex-shrink: 0;
}

.info {
  flex: 1;
  min-width: 0;
}

.info .title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
  margin-bottom: 4px;
}

.info .content {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.info .time {
  font-size: 12px;
  color: #909399;
}

.actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.settings-content {
  padding: 20px;
}

.preference-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>