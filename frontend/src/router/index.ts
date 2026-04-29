import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue')
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
        path: 'projects',
        name: 'projects',
        component: () => import('@/views/ProjectDetailView.vue')
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
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
