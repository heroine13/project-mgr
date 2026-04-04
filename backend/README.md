# 项目进度管理系统 - 后端 (FastAPI)

## 技术栈
- **框架**: FastAPI (Python 3.10+)
- **数据库ORM**: SQLAlchemy 2.0
- **数据库支持**: MySQL, SQLite, SQL Server (通过SQLAlchemy)
- **认证**: JWT令牌 (python-jose[cryptography])
- **异步支持**: async/await
- **数据验证**: Pydantic v2
- **任务队列**: Celery (可选)
- **缓存**: Redis (可选)
- **API文档**: 自动生成OpenAPI文档

## 项目结构
```
backend/
├── app/
│   ├── __init__.py           # 应用初始化
│   ├── main.py              # FastAPI应用入口
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # 配置文件
│   │   ├── database.py      # 数据库连接
│   │   ├── security.py      # 安全认证
│   │   └── dependencies.py  # 依赖注入
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── v1/             # API v1版本
│   │   │   ├── __init__.py
│   │   │   ├── auth.py     # 认证相关API
│   │   │   ├── tasks.py    # 任务管理API
│   │   │   ├── projects.py # 项目管理API
│   │   │   ├── issues.py   # 问答模块API
│   │   │   ├── documents.py # 文档管理API
│   │   │   └── reports.py  # 报告API
│   │   └── deps.py         # API依赖
│   ├── models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py         # 用户模型
│   │   ├── task.py         # 任务模型
│   │   ├── project.py      # 项目模型
│   │   ├── issue.py        # Issue模型
│   │   └── base.py         # 基础模型
│   ├── schemas/            # Pydantic模式
│   │   ├── __init__.py
│   │   ├── user.py         # 用户模式
│   │   ├── task.py         # 任务模式
│   │   └── base.py         # 基础模式
│   ├── crud/               # CRUD操作
│   │   ├── __init__.py
│   │   ├── base.py         # 基础CRUD
│   │   ├── user.py         # 用户CRUD
│   │   └── task.py         # 任务CRUD
│   ├── services/           # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py # 认证服务
│   │   └── task_service.py # 任务服务
│   ├── utils/             # 工具函数
│   │   ├── __init__.py
│   │   ├── security.py    # 安全工具
│   │   └── i18n.py        # 国际化工具
│   └── tests/             # 测试文件
│       ├── __init__.py
│       ├── conftest.py    # 测试配置
│       └── test_auth.py   # 认证测试
├── alembic/               # 数据库迁移
│   ├── versions/          # 迁移版本
│   └── env.py             # 迁移环境配置
├── requirements/          # 依赖文件
│   ├── base.txt           # 基础依赖
│   ├── dev.txt            # 开发依赖
│   └── prod.txt           # 生产依赖
├── .env.example          # 环境变量示例
├── docker-compose.yml    # Docker Compose配置
└── README.md            # 项目说明
```

## 数据库设计原则
1. **数据库抽象**: 使用SQLAlchemy ORM实现数据库无关性
2. **迁移友好**: 使用Alembic进行数据库迁移
3. **性能优化**: 适当的索引和查询优化
4. **数据完整性**: 外键约束和事务支持

## API设计规范
- RESTful API设计
- 版本控制 (v1, v2)
- 统一错误响应格式
- 分页和筛选支持
- 文档自动生成

## 认证与授权
- JWT令牌认证
- 基于角色的访问控制(RBAC)
- API密钥管理
- 用户会话管理

## 国际化支持
- 数据库存储多语言内容
- API支持语言参数
- 翻译内容缓存
- 后台翻译管理API

## 部署配置
- Docker容器化
- 多环境配置（开发/测试/生产）
- 健康检查端点
- 性能监控集成

## 开发环境设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements/dev.txt

# 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
pytest

# 数据库迁移
alembic upgrade head
```

## 代码质量
- 类型提示 (Type Hints)
- 代码格式化 (Black)
- 代码检查 (Flake8)
- 测试覆盖率 (pytest-cov)