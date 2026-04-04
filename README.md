# 项目进度管理系统

## 项目概述
这是一个功能完整的项目进度管理系统，支持多语言界面（包括中文），用于团队协作和项目管理。

## 技术栈
- **前端**: Vue 3 + Element UI + i18next
- **后端**: FastAPI (Python) + SQLAlchemy
- **数据库**: MySQL / SQLite / SQL Server (多数据库支持)
- **部署**: Docker + Nginx
- **域名**: prjmanger.goldfon.cn

## 核心功能
1. 任务管理（创建、分配、跟踪）
2. 时间线与甘特图支持
3. 资源与成本管理
4. 报告与统计分析
5. 文档与附件管理
6. 项目问答功能 (Issue)

## 项目结构
```
project-mgr/
├── frontend/          # Vue 3前端应用
├── backend/           # FastAPI后端服务
├── docs/              # 项目文档
├── docker/            # Docker配置
├── scripts/           # 部署脚本
├── tests/             # 测试文件
└── README.md          # 项目说明
```

## 开发要求
- 按顺序执行开发计划
- 每天至少提交一次代码到GitHub
- 保持代码质量和文档完整性

## 快速开始
### 开发环境
```bash
# 克隆仓库
git clone <repository-url>
cd project-mgr

# 启动开发环境
docker-compose up -d

# 访问应用
# 前端: http://localhost:5173
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 生产部署
```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d
```

## 开发计划
### 第一阶段：基础架构搭建
- 项目骨架创建
- 开发环境配置
- 基础认证系统
- 多语言框架集成

### 第二阶段：核心功能开发
- 任务管理模块
- 时间线/甘特图
- 文档与附件管理
- 项目问答系统

### 第三阶段：高级功能完善
- 资源成本管理
- 报告统计分析
- 系统优化

### 第四阶段：部署上线
- 容器化部署
- 性能测试与优化
- 文档与培训材料

## 许可证
本项目采用MIT许可证。