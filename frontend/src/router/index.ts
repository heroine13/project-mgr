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
    name: 'home',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue')
      }
    ]
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'dashboard-page',
        component: () => import('@/views/DashboardView.vue')
      }
    ]
  },
  {
    path: '/projects',
    name: 'projects',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'projects-page',
        component: () => import('@/views/ProjectListView.vue')
      },
      {
        path: 'archived',
        name: 'projects-archived',
        component: () => import('@/views/ArchivedProjectsView.vue')
      },
      {
        path: ':id',
        name: 'project-detail',
        component: () => import('@/views/ProjectDetailView.vue')
      }
    ]
  },
  {
    path: '/projects/new',
    name: 'create-project',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'create-project-page',
        component: () => import('@/views/CreateProjectView.vue')
      }
    ]
  },
  {
    path: '/tasks',
    name: 'tasks',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'tasks-page',
        component: () => import('@/views/TaskDetailView.vue')
      },
      {
        path: ':id',
        name: 'task-detail',
        component: () => import('@/views/TaskDetailView.vue')
      },
      {
        path: 'my',
        name: 'tasks-my',
        component: () => import('@/views/MyTasksView.vue')
      },
      {
        path: 'overdue',
        name: 'tasks-overdue',
        component: () => import('@/views/OverdueTasksView.vue')
      },
      {
        path: 'new',
        name: 'create-task-page',
        component: () => import('@/views/CreateTaskView.vue')
      }
    ]
  },
  {
    path: '/team',
    name: 'team',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'team-page',
        component: () => import('@/views/TeamCollaborationView.vue')
      }
    ]
  },
  {
    path: '/kanban',
    name: 'kanban',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'kanban-page',
        component: () => import('@/views/kanban/KanbanView.vue')
      }
    ]
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'calendar-page',
        component: () => import('@/views/CalendarView.vue')
      }
    ]
  },
  {
    path: '/documents',
    name: 'documents',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'documents-page',
        component: () => import('@/views/DocumentManagementView.vue')
      }
    ]
  },
  {
    path: '/resources',
    name: 'resources',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'resources-page',
        component: () => import('@/views/ResourceManagementView.vue')
      }
    ]
  },
  {
    path: '/issues',
    name: 'issues',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'issues-page',
        component: () => import('@/views/IssuesView.vue')
      },
      {
        path: ':id',
        name: 'issue-detail',
        component: () => import('@/views/IssueDetailView.vue')
      }
    ]
  },
  {
    path: '/reports',
    name: 'reports',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'reports-page',
        component: () => import('@/views/EnhancedReportsView.vue')
      }
    ]
  },
  {
    path: '/ai',
    name: 'ai',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'ai-page',
        component: () => import('@/views/AIAssistantView.vue')
      }
    ]
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'notifications-page',
        component: () => import('@/views/NotificationsView.vue')
      }
    ]
  },
  {
    path: '/statistics',
    name: 'statistics',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'statistics-page',
        component: () => import('@/views/StatisticsView.vue')
      }
    ]
  },
  {
    path: '/audit-logs',
    name: 'audit-logs',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'audit-logs-page',
        component: () => import('@/views/AuditLogView.vue')
      }
    ]
  },
  {
    path: '/user-mgmt',
    name: 'user-mgmt',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'user-mgmt-page',
        component: () => import('@/views/UserManagementView.vue')
      }
    ]
  },
  {
    path: '/settings',
    name: 'settings',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'settings-page',
        component: () => import('@/views/SettingsView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 导出 router 实例，供 API 拦截器等非组件场景使用
export { router }
export default router