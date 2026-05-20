# 项目进度管理系统 - 设计文档

**文档版本**: v1.0
**创建日期**: 2026-05-20
**项目名称**: project-mgr
**技术栈**: Vue 3 + FastAPI + SQLAlchemy + SQLite/MySQL

---

## 目录

1. [项目概述](#1-项目概述)
2. [模块总览](#2-模块总览)
3. [用户认证模块](#3-用户认证模块)
4. [项目管理模块](#4-项目管理模块)
5. [任务管理模块](#5-任务管理模块)
6. [看板视图模块](#6-看板视图模块)
7. [甘特图模块](#7-甘特图模块)
8. [日历视图模块](#8-日历视图模块)
9. [文档管理模块](#9-文档管理模块)
10. [资源成本管理模块](#10-资源成本管理模块)
11. [Issue问题管理模块](#11-issue问题管理模块)
12. [团队协作模块](#12-团队协作模块)
13. [通知系统模块](#13-通知系统模块)
14. [审计日志模块](#14-审计日志模块)
15. [审批流模块](#15-审批流模块)
16. [报表模块](#16-报表模块)
17. [用户管理模块](#17-用户管理模块)
18. [AI智能助手模块](#18-ai智能助手模块)
19. [项目模板模块](#19-项目模板模块)
20. [系统设置模块](#20-系统设置模块)

---

## 1. 项目概述

项目进度管理系统（project-mgr）是一个面向中小型工厂的综合性项目管理平台，旨在帮助企业实现项目任务的全程追踪、团队协作和资源管理。

### 1.1 系统目标

- 提供可视化的任务管理（看板、甘特图、日历）
- 实现团队协作与实时沟通
- 支持资源分配与成本核算
- 满足企业审计合规需求

### 1.2 技术架构

| 层级 | 技术栈 |
|------|--------|
| 前端 | Vue 3 + Element Plus + Pinia + Vue Router + i18next |
| 后端 | Python FastAPI + SQLAlchemy + JWT + WebSocket |
| 数据库 | SQLite（开发）/ MySQL（生产）|
| 部署 | Docker / Docker Compose |

### 1.3 核心业务对象

- **项目(Project)**：项目管理的基本单元，包含多个任务和团队成员
- **任务(Task)**：项目下的具体工作单元，可分配负责人和截止日期
- **用户(User)**：系统使用者，包含角色和权限控制
- **评论(Comment)**：任务评论，支持@提及和回复

---

## 2. 模块总览

本系统共包含 **20+ 个功能模块**，覆盖项目管理的完整生命周期：

| 序号 | 模块名称 | 路由前缀 | 功能说明 |
|------|----------|----------|----------|
| 1 | 用户认证 | /api/v1/auth | 注册、登录、JWT令牌 |
| 2 | 项目管理 | /api/v1/projects | 项目的CRUD、归档、统计 |
| 3 | 任务管理 | /api/v1/tasks | 任务CRUD、状态流转、逾期检测 |
| 4 | 看板视图 | /api/v1/kanban | 看板列拖拽、任务流转 |
| 5 | 甘特图 | /api/v1/gantt | 时间线视图、依赖关系 |
| 6 | 日历视图 | /api/v1/calendar | 日/周/月日历展示 |
| 7 | 文档管理 | /api/v1/documents | 文档上传、版本控制 |
| 8 | 资源成本 | /api/v1/resources | 资源分配、成本记录 |
| 9 | Issue管理 | /api/v1/issues | Bug/Feature追踪 |
| 10 | 团队协作 | /api/v1/team | 团队成员管理 |
| 11 | 通知系统 | /api/v1/notifications | 站内通知、邮件通知 |
| 12 | 审计日志 | /api/v1/audit | 操作记录、安全追踪 |
| 13 | 审批流 | /api/v1/workflow | 多级审批流程 |
| 14 | 报表 | /api/v1/reports | 数据统计、图表展示 |
| 15 | 用户管理 | /api/v1/users | 用户CRUD、角色权限 |
| 16 | AI助手 | /api/v1/ai | 智能问答、任务建议 |
| 17 | 项目模板 | /api/v1/project-templates | 模板创建、快速复制 |
| 18 | 系统设置 | /api/v1/settings | 系统配置参数 |
| 19 | 数据导出 | /api/v1/export | Excel/CSV导出 |
| 20 | 国际化 | /api/v1/i18n | 多语言支持 |

---

## 3. 用户认证模块

### 3.1 功能说明

用户认证模块负责系统的身份验证与授权管理。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 用户注册 | /auth/register | POST | 邮箱+密码注册，检查唯一性 |
| 用户登录 | /auth/login | POST | 用户名/邮箱+密码登录 |
| 令牌刷新 | /auth/refresh | POST | 使用refresh_token获取新access_token |
| 忘记密码 | /auth/forgot-password | POST | 发送密码重置邮件 |
| 重置密码 | /auth/reset-password | POST | 使用token重置密码 |

### 3.2 数据模型

**users 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String(50) | 用户名，唯一 |
| email | String(100) | 邮箱，唯一 |
| hashed_password | String(255) | bcrypt哈希密码 |
| full_name | String(100) | 真实姓名 |
| is_active | Boolean | 账号是否激活 |
| is_superuser | Boolean | 是否超级管理员 |
| role_id | Integer | 角色外键 |
| created_at | DateTime | 创建时间 |

### 3.3 业务规则

- 密码使用bcrypt哈希存储，不可逆
- JWT access_token有效期短（默认15分钟）
- refresh_token有效期长（默认7天）
- 登录成功后会记录审计日志

### 3.4 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除用户 | 用户为超级管理员 | 禁止删除最后一个超级管理员 |
| 删除用户 | 用户有未完成的任务 | 提示：先转移任务 |
| 禁用用户 | 用户为项目唯一成员 | 提示：项目将没有成员 |
| 修改密码 | 与原密码相同 | 提示：新密码不能与原密码相同 |

### 4.1 功能说明

项目管理模块是系统的核心模块，负责项目的创建、查询、更新、删除和归档操作。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 创建项目 | /projects | POST | 创建新项目，自动生成项目编号（如PRJ-001） |
| 项目列表 | /projects | GET | 支持按状态、名称搜索筛选 |
| 项目详情 | /projects/:id | GET | 获取单个项目的详细信息 |
| 更新项目 | /projects/:id | PUT | 修改项目名称、描述、时间、预算等 |
| 删除项目 | /projects/:id | DELETE | 删除项目（软删除） |
| 归档项目 | /projects/:id/archive | POST | 将项目标记为已归档 |
| 项目总览 | /projects/overview/summary | GET | 获取所有项目汇总数据（含任务数、Issue数、完成率） |
| 项目详情页 | /projects/:id/detail | GET | 获取项目完整数据：任务统计、团队成员、评论时间线、文档附件 |

### 4.2 数据模型

**projects 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(200) | 项目名称 |
| description | Text | 项目描述 |
| code | String(50) | 项目编号，唯一（如PRJ-001） |
| status | String(50) | 状态：active/completed/archived |
| owner_id | Integer | 项目负责人（外键） |
| start_date | DateTime | 开始日期 |
| end_date | DateTime | 结束日期 |
| budget | Integer | 预算金额 |
| actual_cost | Integer | 实际成本 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 4.3 项目状态说明

- **active**：进行中，项目正在执行
- **completed**：已完成，项目已结束
- **archived**：已归档，项目已归档保存

### 4.4 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除项目 | 项目下有进行中的任务 | 提示：先完成或转移任务 |
| 删除项目 | - | 级联删除：任务、评论、Issue、文档、甘特图任务 |
| 归档项目 | 项目状态为completed | 自动归档 |
| 修改项目负责人 | 项目有未完成任务 | 提示：任务负责人可能需要同步 |

### 4.5 状态与字段编辑限制

| 项目状态 | 可编辑字段 | 限制说明 |
|----------|------------|----------|
| active | 全部字段 | 可正常编辑 |
| completed | description, budget | 只读字段：name, code, status, owner |
| archived | description | 只读字段：name, code, status, owner, dates, budget |

### 4.4 业务规则

- 项目编号自动生成，全局唯一
- 删除项目为软删除，实际标记为archived
- 项目负责人默认为创建者

---

## 5. 任务管理模块

### 5.1 功能说明

任务管理模块负责项目下任务的全生命周期管理。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 创建任务 | /tasks | POST | 创建新任务，支持设置截止日期 |
| 任务列表 | /tasks | GET | 支持按项目、状态、负责人筛选 |
| 任务详情 | /tasks/:id | GET | 获取任务详细信息 |
| 更新任务 | /tasks/:id | PUT | 修改任务内容、状态、负责人等 |
| 删除任务 | /tasks/:id | DELETE | 删除任务 |
| 逾期任务 | /tasks/overdue | GET | 获取已逾期任务列表 |

### 5.2 数据模型

**tasks 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String(200) | 任务标题 |
| description | Text | 任务描述 |
| status | String(50) | 状态：pending/in_progress/review/completed/blocked |
| priority | String(50) | 优先级：low/medium/high/urgent |
| assignee_id | Integer | 负责人（外键） |
| project_id | Integer | 所属项目（外键） |
| due_date | DateTime | 截止日期 |
| estimated_hours | Integer | 预估工时 |
| actual_hours | Integer | 实际工时 |
| tags | String(255) | 标签，逗号分隔 |
| created_by | Integer | 创建人（外键） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 5.3 任务状态说明

| 状态 | 说明 |
|------|------|
| pending | 待处理 |
| in_progress | 进行中 |
| review | 待审核 |
| completed | 已完成 |
| blocked | 已阻塞 |

### 5.4 任务优先级说明

| 优先级 | 说明 |
|--------|------|
| low | 低优先级 |
| medium | 中优先级 |
| high | 高优先级 |
| urgent | 紧急 |

### 5.5 逾期任务功能

**触发条件**：当任务的 due_date 已过，且 status 不是 completed 时，就会被判定为逾期。

**使用说明**：
- 目前数据库中没有逾期数据，所以列表为空是正常的
- 创建带 due_date 且已过期的任务即可在逾期列表中看到
- 逾期任务会在任务列表中标记为红色警告

### 5.6 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除项目 | - | 该项目下所有任务、评论、Issue、文档一并删除 |
| 删除任务 | - | 该任务下所有评论、附件一并删除 |
| 修改任务状态 | 已完成(completed)状态的任务 | 只能改为归档或重新开启，无法直接改回进行中 |
| 修改任务负责人 | 任务状态为已完成 | 禁止修改 |

### 5.7 状态与字段编辑限制

| 任务状态 | 可编辑字段 | 限制说明 |
|----------|------------|----------|
| pending | 全部字段 | 可正常编辑 |
| in_progress | 全部字段 | 可正常编辑 |
| review | title, description, priority | status和assignee需审批通过后可改 |
| completed | description, tags, priority | 只读字段：status, assignee, due_date |
| blocked | 全部字段 | 可正常编辑，需填写阻塞原因 |

## 6. 看板视图模块

### 6.1 功能说明

看板视图模块提供基于列的任务拖拽管理，模拟物理看板的体验。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 获取看板 | /kanban/:project_id | GET | 获取项目的看板配置和任务列表 |
| 移动任务 | /kanban/move | POST | 拖拽任务到不同列，更新状态 |
| 创建列 | /kanban/columns | POST | 创建新的看板列 |
| 更新列 | /kanban/columns/:id | PUT | 修改列名称、顺序等 |
| 删除列 | /kanban/columns/:id | DELETE | 删除看板列 |

### 6.2 看板列配置

看板列与任务状态对应，默认列：
- 待处理（对应任务status=pending）
- 进行中（对应任务status=in_progress）
- 待审核（对应任务status=review）
- 已完成（对应任务status=completed）
- 已阻塞（对应任务status=blocked）

### 6.3 业务规则

- 看板列可以自定义名称
- 拖拽任务到不同列会自动更新任务状态
- 列顺序可以调整
- 删除列时，列上的任务会回归到默认列

### 6.4 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除列 | 列上有任务 | 提示：任务将移动到默认列 |
| 拖拽任务 | 目标列与当前状态一致 | 无影响，不更新状态 |
| 拖拽任务 | 任务状态为completed | 提示：已完成任务不能移动 |

### 6.5 状态流转限制

| 当前状态 | 可移动到的列 | 限制说明 |
|----------|--------------|----------|
| pending | in_progress, review, blocked | 可正常拖拽 |
| in_progress | pending, review, completed, blocked | 可正常拖拽 |
| review | in_progress, completed, blocked | 需审批通过后才能移动到完成 |
| completed | 无 | 禁止拖拽，只能查看 |
| blocked | pending, in_progress, review | 解决阻塞后可移动 |

### 7.1 功能说明

甘特图模块提供项目任务的时间线可视化展示，支持任务依赖关系管理。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 获取甘特图 | /gantt/:project_id | GET | 获取项目的甘特图数据 |
| 创建任务 | /gantt/tasks | POST | 在甘特图中创建任务 |
| 更新任务 | /gantt/tasks/:id | PUT | 修改任务时间、进度等 |
| 删除任务 | /gantt/tasks/:id | DELETE | 删除甘特图任务 |
| 设置依赖 | /gantt/dependencies | POST | 设置任务依赖关系 |
| 删除依赖 | /gantt/dependencies/:id | DELETE | 删除任务依赖 |
| 保存视图 | /gantt/views | POST | 保存甘特图视图配置 |

### 7.2 数据模型

**gantt_tasks 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| project_id | Integer | 项目ID（外键） |
| task_id | Integer | 关联的任务ID（外键，可选） |
| name | String(255) | 任务名称 |
| start_date | DateTime | 开始日期 |
| end_date | DateTime | 结束日期 |
| progress | Float | 进度（0.0-1.0） |
| priority | Integer | 优先级：0普通/1重要/2紧急 |
| color | String(20) | 任务颜色 |
| is_milestone | Integer | 是否为里程碑（0否/1是） |
| resource_id | Integer | 分配资源（外键） |

**gantt_dependencies 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| predecessor_id | Integer | 前置任务ID |
| successor_id | Integer | 后置任务ID |
| dependency_type | String(20) | 依赖类型：FS/SS/FF/SF |
| lag_days | Integer | 延迟天数 |

### 7.3 依赖类型说明

| 类型 | 说明 |
|------|------|
| FS | Finish to Start（前置任务完成后开始） |
| SS | Start to Start（前置任务开始后开始） |
| FF | Finish to Finish（前置任务完成后完成） |
| SF | Start to Finish（前置任务开始后完成） |

### 7.4 基线管理

甘特图支持基线（Baseline）功能，用于对比计划与实际执行情况：
- 计划开始/结束日期
- 实际开始/结束日期
- 偏差计算（开始偏差、结束偏差、进度偏差）

### 7.5 业务规则

- 里程碑任务没有结束日期，只显示一个节点
- 任务进度自动根据子任务计算
- 删除有依赖的任务时，关联依赖一并删除

### 7.6 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除任务 | 任务有子任务 | 提示：先删除子任务 |
| 删除任务 | 任务是其他任务的依赖 | 提示：先解除依赖关系 |
| 删除项目 | - | 该项目的甘特图任务、依赖关系、视图配置全部删除 |
| 修改任务日期 | 任务有后置依赖 | 提示：后置任务的日期可能需要同步调整 |

### 7.7 状态与字段编辑限制

| 任务进度 | 可编辑字段 | 限制说明 |
|----------|------------|----------|
| 0% | 全部字段 | 可正常编辑 |
| 1-99% | start_date, end_date, progress | 禁止修改：project_id, is_milestone |
| 100% | progress | 只能设为100%，不能减少 |

### 8.1 功能说明

日历视图模块以日历形式展示任务，支持日/周/月三种视图模式。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 获取日历 | /calendar/:project_id | GET | 获取项目的日历数据 |
| 创建任务 | /calendar/tasks | POST | 在日历中创建任务 |
| 更新任务 | /calendar/tasks/:id | PUT | 拖拽调整任务日期 |

### 8.2 视图模式

| 模式 | 说明 |
|------|------|
| day | 按天展示，每天显示任务列表 |
| week | 按周展示，每周一个表格 |
| month | 按月展示，每月一个日历格 |

### 8.3 业务规则

- 任务按开始日期显示在日历格中
- 跨天任务在多个日期格中显示
- 点击日期格可快速创建任务

### 8.4 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 拖拽调整任务日期 | 任务有依赖 | 提示：后置任务日期可能冲突 |
| 修改任务日期 | 超出项目时间范围 | 提示：日期超出项目开始/结束时间 |

### 8.5 视图限制说明

| 视图模式 | 显示内容 | 限制说明 |
|----------|----------|----------|
| day | 当天所有任务 | 最多显示50条，超出需分页 |
| week | 本周所有任务 | 按天分组显示 |
| month | 本月所有任务 | 只显示有任务的天数 |

### 9.1 功能说明

文档管理模块提供文档的上传、存储和版本控制功能。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 文档列表 | /documents | GET | 获取文档列表，支持分类筛选 |
| 上传文档 | /documents | POST | 上传新文档 |
| 文档详情 | /documents/:id | GET | 获取文档详情和版本历史 |
| 更新文档 | /documents/:id | PUT | 更新文档信息 |
| 删除文档 | /documents/:id | DELETE | 删除文档 |
| 下载文档 | /documents/:id/download | GET | 下载文档 |
| 版本历史 | /documents/:id/versions | GET | 获取文档版本列表 |
| 上传新版本 | /documents/:id/versions | POST | 上传文档新版本 |

### 9.2 数据模型

**documents 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(255) | 文档名称 |
| description | Text | 文档描述 |
| category_id | Integer | 分类ID（外键） |
| project_id | Integer | 关联项目ID（外键） |
| current_version | Integer | 当前版本号，默认1 |
| is_public | Boolean | 是否公开 |
| created_by | Integer | 创建人（外键） |

**document_versions 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| document_id | Integer | 文档ID（外键） |
| version_number | Integer | 版本号 |
| filename | String(255) | 文件名 |
| file_path | String(500) | 文件存储路径 |
| file_size | Integer | 文件大小 |
| mime_type | String(100) | MIME类型 |
| version_notes | Text | 版本说明 |
| is_current | Boolean | 是否为当前版本 |
| created_by | Integer | 上传人（外键） |

### 9.3 业务规则

- 文档支持版本管理，每次上传新版本累加版本号
- 可以查看和下载历史版本
- 文档可以关联到指定项目
- 支持文档分类和标签管理

### 9.4 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除文档 | - | 级联删除：所有版本历史、评论 |
| 删除项目 | - | 该项目下所有文档一并删除 |
| 删除文档分类 | 分类下有文档 | 提示：先转移或删除文档 |

### 9.5 状态与字段编辑限制

| 操作 | 可编辑字段 | 限制说明 |
|------|------------|----------|
| 更新文档信息 | name, description, category_id, tags | 可正常编辑 |
| 上传新版本 | - | 自动创建新版本，版本号+1 |
| 删除旧版本 | is_current=true | 禁止删除当前版本 |
| 下载历史版本 | - | 所有版本均可下载 |

---

## 10. 资源成本管理模块

### 10.1 功能说明

资源成本管理模块用于管理项目资源（人力、设备、物料）的分配和成本核算。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 资源列表 | /resources | GET | 获取资源列表 |
| 创建资源 | /resources | POST | 创建新资源 |
| 更新资源 | /resources/:id | PUT | 修改资源信息 |
| 删除资源 | /resources/:id | DELETE | 删除资源 |
| 资源分配 | /resources/allocations | POST | 分配资源到项目/任务 |
| 成本记录 | /resources/costs | POST | 记录项目成本 |
| 成本报表 | /resources/costs/report | GET | 获取成本统计报表 |

### 10.2 数据模型

**resources 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(200) | 资源名称 |
| resource_type | Enum | 资源类型：human/material/equipment/other |
| description | Text | 资源描述 |
| user_id | Integer | 关联用户ID（如果是人力） |
| unit_cost | Float | 单位成本 |
| currency | String(10) | 货币单位，默认CNY |
| is_available | Boolean | 是否可用 |
| max_capacity | Float | 最大容量（每月工时） |

**resource_allocations 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| resource_id | Integer | 资源ID（外键） |
| project_id | Integer | 项目ID（外键） |
| task_id | Integer | 任务ID（外键，可选） |
| allocation_type | String(50) | 分配类型：percentage/hours/units |
| allocated_value | Float | 分配值 |
| start_date | DateTime | 开始日期 |
| end_date | DateTime | 结束日期 |
| actual_usage | Float | 实际使用量 |
| actual_cost | Float | 实际成本 |
| status | Enum | 状态：pending/active/completed/cancelled |

**cost_records 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| project_id | Integer | 项目ID（外键） |
| task_id | Integer | 任务ID（外键，可选） |
| category | String(100) | 成本类别：labor/material/equipment/other |
| description | Text | 成本描述 |
| amount | Float | 金额 |
| cost_date | DateTime | 成本日期 |
| is_approved | Boolean | 是否已审批 |

### 10.3 资源类型说明

| 类型 | 说明 |
|------|------|
| human | 人力（员工、顾问） |
| material | 物料 |
| equipment | 设备 |
| other | 其他资源 |

### 10.4 业务规则

- 人力资源的user_id关联到系统用户
- 资源分配记录实际使用量
- 成本记录需要审批后生效

### 10.5 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除资源 | 资源有未完成的分配 | 提示：先取消或完成分配 |
| 删除资源 | - | 级联删除：资源分配记录 |
| 删除项目 | - | 该项目的资源分配、成本记录保留（历史） |
| 删除用户 | 用户有人力资源的分配 | 提示：先解除资源关联 |

### 10.6 状态与字段编辑限制

| 分配状态 | 可编辑字段 | 限制说明 |
|----------|------------|----------|
| pending | allocated_value, dates | 可调整分配计划 |
| active | actual_usage, actual_cost | 记录实际使用量 |
| completed | 无 | 完成后不可修改 |
| cancelled | 无 | 取消后不可恢复 |

### 11.1 功能说明

Issue问题管理模块用于追踪项目中的Bug、功能需求、改进建议等。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| Issue列表 | /issues | GET | 获取Issue列表，支持筛选 |
| 创建Issue | /issues | POST | 创建新Issue |
| Issue详情 | /issues/:id | GET | 获取Issue详情 |
| 更新Issue | /issues/:id | PUT | 修改Issue信息 |
| 删除Issue | /issues/:id | DELETE | 删除Issue |
| 添加评论 | /issues/:id/comments | POST | 添加Issue评论 |
| 附件上传 | /issues/:id/attachments | POST | 上传Issue附件 |

### 11.2 数据模型

**issues 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String(255) | Issue标题 |
| description | Text | Issue描述 |
| issue_type | Enum | 类型：bug/feature/improvement/question |
| status | Enum | 状态：open/in_progress/resolved/closed/reopened |
| priority | Enum | 优先级：low/medium/high/critical |
| project_id | Integer | 项目ID（外键） |
| task_id | Integer | 关联任务ID（外键，可选） |
| assignee_id | Integer | 处理人（外键） |
| reporter_id | Integer | 报告人（外键） |
| labels | String(500) | 标签，逗号分隔 |
| is_resolved | Boolean | 是否已解决 |
| resolved_at | DateTime | 解决时间 |

**issue_comments 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| issue_id | Integer | Issue ID（外键） |
| user_id | Integer | 评论人（外键） |
| content | Text | 评论内容 |
| mentioned_users | String(500) | 提及的用户ID |
| is_edited | Boolean | 是否已编辑 |

### 11.3 Issue类型说明

| 类型 | 说明 |
|------|------|
| bug | 缺陷/Bug |
| feature | 功能需求 |
| improvement | 改进建议 |
| question | 问题咨询 |

### 11.4 Issue状态说明

| 状态 | 说明 |
|------|------|
| open | 待处理 |
| in_progress | 处理中 |
| resolved | 已解决 |
| closed | 已关闭 |
| reopened | 已重开 |

### 11.5 业务规则

- Issue必须关联到项目
- Issue可以关联到具体任务
- 评论支持@提及用户
- 解决Issue时记录解决时间

### 11.6 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除项目 | - | 该项目下所有Issue一并删除 |
| 删除任务 | 该任务有关联Issue | 提示：先处理关联的Issue |
| 删除用户 | 用户有关联的Issue | 提示：先转移Issue的负责人 |

### 11.7 状态与字段编辑限制

| Issue状态 | 可编辑字段 | 限制说明 |
|----------|------------|----------|
| open | 全部字段 | 可正常编辑 |
| in_progress | 全部字段 | 可正常编辑 |
| resolved | description, labels | 只读字段：title, status, priority, assignee |
| closed | 无 | 完全只读 |
| reopened | 全部字段 | 可正常编辑 |

---

## 12. 团队协作模块

### 12.1 功能说明

团队协作模块负责项目团队成员的管理和协作功能。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 成员列表 | /team/:project_id/members | GET | 获取项目团队成员列表 |
| 添加成员 | /team/:project_id/members | POST | 添加成员到项目 |
| 移除成员 | /team/:project_id/members/:user_id | DELETE | 从项目移除成员 |
| 修改角色 | /team/:project_id/members/:user_id | PUT | 修改成员在项目中的角色 |
| 获取邀请链接 | /team/:project_id/invite | GET | 获取项目邀请链接 |
| 通过邀请加入 | /team/join/:token | POST | 使用邀请链接加入 |

### 12.2 团队角色

| 角色 | 说明 |
|------|------|
| owner | 项目所有者，拥有全部权限 |
| admin | 管理员，管理项目设置和成员 |
| member | 普通成员，参与任务协作 |
| viewer | 查看者，只能查看不能编辑 |

### 12.3 业务规则

- 项目所有者不能被移除
- 成员角色决定其操作权限
- 邀请链接有过期时间

### 12.4 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 移除成员 | 成员为项目所有者 | 禁止移除 |
| 移除成员 | 成员有未完成任务 | 提示：先转移任务 |
| 修改成员角色 | 目标角色权限高于当前用户 | 需管理员确认 |
| 删除用户 | 用户为项目成员 | 从所有项目中移除 |

---

## 13. 通知系统模块

### 13.1 功能说明

通知系统模块负责向用户发送站内通知和邮件通知。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 通知列表 | /notifications | GET | 获取当前用户的通知列表 |
| 标记已读 | /notifications/:id/read | PUT | 标记通知为已读 |
| 全部已读 | /notifications/read-all | PUT | 标记所有通知为已读 |
| 删除通知 | /notifications/:id | DELETE | 删除通知 |
| 通知设置 | /notifications/preferences | GET/PUT | 获取/修改通知偏好设置 |

### 13.2 通知类型

| 类型 | 触发场景 |
|------|----------|
| task_created | 任务创建时通知 |
| task_updated | 任务更新时通知 |
| task_assigned | 任务分配给用户时通知 |
| task_completed | 任务完成时通知 |
| project_created | 项目创建时通知 |
| project_updated | 项目更新时通知 |
| comment_mentioned | 评论中@提及用户时通知 |
| comment_replied | 评论收到回复时通知 |

### 13.3 数据模型

**notifications 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 接收用户（外键） |
| type | String(50) | 通知类型 |
| title | String(200) | 通知标题 |
| content | Text | 通知内容 |
| related_data | JSON | 关联数据（如task_id、project_id） |
| link | String(500) | 点击跳转链接 |
| is_read | Boolean | 是否已读 |
| created_at | DateTime | 创建时间 |

**notification_preferences 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID（外键） |
| email_task_created | Boolean | 邮件：任务创建通知 |
| email_task_assigned | Boolean | 邮件：任务分配通知 |
| email_comment_mentioned | Boolean | 邮件：@提及通知 |
| site_task_created | Boolean | 站内：任务创建通知 |
| site_task_assigned | Boolean | 站内：任务分配通知 |
| email_frequency | String(20) | 邮件频率：instant/daily/weekly |

### 13.4 邮件通知队列

邮件发送采用队列机制：
- 邮件先存入email_queue表
- 后台任务定期扫描队列发送邮件
- 发送失败可重试（默认3次）

### 13.5 业务规则

- 用户可以自定义每种通知类型的接收方式（站内/邮件/关闭）
- 站内通知默认开启，邮件通知可选
- 支持设置邮件汇总频率（实时/每日/每周）

### 13.6 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除项目 | - | 该项目的所有通知记录保留（记录历史） |
| 删除任务 | - | 该任务的待发送通知取消，已发送保留 |
| 删除用户 | - | 该用户的所有通知记录删除 |
| 禁用邮件通知 | - | 邮件队列中的邮件暂停发送 |

---

## 14. 审计日志模块

### 14.1 功能说明

审计日志模块记录系统中所有关键操作，用于安全追踪、问题排查和合规审计。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 日志列表 | /audit/logs | GET | 获取审计日志列表，支持筛选 |
| 日志详情 | /audit/logs/:id | GET | 获取单条日志详情 |
| 日志统计 | /audit/logs/summary | GET | 获取日志统计汇总 |
| 导出日志 | /audit/logs/export | GET | 导出审计日志 |

### 14.2 记录的操作类型

| 操作 | 说明 |
|------|------|
| login | 用户登录 |
| logout | 用户登出 |
| create | 创建资源 |
| update | 更新资源 |
| delete | 删除资源 |
| view | 查看资源 |
| export | 导出数据 |
| settings_changed | 设置变更 |

### 14.3 审计日志用途

**1. 安全追踪**
- 记录谁在什么时候做了什么操作
- 可追溯到具体的用户、IP地址、操作时间
- 用于发现异常操作行为

**2. 问题排查**
- 操作异常时可通过日志追溯原因
- 定位数据问题的来源
- 还原操作历史

**3. 合规需求**
- 满足企业审计要求
- 提供合规报告数据
- 支持定期审计检查

### 14.4 数据模型

**audit_logs 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 操作人（外键） |
| username | String(100) | 操作人用户名（缓存） |
| action | String(50) | 操作类型：create/update/delete/login等 |
| resource_type | String(50) | 资源类型：task/project/user等 |
| resource_id | Integer | 资源ID |
| old_value | JSON | 变更前的值 |
| new_value | JSON | 变更后的值 |
| ip_address | String(45) | IP地址 |
| user_agent | Text | 用户代理 |
| description | Text | 操作描述 |
| status | String(20) | 状态：success/failed |
| created_at | DateTime | 操作时间 |

**audit_log_summaries 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| date | DateTime | 日期 |
| total_actions | Integer | 总操作数 |
| login_count | Integer | 登录次数 |
| create_count | Integer | 创建次数 |
| update_count | Integer | 更新次数 |
| delete_count | Integer | 删除次数 |
| failed_count | Integer | 失败次数 |
| unique_users | Integer | 活跃用户数 |

### 14.5 业务规则

- 登录/登出操作自动记录审计日志
- 关键资源的CRUD操作需要调用audit_log()函数记录日志
- 日志数据不可修改，保证审计的完整性
- 日志默认保留期限为1年，可通过系统设置调整

### 14.6 当前状态说明

**注意**：目前审计日志列表为空，是正常的。原因如下：
- 后台的CRUD操作还没有集成调用audit_log()函数来记录日志
- 需要在各个API接口的业务逻辑中添加审计日志记录
- 该功能为后续增强功能，当前版本为预留接口

---

## 15. 审批流模块

### 15.1 功能说明

审批流模块提供多级审批流程配置和执行功能。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 审批流列表 | /workflows | GET | 获取审批流列表 |
| 创建审批流 | /workflows | POST | 创建新的审批流定义 |
| 审批流详情 | /workflows/:id | GET | 获取审批流详情 |
| 更新审批流 | /workflows/:id | PUT | 修改审批流配置 |
| 删除审批流 | /workflows/:id | DELETE | 删除审批流 |
| 提交审批 | /workflows/requests | POST | 提交审批申请 |
| 审批操作 | /workflows/requests/:id/approve | POST | 审批通过/拒绝 |
| 审批历史 | /workflows/requests/:id/history | GET | 获取审批历史 |

### 15.2 数据模型

**workflows 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(200) | 审批流名称 |
| description | Text | 审批流描述 |
| entity_type | String(50) | 适用实体类型：task/project/issue等 |
| status | Enum | 状态：draft/active/disabled |
| steps_config | JSON | 审批步骤配置 |
| created_by | Integer | 创建人（外键） |

**approval_requests 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| workflow_id | Integer | 审批流ID（外键） |
| entity_type | String(50) | 实体类型 |
| entity_id | Integer | 实体ID |
| current_step | Integer | 当前步骤索引 |
| status | Enum | 状态：pending/approved/rejected/cancelled |
| requested_by | Integer | 申请人（外键） |
| request_data | JSON | 申请数据快照 |
| result | Text | 审批结果说明 |
| decided_at | DateTime | 审批决定时间 |

**approval_actions 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| request_id | Integer | 审批请求ID（外键） |
| step | Integer | 审批步骤 |
| approver_id | Integer | 审批人（外键） |
| action | String(20) | 审批动作：approve/reject |
| comment | Text | 审批意见 |

### 15.3 审批状态说明

| 状态 | 说明 |
|------|------|
| pending | 待审批 |
| approved | 已通过 |
| rejected | 已拒绝 |
| cancelled | 已取消 |

### 15.4 业务规则

- 审批流支持多级审批（串行/并行）
- 每个步骤可以指定审批人或角色
- 审批拒绝后可以填写拒绝原因
- 审批通过后自动流转到下一步

### 15.5 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除审批流 | 审批流有进行中的申请 | 提示：先完成或取消申请 |
| 审批拒绝 | - | 申请人收到通知，可修改后重新提交 |
| 审批超时 | 审批人超过3天未处理 | 自动提醒审批人 |

### 15.6 状态与字段编辑限制

| 审批状态 | 可编辑字段 | 限制说明 |
|----------|------------|----------|
| pending | request_data | 可修改申请内容 |
| approved | result | 可填写审批意见 |
| rejected | result | 必须填写拒绝原因 |
| cancelled | 无 | 完全只读 |

### 16.1 功能说明

报表模块提供项目数据的统计分析和可视化展示。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 项目统计 | /reports/project-summary | GET | 获取项目汇总统计 |
| 任务统计 | /reports/task-summary | GET | 获取任务统计报表 |
| 团队绩效 | /reports/team-performance | GET | 获取团队绩效报表 |
| 趋势分析 | /reports/trends | GET | 获取趋势分析数据 |
| 导出报表 | /reports/export | GET | 导出报表数据 |

### 16.2 报表类型

| 报表名称 | 说明 |
|----------|------|
| 项目汇总 | 项目总数、进行中、已完成、归档数 |
| 任务统计 | 任务总数、各状态数量、逾期数量 |
| 团队绩效 | 成员完成任务数、工作量统计 |
| 趋势分析 | 任务完成趋势、里程碑达成率 |

### 16.3 业务规则

- 统计数据按项目/时间范围筛选
- 支持图表展示和数据导出
- 定时任务自动生成日报/周报

### 16.4 业务约束说明

| 操作 | 约束条件 | 说明 |
|------|----------|------|
| 查看报表 | 无权限 | 提示：需要报表查看权限 |
| 导出报表 | 数据量>10000条 | 提示：数据量过大，请缩小时间范围 |
| 生成定时报表 | 报表任务进行中 | 提示：请等待当前任务完成 |

### 17.1 功能说明

用户管理模块提供系统用户的增删改查和角色权限管理。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 用户列表 | /users | GET | 获取用户列表 |
| 创建用户 | /users | POST | 创建新用户 |
| 用户详情 | /users/:id | GET | 获取用户详情 |
| 更新用户 | /users/:id | PUT | 修改用户信息 |
| 删除用户 | /users/:id | DELETE | 删除用户 |
| 角色管理 | /users/roles | GET/POST | 获取/创建角色 |
| 部门管理 | /users/departments | GET/POST | 获取/创建部门 |

### 17.2 数据模型

**roles 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(50) | 角色名称，唯一 |
| description | String(255) | 角色描述 |
| permissions | String(1000) | 权限JSON字符串 |
| is_system | Boolean | 是否系统角色（不可删除） |

**user_profiles 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID，唯一 |
| avatar | String(500) | 头像URL |
| phone | String(20) | 电话 |
| department | String(100) | 部门 |
| position | String(100) | 职位 |
| theme | String(20) | 主题：light/dark |
| language | String(10) | 语言：zh-CN/en |
| timezone | String(50) | 时区 |
| last_login_at | DateTime | 最后登录时间 |
| login_count | Integer | 登录次数 |

**departments 表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 部门名称 |
| code | String(50) | 部门编码，唯一 |
| parent_id | Integer | 上级部门ID（支持层级） |
| description | String(500) | 部门描述 |
| is_active | Boolean | 是否启用 |

### 17.3 用户状态说明

| 状态 | 说明 |
|------|------|
| active | 正常活动 |
| inactive | 未激活 |
| suspended | 已停用 |

### 17.4 业务规则

- 超级管理员拥有全部权限
- 系统角色不可删除
- 用户可绑定部门和职位
- 用户可以设置个人偏好（主题、语言、时区）

### 17.5 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除角色 | 角色下有用户 | 提示：先转移用户到其他角色 |
| 删除角色 | is_system=true | 禁止删除系统角色 |
| 删除部门 | 部门下有用户 | 提示：先转移用户到其他部门 |
| 删除用户 | 用户有未完成任务 | 提示：先转移任务 |
| 删除用户 | 用户为超级管理员 | 禁止删除最后一个超级管理员 |

### 17.6 状态与字段编辑限制

| 用户状态 | 可编辑字段 | 限制说明 |
|----------|------------|----------|
| active | 全部字段 | 可正常编辑 |
| inactive | role_id, department | 只读字段：username, email, is_active |
| suspended | 无 | 完全只读，需管理员解除 |

---

## 18. AI智能助手模块

### 18.1 功能说明

AI智能助手模块提供基于大语言模型的智能问答和任务辅助功能。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 智能问答 | /ai/chat | POST | 向AI提问，获取回答 |
| 任务建议 | /ai/task-suggestions | POST | 获取任务拆分/优先级建议 |
| 内容生成 | /ai/generate | POST | 生成文档/报告草稿 |
| 总结功能 | /ai/summarize | POST | 对话/文档自动总结 |

### 18.2 功能场景

| 场景 | 说明 |
|------|------|
| 项目咨询 | 查询项目状态、任务进度等 |
| 任务拆分 | 将大任务拆分为可执行的小任务 |
| 优先级建议 | 根据紧急程度建议任务优先级 |
| 文案生成 | 生成任务描述、会议纪要等 |
| 智能总结 | 对长对话/文档自动提取要点 |

### 18.3 业务规则

- AI对话上下文最多保留10轮
- 支持自定义AI角色/人格
- 敏感操作需要二次确认

### 18.4 业务约束说明

| 操作 | 约束条件 | 说明 |
|------|----------|------|
| 连续提问 | 60秒内超过10次 | 提示：请求过于频繁，请稍后再试 |
| 生成内容 | 包含敏感词 | 提示：内容包含敏感信息，请修改 |
| 上下文超时 | 超过30分钟无交互 | 上下文已清除，需重新开始 |

### 19.1 功能说明

项目模板模块允许用户创建和使用项目模板，快速复制已有项目的结构。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 模板列表 | /project-templates | GET | 获取项目模板列表 |
| 创建模板 | /project-templates | POST | 从现有项目创建模板 |
| 模板详情 | /project-templates/:id | GET | 获取模板详情 |
| 更新模板 | /project-templates/:id | PUT | 修改模板信息 |
| 删除模板 | /project-templates/:id | DELETE | 删除模板 |
| 使用模板 | /project-templates/:id/use | POST | 使用模板创建项目 |

### 19.2 模板内容

项目模板包含以下内容：
- 项目基础信息（名称、描述、预算）
- 预设任务列表（含状态、优先级）
- 看板列配置
- 团队角色默认配置
- 文档分类预设置

### 19.3 业务规则

- 模板可以设置为公开或私有
- 使用模板创建项目时，可选择是否包含历史数据
- 系统提供预设模板（敏捷开发、瀑布模型等）

### 19.4 业务约束与级联关系

| 操作 | 约束条件 | 影响范围 |
|------|----------|----------|
| 删除模板 | is_system=true | 禁止删除系统预设模板 |
| 删除模板 | 模板已被使用过 | 提示：模板已被使用，删除后不影响已有项目 |
| 使用模板 | 模板包含的任务已在其他项目存在 | 提示：可能产生重复任务名称 |

### 19.5 模板使用限制

| 模板类型 | 可操作 | 限制说明 |
|----------|--------|----------|
| 系统模板 | 查看、使用 | 不可修改、不可删除 |
| 私有模板 | 全部操作 | 仅模板创建者可管理 |
| 公开模板 | 查看、使用、复制 | 不可删除他人创建的公开模板 |

### 20.1 功能说明

系统设置模块提供系统级别的配置参数管理。

| 功能 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 获取设置 | /settings | GET | 获取系统设置 |
| 更新设置 | /settings | PUT | 更新系统设置 |
| 设置分类 | /settings/categories | GET | 获取设置分类列表 |

### 20.2 设置分类

| 分类 | 说明 |
|------|------|
| 系统 | 系统名称、Logo、时区等 |
| 邮件 | SMTP服务器配置 |
| 安全 | 密码策略、会话超时等 |
| 通知 | 全局通知开关 |
| 日志 | 日志保留期限、审计开关 |

### 20.3 业务规则

- 系统设置只有管理员可以修改
- 部分设置修改后需要重启生效
- 敏感配置需要二次确认

### 20.4 业务约束说明

| 操作 | 约束条件 | 说明 |
|------|----------|------|
| 修改系统设置 | 非管理员用户 | 提示：需要管理员权限 |
| 修改SMTP配置 | 邮件正在发送中 | 提示：请等待邮件发送完成 |
| 修改日志保留期 | 新期限短于现有日志 | 提示：将删除超出新期限的日志 |
| 禁用审计日志 | - | 提示：禁用后将无法追踪操作 |

### 附录A：数据库表清单

| 表名 | 说明 |
|------|------|
| users | 用户表 |
| roles | 角色表 |
| user_profiles | 用户配置表 |
| departments | 部门表 |
| projects | 项目表 |
| tasks | 任务表 |
| comments | 评论表 |
| notifications | 通知表 |
| audit_logs | 审计日志表 |
| documents | 文档表 |
| document_versions | 文档版本表 |
| issues | Issue表 |
| resources | 资源表 |
| resource_allocations | 资源分配表 |
| cost_records | 成本记录表 |
| workflows | 审批流表 |
| approval_requests | 审批请求表 |
| gantt_tasks | 甘特图任务表 |
| gantt_dependencies | 甘特图依赖表 |

### 附录B：API路由前缀汇总

| 模块 | 路由前缀 |
|------|----------|
| 认证 | /api/v1/auth |
| 项目 | /api/v1/projects |
| 任务 | /api/v1/tasks |
| 看板 | /api/v1/kanban |
| 甘特图 | /api/v1/gantt |
| 日历 | /api/v1/calendar |
| 文档 | /api/v1/documents |
| 资源 | /api/v1/resources |
| Issue | /api/v1/issues |
| 团队 | /api/v1/team |
| 通知 | /api/v1/notifications |
| 审计 | /api/v1/audit |
| 审批流 | /api/v1/workflow |
| 报表 | /api/v1/reports |
| 用户 | /api/v1/users |
| AI | /api/v1/ai |
| 模板 | /api/v1/project-templates |
| 设置 | /api/v1/settings |
| 导出 | /api/v1/export |
| 国际化 | /api/v1/i18n |

---

## 附录

*本设计文档将作为测试参考依据，所有功能模块的测试用例应以本文档为准。*