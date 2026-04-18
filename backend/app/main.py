from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from app.api.v1 import scheduler
from app.services.scheduler import scheduler as task_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    task_scheduler.start()
    print("✅ 任务调度器已启动")
    yield
    # 关闭时
    task_scheduler.stop()
    print("🛑 任务调度器已停止")

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
app.include_router(scheduler.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)