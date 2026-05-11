# 项目进度管理系统 - 部署环境配置指南

## 跨域配置说明

### 环境文件说明

| 文件 | 用途 | 是否提交 Git |
|------|------|-------------|
| `.env.example` | 配置模板（已有） | ✅ 提交 |
| `.env.development` | 本地开发环境 | ❌ 不提交 |
| `.env.production` | 生产环境 | ❌ 不提交 |
| `.env.local` | 本地临时覆盖 | ❌ 不提交 |

---

## 场景一：本地开发（含 Docker）

### 非 Docker 方式

1. 启动后端：
```bash
cd backend
# .env 中配置：
# BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:8000
# ENVIRONMENT=development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. 启动前端：
```bash
cd frontend
# .env.development 中已配置：
# VITE_API_BASE_URL=http://localhost:8000
# VITE_WS_URL=ws://localhost:8000
npm run dev
```

### Docker 方式

```bash
cd ..
docker compose -f docker-compose-simple.yml up
```

- 前端访问：`http://localhost:5173`
- 后端访问：`http://localhost:8000`
- Swagger 文档：`http://localhost:8000/docs`

---

## 场景二：非本地环境（不同域名/IP）

### 后端配置

在 `.env` 或 Docker 环境变量中设置：

```bash
ENVIRONMENT=production
BACKEND_CORS_ORIGINS="https://frontend.example.com,https://admin.example.com"
```

### 前端配置

编辑 `frontend/.env.production`：

```bash
# API 后端地址
VITE_API_BASE_URL=https://api.example.com

# WebSocket 地址
VITE_WS_URL=wss://api.example.com
```

### Nginx 配置

```bash
# docker-compose 中设置
environment:
  CORS_ORIGIN: "https://frontend.example.com"
```

---

## 场景三：GitHub Codespaces 部署

### 后端配置

在 Codespaces 中启动后端时设置环境变量：

```bash
export ENVIRONMENT=development
export BACKEND_CORS_ORIGINS="https://*.github.dev"
```

### 前端配置

创建 `frontend/.env.development`：

```bash
# Codespaces 中前端和后端都在不同端口
# 前端: https://<CODESPACE_NAME>-5173.app.github.dev
# 后端: https://<CODESPACE_NAME>-8000.app.github.dev

VITE_API_BASE_URL=https://$(gh codespace ports visibility 8000:public 2>/dev/null | grep 8000 | awk '{print $2}' || echo "http://localhost:8000")
VITE_WS_URL=wss://$(gh codespace ports visibility 8000:public 2>/dev/null | grep 8000 | awk '{print $2}' || echo "ws://localhost:8000")
```

**简化方式**（推荐）：

```bash
# .env.development
VITE_API_BASE_URL=https://<YOUR-CODESPACE>-8000.app.github.dev
VITE_WS_URL=wss://<YOUR-CODESPACE>-8000.app.github.dev
```

### Nginx 配置（可选）

```bash
CORS_ORIGIN="https://*.github.dev"
```

---

## 快速参考

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `ENVIRONMENT` | 运行环境 | `development` |
| `BACKEND_CORS_ORIGINS` | 允许的源（逗号分隔） | `http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000` |
| `VITE_API_BASE_URL` | 前端代理后端地址 | `http://localhost:8000` |
| `VITE_WS_URL` | WebSocket 地址 | `ws://localhost:8000` |
| `CORS_ORIGIN` | Nginx CORS 头 | `*` |
