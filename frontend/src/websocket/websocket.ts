/**
 * WebSocket客户端
 */
import { ref, computed } from 'vue'
import type { WebSocketMessage, CommentMessage, TypingMessage, ReactionMessage } from '@/types/websocket'

export class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectTimer: number | null = null
  private messageHandlers: Map<string, Function[]> = new Map()
  private pingInterval: number | null = null
  
  // 连接状态
  isConnected = ref(false)
  isConnecting = ref(false)
  lastError = ref<string | null>(null)
  connectionId = ref<string | null>(null)
  
  // 连接配置（通过环境变量支持不同部署环境）
  // .env.development → VITE_WS_URL=ws://localhost:8000
  // .env.production → VITE_WS_URL=wss://your-domain.com
  // Codespaces  → VITE_WS_URL=wss://8000-yourname-xxxx.github.dev
  private baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
  private reconnectDelay = 5000  // 5秒重连延迟
  private pingIntervalMs = 30000 // 30秒心跳间隔
  
  // 项目信息
  private currentProjectId: number | null = null
  private currentUserId: number | null = null
  private currentToken: string | null = null
  
  // 连接方法
  async connect(projectId: number, userId: number, token: string): Promise<boolean> {
    if (this.isConnecting.value || this.isConnected.value) {
      console.log('WebSocket已在连接或已连接，跳过')
      return false
    }
    
    this.currentProjectId = projectId
    this.currentUserId = userId
    this.currentToken = token
    
    this.isConnecting.value = true
    this.lastError.value = null
    
    return new Promise((resolve) => {
      try {
        // 构建WebSocket URL
        const wsUrl = `${this.baseUrl}/api/v1/ws/${projectId}?token=${token}`
        console.log('连接WebSocket:', wsUrl)
        
        this.ws = new WebSocket(wsUrl)
        
        this.ws.onopen = () => {
          console.log('WebSocket连接已建立')
          this.isConnected.value = true
          this.isConnecting.value = false
          this.connectionId.value = `ws_${Date.now()}`
          
          // 开始心跳
          this.startPingInterval()
          
          // 发送连接成功事件
          this.triggerEvent('connected', {
            projectId,
            userId,
            connectionId: this.connectionId.value
          })
          
          resolve(true)
        }
        
        this.ws.onclose = (event) => {
          console.log('WebSocket连接已关闭', event.code, event.reason)
          this.isConnected.value = false
          this.isConnecting.value = false
          
          // 停止心跳
          this.stopPingInterval()
          
          // 触发断开连接事件
          this.triggerEvent('disconnected', {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean
          })
          
          // 如果不是正常关闭，尝试重新连接
          if (!event.wasClean) {
            this.handleDisconnect()
          }
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
    console.log('主动断开WebSocket连接')
    
    // 清除重连计时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    // 停止心跳
    this.stopPingInterval()
    
    // 关闭WebSocket连接
    if (this.ws) {
      this.ws.close(1000, '用户主动断开')
      this.ws = null
    }
    
    // 重置状态
    this.isConnected.value = false
    this.isConnecting.value = false
    this.currentProjectId = null
    this.currentUserId = null
    this.currentToken = null
    this.connectionId.value = null
  }
  
  // 重新连接
  private handleDisconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }
    
    this.reconnectTimer = window.setTimeout(() => {
      if (this.currentProjectId && this.currentUserId && this.currentToken) {
        console.log('尝试重新连接WebSocket...')
        this.connect(this.currentProjectId, this.currentUserId, this.currentToken)
      }
    }, this.reconnectDelay)
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
  sendTypingStatus(taskId: number | null, isTyping: boolean): boolean {
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
  
  // 发送已读状态
  sendReadStatus(commentId?: number, taskId?: number): boolean {
    return this.send({
      type: 'read_status',
      data: {
        comment_id: commentId,
        task_id: taskId
      }
    })
  }
  
  // 发送心跳
  sendPing(): boolean {
    return this.send({
      type: 'ping',
      data: {}
    })
  }
  
  // 消息处理
  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data)
      
      // 触发特定类型的事件
      this.triggerEvent(message.type, message)
      
      // 触发通用消息事件
      this.triggerEvent('message', message)
      
    } catch (error) {
      console.error('处理WebSocket消息失败', error, data)
    }
  }
  
  // 心跳机制
  private startPingInterval(): void {
    this.stopPingInterval()
    
    this.pingInterval = window.setInterval(() => {
      if (this.isConnected.value) {
        this.sendPing()
      }
    }, this.pingIntervalMs)
  }
  
  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }
  
  // 事件系统
  private triggerEvent(eventType: string, data: any): void {
    const handlers = this.messageHandlers.get(eventType)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`事件处理器 ${eventType} 执行失败`, error)
        }
      })
    }
  }
  
  // 注册事件处理器
  on(eventType: string, handler: Function): void {
    if (!this.messageHandlers.has(eventType)) {
      this.messageHandlers.set(eventType, [])
    }
    this.messageHandlers.get(eventType)!.push(handler)
  }
  
  // 移除事件处理器
  off(eventType: string, handler: Function): void {
    if (this.messageHandlers.has(eventType)) {
      const handlers = this.messageHandlers.get(eventType)!
      const index = handlers.indexOf(handler)
      if (index !== -1) {
        handlers.splice(index, 1)
      }
    }
  }
  
  // 获取连接状态
  getConnectionInfo() {
    return {
      isConnected: this.isConnected.value,
      isConnecting: this.isConnecting.value,
      lastError: this.lastError.value,
      connectionId: this.connectionId.value,
      projectId: this.currentProjectId,
      userId: this.currentUserId
    }
  }
}

// 导出单例实例
export const websocketClient = new WebSocketClient()

// Vue 3 Composition API封装
export function useWebSocket() {
  const client = websocketClient
  
  // 连接WebSocket
  const connect = async (projectId: number, userId: number, token: string) => {
    return await client.connect(projectId, userId, token)
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
  const sendTypingStatus = (taskId: number | null, isTyping: boolean) => {
    return client.sendTypingStatus(taskId, isTyping)
  }
  
  // 发送反应
  const sendReaction = (commentId: number, reaction: string, action: 'add' | 'remove' = 'add') => {
    return client.sendReaction(commentId, reaction, action)
  }
  
  // 发送已读状态
  const sendReadStatus = (commentId?: number, taskId?: number) => {
    return client.sendReadStatus(commentId, taskId)
  }
  
  // 监听事件
  const on = (eventType: string, handler: Function) => {
    client.on(eventType, handler)
  }
  
  // 取消监听
  const off = (eventType: string, handler: Function) => {
    client.off(eventType, handler)
  }
  
  // 获取状态
  const getConnectionInfo = () => {
    return client.getConnectionInfo()
  }
  
  return {
    // 状态
    isConnected: client.isConnected,
    isConnecting: client.isConnecting,
    lastError: client.lastError,
    connectionId: client.connectionId,
    
    // 方法
    connect,
    disconnect,
    sendComment,
    sendTypingStatus,
    sendReaction,
    sendReadStatus,
    on,
    off,
    getConnectionInfo
  }
}