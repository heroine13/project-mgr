"""
WebSocket消息处理器
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import WebSocket
from app.websocket.connection_manager import connection_manager
from app.crud import crud_comment


class MessageHandler:
    """WebSocket消息处理器"""
    
    def __init__(self):
        self.message_handlers = {
            "comment": self.handle_comment_message,
            "typing": self.handle_typing_message,
            "reaction": self.handle_reaction_message,
            "read_status": self.handle_read_status_message,
            "ping": self.handle_ping_message
        }
    
    async def handle_message(self, websocket: WebSocket, message: str, user_id: int, project_id: int) -> Dict[str, Any]:
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type in self.message_handlers:
                result = await self.message_handlers[message_type](data, user_id, project_id)
                return {"success": True, "type": message_type, **result}
            else:
                return {"success": False, "error": f"未知的消息类型: {message_type}"}
                
        except json.JSONDecodeError:
            return {"success": False, "error": "消息格式错误"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def handle_comment_message(self, data: Dict[str, Any], user_id: int, project_id: int) -> Dict[str, Any]:
        """处理评论消息"""
        comment_data = data.get("data", {})
        
        # 验证必要字段
        required_fields = ["task_id", "content"]
        for field in required_fields:
            if field not in comment_data:
                return {"error": f"缺少必要字段: {field}"}
        
        # 这里简化处理，实际应该调用CRUD操作保存评论到数据库
        # 为了演示，我们创建模拟的评论数据
        comment = {
            "id": self._generate_id(),
            "task_id": comment_data["task_id"],
            "user_id": user_id,
            "content": comment_data["content"],
            "mentions": comment_data.get("mentions", ""),
            "created_at": datetime.utcnow().isoformat(),
            "user": {
                "id": user_id,
                "name": f"用户{user_id}",
                "avatar": None
            }
        }
        
        # 广播评论
        broadcast_count = await connection_manager.broadcast_comment(comment, project_id)
        
        # 处理提及
        mentions = comment_data.get("mentions", "")
        if mentions:
            mentioned_user_ids = [int(uid) for uid in mentions.split(",") if uid]
            for mentioned_id in mentioned_user_ids:
                mention_data = {
                    "comment_id": comment["id"],
                    "mentioned_user_id": mentioned_id,
                    "project_id": project_id,
                    "comment_content": comment["content"][:100]  # 截取前100字符
                }
                
                # 发送提及通知
                await connection_manager.broadcast_mention(mention_data, mentioned_id)
        
        return {
            "comment": comment,
            "message": "评论已发送",
            "broadcast_count": broadcast_count
        }
    
    async def handle_typing_message(self, data: Dict[str, Any], user_id: int, project_id: int) -> Dict[str, Any]:
        """处理输入状态消息"""
        typing_data = data.get("data", {})
        
        # 广播输入状态
        broadcast_data = {
            "user_id": user_id,
            "task_id": typing_data.get("task_id"),
            "is_typing": typing_data.get("is_typing", False),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        broadcast_count = await connection_manager.broadcast_typing_status(
            broadcast_data, project_id
        )
        
        return {
            "typing_status": broadcast_data,
            "broadcast_count": broadcast_count
        }
    
    async def handle_reaction_message(self, data: Dict[str, Any], user_id: int, project_id: int) -> Dict[str, Any]:
        """处理表情反应消息"""
        reaction_data = data.get("data", {})
        
        # 验证必要字段
        required_fields = ["comment_id", "reaction"]
        for field in required_fields:
            if field not in reaction_data:
                return {"error": f"缺少必要字段: {field}"}
        
        # 广播反应
        broadcast_data = {
            "user_id": user_id,
            "comment_id": reaction_data["comment_id"],
            "reaction": reaction_data["reaction"],
            "action": reaction_data.get("action", "add")
        }
        
        broadcast_count = await connection_manager.broadcast_reaction(broadcast_data, project_id)
        
        return {
            "reaction": broadcast_data,
            "broadcast_count": broadcast_count
        }
    
    async def handle_read_status_message(self, data: Dict[str, Any], user_id: int, project_id: int) -> Dict[str, Any]:
        """处理已读状态消息"""
        read_data = data.get("data", {})
        
        # 这里简化处理，实际应该更新数据库中的已读状态
        
        return {
            "read_status": read_data,
            "message": "已读状态已更新"
        }
    
    async def handle_ping_message(self, data: Dict[str, Any], user_id: int, project_id: int) -> Dict[str, Any]:
        """处理心跳消息"""
        return {
            "pong": True,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "project_id": project_id
        }
    
    def _generate_id(self) -> int:
        """生成ID（这里简化处理，实际应该从数据库生成）"""
        import random
        return random.randint(1000, 9999)
    
    async def handle_system_message(self, message_type: str, data: Dict[str, Any], project_id: int) -> int:
        """处理系统消息"""
        system_messages = {
            "user_joined": "用户加入",
            "user_left": "用户离开",
            "task_created": "任务创建",
            "task_updated": "任务更新",
            "task_deleted": "任务删除",
            "project_updated": "项目更新"
        }
        
        if message_type not in system_messages:
            return 0
        
        message_data = {
            "type": "system_notification",
            "subtype": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "message": system_messages[message_type]
        }
        
        return await connection_manager.broadcast_to_project(
            json.dumps(message_data),
            project_id
        )


# 创建全局消息处理器实例
message_handler = MessageHandler()