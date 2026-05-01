import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue')
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPasswordView.vue')
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue')
      },
      {
        path: 'tasks',
        name: 'tasks',
        component: () => import('@/views/TaskDetailView.vue')
      },
      {
        path: 'tasks/new',
        name: 'tasks-new',
        component: () => import('@/views/CreateTaskView.vue'),
        meta: { title: '创建任务' }
      },
      {
        path: 'tasks/my',
        name: 'tasks-my',
        component: () => import('@/views/TaskDetailView.vue'),
        meta: { title: '我的任务' }
      },
      {
        path: 'tasks/overdue',
        name: 'tasks-overdue',
        component: () => import('@/views/TaskDetailView.vue'),
        meta: { title: '逾期任务' }
      },
      {
        path: 'projects',
        name: 'projects',
        component: () => import('@/views/ProjectDetailView.vue')
      },
      {
        path: 'projects/new',
        name: 'projects-new',
        component: () => import('@/views/CreateProjectView.vue'),
        meta: { title: '创建项目' }
      },
      {
        path: 'projects/archived',
        name: 'projects-archived',
        component: () => import('@/views/ProjectDetailView.vue'),
        meta: { title: '已归档项目' }
      },
      {
        path: 'notifications',
        name: 'notifications',
        component: () => import('@/views/NotificationsView.vue')
      },
      {
        path: 'issues',
        name: 'issues',
        component: () => import('@/views/IssuesView.vue')
      },
      {
        path: 'issues/:id',
        name: 'issue-detail',
        component: () => import('@/views/IssueDetailView.vue')
      },
      {
        path: 'resources',
        name: 'resources',
        component: () => import('@/views/ResourceManagementView.vue')
      },
      {
        path: 'documents',
        name: 'documents',
        component: () => import('@/views/DocumentManagementView.vue')
      },
      {
        path: 'i18n',
        name: 'i18n',
        component: () => import('@/views/TranslationManagementView.vue')
      },
      {
        path: 'documents-search',
        name: 'document-search',
        component: () => import('@/views/DocumentSearchView.vue')
      },
      {
        path: 'backup',
        name: 'backup',
        component: () => import('@/views/BackupManagementView.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'workflows',
        name: 'workflows',
        component: () => import('@/views/WorkflowManagementView.vue')
      },
      {
        path: 'kanban',
        name: 'kanban',
        component: () => import('@/views/kanban/KanbanView.vue')
      },
      {
        path: 'audit',
        name: 'audit',
        component: () => import('@/views/AuditLogView.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'reports',
        name: 'reports',
        component: () => import('@/views/EnhancedReportsView.vue')
      },
      {
        path: 'ai-assistant',
        name: 'ai-assistant',
        component: () => import('@/views/AIAssistantView.vue')
      },
      {
        path: 'calendar',
        name: 'calendar',
        component: () => import('@/views/CalendarView.vue')
      },
      {
        path: 'project-templates',
        name: 'project-templates',
        component: () => import('@/views/ProjectTemplateView.vue')
      },
      {
        path: 'team',
        name: 'team',
        component: () => import('@/views/TeamCollaborationView.vue')
      },
      {
        path: 'external-contacts',
        name: 'external-contacts',
        component: () => import('@/views/ExternalContactView.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'statistics',
        name: 'statistics',
        component: () => import('@/views/StatisticsView.vue')
      },
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/UserManagementView.vue')
      },
      {
        path: 'permissions',
        name: 'permissions',
        component: () => import('@/views/PermissionsView.vue')
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/SettingsView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
