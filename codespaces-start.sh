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
NC='\033[0m' # No Color

# 1. 检查并初始化数据库
echo -e "${YELLOW}[1/4] 检查数据库...${NC}"
if [ ! -f "test_db/project_mgr.db" ]; then
    echo "数据库不存在，正在初始化..."
    python3 init_db.py
else
    echo "数据库已存在"
fi

# 2. 启动后端
echo -e "${YELLOW}[2/4] 启动后端服务 (端口 8000)...${NC}"
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

# 3. 启动前端
echo -e "${YELLOW}[3/4] 启动前端服务 (端口 5173)...${NC}"
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"
cd ..

# 等待前端启动
sleep 5

echo -e "${YELLOW}[4/4] 检查服务状态...${NC}"

# 4. 输出结果
echo ""
echo "============================================"
echo -e "  ${GREEN}✅ 启动完成！${NC}"
echo "============================================"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
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