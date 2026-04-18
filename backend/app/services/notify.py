"""
企业微信机器人通知服务
用于定时任务主动发送通知给用户
"""
import json
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

# 机器人 Webhook 配置存储路径
WEBHOOK_CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "webhook.json"


class WeComNotifier:
    """企业微信机器人通知器"""
    
    def __init__(self, webhook_url: str = None):
        """
        初始化通知器
        
        Args:
            webhook_url: 企业微信机器人 Webhook 地址
        """
        self.webhook_url = webhook_url or self._load_webhook_url()
        
    def _load_webhook_url(self) -> Optional[str]:
        """从配置文件加载 Webhook URL"""
        try:
            if WEBHOOK_CONFIG_PATH.exists():
                with open(WEBHOOK_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("webhook_url")
        except Exception as e:
            logger.warning(f"加载Webhook配置失败: {e}")
        return None
    
    def save_webhook_url(self, webhook_url: str) -> bool:
        """保存 Webhook URL 到配置文件"""
        try:
            # 确保目录存在
            WEBHOOK_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            config = {"webhook_url": webhook_url}
            with open(WEBHOOK_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.webhook_url = webhook_url
            logger.info("Webhook URL 已保存")
            return True
        except Exception as e:
            logger.error(f"保存Webhook配置失败: {e}")
            return False
    
    def send_text(self, content: str, mentioned_list: List[str] = None) -> bool:
        """
        发送文本消息
        
        Args:
            content: 消息内容
            mentioned_list: @成员的手机号列表
        
        Returns:
            bool: 发送是否成功
        """
        if not self.webhook_url:
            logger.error("Webhook URL 未配置")
            return False
            
        try:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": content,
                    "mentioned_list": mentioned_list or []
                }
            }
            
            response = requests.post(
                self.webhook_url, 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info(f"消息发送成功: {content[:50]}...")
                    return True
                else:
                    logger.error(f"消息发送失败: {result}")
                    return False
            return False
            
        except Exception as e:
            logger.error(f"发送消息异常: {e}")
            return False
    
    def send_markdown(self, content: str) -> bool:
        """
        发送 Markdown 消息
        
        Args:
            content: Markdown 格式的消息内容
        """
        if not self.webhook_url:
            logger.error("Webhook URL 未配置")
            return False
            
        try:
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            
            response = requests.post(
                self.webhook_url, 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info("Markdown 消息发送成功")
                    return True
                else:
                    logger.error(f"Markdown消息发送失败: {result}")
                    return False
            return False
            
        except Exception as e:
            logger.error(f"发送Markdown消息异常: {e}")
            return False
    
    def send_news(self, articles: List[Dict[str, str]]) -> bool:
        """
        发送图文消息
        
        Args:
            articles: 图文列表，每个包含 title, description, url, picurl
        """
        if not self.webhook_url:
            logger.error("Webhook URL 未配置")
            return False
            
        try:
            payload = {
                "msgtype": "news",
                "news": {
                    "articles": articles
                }
            }
            
            response = requests.post(
                self.webhook_url, 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info("图文消息发送成功")
                    return True
                else:
                    logger.error(f"图文消息发送失败: {result}")
                    return False
            return False
            
        except Exception as e:
            logger.error(f"发送图文消息异常: {e}")
            return False


# ==================== 通知模板 ====================

class NotificationTemplates:
    """通知模板"""
    
    @staticmethod
    def daily_summary(tasks_completed: int, tasks_pending: int, project_name: str = "项目进度管理系统") -> str:
        """每日工作汇总"""
        return f"""## 📊 每日工作汇总

**项目**: {project_name}

### ✅ 今日完成
- 完成任务数: **{tasks_completed}**

### ⏳ 待处理任务
- 剩余任务数: **{tasks_pending}**

---
> 祝您工作愉快！💪"""

    @staticmethod
    def task_reminder(task_name: str, due_date: str, priority: str = "中") -> str:
        """任务提醒"""
        emoji = "🔴" if priority == "高" else "🟡" if priority == "中" else "🟢"
        return f"""## ⏰ 任务提醒

{emoji} **任务**: {task_name}
- 📅 截止日期: {due_date}
- ⚡ 优先级: {priority}

请及时处理！"""

    @staticmethod
    def system_status(status: str, details: str = "") -> str:
        """系统状态通知"""
        return f"""## 🖥️ 系统状态

**状态**: {status}

{details}

---
> 自动发送