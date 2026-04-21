-- ========================================
-- 演示环境初始化SQL
-- 创建演示数据
-- ========================================

-- 创建管理员用户 (密码: admin123)
INSERT INTO users (id, username, email, hashed_password, is_active, is_superuser, created_at)
VALUES 
    (1, 'admin', 'admin@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIUeKQ4J4e', true, true, NOW()),
    (2, 'demo_user', 'demo@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIUeKQ4J4e', true, false, NOW()),
    (3, 'manager', 'manager@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIUeKQ4J4e', true, false, NOW()),
    (4, 'developer', 'dev@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIUeKQ4J4e', true, false, NOW())
ON CONFLICT DO NOTHING;

-- 创建项目
INSERT INTO projects (id, name, description, status, owner_id, created_at)
VALUES 
    (1, '演示项目A', '这是一个演示项目，用于展示系统功能', 'active', 1, NOW()),
    (2, '演示项目B', '第二个演示项目，展示团队协作', 'active', 1, NOW()),
    (3, '已完成项目', '展示已完成状态的项目', 'completed', 2, NOW())
ON CONFLICT DO NOTHING;

-- 创建任务
INSERT INTO tasks (id, title, description, status, priority, project_id, assignee_id, created_by, created_at)
VALUES 
    (1, '完成需求文档', '编写项目需求规格说明书', 'in_progress', 'high', 1, 3, 1, NOW()),
    (2, '设计数据库结构', '设计数据库ER图和表结构', 'pending', 'high', 1, 4, 1, NOW()),
    (3, '开发用户认证模块', '实现用户注册登录功能', 'completed', 'medium', 1, 4, 1, NOW()),
    (4, '前端界面开发', '开发项目管理界面', 'in_progress', 'medium', 1, 3, 1, NOW()),
    (5, '编写测试用例', '编写单元测试和集成测试', 'pending', 'low', 2, 4, 1, NOW()),
    (6, '部署上线', '部署到生产环境', 'pending', 'high', 3, 1, 1, NOW())
ON CONFLICT DO NOTHING;

-- 创建甘特图任务关系
INSERT INTO gantt_tasks (id, task_id, start_date, end_date, progress, dependencies)
VALUES 
    (1, 1, '2026-04-01', '2026-04-10', 80, NULL),
    (2, 2, '2026-04-08', '2026-04-15', 30, '1'),
    (3, 3, '2026-04-01', '2026-04-05', 100, NULL),
    (4, 4, '2026-04-10', '2026-04-20', 50, '2')
ON CONFLICT DO NOTHING;

-- 创建Issue问答
INSERT INTO issues (id, title, description, status, priority, project_id, created_by, created_at)
VALUES 
    (1, '如何创建新项目？', '我想知道如何创建新项目，请帮助', 'open', 'medium', 1, 2, NOW()),
    (2, '任务无法分配', '尝试分配任务时出现错误', 'resolved', 'high', 1, 3, NOW()),
    (3, '建议增加导出Excel功能', '希望能够导出Excel格式的报告', 'open', 'low', 2, 4, NOW())
ON CONFLICT DO NOTHING;

-- 创建文档
INSERT INTO documents (id, title, content, category, project_id, created_by, created_at)
VALUES 
    (1, '项目介绍', '# 演示项目A\n\n这是一个用于演示的项目管理系统。', 'readme', 1, 1, NOW()),
    (2, '使用手册', '# 使用手册\n\n本手册介绍系统使用方法。', 'manual', 1, 1, NOW()),
    (3, 'API文档', '# API接口文档\n\n详细API接口说明。', 'api', 1, 1, NOW())
ON CONFLICT DO NOTHING;

-- 创建团队成员关系
INSERT INTO project_members (project_id, user_id, role)
VALUES 
    (1, 1, 'owner'),
    (1, 3, 'member'),
    (1, 4, 'developer'),
    (2, 1, 'member'),
    (2, 3, 'owner'),
    (2, 4, 'developer'),
    (3, 2, 'owner'),
    (3, 3, 'member')
ON CONFLICT DO NOTHING;

-- 设置序列 (如果使用PostgreSQL)
SELECT setval('users_id_seq', 10, true);
SELECT setval('projects_id_seq', 10, true);
SELECT setval('tasks_id_seq', 10, true);