# GitHub Codespaces 运行指南

## 前置条件
确保 Codespaces 环境已创建完成，依赖已安装。

## 启动步骤

### 1. 启动后端 (API)
在终端中执行：
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
等待看到 `Uvicorn running on http://0.0.0.0:8000`

### 2. 启动前端 (Vue)
打开**新的终端**执行：
```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```
等待看到 `Local: http://localhost:5173/`

### 3. 访问应用
- 前端: 点击端口 **5173** → **Open in Browser**
- 后端API: 点击端口 **8000** → **Open in Browser**
- API文档: http://localhost:8000/docs

## 登录测试
- 用户名: `admin`
- 密码: `admin123`

## 常见问题

### Q: 登录报错 "Network Error" 或 "CORS"
A: 后端没有启动，请先启动后端服务。

### Q: 登录一直转圈
A: 检查后端是否正常运行，确保端口 8000 可访问。

### Q: npm run dev 报错
A: 确保已经运行 `npm install`:
```bash
cd frontend
npm install --legacy-peer-deps
```

## 一键启动脚本
如果上述步骤繁琐，可以直接运行：
```bash
./scripts/codespaces-start.sh
```