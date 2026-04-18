<template>
  <div class="notification-center">
    <!-- 通知图标按钮 -->
    <el-popover
      placement="bottom-end"
      :width="380"
      trigger="click"
      popper-class="notification-popover"
    >
      <template #reference>
        <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99">
          <el-button :icon="Bell" circle class="notification-btn" />
        </el-badge>
      </template>
      
      <!-- 通知列表 -->
      <div class="notification-panel">
        <!-- 头部 -->
        <div class="notification-header">
          <span class="title">通知中心</span>
          <div class="actions">
            <el-button link type="primary" @click="handleMarkAllRead" :disabled="unreadCount === 0">
              全部已读
            </el-button>
            <el-button link type="primary" @click="handleOpenSettings">
              设置
            </el-button>
          </div>
        </div>
        
        <!-- 列表 -->
        <div class="notification-list" v-loading="isLoading">
          <template v-if="notifications.length > 0">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="notification-item"
              :class="{ unread: !notification.is_read }"
              @click="handleItemClick(notification)"
            >
              <div class="notification-icon">
                {{ getIcon(notification.type) }}
              </div>
              <div class="notification-content">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-desc" v-if="notification.content">
                  {{ notification.content }}
                </div>
                <div class="notification-time">
                  {{ formatTime(notification.created_at) }}
                </div>
              </div>
              <el-button
                class="delete-btn"
                :icon="Close"
                link
                size="small"
                @click.stop="handleDelete(notification.id)"
              />
            </div>
          </template>
          <el-empty v-else description="暂无通知" :image-size="60" />
        </div>
        
        <!-- 底部 -->
        <div class="notification-footer">
          <el-button link type="primary" @click="handleViewAll">
            查看全部通知
          </el-button>
        </div>
      </div>
    </el-popover>
    
    <!-- 通知设置抽屉 -->
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useNotificationStore, type Notification } from '@/stores/notification'
import request from '@/services/request'

const router = useRouter()
const notificationStore = useNotificationStore()

const notifications = computed(() => notificationStore.notifications)
const unreadCount = computed(() => notificationStore.unreadCount)
const isLoading = computed(() => notificationStore.isLoading)

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
  await Promise.all([
    notificationStore.fetchNotifications(),
    notificationStore.fetchUnreadCount()
  ])
})

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

// 点击通知项
function handleItemClick(notification: Notification) {
  // 标记为已读
  if (!notification.is_read) {
    notificationStore.markAsRead(notification.id)
  }
  
  // 跳转到对应页面
  if (notification.link) {
    router.push(notification.link)
  }
}

// 标记全部已读
async function handleMarkAllRead() {
  await notificationStore.markAllAsRead()
  ElMessage.success('已全部标记为已读')
}

// 删除通知
async function handleDelete(id: number) {
  await notificationStore.deleteNotification(id)
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

// 查看全部
function handleViewAll() {
  router.push('/notifications')
}
</script>

<style scoped>
.notification-center {
  display: inline-block;
}

.notification-btn {
  border: none;
  background: transparent;
  font-size: 20px;
}

.notification-panel {
  margin: -12px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.notification-header .title {
  font-weight: 600;
  font-size: 16px;
}

.notification-header .actions {
  display: flex;
  gap: 8px;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f5f5f5;
}

.notification-item:hover {
  background: #f8f9fa;
}

.notification-item.unread {
  background: #f0f7ff;
}

.notification-item.unread::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #409eff;
}

.notification-icon {
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.notification-desc {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-time {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.notification-item:hover .delete-btn {
  opacity: 1;
}

.notification-footer {
  padding: 12px 16px;
  border-top: 1px solid #eee;
  text-align: center;
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