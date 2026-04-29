"""
WebSocket API端点
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.websocket.connection_manager import connection_manager
from app.websocket.message_handler import message_handler
from app.core.database import get_db
from app.auth import verify_token

router = APIRouter()


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """WebSocket端点"""
    # 验证Token获取用户ID（这里简化处理）
    # 实际应该验证JWT token
    user_id = 1  # 从token解析用户ID，这里暂时固定
    
    try:
        # 连接到项目房间
        connected = await connection_manager.connect(websocket, project_id, user_id)
        if not connected:
            await websocket.close()
            return
        
        print(f"用户 {user_id} 已连接到项目 {project_id}")
        
        # 主消息循环
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                
                # 处理消息
                result = await message_handler.handle_message(
                    websocket, data, user_id, project_id
                )
                
                # 发送处理结果
                await websocket.send_text(json.dumps(result))
                
            except WebSocketDisconnect:
                print(f"用户 {user_id} 主动断开连接")
                break
            except Exception as e:
                print(f"处理消息时出错: {e}")
                # 发送错误消息
                await websocket.send_text(json.dumps({
                    "success": False,
                    "error": str(e),
                    "timestamp": "2026-04-06T14:30:00Z"
                }))
                
    except Exception as e:
        print(f"WebSocket连接异常: {e}")
    finally:
        # 断开连接
        await connection_manager.disconnect(websocket)
        print(f"用户 {user_id} 已从项目 {project_id} 断开连接")


@router.get("/ws/status")
async def get_websocket_status():
    """获取WebSocket连接状态"""
    return {
        "active_projects": connection_manager.get_connected_projects(),
        "project_stats": {
            project_id: connection_manager.get_active_users_count(project_id)
            for project_id in connection_manager.get_connected_projects()
        },
        "total_connections": sum(
            connection_manager.get_active_users_count(project_id)
            for project_id in connection_manager.get_connected_projects()
        )
    }


@router.post("/ws/broadcast/{project_id}")
async def broadcast_message(
    project_id: int,
    message_type: str,
    message_data: dict,
    current_user: dict = Depends(verify_token)
):
    """广播消息到项目房间（需要管理员权限）"""
    # 检查权限（这里简化处理）
    # 实际应该检查用户是否有项目管理员权限
    
    if message_type == "comment":
        broadcast_count = await connection_manager.broadcast_comment(message_data, project_id)
    elif message_type == "task_update":
        broadcast_count = await connection_manager.broadcast_task_update(message_data, project_id)
    elif message_type == "notification":
        broadcast_count = await connection_manager.broadcast_notification(message_data, project_id)
    else:
        return {"success": False, "error": f"不支持的消息类型: {message_type}"}
    
    return {
        "success": True,
        "message": f"消息已广播到 {broadcast_count} 个连接",
        "broadcast_count": broadcast_count,
        "project_id": project_id
    }


@router.post("/ws/notify/{user_id}")
async def notify_user(
    user_id: int,
    notification_data: dict,
    current_user: dict = Depends(verify_token)
):
    """发送通知给特定用户"""
    success = await connection_manager.send_to_user(
        json.dumps({
            "type": "personal_notification",
            "data": notification_data,
            "timestamp": "2026-04-06T14:30:00Z"
        }),
        user_id
    )
    
    if success:
        return {
            "success": True,
            "message": f"通知已发送给用户 {user_id}"
        }
    else:
        return {
            "success": False,
            "error": f"用户 {user_id} 未连接或发送失败"
        }


@router.get("/ws/test")
async def websocket_test():
    """WebSocket测试端点"""
    return {
        "message": "WebSocket服务已启动",
        "endpoints": {
            "websocket": "/api/v1/ws/{project_id}",
            "status": "/api/v1/ws/status",
            "broadcast": "/api/v1/ws/broadcast/{project_id}",
            "notify": "/api/v1/ws/notify/{user_id}"
        },
        "supported_message_types": [
            "comment",
            "typing", 
            "reaction",
            "read_status",
            "ping"
        ]
    }