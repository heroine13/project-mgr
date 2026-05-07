#!/bin/bash
# GitHub Codespaces / 本地开发 一键启动脚本

set -e

echo "============================================"
echo "  项目管理系统 - 启动脚本"
echo "============================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 0. 停止已有服务
echo -e "${YELLOW}[0/4] 停止已有服务...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1
echo "已清理旧进程"

# 1. 检查并初始化数据库
echo -e "${YELLOW}[1/4] 检查数据库...${NC}"
if [ ! -f "test_db/project_mgr.db" ]; then
    echo "数据库不存在，正在初始化..."
    python3 init_db.py
else
    echo "数据库已存在"
fi

# 2. 启动后端 (端口 8000)
echo -e "${YELLOW}[2/4] 启动后端服务 (端口 8000)...${NC}"
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

# 3. 启动前端 (端口 5173)
echo -e "${YELLOW}[3/4] 启动前端服务 (端口 5173)...${NC}"
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"
cd ..

sleep 5

# 4. 输出结果
echo -e "${YELLOW}[4/4] 检查服务状态...${NC}"

# 检测运行环境
IS_CODESPACE=false
CODENAME=""

# 检查是否是 Codespace 环境
if [ -n "$CODESPACE_NAME" ]; then
    # CODESPACE_NAME 格式示例: improved-space-couscous-69jxq6grp47g2rp9p-5173
    CODENAME=$(echo "$CODESPACE_NAME" | sed 's/-5173$//;s/-8000$//;s/-3000$//;s/-[0-9]*$//')
    IS_CODESPACE=true
elif hostname | grep -q "codesandbox\\|github.dev"; then
    # 备用检测方法
    CODENAME=$(hostname | sed 's/-[0-9]*$//')
    IS_CODESPACE=true
fi

echo ""
echo "============================================"
echo -e "  ${GREEN}✅ 启动完成！${NC}"
echo "============================================"
echo ""

if [ "$IS_CODESPACE" = true ] && [ -n "$CODENAME" ]; then
    FRONTEND_URL="https://${CODENAME}-5173.app.github.dev"
    BACKEND_URL="https://${CODENAME}-8000.app.github.dev"
    echo "Codespace 环境检测成功"
    echo ""
    echo "访问地址:"
    echo "  前端: $FRONTEND_URL"
    echo "  后端: $BACKEND_URL"
    echo "  API文档: $BACKEND_URL/docs"
else
    echo "本地开发环境"
    echo ""
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
echo "日志文件:"
echo "  后端日志: backend.log"
echo "  前端日志: frontend.log"
echo ""
echo "停止服务: kill $BACKEND_PID $FRONTEND_PID"

# 保存PID
echo "$BACKEND_PID $FRONTEND_PID" > .codespaces-pids