"""
评论相关数据模式
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    """评论基础模式"""
    task_id: int = Field(..., description="任务ID")
    content: str = Field(..., description="评论内容")
    mentions: Optional[str] = Field(None, description="提及的用户ID列表")
    parent_id: Optional[int] = Field(None, description="父评论ID")


class CommentCreate(CommentBase):
    """创建评论模式"""
    pass


class CommentUpdate(BaseModel):
    """更新评论模式"""
    content: Optional[str] = Field(None, description="评论内容")
    is_edited: Optional[int] = Field(None, description="是否已编辑")


class CommentResponse(CommentBase):
    """评论响应模式"""
    id: int
    user_id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    is_edited: int
    user_name: Optional[str] = Field(None, description="用户名")
    user_avatar: Optional[str] = Field(None, description="用户头像")
    reply_count: Optional[int] = Field(0, description="回复数量")
    reaction_count: Optional[int] = Field(0, description="反应总数")
    
    class Config:
        from_attributes = True


class MentionBase(BaseModel):
    """提及基础模式"""
    comment_id: int = Field(..., description="评论ID")
    mentioned_user_id: int = Field(..., description="被提及的用户ID")


class MentionCreate(MentionBase):
    """创建提及模式"""
    pass


class MentionUpdate(BaseModel):
    """更新提及模式"""
    is_read: Optional[int] = Field(None, description="是否已读")
    read_at: Optional[datetime] = Field(None, description="已读时间")


class MentionResponse(MentionBase):
    """提及响应模式"""
    id: int
    is_read: int
    read_at: Optional[datetime]
    comment_content: Optional[str] = Field(None, description="评论内容")
    task_name: Optional[str] = Field(None, description="任务名称")
    project_name: Optional[str] = Field(None, description="项目名称")
    
    class Config:
        from_attributes = True


class ReactionBase(BaseModel):
    """反应基础模式"""
    comment_id: int = Field(..., description="评论ID")
    reaction_type: str = Field(..., description="反应类型")


class ReactionCreate(ReactionBase):
    """创建反应模式"""
    pass


class ReactionResponse(ReactionBase):
    """反应响应模式"""
    id: int
    user_id: int
    created_at: datetime
    user_name: Optional[str] = Field(None, description="用户名")
    
    class Config:
        from_attributes = True


class TypingStatusBase(BaseModel):
    """输入状态基础模式"""
    project_id: int = Field(..., description="项目ID")
    task_id: Optional[int] = Field(None, description="任务ID")
    is_typing: int = Field(1, description="是否正在输入")


class TypingStatusCreate(TypingStatusBase):
    """创建输入状态模式"""
    pass


class TypingStatusResponse(TypingStatusBase):
    """输入状态响应模式"""
    id: int
    user_id: int
    last_activity: datetime
    user_name: Optional[str] = Field(None, description="用户名")
    
    class Config:
        from_attributes = True


class ReadStatusBase(BaseModel):
    """已读状态基础模式"""
    comment_id: Optional[int] = Field(None, description="评论ID")
    task_id: Optional[int] = Field(None, description="任务ID")


class ReadStatusCreate(ReadStatusBase):
    """创建已读状态模式"""
    pass


class ReadStatusResponse(ReadStatusBase):
    """已读状态响应模式"""
    id: int
    user_id: int
    read_at: datetime
    
    class Config:
        from_attributes = True


class CommentWithReplies(BaseModel):
    """带回复的评论"""
    comment: CommentResponse
    replies: List[CommentResponse] = Field(default_factory=list)
    reactions: List[ReactionResponse] = Field(default_factory=list)


class CommentStats(BaseModel):
    """评论统计"""
    total_comments: int = Field(0, description="总评论数")
    today_comments: int = Field(0, description="今日评论数")
    unread_mentions: int = Field(0, description="未读提及数")
    recent_comments: List[CommentResponse] = Field(default_factory=list)


class WebSocketMessage(BaseModel):
    """WebSocket消息格式"""
    type: str = Field(..., description="消息类型")
    data: dict = Field(default_factory=dict, description="消息数据")
    timestamp: Optional[datetime] = Field(None, description="时间戳")
    sender_id: Optional[int] = Field(None, description="发送者ID")


class CommentMessage(BaseModel):
    """评论消息"""
    task_id: int = Field(..., description="任务ID")
    content: str = Field(..., description="评论内容")
    mentions: List[int] = Field(default_factory=list, description="提及的用户ID列表")


class TypingMessage(BaseModel):
    """输入状态消息"""
    task_id: Optional[int] = Field(None, description="任务ID")
    is_typing: bool = Field(True, description="是否正在输入")


class ReactionMessage(BaseModel):
    """反应消息"""
    comment_id: int = Field(..., description="评论ID")
    reaction_type: str = Field(..., description="反应类型")
    action: str = Field("add", description="操作类型: add/remove")


class NotificationMessage(BaseModel):
    """通知消息"""
    type: str = Field(..., description="通知类型")
    title: str = Field(..., description="通知标题")
    message: str = Field(..., description="通知内容")
    data: dict = Field(default_factory=dict, description="附加数据")