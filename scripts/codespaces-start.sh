#!/bin/bash
# GitHub Codespaces 启动脚本

echo "========================================="
echo "项目管理系统 - 开发环境启动"
echo "========================================="

# 检查环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
export DATABASE_URL="sqlite:///./backend/project_mgr.db"

# 启动后端
echo "🚀 启动后端服务 (端口 8000)..."
cd backend

# 初始化数据库（如果不存在）
if [ ! -f "project_mgr.db" ]; then
    echo "📦 初始化数据库..."
    python3 -c "
import sys
sys.path.insert(0, '.')
from app.core.database import engine, Base
from app.models import *
print('Creating tables...')
Base.metadata.create_all(bind=engine)
print('Database initialized!')
"
fi

# 启动后端服务
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID)"
cd ..

# 等待后端启动
sleep 5

# 启动前端
echo "🚀 启动前端服务 (端口 5173)..."
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端已启动 (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "========================================="
echo "✅ 服务启动完成！"
echo "========================================="
echo "📱 前端: http://localhost:5173"
echo "🔧 后端: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 保持脚本运行
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait