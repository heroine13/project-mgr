# Day 4下午开发进度报告 (2026-04-06)

## ✅ 当前状态
- **时间**: 开始实施Day 4下午计划
- **开发阶段**: 高级功能开发 (Day 4)
- **下午目标**: 实时评论系统、通知系统、导出功能开发

## 🎯 下午开发计划执行

### 第一阶段：实时评论系统 (13:00-15:00)

#### **1. WebSocket架构设计**
**技术选择**:
- **后端**: FastAPI WebSocket集成
- **前端**: Vue 3 WebSocket客户端
- **消息格式**: JSON消息协议
- **房间管理**: 基于项目的房间/频道机制

**架构设计**:
```
backend/websocket/
├── connection_manager.py   # WebSocket连接管理
├── message_handler.py      # 消息处理器
├── room_manager.py        # 房间/频道管理
└── events.py              # 事件定义

frontend/src/websocket/
├── websocket.ts           # WebSocket客户端
├── message.ts             # 消息类型和格式化
└── room.ts               # 房间管理
```

#### **2. 评论数据模型扩展**
需要在现有任务模型基础上扩展评论功能：

```python
# backend/app/models/comment.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Comment(Base):
    """评论模型"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 评论内容
    content = Column(Text, nullable=False)
    mentions = Column(String(500))  # 提及的用户ID列表，逗号分隔
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_edited = Column(Integer, default=0)  # 0:未编辑, 1:已编辑
    
    # 父评论（支持回复）
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    # 关系
    task = relationship("Task", backref="comments")
    project = relationship("Project", backref="comments")
    user = relationship("User", backref="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f"<Comment(id={self.id}, task_id={self.task_id}, user_id={self.user_id})>"


class Mention(Base):
    """提及记录模型"""
    __tablename__ = "mentions"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    mentioned_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_read = Column(Integer, default=0)  # 0:未读, 1:已读
    read_at = Column(DateTime, nullable=True)
    
    # 关系
    comment = relationship("Comment", backref="mention_records")
    mentioned_user = relationship("User", foreign_keys=[mentioned_user_id])
    
    def __repr__(self):
        return f"<Mention(id={self.id}, comment_id={self.comment_id}, user_id={self.mentioned_user_id})>"
```

#### **3. WebSocket连接管理器**
实现FastAPI WebSocket连接管理：

```python
# backend/app/websocket/connection_manager.py
from typing import Dict, List, Set
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 项目房间管理: {project_id: Set[WebSocket]}
        self.project_rooms: Dict[int, Set[WebSocket]] = {}
        # 用户连接映射: {user_id: WebSocket}
        self.user_connections: Dict[int, WebSocket] = {}
        # 连接锁
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, project_id: int, user_id: int):
        """连接WebSocket到项目房间"""
        await websocket.accept()
        
        async with self.lock:
            # 创建项目房间（如果不存在）
            if project_id not in self.project_rooms:
                self.project_rooms[project_id] = set()
            
            # 添加到项目房间
            self.project_rooms[project_id].add(websocket)
            
            # 记录用户连接
            self.user_connections[user_id] = websocket
            
        # 发送连接确认
        await self.send_personal_message(
            json.dumps({
                "type": "connection_established",
                "message": "WebSocket连接已建立",
                "project_id": project_id,
                "user_id": user_id
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
                "timestamp": str(datetime.utcnow())
            }),
            project_id,
            exclude=websocket
        )
    
    async def disconnect(self, websocket: WebSocket, project_id: int, user_id: int):
        """断开WebSocket连接"""
        async with self.lock:
            # 从项目房间移除
            if project_id in self.project_rooms:
                self.project_rooms[project_id].discard(websocket)
                # 如果房间为空，删除房间
                if not self.project_rooms[project_id]:
                    del self.project_rooms[project_id]
            
            # 移除用户连接
            if user_id in self.user_connections:
                del self.user_connections[user_id]
        
        # 广播用户离开通知
        await self.broadcast_to_project(
            json.dumps({
                "type": "user_left",
                "message": f"用户 {user_id} 已离开项目",
                "user_id": user_id,
                "project_id": project_id,
                "timestamp": str(datetime.utcnow())
            }),
            project_id
        )
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_text(message)
        except Exception:
            pass  # 忽略发送失败
    
    async def broadcast_to_project(self, message: str, project_id: int, exclude: WebSocket = None):
        """广播消息到项目房间"""
        if project_id not in self.project_rooms:
            return
        
        # 创建需要发送的连接列表
        connections = list(self.project_rooms[project_id])
        if exclude:
            connections = [conn for conn in connections if conn != exclude]
        
        # 异步发送消息
        tasks = []
        for connection in connections:
            try:
                tasks.append(connection.send_text(message))
            except Exception:
                continue
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_to_user(self, message: str, user_id: int):
        """发送消息给特定用户"""
        if user_id not in self.user_connections:
            return
        
        try:
            await self.user_connections[user_id].send_text(message)
        except Exception:
            pass
    
    async def broadcast_comment(self, comment_data: dict, project_id: int):
        """广播评论消息"""
        message = json.dumps({
            "type": "new_comment",
            "data": comment_data,
            "timestamp": str(datetime.utcnow())
        })
        
        await self.broadcast_to_project(message, project_id)
    
    async def broadcast_mention(self, mention_data: dict, mentioned_user_id: int):
        """广播提及通知"""
        message = json.dumps({
            "type": "mention_notification",
            "data": mention_data,
            "timestamp": str(datetime.utcnow())
        })
        
        # 发送给被提及的用户
        await self.send_to_user(message, mentioned_user_id)
    
    async def broadcast_task_update(self, task_data: dict, project_id: int):
        """广播任务更新"""
        message = json.dumps({
            "type": "task_updated",
            "data": task_data,
            "timestamp": str(datetime.utcnow())
        })
        
        await self.broadcast_to_project(message, project_id)
```

#### **4. WebSocket消息处理器**
处理不同类型的WebSocket消息：

```python
# backend/app/websocket/message_handler.py
import json
from typing import Dict, Any
from datetime import datetime
from fastapi import WebSocket

class MessageHandler:
    """WebSocket消息处理器"""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.message_handlers = {
            "comment": self.handle_comment_message,
            "typing": self.handle_typing_message,
            "read_status": self.handle_read_status_message,
            "reaction": self.handle_reaction_message
        }
    
    async def handle_message(self, websocket: WebSocket, message: str, user_id: int, project_id: int) -> Dict[str, Any]:
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type in self.message_handlers:
                return await self.message_handlers[message_type](data, user_id, project_id)
            else:
                return {"error": f"未知的消息类型: {message_type}"}
                
        except json.JSONDecodeError:
            return {"error": "消息格式错误"}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_comment_message(self, data: Dict[str, Any], user_id: int, project_id: int) -> Dict[str, Any]:
        """处理评论消息"""
        comment_data = data.get("data", {})
        
        # 验证必要字段
        required_fields = ["task_id", "content"]
        for field in required_fields:
            if field not in comment_data:
                return {"error": f"缺少必要字段: {field}"}
        
        # 保存评论到数据库（这里简化处理，实际应该调用CRUD操作）
        comment = {
            "id": self._generate_id(),  # 实际应该从数据库生成
            "task_id": comment_data["task_id"],
            "user_id": user_id,
            "content": comment_data["content"],
            "mentions": comment_data.get("mentions", ""),
            "created_at": str(datetime.utcnow()),
            "user": {
                "id": user_id,
                "name": f"用户{user_id}"  # 实际应该从数据库获取
            }
        }
        
        # 广播评论
        await self.connection_manager.broadcast_comment(comment, project_id)
        
        # 处理提及
        mentions = comment_data.get("mentions", "")
        if mentions:
            await self._process_mentions(mentions, comment["id"], project_id)
        
        return {
            "success": True,
            "comment": comment,
            "message": "评论已发送"
        }
    
    async def handle_typing_message(self, data: Dict[str, Any], user_id: int, project_id: int) -> Dict[str, Any]:
        """处理输入状态消息"""
        typing_data = data.get("data", {})
        
        # 广播输入状态
        await self.connection_manager.broadcast_to_project(
            json.dumps({
                "type": "user_typing",
                "data": {
                    "user_id": user_id,
                    "task_id": typing_data.get("task_id"),
                    "is_typing": typing_data.get("is_typing", False)
                },
                "timestamp": str(datetime.utcnow())
            }),
            project_id
        )
        
        return {"success": True}
    
    async def handle_read_status_message(self, data: Dict[str, Any], user_id: int, project_id: int) -> Dict[str, Any]:
        """处理已读状态消息"""
        read_data = data.get("data", {})
        
        # 更新已读状态（这里简化处理）
        # 实际应该更新数据库中的mention记录
        
        return {"success": True}
    
    async def handle_reaction_message(self, data: Dict[str, Any], user_id: int, project_id: int) -> Dict[str, Any]:
        """处理表情反应消息"""
        reaction_data = data.get("data", {})
        
        # 广播表情反应
        await self.connection_manager.broadcast_to_project(
            json.dumps({
                "type": "reaction",
                "data": {
                    "user_id": user_id,
                    "comment_id": reaction_data.get("comment_id"),
                    "reaction": reaction_data.get("reaction"),
                    "action": reaction_data.get("action", "add")  # add/remove
                },
                "timestamp": str(datetime.utcnow())
            }),
            project_id
        )
        
        return {"success": True}
    
    async def _process_mentions(self, mentions: str, comment_id: int, project_id: int):
        """处理提及的用户"""
        mentioned_user_ids = [int(uid) for uid in mentions.split(",") if uid]
        
        for user_id in mentioned_user_ids:
            mention_data = {
                "comment_id": comment_id,
                "mentioned_user_id": user_id,
                "project_id": project_id
            }
            
            # 发送提及通知
            await self.connection_manager.broadcast_mention(mention_data, user_id)
    
    def _generate_id(self) -> int:
        """生成ID（这里简化处理，实际应该从数据库生成）"""
        import random
        return random.randint(1000, 9999)
```

## 🚀 立即开始实施

### **步骤1：创建评论相关数据模型**
首先实现评论和提及的数据模型：

```python
# 创建评论数据模型文件
# backend/app/models/comment.py
# 上面已经提供了完整的Comment和Mention模型

# 需要更新backend/app/models/__init__.py
from .comment import Comment, Mention
__all__ = ["Comment", "Mention", ...]
```

### **步骤2：创建评论CRUD操作**
创建评论相关的数据库操作：

```python
# backend/app/crud/comment.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.comment import Comment, Mention
from app.schemas.comment import CommentCreate, CommentUpdate, MentionCreate

def create_comment(db: Session, comment_in: CommentCreate, user_id: int) -> Comment:
    """创建评论"""
    db_comment = Comment(
        **comment_in.dict(exclude_unset=True),
        user_id=user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # 创建提及记录
    if comment_in.mentions:
        mentioned_user_ids = [int(uid) for uid in comment_in.mentions.split(",") if uid]
        for mentioned_id in mentioned_user_ids:
            mention = Mention(
                comment_id=db_comment.id,
                mentioned_user_id=mentioned_id
            )
            db.add(mention)
    
    db.commit()
    return db_comment

def get_comments_by_task(db: Session, task_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
    """获取任务的评论列表"""
    return db.query(Comment).filter(Comment.task_id == task_id)\
        .order_by(Comment.created_at.desc())\
        .offset(skip).limit(limit).all()

# 更多CRUD函数...
```

### **步骤3：创建评论数据模式**
定义评论的Pydantic模式：

```python
# backend/app/schemas/comment.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class CommentBase(BaseModel):
    task_id: int = Field(..., description="任务ID")
    content: str = Field(..., description="评论内容")
    mentions: Optional[str] = Field(None, description="提及的用户ID列表")
    parent_id: Optional[int] = Field(None, description="父评论ID")

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, description="评论内容")
    is_edited: Optional[int] = Field(None, description="是否已编辑")

class CommentResponse(CommentBase):
    id: int
    user_id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    is_edited: int
    
    class Config:
        from_attributes = True

class MentionBase(BaseModel):
    comment_id: int = Field(..., description="评论ID")
    mentioned_user_id: int = Field(..., description="被提及的用户ID")

class MentionCreate(MentionBase):
    pass

class MentionResponse(MentionBase):
    id: int
    is_read: int
    read_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

### **步骤4：实现WebSocket端点**
在FastAPI中实现WebSocket端点：

```python
# backend/app/api/v1/endpoints/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.websocket.connection_manager import ConnectionManager
from app.websocket.message_handler import MessageHandler
from app.api import deps
from app.models import User

router = APIRouter()

# 创建连接管理器实例
connection_manager = ConnectionManager()
message_handler = MessageHandler(connection_manager)

@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: int,
    token: str,
    db: Session = Depends(deps.get_db)
):
    """WebSocket端点"""
    # 验证Token获取用户ID（这里简化处理）
    # 实际应该验证JWT token
    
    user_id = 1  # 从token解析用户ID，这里暂时固定
    
    # 连接到项目房间
    await connection_manager.connect(websocket, project_id, user_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            # 处理消息
            result = await message_handler.handle_message(
                websocket, data, user_id, project_id
            )
            
            # 发送处理结果
            await websocket.send_text(json.dumps(result))
            
    except WebSocketDisconnect:
        # 断开连接
        await connection_manager.disconnect(websocket, project_id, user_id)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        await connection_manager.disconnect(websocket, project_id, user_id)

@router.get("/ws/test")
async def websocket_test():
    """WebSocket测试端点"""
    return {"message": "WebSocket服务已启动"}
```

### **步骤5：前端WebSocket客户端实现**
创建Vue 3的WebSocket客户端：

```typescript
// frontend/src/websocket/websocket.ts
import { ref, computed } from 'vue'
import type { Comment, Mention } from '@/types/gantt'

class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectTimer: number | null = null
  private messageHandlers: Map<string, Function[]> = new Map()
  
  // 连接状态
  isConnected = ref(false)
  isConnecting = ref(false)
  lastError = ref<string | null>(null)
  
  // 连接配置
  private baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
  
  // 连接方法
  async connect(projectId: number, token: string): Promise<boolean> {
    if (this.isConnecting.value || this.isConnected.value) {
      return false
    }
    
    this.isConnecting.value = true
    this.lastError.value = null
    
    return new Promise((resolve) => {
      try {
        const wsUrl = `${this.baseUrl}/api/v1/ws/${projectId}?token=${token}`
        this.ws = new WebSocket(wsUrl)
        
        this.ws.onopen = () => {
          console.log('WebSocket连接已建立')
          this.isConnected.value = true
          this.isConnecting.value = false
          resolve(true)
        }
        
        this.ws.onclose = (event) => {
          console.log('WebSocket连接已关闭', event)
          this.isConnected.value = false
          this.isConnecting.value = false
          this.handleDisconnect()
        }
        
        this.ws.onerror = (error) => {
          console.error('WebSocket连接错误', error)
          this.lastError.value = 'WebSocket连接失败'
          this.isConnecting.value = false
          resolve(false)
        }
        
        this.ws.onmessage = (event) => {
          this.handleMessage(event.data)
        }
        
      } catch (error) {
        console.error('WebSocket连接异常', error)
        this.lastError.value = '连接异常'
        this.isConnecting.value = false
        resolve(false)
      }
    })
  }
  
  // 断开连接
  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    this.isConnected.value = false
    this.isConnecting.value = false
  }
  
  // 重新连接
  private handleDisconnect(): void {
    // 5秒后尝试重新连接
    this.reconnectTimer = window.setTimeout(() => {
      if (!this.isConnected.value && !this.isConnecting.value) {
        // 这里需要重新获取token和projectId
        // this.connect(projectId, token)
      }
    }, 5000)
  }
  
  // 发送消息
  send(message: any): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket未连接，无法发送消息')
      return false
    }
    
    try {
      const messageStr = typeof message === 'string' ? message : JSON.stringify(message)
      this.ws.send(messageStr)
      return true
    } catch (error) {
      console.error('发送WebSocket消息失败', error)
      return false
    }
  }
  
  // 发送评论
  sendComment(taskId: number, content: string, mentions: number[] = []): boolean {
    return this.send({
      type: 'comment',
      data: {
        task_id: taskId,
        content: content,
        mentions: mentions.join(',')
      }
    })
  }
  
  // 发送输入状态
  sendTypingStatus(taskId: number, isTyping: boolean): boolean {
    return this.send({
      type: 'typing',
      data: {
        task_id: taskId,
        is_typing: isTyping
      }
    })
  }
  
  // 发送反应
  sendReaction(commentId: number, reaction: string, action: 'add' | 'remove' = 'add'): boolean {
    return this.send({
      type: 'reaction',
      data: {
        comment_id: commentId,
        reaction: reaction,
        action: action
      }
    })
  }
  
  // 消息处理
  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data)
      const handlers = this.messageHandlers.get(message.type)
      
      if (handlers) {
        handlers.forEach(handler => handler(message))
      }
    } catch (error) {
      console.error('处理WebSocket消息失败', error, data)
    }
  }
  
  // 注册消息处理器
  on(messageType: string, handler: Function): void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, [])
    }
    this.messageHandlers.get(messageType)!.push(handler)
  }
  
  // 移除消息处理器
  off(messageType: string, handler: Function): void {
    if (this.messageHandlers.has(messageType)) {
      const handlers = this.messageHandlers.get(messageType)!
      const index = handlers.indexOf(handler)
      if (index !== -1) {
        handlers.splice(index, 1)
      }
    }
  }
}

// 导出单例实例
export const websocketClient = new WebSocketClient()

// Vue 3 Composition API封装
export function useWebSocket() {
  const client = websocketClient
  
  // 连接WebSocket
  const connect = async (projectId: number, token: string) => {
    return await client.connect(projectId, token)
  }
  
  // 断开连接
  const disconnect = () => {
    client.disconnect()
  }
  
  // 发送评论
  const sendComment = (taskId: number, content: string, mentions: number[] = []) => {
    return client.sendComment(taskId, content, mentions)
  }
  
  // 发送输入状态
  const sendTypingStatus = (taskId: number, isTyping: boolean) => {
    return client.sendTypingStatus(taskId, isTyping)
  }
  
  // 发送反应
  const sendReaction = (commentId: number, reaction: string, action: 'add' | 'remove' = 'add') => {
    return client.sendReaction(commentId, reaction, action)
  }
  
  // 监听消息
  const on = (messageType: string, handler: Function) => {
    client.on(messageType, handler)
  }
  
  // 取消监听
  const off = (messageType: string, handler: Function) => {
    client.off(messageType, handler)
  }
  
  return {
    isConnected: client.isConnected,
    isConnecting: client.isConnecting,
    lastError: client.lastError,
    connect,
    disconnect,
    sendComment,
    sendTypingStatus,
    sendReaction,
    on,
    off
  }
}
```

## 📊 下午进度追踪

### **已完成架构设计 (13:00-14:00)**
- ✅ WebSocket架构和技术选型
- ✅ 评论数据模型设计
- ✅ WebSocket连接管理器设计
- ✅ 消息处理器设计

### **正在实施 (14:00-15:00)**
1. **后端数据模型实现** - 进行中
2. **CRUD操作实现** - 进行中
3. **WebSocket端点实现** - 待开始
4. **前端WebSocket客户端** - 待开始

### **预计完成时间**
- **评论系统后端**: 15:00完成
- **WebSocket后端**: 16:00完成  
- **前端WebSocket集成**: 17:00完成
- **通知系统开发**: 18:00完成
- **导出功能**: 19:00完成

## 🔄 下一步实施计划

### **立即执行**
1. **14:00-15:00**: 完成后端评论数据模型和CRUD操作
2. **15:00-16:00**: 实现WebSocket端点和消息处理
3. **16:00-17:00**: 完成前端WebSocket客户端集成
4. **17:00-18:00**: 开始通知系统开发
5. **18:00-19:00**: 实现导出功能

### **风险评估**
1. **WebSocket复杂性**: 实时系统比预期复杂
   - **应对**: 分模块实现，先核心功能
2. **时间压力**: 下午任务较重
   - **应对**: 优先实现评论功能，通知和导出简化

### **质量保证**
- **单元测试**: 每个模块完成后立即测试
- **集成测试**: WebSocket连接测试
- **性能测试**: 消息发送和接收性能
- **安全测试**: WebSocket连接认证

**严格按照"按顺序实施"的要求，继续执行实时评论系统的代码实现！**