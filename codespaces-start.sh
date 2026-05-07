#!/bin/bash
# GitHub Codespaces 一键启动脚本
# 作者: dev

set -e

echo "============================================"
echo "  项目管理系统 - Codespaces 启动脚本"
echo "============================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 0. 停止已有服务
echo -e "${YELLOW}[0/5] 停止已有服务...${NC}"
if [ -f ".codespaces-pids" ]; then
    PIDS=$(cat .codespaces-pids)
    if [ -n "$PIDS" ]; then
        kill $PIDS 2>/dev/null || true
        echo "已停止已有服务"
    fi
fi
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# 1. 检查并初始化数据库
echo -e "${YELLOW}[1/5] 检查数据库...${NC}"
if [ ! -f "test_db/project_mgr.db" ]; then
    echo "数据库不存在，正在初始化..."
    python3 init_db.py
else
    echo "数据库已存在"
fi

# 2. 启动后端
echo -e "${YELLOW}[2/5] 启动后端服务 (端口 8000)...${NC}"
cd backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"
cd ..

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端启动成功${NC}"
else
    echo -e "${YELLOW}⚠ 后端可能还在启动中...${NC}"
fi

# 3. 检测环境并配置前端API地址

echo -e "${YELLOW}[3/5] 配置前端 API 地址...${NC}"

# 检测是否为 Codespace 环境
if [ -n "$CODESPACE" ] || [ -n "$GITHUB_CODESPACES" ]; then
    # Codespace 环境：使用后端的绝对地址
    if [ -n "$CODESPACE_NAME" ]; then
        # 将 -5173 后缀替换为 -8000
        CODENAME=$(echo "$CODESPACE_NAME" | sed 's/-5173$//')
        BACKEND_URL="https://${CODENAME}-8000.app.github.dev"
    else
        BACKEND_URL="http://localhost:8000"
    fi
    API_BASE_URL="${BACKEND_URL}/api/v1"
    echo "检测到 Codespace 环境: VITE_API_BASE_URL=$API_BASE_URL"
else
    # 本地开发环境：使用相对路径（Vite 代理）
    API_BASE_URL="/api/v1"
    echo "本地开发环境: VITE_API_BASE_URL=$API_BASE_URL"
fi

# 创建前端的 .env.local 文件（优先级高于 .env）
echo "VITE_API_BASE_URL=$API_BASE_URL" > frontend/.env.local
echo "已写入 frontend/.env.local"

# 4. 启动前端
echo -e "${YELLOW}[4/5] 启动前端服务 (端口 5173)...${NC}"
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"
cd ..

# 等待前端启动
sleep 5

echo -e "${YELLOW}[5/5] 检查服务状态...${NC}"

# 5. 输出结果

# 检测是否为 Codespace 环境
if [ -n "$CODESPACE" ] || [ -n "$GITHUB_CODESPACES" ]; then
    if [ -n "$CODESPACE_NAME" ]; then
        CODENAME=$(echo "$CODESPACE_NAME" | sed 's/-5173$//')
        FRONTEND_URL="https://${CODENAME}-5173.app.github.dev"
        BACKEND_URL="https://${CODENAME}-8000.app.github.dev"
    fi
fi

echo ""
echo "============================================"
echo -e "  ${GREEN}✅ 启动完成！${NC}"
echo "============================================"
echo ""
echo "访问地址:"
if [ -n "$CODESPACE" ] || [ -n "$GITHUB_CODESPACES" ]; then
    echo "  前端: $FRONTEND_URL"
    echo "  后端: $BACKEND_URL"
    echo "  API文档: $BACKEND_URL/docs"
else
    echo "  前端: http://localhost:5173"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
fi
echo ""
echo "登录账号:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "日志文件:"
echo "  后端日志: backend.log"
echo "  前端日志: frontend.log"
echo ""
echo "停止服务命令:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

# 保存PID到文件
echo "$BACKEND_PID $FRONTEND_PID" > .codespaces-pids

echo "按 Ctrl+C 停止服务"