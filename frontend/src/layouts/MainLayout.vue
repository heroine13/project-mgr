<template>
  <div class="main-layout">
    <!-- Sidebar Navigation -->
    <div 
      class="sidebar" 
      :class="{ 'sidebar-collapsed': isCollapsed }"
    >
      <div class="sidebar-header">
        <div class="logo">
          <img src="@/assets/logo.svg" alt="Logo" v-if="!isCollapsed" />
          <h2 v-if="!isCollapsed">{{ $t('app.name') }}</h2>
          <h2 v-else>PMS</h2>
        </div>
        <el-button 
          class="collapse-btn"
          type="text"
          @click="toggleSidebar"
          :icon="isCollapsed ? 'Expand' : 'Fold'"
        />
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        :collapse="isCollapsed"
        :collapse-transition="false"
        router
        @select="handleMenuSelect"
      >
        <!-- Dashboard -->
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>{{ $t('navigation.dashboard') }}</template>
        </el-menu-item>
        
        <!-- Projects -->
        <el-sub-menu index="projects">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>{{ $t('navigation.projects') }}</span>
          </template>
          <el-menu-item index="/projects">{{ $t('navigation.projects') }}</el-menu-item>
          <el-menu-item index="/projects/new">{{ $t('dashboard.newProject') }}</el-menu-item>
          <el-menu-item index="/projects/archived">{{ $t('status.archived') }}</el-menu-item>
        </el-sub-menu>
        
        <!-- Tasks -->
        <el-sub-menu index="tasks">
          <template #title>
            <el-icon><Tickets /></el-icon>
            <span>{{ $t('navigation.tasks') }}</span>
          </template>
          <el-menu-item index="/tasks">{{ $t('navigation.tasks') }}</el-menu-item>
          <el-menu-item index="/tasks/new">新建任务</el-menu-item>
        <el-menu-item index="/tasks/my">{{ $t('task.assignee') }}</el-menu-item>
          <el-menu-item index="/tasks/overdue">{{ $t('dashboard.overdueTasks') }}</el-menu-item>
        </el-sub-menu>
        
        <!-- Team -->
        <el-menu-item index="/team">
          <el-icon><User /></el-icon>
          <template #title>{{ $t('navigation.team') }}</template>
        </el-menu-item>
        
        <!-- Calendar -->
        <el-menu-item index="/calendar">
          <el-icon><Calendar /></el-icon>
          <template #title>{{ $t('navigation.calendar') }}</template>
        </el-menu-item>
        
        <!-- Kanban -->
        <el-menu-item index="/kanban">
          <el-icon><Grid /></el-icon>
          <template #title>{{ $t('navigation.kanban') }}</template>
        </el-menu-item>
        
        <!-- Documents -->
        <el-menu-item index="/documents">
          <el-icon><Document /></el-icon>
          <template #title>{{ $t('navigation.documents') }}</template>
        </el-menu-item>
        
        <!-- Resources -->
        <el-menu-item index="/resources">
          <el-icon><Box /></el-icon>
          <template #title>{{ $t('navigation.resources') }}</template>
        </el-menu-item>
        
        <!-- Issues -->
        <el-menu-item index="/issues">
          <el-icon><Warning /></el-icon>
          <template #title>{{ $t('navigation.issues') }}</template>
        </el-menu-item>
        
        <!-- AI Assistant -->
        <el-menu-item index="/ai">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>{{ $t('navigation.aiAssistant') }}</template>
        </el-menu-item>
        
        <!-- Reports -->
        <el-menu-item index="/reports">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>{{ $t('navigation.reports') }}</template>
        </el-menu-item>
        
        <!-- Statistics -->
        <el-menu-item index="/statistics">
          <el-icon><TrendCharts /></el-icon>
          <template #title>{{ $t('navigation.statistics') }}</template>
        </el-menu-item>
        
        <!-- User & Department Management -->
        <el-menu-item index="/user-mgmt">
          <el-icon><UserFilled /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        
        <!-- Audit Logs -->
        <el-menu-item index="/audit-logs">
          <el-icon><Document /></el-icon>
          <template #title>审计日志</template>
        </el-menu-item>


        <!-- Settings -->
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>{{ $t('navigation.settings') }}</template>
        </el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <div class="user-info">
          <el-avatar :size="isCollapsed ? 32 : 40" :src="userAvatar">
            {{ userInitials }}
          </el-avatar>
          <div class="user-details" v-if="!isCollapsed">
            <div class="user-name">{{ user?.full_name || user?.username }}</div>
            <div class="user-role">{{ userRole }}</div>
          </div>
        </div>
        
        <div class="sidebar-actions">
          <el-button type="text" @click="toggleTheme">
            <el-icon><Moon v-if="isDarkTheme" /><Sunny v-else /></el-icon>
            <span v-if="!isCollapsed">{{ isDarkTheme ? $t('common.dark') : $t('common.light') }}</span>
          </el-button>
          
          <el-dropdown @command="handleUserCommand">
            <el-button type="text">
              <el-icon><More /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">{{ $t('common.profile') }}</el-dropdown-item>
                <el-dropdown-item command="settings">{{ $t('navigation.settings') }}</el-dropdown-item>
                <el-dropdown-item command="logout" divided>{{ $t('navigation.logout') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- Sidebar expand trigger (shown only when sidebar is collapsed) -->
    <div
      v-if="isCollapsed"
      class="sidebar-expand-trigger"
      @click="toggleSidebar"
    >
      <el-icon><ArrowRightBold /></el-icon>
    </div>
    
    <!-- Main Content -->
    <div class="main-content" :class="{ 'content-expanded': isCollapsed }">
      <!-- Top Navigation -->
      <div class="top-nav">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">
              {{ $t('navigation.dashboard') }}
            </el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumb" :key="item.path">
              <span v-if="item.path">{{ item.name }}</span>
              <router-link v-else :to="item.path">{{ item.name }}</router-link>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="top-actions">
          <!-- Quick Actions -->
          <el-button-group class="quick-actions">
            <el-button type="primary" @click="createNewTask">
              <el-icon><Plus /></el-icon>
              {{ $t('dashboard.createTask') }}
            </el-button>
            <el-button @click="createNewProject">
              <el-icon><FolderAdd /></el-icon>
              {{ $t('dashboard.newProject') }}
            </el-button>
          </el-button-group>
          
          <!-- Search -->
          <el-input
            v-model="searchQuery"
            :placeholder="$t('common.search')"
            class="search-input"
            :prefix-icon="Search"
            size="small"
            @keyup.enter="handleSearch"
          />
          
          <!-- Notifications -->
          <el-dropdown class="notification-dropdown">
            <el-badge :value="unreadNotifications" :max="99" class="notification-badge">
              <el-button type="text" :icon="Bell" />
            </el-badge>
            <template #dropdown>
              <el-dropdown-menu>
                <div class="notification-header">
                  <h4>{{ $t('common.notifications') }}</h4>
                  <el-button type="text" size="small" @click="markAllAsRead">
                    {{ $t('common.markAllRead') }}
                  </el-button>
                </div>
                <div class="notification-list">
                  <div v-for="notification in notifications" :key="notification.id" 
                    class="notification-item" :class="{ unread: !notification.read }"
                    @click="handleNotificationClick(notification)">
                    <div class="notification-icon">
                      <el-icon :class="notification.type">
                        <component :is="getNotificationIcon(notification.type)" />
                      </el-icon>
                    </div>
                    <div class="notification-content">
                      <div class="notification-title">{{ notification.title }}</div>
                      <div class="notification-time">{{ formatTime(notification.time) }}</div>
                    </div>
                  </div>
                </div>
                <el-dropdown-item divided @click="viewAllNotifications">
                  {{ $t('common.viewAll') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <!-- User Menu -->
          <el-dropdown class="user-dropdown" @command="handleUserCommand">
            <div class="user-avatar">
              <el-avatar :size="32" :src="userAvatar">
                {{ userInitials }}
              </el-avatar>
              <span class="user-name">{{ user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">{{ $t('common.profile') }}</el-dropdown-item>
                <el-dropdown-item command="settings">{{ $t('navigation.settings') }}</el-dropdown-item>
                <el-dropdown-item command="logout" divided>{{ $t('navigation.logout') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <!-- Language Switcher -->
          <el-select
            v-model="currentLocale"
            size="small"
            class="language-select"
            @change="changeLanguage"
          >
            <el-option
              v-for="lang in languages"
              :key="lang.value"
              :label="lang.label"
              :value="lang.value"
            />
          </el-select>
        </div>
      </div>
      
      <!-- Page Content -->
      <div class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
      
      <!-- Footer -->
      <div class="page-footer">
        <div class="footer-content">
          <span>© 2026 {{ $t('app.name') }}</span>
          <span class="footer-links">
            <el-link type="info" href="/help">{{ $t('common.help') }}</el-link>
            <el-link type="info" href="/privacy">{{ $t('common.privacy') }}</el-link>
            <el-link type="info" href="/terms">{{ $t('common.terms') }}</el-link>
          </span>
          <span class="footer-status" :class="getStatusClass(apiStatus)">
            <el-icon><CircleCheck v-if="apiStatus === 'online'" /><Warning v-else /></el-icon>
            {{ getStatusText(apiStatus) }}
          </span>
        </div>
      </div>
    </div>
  </div>

  <!-- Profile Dialog -->
  <el-dialog v-model="showProfileDialog" title="个人资料" width="500px">
    <el-descriptions :column="1" border v-if="user">
      <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
      <el-descriptions-item label="邮箱">{{ user.email }}</el-descriptions-item>
      <el-descriptions-item label="姓名">{{ user.full_name || '未设置' }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ user.is_active ? '启用' : '禁用' }}</el-descriptions-item>
      <el-descriptions-item label="超级管理员">{{ user.is_superuser ? '是' : '否' }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ user.created_at }}</el-descriptions-item>
    </el-descriptions>
    <el-descriptions :column="1" border v-else>
      <el-descriptions-item label="加载中..."></el-descriptions-item>
    </el-descriptions>
    <template #footer>
      <el-button @click="showProfileDialog = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'

// Icons
import {
  Odometer, Folder, Tickets, User, 
  DataAnalysis, Setting, Expand, Fold,
  Moon, Sunny, More, Plus, FolderAdd,
  Search, Bell, ArrowDown, CircleCheck,
  Warning,
  ArrowRightBold
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const { t, locale } = useI18n()

// Store
const userStore = useUserStore()
const themeStore = useThemeStore()
const { user } = storeToRefs(userStore)
const { isDarkTheme } = storeToRefs(themeStore)

// State
const isCollapsed = ref(false)
const activeMenu = ref('/dashboard')
const searchQuery = ref('')
const currentLocale = ref(locale.value)
const apiStatus = ref('online')
const unreadNotifications = ref(3)

// Mock data
const userAvatar = ref('')
const userRole = ref('Administrator')
const breadcrumb = ref([
  { name: 'Dashboard', path: '/dashboard' }
])

const notifications = ref([
  { id: 1, type: 'task', title: 'New task assigned to you', time: '2026-04-05T08:30:00Z', read: false },
  { id: 2, type: 'project', title: 'Project status updated', time: '2026-04-05T10:15:00Z', read: true },
  { id: 3, type: 'system', title: 'System maintenance scheduled', time: '2026-04-05T12:45:00Z', read: false }
])

const languages = [
  { value: 'zh-CN', label: '中文' },
  { value: 'en-US', label: 'English' }
]

const showProfileDialog = ref(false)

// Computed
const userInitials = computed(() => {
  if (!user.value) return 'U'
  const name = user.value.full_name || user.value.username
  return name.charAt(0).toUpperCase()
})

// Methods
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  // 导航到对应路由
  if (index && router.currentRoute.value.path !== index) {
    router.push(index)
  }
}

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      userStore.getProfile()
      showProfileDialog.value = true
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const createNewTask = () => {
  router.push('/tasks/new')
}

const createNewProject = () => {
  router.push('/projects/new')
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
  }
}

const getNotificationIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    task: 'Tickets',
    project: 'Folder',
    system: 'Setting',
    user: 'User'
  }
  return iconMap[type] || 'Bell'
}

const formatTime = (timeString: string) => {
  const time = new Date(timeString)
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  
  if (diff < 3600000) { // Less than 1 hour
    const minutes = Math.floor(diff / 60000)
    return `${minutes}分钟前`
  } else if (diff < 86400000) { // Less than 1 day
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  } else {
    return time.toLocaleDateString()
  }
}

const handleNotificationClick = (notification: any) => {
  notification.read = true
  unreadNotifications.value = Math.max(0, unreadNotifications.value - 1)
  // Navigate based on notification type
  if (notification.type === 'task') {
    router.push('/tasks')
  } else if (notification.type === 'project') {
    router.push('/projects')
  }
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
  unreadNotifications.value = 0
}

const viewAllNotifications = () => {
  router.push('/notifications')
}

const changeLanguage = (lang: string) => {
  locale.value = lang
  localStorage.setItem('user_language', lang)
}

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    online: 'status-online',
    offline: 'status-offline',
    degraded: 'status-degraded'
  }
  return statusMap[status] || ''
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    online: t('common.online'),
    offline: t('common.offline'),
    degraded: t('common.degraded')
  }
  return textMap[status] || status
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// Lifecycle
onMounted(() => {
  // Update breadcrumb based on route
  watch(
    () => route.matched,
    (matched) => {
      breadcrumb.value = matched.map(match => ({
        name: match.meta.title || match.name || '',
        path: match.path
      }))
    },
    { immediate: true }
  )
  
  // Update active menu
  watch(
    () => route.path,
    (path) => {
      activeMenu.value = path
    },
    { immediate: true }
  )
})
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  position: relative;
}

/* Expand button when sidebar is collapsed */
.sidebar-expand-trigger {
  position: fixed;
  left: 64px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 64px;
  background: var(--el-color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  z-index: 1000;
  transition: left 0.3s ease, all 0.3s ease;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-expand-trigger:hover {
  width: 32px;
  left: 56px;
}

.sidebar-expand-trigger .el-icon {
  font-size: 16px;
}

.sidebar {
  width: 260px;
  background: var(--el-bg-color-page);
  border-right: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 1000;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color-light);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo img {
  height: 32px;
  width: 32px;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.collapse-btn {
  font-size: 18px;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid var(--el-border-color-light);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.user-role {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.sidebar-actions {
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-left: 260px;
  transition: margin-left 0.3s ease;
}

.content-expanded {
  margin-left: 64px;
}

/* Top Navigation */
.top-nav {
  height: 64px;
  padding: 0 24px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 999;
}

.breadcrumb {
  flex: 1;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.quick-actions {
  margin-right: 16px;
}

.search-input {
  width: 240px;
}

.notification-dropdown {
  cursor: pointer;
}

.notification-badge :deep(.el-badge__content) {
  top: 8px;
  right: 8px;
}

.notification-header {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--el-border-color-light);
}

.notification-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.notification-list {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--el-border-color-light);
}

.notification-item:hover {
  background: var(--el-fill-color-light);
}

.notification-item.unread {
  background: var(--el-color-primary-light-9);
}

.notification-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: var(--el-color-primary-light-9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-primary);
}

.notification-icon .el-icon {
  font-size: 16px;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-size: 14px;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.notification-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.user-dropdown {
  cursor: pointer;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.language-select {
  width: 100px;
}

/* Page Content */
.page-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: var(--el-bg-color-page);
}

/* Footer */
.page-footer {
  height: 48px;
  padding: 0 24px;
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  align-items: center;
  background: var(--el-bg-color);
}

.footer-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.footer-links {
  display: flex;
  gap: 16px;
}

.footer-status {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-online {
  color: var(--el-color-success);
}

.status-offline {
  color: var(--el-color-error);
}

.status-degraded {
  color: var(--el-color-warning);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.show {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0 !important;
  }
  
  .top-nav {
    padding: 0 16px;
  }
  
  .search-input {
    display: none;
  }
  
  .quick-actions {
    display: none;
  }
  
  .language-select {
    display: none;
  }
  
  .page-content {
    padding: 16px;
  }
}
</style>