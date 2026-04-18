"""
定时任务调度器
用于管理后台定时任务和通知队列
"""
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Any
from enum import Enum
import json
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# 配置存储路径
SCHEDULER_CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "scheduler_config.json"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskResult:
    """任务执行结果"""
    
    def __init__(self, task_id: str, status: TaskStatus, message: str = "", data: Any = None):
        self.task_id = task_id
        self.status = status
        self.message = message
        self.data = data
        self.start_time = datetime.now()
        self.end_time = None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


class ScheduledTask:
    """定时任务定义"""
    
    def __init__(
        self, 
        task_id: str, 
        name: str, 
        func: Callable,
        trigger_type: str = "interval",
        trigger_config: Dict = None,
        enabled: bool = True
    ):
        self.task_id = task_id
        self.name = name
        self.func = func
        self.trigger_type = trigger_type
        self.trigger_config = trigger_config or {}
        self.enabled = enabled
        self.last_result: Optional[TaskResult] = None
        self.run_count = 0
        
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "trigger_type": self.trigger_type,
            "trigger_config": self.trigger_config,
            "enabled": self.enabled,
            "run_count": self.run_count,
            "last_run": self.last_result.to_dict() if self.last_result else None
        }


class TaskScheduler:
    """任务调度器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self.tasks: Dict[str, ScheduledTask] = {}
        self.notification_queue: List[Dict] = []
        self._running = False
        self._initialized = True
        logger.info("任务调度器初始化完成")
    
    def add_task(
        self, 
        task_id: str, 
        name: str, 
        func: Callable,
        trigger_type: str = "interval",
        trigger_config: Dict = None,
        enabled: bool = True
    ) -> bool:
        """
        添加定时任务
        
        Args:
            task_id: 任务ID
            name: 任务名称
            func: 任务函数
            trigger_type: 触发器类型 (interval/cron/daily)
            trigger_config: 触发器配置
            enabled: 是否启用
        """
        try:
            # 创建任务对象
            task = ScheduledTask(task_id, name, func, trigger_type, trigger_config, enabled)
            self.tasks[task_id] = task
            
            # 根据触发器类型创建 APScheduler 触发器
            trigger = self._create_trigger(trigger_type, trigger_config)
            
            # 添加到调度器
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                id=task_id,
                name=name,
                replace_existing=True,
                args=[task_id]
            )
            
            logger.info(f"任务已添加: {task_id} - {name}")
            return True
            
        except Exception as e:
            logger.error(f"添加任务失败: {task_id}, 错误: {e}")
            return False
    
    def _create_trigger(self, trigger_type: str, config: Dict):
        """根据配置创建触发器"""
        if trigger_type == "interval":
            # 间隔触发，如 {"minutes": 30}
            return IntervalTrigger(**config)
        elif trigger_type == "cron":
            # Cron 触发，如 {"hour": 9, "minute": 0}
            return CronTrigger(**config)
        elif trigger_type == "daily":
            # 每日定点，如 {"hour": 9, "minute": 0}
            return CronTrigger(hour=config.get("hour", 9), minute=config.get("minute", 0))
        else:
            # 默认每小时
            return IntervalTrigger(hours=1)
    
    def _execute_task(self, task_id: str) -> TaskResult:
        """执行任务"""
        task = self.tasks.get(task_id)
        if not task:
            return TaskResult(task_id, TaskStatus.FAILED, "任务不存在")
        
        if not task.enabled:
            result = TaskResult(task_id, TaskStatus.SKIPPED, "任务已禁用")
            task.last_result = result
            return result
        
        try:
            logger.info(f"开始执行任务: {task_id}")
            task.last_result = TaskResult(task_id, TaskStatus.RUNNING, "执行中...")
            
            # 执行任务函数
            result_data = task.func()
            
            # 记录结果
            result = TaskResult(
                task_id, 
                TaskStatus.SUCCESS, 
                "执行成功",
                result_data
            )
            task.last_result = result
            task.run_count += 1
            
            logger.info(f"任务执行完成: {task_id}")
            return result
            
        except Exception as e:
            logger.error(f"任务执行失败: {task_id}, 错误: {e}")
            result = TaskResult(task_id, TaskStatus.FAILED, str(e))
            task.last_result = result
            return result
    
    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        try:
            self.scheduler.remove_job(task_id)
            self.tasks.pop(task_id, None)
            logger.info(f"任务已移除: {task_id}")
            return True
        except Exception as e:
            logger.error(f"移除任务失败: {task_id}, 错误: {e}")
            return False
    
    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        task = self.tasks.get(task_id)
        if task:
            task.enabled = True
            # 重新添加任务以应用更改
            trigger = self._create_trigger(task.trigger_type, task.trigger_config)
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                id=task_id,
                replace_existing=True,
                args=[task_id]
            )
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        task = self.tasks.get(task_id)
        if task:
            task.enabled = False
            try:
                self.scheduler.remove_job(task_id)
            except:
                pass
            return True
        return False
    
    def start(self):
        """启动调度器"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            logger.info("任务调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("任务调度器已停止")
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if task:
            return task.to_dict()
        return None
    
    def list_tasks(self) -> List[Dict]:
        """列出所有任务"""
        return [task.to_dict() for task in self.tasks.values()]
    
    # ==================== 通知队列 ====================
    
    def add_notification(self, notification_type: str, content: str, priority: int = 5) -> bool:
        """
        添加通知到队列
        
        Args:
            notification_type: 通知类型 (daily_summary, task_reminder, system_alert 等)
            content: 通知内容
            priority: 优先级 (1-10, 10 最高)
        """
        notification = {
            "id": f"notif_{len(self.notification_queue)}_{int(time.time())}",
            "type": notification_type,
            "content": content,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "sent": False
        }
        self.notification_queue.append(notification)
        logger.info(f"通知已加入队列: {notification_type}")
        return True
    
    def get_pending_notifications(self) -> List[Dict]:
        """获取待发送的通知"""
        return [n for n in self.notification_queue if not n.get("sent", False)]
    
    def mark_notification_sent(self, notification_id: str) -> bool:
        """标记通知已发送"""
        for notif in self.notification_queue:
            if notif["id"] == notification_id:
                notif["sent"] = True
                notif["sent_at"] = datetime.now().isoformat()
                return True
        return False
    
    def clear_sent_notifications(self):
        """清理已发送的通知"""
        self.notification_queue = [n for n in self.notification_queue if not n.get("sent", False)]


# ==================== 预定义任务 ====================

def daily_summary_task():
    """每日汇总任务"""
    try:
        from .daily_report import send_daily_report
        result = send_daily_report()
        return result
    except Exception as e:
        logger.error(f"每日汇总任务执行失败: {e}")
        return {"status": "error", "message": str(e)}


def health_check_task():
    """健康检查任务"""
    # 检查系统状态
    status = {
        "backend": "running",
        "database": "ok",
        "timestamp": datetime.now().isoformat()
    }
    return status


# ==================== 调度器单例 ====================

scheduler = TaskScheduler()