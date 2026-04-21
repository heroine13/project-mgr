import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/dashboard/DashboardView.vue')
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('@/views/tasks/TaskListView.vue')
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/projects/ProjectListView.vue')
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: () => import('@/views/NotificationsView.vue')
    },
    {
      path: '/issues',
      name: 'issues',
      component: () => import('@/views/IssuesView.vue')
    },
    {
      path: '/issues/:id',
      name: 'issue-detail',
      component: () => import('@/views/IssueDetailView.vue')
    },
    {
      path: '/resources',
      name: 'resources',
      component: () => import('@/views/ResourceManagementView.vue')
    },
    {
      path: '/documents',
      name: 'documents',
      component: () => import('@/views/DocumentManagementView.vue')
    },
    {
      path: '/i18n',
      name: 'i18n',
      component: () => import('@/views/TranslationManagementView.vue')
    },
    {
      path: '/documents-search',
      name: 'document-search',
      component: () => import('@/views/DocumentSearchView.vue')
    },
    {
      path: '/backup',
      name: 'backup',
      component: () => import('@/views/BackupManagementView.vue'),
      meta: { requiresAdmin: true }
    },
    {
      path: '/workflows',
      name: 'workflows',
      component: () => import('@/views/WorkflowManagementView.vue')
    },
    {
      path: '/kanban',
      name: 'kanban',
      component: () => import('@/views/kanban/KanbanView.vue')
    },
    {
      path: '/audit',
      name: 'audit',
      component: () => import('@/views/AuditLogView.vue'),
      meta: { requiresAdmin: true }
    }
  ]
})

export default router