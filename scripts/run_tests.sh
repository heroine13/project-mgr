#!/bin/bash
# Test runner script for project-mgr

echo "========================================="
echo "项目进度管理系统 - 测试执行"
echo "========================================="

cd /root/.openclaw/workspace/project-mgr/backend

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "安装测试依赖..."
    pip install pytest pytest-asyncio httpx -q
fi

# Run tests
echo ""
echo "运行所有测试..."
pytest app/tests/ -v --tb=short

echo ""
echo "========================================="
echo "测试执行完成"
echo "========================================="

# Test coverage summary
echo ""
echo "测试覆盖率检查..."
pytest app/tests/ --cov=app --cov-report=term-missing 2>/dev/null || echo "（需要安装pytest-cov）"

echo ""
echo "测试结果汇总:"
echo "- test_auth.py: 认证测试"
echo "- test_tasks.py: 任务管理测试"
echo "- test_integration.py: 集成测试"
echo "- test_issues.py: Issue模块测试"
echo "- test_resources.py: 资源管理测试"
echo "- test_documents.py: 文档模块测试"