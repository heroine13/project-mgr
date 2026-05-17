/**
 * 通知状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/services/request'

export interface Notification {
  id: number
  user_id: number
  type: string
  title: string
  content: string | null
  related_data: Record<string, any> | null
  link: string | null
  is_read: boolean
  created_at: string
  read_at: string | null
}

export interface NotificationPreference {
  id: number
  user_id: number
  email_task_created: boolean
  email_task_updated: boolean
  email_task_assigned: boolean
  email_task_completed: boolean
  email_comment_mentioned: boolean
  email_comment_replied: boolean
  email_project_updated: boolean
  site_task_created: boolean
  site_task_updated: boolean
  site_task_assigned: boolean
  site_task_completed: boolean
  site_comment_mentioned: boolean
  site_comment_replied: boolean
  site_project_updated: boolean
  email_frequency: string
}

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const preference = ref<NotificationPreference | null>(null)
  
  const hasUnread = computed(() => unreadCount.value > 0)
  
  async function fetchNotifications(unreadOnly = false) {
    isLoading.value = true
    try {
      const params = unreadOnly ? { unread_only: 'true' } : {}
      const res = await request.get('/notifications/', { params })
      notifications.value = res || []
      return res || []
    } catch (error) {
      console.error('获取通知列表失败:', error)
      return []
    } finally {
      isLoading.value = false
    }
  }
  
  async function fetchUnreadCount() {
    try {
      const res = await request.get('/notifications/unread-count')
      unreadCount.value = res.unread_count || 0
      return res.unread_count || 0
    } catch (error) {
      console.error('获取未读数量失败:', error)
      return 0
    }
  }
  
  async function markAsRead(notificationId: number) {
    try {
      await request.post(`/notifications/${notificationId}/read`)
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification && !notification.is_read) {
        notification.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }
  
  async function markAllAsRead() {
    try {
      await request.post('/notifications/read-all')
      notifications.value.forEach(n => {
        n.is_read = true
        n.read_at = new Date().toISOString()
      })
      unreadCount.value = 0
    } catch (error) {
      console.error('标记全部已读失败:', error)
    }
  }
  
  async function deleteNotification(notificationId: number) {
    try {
      await request.delete(`/notifications/${notificationId}`)
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        if (!notifications.value[index].is_read) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
        notifications.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除通知失败:', error)
    }
  }
  
  async function fetchPreferences() {
    try {
      const res = await request.get('/notifications/preferences')
      preference.value = res
      return res
    } catch (error) {
      console.error('获取通知偏好失败:', error)
      return null
    }
  }
  
  async function updatePreferences(prefs: Partial<NotificationPreference>) {
    try {
      const res = await request.put('/notifications/preferences', prefs)
      preference.value = res
      return res
    } catch (error) {
      console.error('更新通知偏好失败:', error)
      return null
    }
  }
  
  function getNotificationIcon(type: string): string {
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
  
  return {
    notifications,
    unreadCount,
    isLoading,
    preference,
    hasUnread,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    fetchPreferences,
    updatePreferences,
    getNotificationIcon,
    formatTime
  }
})
