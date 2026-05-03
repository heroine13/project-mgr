# 项目进度管理系统 - 架构设计文档

## 一、系统概述

### 1.1 系统简介
**项目名称**: 项目进度管理系统 (Project Management System)
**域名**: prjmanger.goldfon.cn
**技术栈**: Vue 3 + FastAPI + SQLAlchemy + MySQL/SQLite

### 1.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3 + Element Plus)              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │Dashboard│ │ Projects│ │  Tasks  │ │  Team   │ │ Reports │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
┌────────────────────────────┴────────────────────────────────────┐
│                      后端 (FastAPI + Python)                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     API Router Layer                       │ │
│  │  auth │ projects │ tasks │ team │ reports │ notifications │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   Business Logic Layer                     │ │
│  │         CRUD │ Services │ WebSocket │ Scheduler            │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      Data Access Layer                      │ │
│  │              SQLAlchemy ORM + Database Models              │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                        数据库 (MySQL/SQLite)                     │
│  users │ projects │ tasks │ comments │ documents │ notifications│
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、前端架构

### 2.1 技术栈
- **框架**: Vue 3 (Composition API + TypeScript)
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **国际化**: vue-i18n
- **构建工具**: Vite

### 2.2 目录结构
```
frontend/src/
├── api/                 # API请求
│   └── api.ts          # axios封装
├── assets/             # 静态资源
├── components/         # 公共组件
├── composables/        # 组合式函数
├── locales/            # 国际化语言包
│   ├── zh.json
│   └── en.json
├── router/             # 路由配置
│   └── index.ts
├── services/           # 服务层
│   ├── api.ts         # API接口
│   └── request.ts     # axios实例
├── stores/             # Pinia状态管理
│   ├── user.ts
│   ├── notification.ts
│   └── gantt.ts
├── utils/              # 工具函数
├── views/              # 页面组件
│   ├── DashboardView.vue
│   ├── ProjectDetailView.vue
│   ├── TaskDetailView.vue
│   ├── UserManagementView.vue
│   └── ... (30+ 页面)
├── websocket/          # WebSocket
│   └── websocket.ts
├── App.vue
└── main.ts
```

### 2.3 页面模块 (30+页面)

| 模块 | 页面 | 功能描述 |
|------|------|----------|
| **认证** | LoginView.vue | 用户登录 |
| | RegisterView.vue | 用户注册 |
| | ForgotPasswordView.vue | 忘记密码 |
| **仪表盘** | DashboardView.vue | 数据统计、快捷入口 |
| **项目管理** | ProjectListView.vue | 项目列表 |
| | CreateProjectView.vue | 创建项目 |
| | ProjectDetailView.vue | 项目详情 |
| **任务管理** | TaskListView.vue | 任务列表 |
| | CreateTaskView.vue | 创建任务 |
| | TaskDetailView.vue | 任务详情 |
| **日历** | CalendarView.vue | 日历视图 |
| **看板** | KanbanView.vue | Kanban看板 |
| **团队** | TeamCollaborationView.vue | 团队协作 |
| **文档** | DocumentManagementView.vue | 文档管理 |
| | DocumentSearchView.vue | 文档搜索 |
| **报表** | StatisticsView.vue | 统计报表 |
| | EnhancedReportsView.vue | 增强报表 |
| **资源** | ResourceManagementView.vue | 资源管理 |
| **问题追踪** | IssuesView.vue | 问题列表 |
| | IssueDetailView.vue | 问题详情 |
| **工作流** | WorkflowManagementView.vue | 工作流管理 |
| **通知** | NotificationsView.vue | 通知中心 |
| **用户管理** | UserManagementView.vue | 用户/角色/部门管理 |
| **权限** | PermissionsView.vue | 权限管理 |
| **AI助手** | AIAssistantView.vue | AI问答 |
| **备份** | BackupManagementView.vue | 数据备份 |
| **审计** | AuditLogView.vue | 审计日志 |
| **国际化** | TranslationManagementView.vue | 翻译管理 |
| **设置** | SettingsView.vue | 系统设置 |
| **模板** | ProjectTemplateView.vue | 项目模板 |
| **外部联系人** | ExternalContactView.vue | 外部联系人 |

---

## 三、后端架构

### 3.1 技术栈
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT (python-jose)
- **数据库**: MySQL / SQLite
- **任务调度**: APScheduler
- **WebSocket**: Starlette
- **验证**: Pydantic

### 3.2 目录结构
```
backend/app/
├── api/                    # API路由层
│   └── v1/
│       ├── auth.py         # 认证接口
│       ├── projects.py     # 项目接口
│       ├── tasks.py        # 任务接口
│       ├── team.py         # 团队接口
│       ├── documents.py    # 文档接口
│       ├── notifications.py # 通知接口
│       ├── reports.py      # 报表接口
│       ├── kanban.py       # 看板接口
│       ├── workflow.py     # 工作流接口
│       ├── user_mgmt.py    # 用户管理
│       └── ...
├── auth/                   # 认证模块
│   ├── jwt_handler.py     # JWT处理
│   └── password.py        # 密码加密
├── core/                   # 核心配置
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   └── performance.py     # 性能优化
├── crud/                   # 数据库操作
│   ├── user.py
│   ├── project.py
│   ├── task.py
│   └── ...
├── models/                 # 数据模型
│   ├── user.py            # 用户模型
│   ├── user_mgmt.py       # 角色/部门模型
│   ├── project.py         # 项目模型
│   ├── task.py            # 任务模型
│   ├── comment.py         # 评论模型
│   ├── document.py        # 文档模型
│   ├── notification.py    # 通知模型
│   └── ...
├── schemas/                # Pydantic模型
├── services/               # 业务逻辑
│   ├── notify.py          # 通知服务
│   └── scheduler.py       # 定时任务
├── utils/                  # 工具函数
├── websocket/              # WebSocket处理
├── middleware/             # 中间件
├── tests/                  # 单元测试
└── main.py                 # 应用入口
```

### 3.3 API接口 (30+ 模块)

| 模块 | 接口路径 | 功能 |
|------|----------|------|
| **认证** | `/api/v1/auth/login` | 用户登录 |
| | `/api/v1/auth/register` | 用户注册 |
| **用户管理** | `/api/v1/users/users` | 用户CRUD |
| | `/api/v1/users/roles` | 角色管理 |
| | `/api/v1/users/departments` | 部门管理 |
| **项目** | `/api/v1/projects/` | 项目CRUD |
| **任务** | `/api/v1/tasks/` | 任务CRUD |
| **团队** | `/api/v1/team/` | 团队管理 |
| **文档** | `/api/v1/documents/` | 文档管理 |
| **日历** | `/api/v1/calendar/` | 日历事件 |
| **看板** | `/api/v1/kanban/` | Kanban管理 |
| **报表** | `/api/v1/reports/` | 数据报表 |
| **资源** | `/api/v1/resources/` | 资源管理 |
| **问题** | `/api/v1/issues/` | 问题追踪 |
| **工作流** | `/api/v1/workflow/` | 审批流 |
| **通知** | `/api/v1/notifications/` | 通知中心 |
| **AI** | `/api/v1/ai/` | AI助手 |
| **备份** | `/api/v1/backup/` | 数据备份 |
| **审计** | `/api/v1/audit/` | 审计日志 |
| **导入导出** | `/api/v1/export/` | 数据导出 |

---

## 四、数据库设计

### 4.1 核心数据表

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `users` | 用户表 | id, username, email, password, role_id |
| `roles` | 角色表 | id, name, permissions |
| `departments` | 部门表 | id, name, parent_id (自引用) |
| `projects` | 项目表 | id, name, code, status, owner_id |
| `tasks` | 任务表 | id, title, status, priority, project_id, assignee_id |
| `comments` | 评论表 | id, content, user_id, task_id |
| `documents` | 文档表 | id, name, project_id, uploader_id |
| `notifications` | 通知表 | id, user_id, type, content |
| `issues` | 问题表 | id, title, status, project_id |
| `resources` | 资源表 | id, name, type, quantity |
| `resource_allocations` | 资源分配 | id, resource_id, project_id, quantity |
| `gantt_tasks` | 甘特图任务 | id, task_id, start_date, end_date |
| `workflows` | 工作流 | id, name, status |
| `approval_requests` | 审批请求 | id, workflow_id, status |
| `audit_logs` | 审计日志 | id, user_id, action, resource |

### 4.2 核心模型关系

```
User (1) ─────< Role
User (1) ─────< Department
User (1) ─────< Notifications
User (1) ─────< UserProfile

Project (1) ─────< Task
Project (1) ─────< Document
Project (1) ─────< Issue
Project (1) ─────< ResourceAllocation
Project (1) ─────< ApprovalRequest

Task (1) ─────< Comment
Task (1) ─────< ResourceAllocation
Task (1) ─────< GanttTask

Department (1) ─────< Department (自引用)
```

---

## 五、功能模块

### 5.1 核心功能

| 功能 | 描述 | 状态 |
|------|------|------|
| 用户认证 | JWT登录/注册/登出 | ✅ |
| 项目管理 | 创建/编辑/删除/查询项目 | ✅ |
| 任务管理 | 创建/编辑/删除/指派任务 | ✅ |
| 甘特图 | 可视化项目进度 | ✅ |
| 看板视图 | Kanban风格任务管理 | ✅ |
| 日历视图 | 日历形式展示任务 | ✅ |
| 团队协作 | 成员管理、权限控制 | ✅ |
| 文档管理 | 文件上传、版本控制 | ✅ |
| 通知系统 | 站内通知、邮件通知 | ✅ |
| 数据导出 | Excel/CSV/PDF导出 | ✅ |
| AI助手 | 智能问答功能 | ✅ |
| 工作流 | 审批流自定义 | ✅ |
| 资源管理 | 资源分配与跟踪 | ✅ |
| 问题追踪 | Issue管理 | ✅ |
| 数据备份 | 手动/自动备份 | ✅ |
| 审计日志 | 操作记录追踪 | ✅ |
| 国际化 | 中英文支持 | ✅ |
| 暗色主题 | 深色主题切换 | ✅ |

---

## 六、部署架构

### 6.1 生产环境
```
                    ┌─────────────────┐
                    │   Nginx (80/443)│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │Frontend  │  │  Backend │  │  Backend │
       │  (Vue)   │  │ (FastAPI)│  │ (FastAPI)│
       └──────────┘  └──────────┘  └──────────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │  MySQL   │  │   Redis  │  │   Redis  │
       │ Primary  │  │  Cache   │  │   Queue  │
       └──────────┘  └──────────┘  └──────────┘
```

### 6.2 测试环境 (当前)
- **前端**: Docker容器 (http://test.prjmanger.goldfon.cn)
- **后端**: Docker容器 (http://test-api.prjmanger.goldfon.cn)
- **数据库**: SQLite (文件存储)

---

## 七、测试账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 全部权限 |
| 项目经理 | pm | pm123 | 项目管理权限 |
| 普通用户 | user | user123 | 基本权限 |
| 团队成员 | member | member123 | 被指派任务 |

---

*文档版本: 1.0*
*最后更新: 2026-05-03*