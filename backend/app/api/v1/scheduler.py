"""
定时任务管理 API
提供定时任务的配置、查询、管理接口
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..services.scheduler import scheduler, daily_summary_task, health_check_task
from ..services.notify import WeComNotifier, NotificationTemplates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/scheduler", tags=["调度管理"])


# ==================== 请求/响应模型 ====================

class TaskCreate(BaseModel):
    """创建任务请求"""
    task_id: str
    name: str
    trigger_type: str = "interval"  # interval, cron, daily
    trigger_config: Dict[str, Any]
    enabled: bool = True


class TaskUpdate(BaseModel):
    """更新任务请求"""
    name: Optional[str] = None
    enabled: Optional[bool] = None
    trigger_config: Optional[Dict[str, Any]] = None


class NotificationSend(BaseModel):
    """发送通知请求"""
    notification_type: str  # daily_summary, task_reminder, system_status
    content: Optional[str] = None
    mentioned_list: Optional[List[str]] = None
    priority: int = 5


class WebhookConfig(BaseModel):
    """Webhook 配置"""
    webhook_url: str


# ==================== 任务管理接口 ====================

@router.get("/tasks", summary="获取所有任务")
async def get_all_tasks():
    """获取所有定时任务列表"""
    tasks = scheduler.list_tasks()
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "total": len(tasks),
            "tasks": tasks
        }
    }


@router.get("/tasks/{task_id}", summary="获取任务详情")
async def get_task(task_id: str):
    """获取指定任务的详细信息"""
    task = scheduler.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {
        "code": 0,
        "msg": "success",
        "data": task
    }


@router.post("/tasks", summary="创建任务")
async def create_task(task_data: TaskCreate):
    """创建新的定时任务"""
    # 检查任务是否已存在
    if task_data.task_id in scheduler.tasks:
        raise HTTPException(status_code=400, detail="任务ID已存在")
    
    # 添加任务
    success = scheduler.add_task(
        task_id=task_data.task_id,
        name=task_data.name,
        func=lambda: {"status": "ok"},  # 临时函数
        trigger_type=task_data.trigger_type,
        trigger_config=task_data.trigger_config,
        enabled=task_data.enabled
    )
    
    if success:
        return {"code": 0, "msg": "任务创建成功", "data": {"task_id": task_data.task_id}}
    raise HTTPException(status_code=500, detail="任务创建失败")


@router.put("/tasks/{task_id}", summary="更新任务")
async def update_task(task_id: str, task_data: TaskUpdate):
    """更新定时任务配置"""
    task = scheduler.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task_data.name is not None:
        task.name = task_data.name
    if task_data.enabled is not None:
        if task_data.enabled:
            scheduler.enable_task(task_id)
        else:
            scheduler.disable_task(task_id)
    if task_data.trigger_config is not None:
        task.trigger_config = task_data.trigger_config
        # 重新创建触发器
        trigger = scheduler._create_trigger(task.trigger_type, task.trigger_config)
        scheduler.scheduler.remove_job(task_id)
        scheduler.scheduler.add_job(
            func=scheduler._execute_task,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
            args=[task_id]
        )
    
    return {"code": 0, "msg": "任务更新成功"}


@router.delete("/tasks/{task_id}", summary="删除任务")
async def delete_task(task_id: str):
    """删除定时任务"""
    success = scheduler.remove_task(task_id)
    if success:
        return {"code": 0, "msg": "任务删除成功"}
    raise HTTPException(status_code=404, detail="任务不存在")


@router.post("/tasks/{task_id}/run", summary="立即执行任务")
async def run_task_now(task_id: str, background_tasks: BackgroundTasks):
    """立即执行指定任务"""
    task = scheduler.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    def execute():
        scheduler._execute_task(task_id)
    
    background_tasks.add_task(execute)
    return {"code": 0, "msg": "任务已加入执行队列"}


# ==================== 通知管理接口 ====================

@router.post("/notify/send", summary="发送通知")
async def send_notification(notification: NotificationSend):
    """发送即时通知"""
    notifier = WeComNotifier()
    
    if not notifier.webhook_url:
        raise HTTPException(status_code=400, detail="Webhook URL 未配置，请先配置机器人")
    
    # 根据通知类型构建内容
    content = notification.content
    if notification.notification_type == "daily_summary":
        content = content or NotificationTemplates.daily_summary(5, 3)
    elif notification.notification_type == "task_reminder":
        content = content or NotificationTemplates.task_reminder("任务名称", "2026-04-20", "中")
    elif notification.notification_type == "system_status":
        content = content or NotificationTemplates.system_status("运行正常", "一切正常")
    
    # 发送消息
    success = notifier.send_markdown(content)
    
    if success:
        return {"code": 0, "msg": "通知发送成功"}
    raise HTTPException(status_code=500, detail="通知发送失败")


@router.get("/notify/queue", summary="获取通知队列")
async def get_notification_queue():
    """获取待发送的通知队列"""
    pending = scheduler.get_pending_notifications()
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "total": len(pending),
            "notifications": pending
        }
    }


# ==================== Webhook 配置接口 ====================

@router.get("/webhook/config", summary="获取 Webhook 配置")
async def get_webhook_config():
    """获取当前 Webhook 配置"""
    notifier = WeComNotifier()
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "configured": notifier.webhook_url is not None,
            "webhook_url": notifier.webhook_url[:20] + "..." if notifier.webhook_url else None
        }
    }


@router.post("/webhook/config", summary="配置 Webhook")
async def set_webhook_config(config: WebhookConfig):
    """配置企业微信机器人 Webhook"""
    notifier = WeComNotifier()
    success = notifier.save_webhook_url(config.webhook_url)
    
    if success:
        return {"code": 0, "msg": "Webhook 配置成功"}
    raise HTTPException(status_code=500, detail="Webhook 配置失败")


# ==================== 调度器状态接口 ====================

@router.get("/status", summary="获取调度器状态")
async def get_scheduler_status():
    """获取调度器运行状态"""
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "running": scheduler._running,
            "task_count": len(scheduler.tasks),
            "pending_notifications": len(scheduler.get_pending_notifications())
        }
    }


@router.post("/start", summary="启动调度器")
async def start_scheduler():
    """启动任务调度器"""
    if scheduler._running:
        return {"code": 0, "msg": "调度器已在运行中"}
    
    scheduler.start()
    return {"code": 0, "msg": "调度器已启动"}


@router.post("/stop", summary="停止调度器")
async def stop_scheduler():
    """停止任务调度器"""
    if not scheduler._running:
        return {"code": 0, "msg": "调度器已停止"}
    
    scheduler.stop()
    return {"code": 0, "msg": "调度器已停止"}


# ==================== 预定义任务配置接口 ====================

@router.post("/preset/daily-summary", summary="配置每日汇总任务")
async def setup_daily_summary(hour: int = 17, minute: int = 0):
    """配置每日汇总任务（默认每天 17:00 执行）"""
    success = scheduler.add_task(
        task_id="daily_summary",
        name="每日工作汇总",
        func=daily_summary_task,
        trigger_type="cron",
        trigger_config={"hour": hour, "minute": minute},
        enabled=True
    )
    
    if success:
        return {"code": 0, "msg": f"每日汇总任务已配置为每天 {hour}:{minute:02d} 执行"}
    raise HTTPException(status_code=500, detail="任务配置失败")


@router.post("/preset/health-check", summary="配置健康检查任务")
async def setup_health_check(interval_minutes: int = 30):
    """配置健康检查任务（默认每30分钟执行）"""
    success = scheduler.add_task(
        task_id="health_check",
        name="系统健康检查",
        func=health_check_task,
        trigger_type="interval",
        trigger_config={"minutes": interval_minutes},
        enabled=True
    )
    
    if success:
        return {"code": 0, "msg": f"健康检查任务已配置为每 {interval_minutes} 分钟执行"}
    raise HTTPException(status_code=500, detail="任务配置失败")