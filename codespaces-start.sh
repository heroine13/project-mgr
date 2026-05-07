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
if [ ! -f "test_db/project_mgr.db" ]; then
    echo "数据库不存在，正在初始化..."
    python3 init_db.py
else
    echo "数据库已存在"
fi

# 2. 启动后端 (端口 8000)
echo -e "${YELLOW}[2/5] 启动后端服务 (端口 8000)...${NC}"
cd backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"
cd ..

sleep 3
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端启动成功${NC}"
else
    echo -e "${YELLOW}⚠ 后端可能还在启动中...${NC}"
fi

# 3. 检测环境并配置前端API地址
echo -e "${YELLOW}[3/5] 配置前端 API 地址...${NC}"

# 检测 Codespace 环境
CODENAME=""
if [ -n "$CODESPACE_NAME" ]; then
    # CODESPACE_NAME 格式: xxx-xxx-xxx-xxx-5173
    # 提取基础名称 (去掉末尾的 -端口号)
    CODENAME=$(echo "$CODESPACE_NAME" | sed 's/-5173$//;s/-8000$//;s/-3000$//;s/-[0-9]*$//')
    echo "检测到 CODESPACE_NAME: $CODESPACE_NAME"
    echo "提取的 Codespace 名称: $CODENAME"
fi

# 写入 .env.local
if [ -n "$CODENAME" ]; then
    # Codespace 环境：使用绝对地址
    BACKEND_URL="https://${CODENAME}-8000.app.github.dev"
    API_BASE_URL="${BACKEND_URL}/api/v1"
    WS_URL="wss://${CODENAME}-8000.app.github.dev/ws"
    echo "Codespace 环境配置:"
    echo "  API: $API_BASE_URL"
    echo "  WS: $WS_URL"
else
    # 本地开发环境：使用相对路径
    API_BASE_URL="/api/v1"
    WS_URL="ws://localhost:8000"
    echo "本地开发环境配置:"
    echo "  API: $API_BASE_URL"
fi

# 写入 .env.local (优先级高于 .env)
cat > frontend/.env.local << EOF
VITE_API_BASE_URL=$API_BASE_URL
VITE_WS_URL=$WS_URL
EOF
echo "已写入 frontend/.env.local"

# 4. 启动前端 (端口 5173)
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