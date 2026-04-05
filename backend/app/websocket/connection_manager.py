"""
WebSocket连接管理器
"""
import json
import asyncio
from typing import Dict, Set, Optional
from datetime import datetime
from fastapi import WebSocket


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 项目房间管理: {project_id: Set[WebSocket]}
        self.project_rooms: Dict[int, Set[WebSocket]] = {}
        # 用户连接映射: {user_id: WebSocket}
        self.user_connections: Dict[int, WebSocket] = {}
        # 用户项目映射: {user_id: project_id}
        self.user_projects: Dict[int, int] = {}
        # 连接锁
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, project_id: int, user_id: int) -> bool:
        """连接WebSocket到项目房间"""
        try:
            await websocket.accept()
            
            async with self.lock:
                # 创建项目房间（如果不存在）
                if project_id not in self.project_rooms:
                    self.project_rooms[project_id] = set()
                
                # 添加到项目房间
                self.project_rooms[project_id].add(websocket)
                
                # 记录用户连接和项目
                self.user_connections[user_id] = websocket
                self.user_projects[user_id] = project_id
            
            # 发送连接确认
            await self._send_personal_message(
                json.dumps({
                    "type": "connection_established",
                    "message": "WebSocket连接已建立",
                    "project_id": project_id,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                websocket
            )
            
            # 广播用户加入通知
            await self.broadcast_to_project(
                json.dumps({
                    "type": "user_joined",
                    "message": f"用户 {user_id} 已加入项目",
                    "user_id": user_id,
                    "project_id": project_id,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                project_id,
                exclude=websocket
            )
            
            return True
            
        except Exception as e:
            print(f"WebSocket连接失败: {e}")
            return False
    
    async def disconnect(self, websocket: WebSocket) -> bool:
        """断开WebSocket连接"""
        try:
            # 找到对应的用户ID和项目ID
            user_id = None
            project_id = None
            
            for uid, ws in self.user_connections.items():
                if ws == websocket:
                    user_id = uid
                    break
            
            if user_id and user_id in self.user_projects:
                project_id = self.user_projects[user_id]
            
            async with self.lock:
                # 从项目房间移除
                if project_id and project_id in self.project_rooms:
                    self.project_rooms[project_id].discard(websocket)
                    # 如果房间为空，删除房间
                    if not self.project_rooms[project_id]:
                        del self.project_rooms[project_id]
                
                # 移除用户映射
                if user_id:
                    if user_id in self.user_connections:
                        del self.user_connections[user_id]
                    if user_id in self.user_projects:
                        del self.user_projects[user_id]
            
            # 广播用户离开通知
            if project_id and user_id:
                await self.broadcast_to_project(
                    json.dumps({
                        "type": "user_left",
                        "message": f"用户 {user_id} 已离开项目",
                        "user_id": user_id,
                        "project_id": project_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    project_id
                )
            
            return True
            
        except Exception as e:
            print(f"WebSocket断开连接失败: {e}")
            return False
    
    async def _send_personal_message(self, message: str, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"发送个人消息失败: {e}")
    
    async def send_to_user(self, message: str, user_id: int) -> bool:
        """发送消息给特定用户"""
        if user_id not in self.user_connections:
            return False
        
        try:
            await self.user_connections[user_id].send_text(message)
            return True
        except Exception as e:
            print(f"发送给用户 {user_id} 的消息失败: {e}")
            return False
    
    async def broadcast_to_project(self, message: str, project_id: int, exclude: Optional[WebSocket] = None) -> int:
        """广播消息到项目房间，返回成功发送的连接数"""
        if project_id not in self.project_rooms:
            return 0
        
        # 创建需要发送的连接列表
        connections = list(self.project_rooms[project_id])
        if exclude:
            connections = [conn for conn in connections if conn != exclude]
        
        if not connections:
            return 0
        
        # 异步发送消息
        tasks = []
        for connection in connections:
            try:
                tasks.append(connection.send_text(message))
            except Exception:
                continue
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # 计算成功发送的数量
            success_count = sum(1 for result in results if not isinstance(result, Exception))
            return success_count
        
        return 0
    
    async def broadcast_comment(self, comment_data: dict, project_id: int) -> int:
        """广播评论消息"""
        message = json.dumps({
            "type": "new_comment",
            "data": comment_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return await self.broadcast_to_project(message, project_id)
    
    async def broadcast_mention(self, mention_data: dict, mentioned_user_id: int) -> bool:
        """发送提及通知给被提及的用户"""
        message = json.dumps({
            "type": "mention_notification",
            "data": mention_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return await self.send_to_user(message, mentioned_user_id)
    
    async def broadcast_task_update(self, task_data: dict, project_id: int) -> int:
        """广播任务更新"""
        message = json.dumps({
            "type": "task_updated",
            "data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return await self.broadcast_to_project(message, project_id)
    
    async def broadcast_typing_status(self, typing_data: dict, project_id: int, exclude: Optional[WebSocket] = None) -> int:
        """广播输入状态"""
        message = json.dumps({
            "type": "user_typing",
            "data": typing_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return await self.broadcast_to_project(message, project_id, exclude)
    
    async def broadcast_reaction(self, reaction_data: dict, project_id: int) -> int:
        """广播反应消息"""
        message = json.dumps({
            "type": "reaction",
            "data": reaction_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return await self.broadcast_to_project(message, project_id)
    
    async def broadcast_notification(self, notification_data: dict, project_id: int) -> int:
        """广播通知消息"""
        message = json.dumps({
            "type": "notification",
            "data": notification_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return await self.broadcast_to_project(message, project_id)
    
    def get_active_users_count(self, project_id: int) -> int:
        """获取项目的活跃用户数"""
        if project_id not in self.project_rooms:
            return 0
        return len(self.project_rooms[project_id])
    
    def get_connected_projects(self) -> list:
        """获取有连接的项目列表"""
        return list(self.project_rooms.keys())
    
    def get_user_project(self, user_id: int) -> Optional[int]:
        """获取用户当前所在的项目"""
        return self.user_projects.get(user_id)
    
    def is_user_connected(self, user_id: int) -> bool:
        """检查用户是否已连接"""
        return user_id in self.user_connections


# 创建全局连接管理器实例
connection_manager = ConnectionManager()