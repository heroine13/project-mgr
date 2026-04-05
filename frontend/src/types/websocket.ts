/**
 * WebSocket相关类型定义
 */

export interface WebSocketMessage {
  type: string
  data: any
  timestamp?: string
  sender_id?: number
  success?: boolean
  error?: string
}

export interface CommentMessage {
  task_id: number
  content: string
  mentions: number[]
}

export interface TypingMessage {
  task_id?: number
  is_typing: boolean
}

export interface ReactionMessage {
  comment_id: number
  reaction: string
  action: 'add' | 'remove'
}

export interface ReadStatusMessage {
  comment_id?: number
  task_id?: number
}

export interface PingMessage {
  pong: boolean
  timestamp: string
}

// 连接事件
export interface ConnectionEvent {
  type: 'connected' | 'disconnected'
  projectId: number
  userId: number
  connectionId?: string
  code?: number
  reason?: string
  wasClean?: boolean
}

// 新评论事件
export interface NewCommentEvent {
  type: 'new_comment'
  data: {
    id: number
    task_id: number
    user_id: number
    content: string
    mentions: string
    created_at: string
    user: {
      id: number
      name: string
      avatar?: string
    }
  }
  timestamp: string
}

// 用户输入状态事件
export interface UserTypingEvent {
  type: 'user_typing'
  data: {
    user_id: number
    task_id?: number
    is_typing: boolean
    timestamp: string
  }
  timestamp: string
}

// 反应事件
export interface ReactionEvent {
  type: 'reaction'
  data: {
    user_id: number
    comment_id: number
    reaction: string
    action: 'add' | 'remove'
  }
  timestamp: string
}

// 提及通知事件
export interface MentionNotificationEvent {
  type: 'mention_notification'
  data: {
    comment_id: number
    mentioned_user_id: number
    project_id: number
    comment_content: string
  }
  timestamp: string
}

// 系统通知事件
export interface SystemNotificationEvent {
  type: 'system_notification'
  subtype: string
  data: any
  message: string
  timestamp: string
}

// 用户加入/离开事件
export interface UserPresenceEvent {
  type: 'user_joined' | 'user_left'
  user_id: number
  project_id: number
  message: string
  timestamp: string
}

// 任务更新事件
export interface TaskUpdateEvent {
  type: 'task_updated'
  data: any
  timestamp: string
}

// 个人通知事件
export interface PersonalNotificationEvent {
  type: 'personal_notification'
  data: any
  timestamp: string
}

// 连接建立事件
export interface ConnectionEstablishedEvent {
  type: 'connection_established'
  message: string
  project_id: number
  user_id: number
  timestamp: string
}

// 所有事件类型
export type WebSocketEvent =
  | NewCommentEvent
  | UserTypingEvent
  | ReactionEvent
  | MentionNotificationEvent
  | SystemNotificationEvent
  | UserPresenceEvent
  | TaskUpdateEvent
  | PersonalNotificationEvent
  | ConnectionEstablishedEvent

// WebSocket配置
export interface WebSocketConfig {
  url: string
  reconnectDelay: number
  pingInterval: number
  maxReconnectAttempts: number
}

// WebSocket状态
export interface WebSocketState {
  isConnected: boolean
  isConnecting: boolean
  lastError: string | null
  connectionId: string | null
  projectId: number | null
  userId: number | null
  messageCount: number
  lastMessageTime: string | null
}

// 消息处理器
export interface MessageHandler {
  (event: WebSocketEvent): void
}

// 连接管理器
export interface ConnectionManager {
  connect(projectId: number, userId: number, token: string): Promise<boolean>
  disconnect(): void
  send(message: any): boolean
  on(eventType: string, handler: MessageHandler): void
  off(eventType: string, handler: MessageHandler): void
}

// 反应类型定义
export const REACTION_TYPES = {
  LIKE: 'like',
  LOVE: 'love',
  LAUGH: 'laugh',
  WOW: 'wow',
  SAD: 'sad',
  ANGRY: 'angry'
} as const

export type ReactionType = typeof REACTION_TYPES[keyof typeof REACTION_TYPES]

// 输入状态
export interface TypingStatus {
  user_id: number
  task_id?: number
  is_typing: boolean
  last_activity: string
  user_name?: string
}

// 评论统计
export interface CommentStats {
  total_comments: number
  today_comments: number
  unread_mentions: number
  recent_comments: any[]
}

// WebSocket错误
export interface WebSocketError {
  code: number
  message: string
  timestamp: string
  fatal: boolean
}