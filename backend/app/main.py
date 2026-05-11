import sys
import os

# 确保当前目录在 Python 路径中
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from app.core.config import settings

# 尝试导入，失败则跳过
try:
    from app.services.scheduler import scheduler as task_scheduler
    _scheduler_available = True
except Exception as e:
    print(f"⚠️ 调度器导入失败: {e}")
    _scheduler_available = False
    task_scheduler = None

try:
    from app.api.v1 import scheduler, reports
    _api_available = True
except Exception as e:
    print(f"⚠️ API导入失败: {e}")
    _api_available = False
    scheduler = None
    reports = None

try:
    from app.api.v1 import integration
except Exception as e:
    print(f"⚠️ integration导入失败: {e}")
    integration = None

async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    if _scheduler_available and task_scheduler:
        task_scheduler.start()
        print("✅ 任务调度器已启动")
    yield
    # 关闭时
    if _scheduler_available and task_scheduler:
        task_scheduler.stop()
        print("🛑 任务调度器已停止")

app = FastAPI(
    title="项目进度管理系统 API",
    description="项目进度管理系统的RESTful API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置 — 使用 config.py 中的环境变量
# 解析 BACKEND_CORS_ORIGINS（支持逗号分隔和 JSON 数组格式）
_cors_origins_raw = settings.BACKEND_CORS_ORIGINS if isinstance(settings.BACKEND_CORS_ORIGINS, list) else []
try:
    if isinstance(settings.BACKEND_CORS_ORIGINS, str) and settings.BACKEND_CORS_ORIGINS.strip():
        _cors_origins_raw = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")]
except Exception:
    _cors_origins_raw = []

# 开发环境或为空时允许所有来源；生产环境建议按环境配置具体域名
if settings.ENVIRONMENT == "development" or not _cors_origins_raw:
    _cors_origins = ["*"]
else:
    _cors_origins = _cors_origins_raw

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "项目进度管理系统 API",
        "version": "1.0.0",
        "status": "运行正常",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "message": "API测试端点",
        "endpoints": {
            "health": "/health",
            "root": "/",
            "docs": "/docs"
        }
    }

# 注册路由
if _api_available:
    # 导入并注册所有API路由
    try:
        from app.api.v1 import auth, projects, tasks
        app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
        app.include_router(projects.router, prefix="/api/v1/projects", tags=["项目"])
        app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["任务"])
    except Exception as e:
        print(f"⚠️ 核心API导入失败: {e}")
    
    if scheduler:
        app.include_router(scheduler.router)
    if reports:
        app.include_router(reports.router)
    if integration:
        try:
            app.include_router(integration.router)
        except:
            pass

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)