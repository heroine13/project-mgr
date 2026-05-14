import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/DashboardView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue')
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/ProjectDetailView.vue')
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('@/views/TaskDetailView.vue')
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: () => import('@/views/NotificationsView.vue')
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('@/views/StatisticsView.vue')
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('@/views/UsersView.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue')
    },
    {
      path: '/projects/new',
      name: 'create-project',
      component: () => import('@/views/CreateProjectView.vue')
    },
    {
      path: '/tasks/new',
      name: 'create-task',
      component: () => import('@/views/CreateTaskView.vue')
    },
    {
      path: '/team',
      name: 'team',
      component: () => import('@/views/TeamCollaborationView.vue')
    },
    {
      path: '/kanban',
      name: 'kanban',
      component: () => import('@/views/kanban/KanbanView.vue')
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/CalendarView.vue')
    },
    {
      path: '/documents',
      name: 'documents',
      component: () => import('@/views/DocumentManagementView.vue')
    },
    {
      path: '/resources',
      name: 'resources',
      component: () => import('@/views/ResourceManagementView.vue')
    },
    {
      path: '/issues',
      name: 'issues',
      component: () => import('@/views/IssuesView.vue')
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('@/views/EnhancedReportsView.vue')
    },
    {
      path: '/ai',
      name: 'ai',
      component: () => import('@/views/AIAssistantView.vue')
    }
  ]
})

export default router