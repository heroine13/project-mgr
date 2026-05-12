#!/bin/bash
# GitHub Codespaces / 本地开发 一键启动脚本

set -e

echo "============================================"
echo "  项目管理系统 - 启动脚本"
echo "============================================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 0. 停止已有服务
echo -e "${YELLOW}[0/5] 停止已有服务...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# 1. 检查并初始化数据库
echo -e "${YELLOW}[1/5] 检查数据库...${NC}"
# 后端使用相对路径 ./project_mgr.db（相对于 backend 目录）
if [ ! -f "backend/project_mgr.db" ]; then
    echo "数据库不存在，正在初始化..."
    python3 init_db.py
else
    echo "数据库已存在于 backend/project_mgr.db"
fi

# 2. 检测环境并配置
echo -e "${YELLOW}[2/5] 检测环境并配置...${NC}"

CODENAME=""
CORS_ORIGINS=""

if [ -n "$CODESPACE_NAME" ]; then
    CODENAME=$(echo "$CODESPACE_NAME" | sed 's/-5173$//;s/-8000$//;s/-3000$//;s/-[0-9]*$//')
fi

if [ -n "$CODENAME" ]; then
    # Codespace 环境
    FRONTEND_ORIGIN="https://${CODENAME}-5173.app.github.dev"
    BACKEND_ORIGIN="https://${CODENAME}-8000.app.github.dev"
    API_BASE_URL="${BACKEND_ORIGIN}/api/v1"
    WS_URL="wss://${CODENAME}-8000.app.github.dev/ws"
    CORS_ORIGINS="${FRONTEND_ORIGIN},${BACKEND_ORIGIN}"
    echo "Codespace 环境: $CODENAME"
    echo "  前端: $FRONTEND_ORIGIN"
    echo "  后端: $BACKEND_ORIGIN"
    echo "  CORS: $CORS_ORIGINS"
else
    # 本地开发环境
    API_BASE_URL="/api/v1"
    WS_URL="ws://localhost:8000"
    echo "本地开发环境"
fi

# 写入前端 .env.local
cat > frontend/.env.local << EOF
VITE_API_BASE_URL=$API_BASE_URL
VITE_WS_URL=$WS_URL
VITE_CODESPACES_BACKEND_URL=$BACKEND_ORIGIN
EOF
echo "已写入 frontend/.env.local"
echo "  VITE_API_BASE_URL=$API_BASE_URL"

# 3. 启动后端
echo -e "${YELLOW}[3/5] 启动后端服务 (端口 8000)...${NC}"
cd backend

# 使用环境变量传入 CORS 配置（直接在命令前设置）
if [ -n "$CORS_ORIGINS" ]; then
    CORS_ORIGINS="$CORS_ORIGINS" CODESPACE_ORIGIN="$BACKEND_ORIGIN" nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
else
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
fi

BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"
cd ..

sleep 3
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端启动成功${NC}"
else
    echo -e "${YELLOW}⚠ 后端可能还在启动中...${NC}"
fi

# 4. 启动前端
echo -e "${YELLOW}[4/5] 启动前端服务 (端口 5173)...${NC}"
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"
cd ..

sleep 5

# 5. 输出结果
echo -e "${YELLOW}[5/5] 检查服务状态...${NC}"

echo ""
echo "============================================"
echo -e "  ${GREEN}✅ 启动完成！${NC}"
echo "============================================"
echo ""

if [ -n "$CODENAME" ]; then
    FRONTEND_URL="https://${CODENAME}-5173.app.github.dev"
    BACKEND_URL="https://${CODENAME}-8000.app.github.dev"
    echo "访问地址:"
    echo "  前端: $FRONTEND_URL"
    echo "  后端: $BACKEND_URL"
    echo "  API文档: $BACKEND_URL/docs"
else
    echo "访问地址:"
    echo "  前端: http://localhost:5173"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
fi

echo ""
echo "登录账号:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "停止服务: kill $BACKEND_PID $FRONTEND_PID"

# 保存PID
echo "$BACKEND_PID $FRONTEND_PID" > .codespaces-pids