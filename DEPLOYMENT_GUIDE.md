# 🧪 测试环境 & 🎬 演示环境 部署指南

---

## 环境概述

| 环境 | 用途 | 端口 | 数据库 | 特点 |
|------|------|------|--------|------|
| **测试环境** | 开发测试、单元测试 | 后端:8001, 前端:3001 | SQLite | 轻量、快速启动 |
| **演示环境** | 客户展示、功能演示 | 后端:8002, 前端:3002, Nginx:8080 | PostgreSQL | 数据持久化、包含演示数据 |

---

## 🚀 快速启动

### 测试环境

```bash
# 进入项目目录
cd project-mgr

# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 查看日志
docker-compose -f docker-compose.test.yml logs -f

# 停止
docker-compose -f docker-compose.test.yml down
```

访问地址：
- 前端: http://localhost:3001
- 后端API: http://localhost:8001
- API文档: http://localhost:8001/docs

---

### 演示环境

```bash
# 进入项目目录
cd project-mgr

# 启动演示环境
docker-compose -f docker-compose.demo.yml up -d

# 查看日志
docker-compose -f docker-compose.demo.yml logs -f

# 停止
docker-compose -f docker-compose.demo.yml down
```

访问地址：
- 前端: http://localhost:3002
- 后端API: http://localhost:8002
- Nginx代理: http://localhost:8080
- API文档: http://localhost:8002/docs

---

## 📋 环境配置

### 测试环境变量

| 变量 | 值 | 说明 |
|------|-----|------|
| DATABASE_URL | sqlite:///./test_db/project_mgr_test.db | SQLite数据库 |
| ENVIRONMENT | test | 环境标识 |
| DEBUG | true | 开启调试模式 |

### 演示环境变量

| 变量 | 值 | 说明 |
|------|-----|------|
| DATABASE_URL | postgresql://demo:demo123@postgres-demo:5432/... | PostgreSQL |
| ENVIRONMENT | demo | 环境标识 |
| DEBUG | false | 关闭调试 |
| ALLOWED_ORIGINS | http://demo.yourdomain.com,http://localhost:3002 | 允许的源 |

---

## 👤 演示账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 超级管理员权限 |
| 普通用户 | demo_user | admin123 | 普通用户权限 |
| 经理 | manager | admin123 | 项目管理权限 |
| 开发人员 | developer | admin123 | 开发人员权限 |

---

## 🔧 常用命令

```bash
# 查看运行中的容器
docker ps

# 查看日志
docker logs project-mgr-backend-test
docker logs project-mgr-backend-demo

# 进入容器
docker exec -it project-mgr-backend-test /bin/bash
docker exec -it project-mgr-postgres-demo psql -U demo

# 重启服务
docker-compose -f docker-compose.test.yml restart backend
docker-compose -f docker-compose.demo.yml restart backend

# 重建容器
docker-compose -f docker-compose.demo.yml build --no-cache
```

---

## 🆘 故障排除

### 数据库连接失败

```bash
# 检查数据库是否运行
docker ps | grep postgres

# 查看数据库日志
docker logs project-mgr-postgres-demo
```

### 端口冲突

```bash
# 查看端口占用
netstat -tulpn | grep 8001

# 修改端口
# 编辑 docker-compose.test.yml 修改端口映射
```

### 清理数据

```bash
# 测试环境: 删除SQLite数据库文件
rm -rf test_db/

# 演示环境: 删除PostgreSQL数据卷
docker volume rm project-mgr_postgres_demo_data
```

---

## 📁 文件结构

```
project-mgr/
├── docker-compose.test.yml      # 测试环境配置
├── docker-compose.demo.yml      # 演示环境配置
├── scripts/
│   └── demo-init.sql            # 演示数据初始化
└── nginx/
    └── nginx.demo.conf          # 演示环境Nginx配置
```

---

**版本**: 1.0.0  
**更新日期**: 2026-04-21