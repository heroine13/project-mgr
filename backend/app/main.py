from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from app.api.v1 import scheduler, reports
from app.api.v1 import integration, backup, workflow, kanban, audit
from app.api.v1 import reports as reports_enhanced
from app.api.v1 import ai
from app.api.v1 import calendar
from app.services.scheduler import scheduler as task_scheduler
from app.core.performance import cache_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    task_scheduler.start()
    
    # 自动配置每日汇报任务 (每天 17:00)
    from app.services.scheduler import daily_summary_task
    task_scheduler.add_task(
        task_id="daily_summary",
        name="每日自动汇报",
        func=daily_summary_task,
        trigger_type="cron",
        trigger_config={"hour": 17, "minute": 0},
        enabled=True
    )
    print("✅ 每日汇报任务已配置 (每天 17:00)")
    print("✅ 任务调度器已启动")
    yield
    # 关闭时
    task_scheduler.stop()
    # 清理缓存
    cache_manager.clear()
    print("🛑 任务调度器已停止")
    print("🛑 缓存已清理")

app = FastAPI(
    title="项目进度管理系统 API",
    description="项目进度管理系统的RESTful API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    from app.core.performance import cache_manager
    return {
        "status": "healthy",
        "cache_entries": len(cache_manager._cache),
        "cache_ttl_count": len(cache_manager._ttl)
    }

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
app.include_router(scheduler.router)
app.include_router(reports.router)
app.include_router(reports_enhanced.router)
app.include_router(integration.router)
app.include_router(backup.router)
app.include_router(workflow.router)
app.include_router(kanban.router)
app.include_router(audit.router)
app.include_router(ai.router)
app.include_router(calendar.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)