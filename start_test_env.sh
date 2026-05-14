#!/bin/bash

# project-mgr 测试环境启动脚本
# 用法: ./start_test_env.sh

set -e

echo "=========================================="
echo "  项目进度管理系统 - 测试环境启动脚本"
echo "=========================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js"
    exit 1
fi

# 检查并创建虚拟环境
echo ""
echo "📦 检查后端依赖..."
if [ ! -d "venv" ]; then
    echo "  创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "  安装后端依赖..."
source venv/bin/activate
pip install --quiet fastapi uvicorn sqlalchemy pydantic pydantic-settings pyjwt cryptography apscheduler pymysql

# 启动后端
echo ""
echo "🚀 启动后端服务 (端口 8000)..."
cd backend
if [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
fi
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "  后端 PID: $BACKEND_PID"
cd ..

# 等待后端启动
sleep 3
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ 后端启动成功"
else
    echo "  ⚠️ 后端可能还在启动中"
fi

# 启动前端
echo ""
echo "🚀 启动前端服务 (端口 5173)..."
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "  前端 PID: $FRONTEND_PID"
cd ..

# 等待前端启动
sleep 5
if curl -s -I http://localhost:5173/ > /dev/null 2>&1; then
    echo "  ✅ 前端启动成功"
else
    echo "  ⚠️ 前端可能还在启动中"
fi

# 输出结果
echo ""
echo "=========================================="
echo "  🎉 测试环境启动完成!"
echo "=========================================="
echo ""
echo "📍 访问地址:"
echo "  - 后端 API: http://localhost:8000"
echo "  - API 文档:   http://localhost:8000/docs"
echo "  - 前端页面:   http://localhost:5173"
echo ""
echo "📝 日志位置:"
echo "  - 后端日志: logs/backend.log"
echo "  - 前端日志: logs/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "  pkill -f uvicorn"
echo "  pkill -f vite"
echo ""

# 保存 PID
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid