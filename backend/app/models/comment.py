"""
评论相关数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
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


class Reaction(Base):
    """评论反应（点赞、表情）模型"""
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reaction_type = Column(String(20), nullable=False)  # like, love, laugh, wow, sad, angry
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 唯一约束：同一个用户对同一个评论只能有一种反应
    __table_args__ = (
        UniqueConstraint('comment_id', 'user_id', name='uq_comment_user_reaction'),
    )
    
    # 关系
    comment = relationship("Comment", backref="reactions")
    user = relationship("User", backref="reactions_given")
    
    def __repr__(self):
        return f"<Reaction(id={self.id}, comment_id={self.comment_id}, user_id={self.user_id}, type='{self.reaction_type}')>"


class TypingStatus(Base):
    """用户输入状态模型"""
    __tablename__ = "typing_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_typing = Column(Integer, default=0)  # 0:未输入, 1:正在输入
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    project = relationship("Project", backref="typing_statuses")
    task = relationship("Task", backref="typing_statuses")
    user = relationship("User", backref="typing_statuses")
    
    def __repr__(self):
        return f"<TypingStatus(id={self.id}, user_id={self.user_id}, project_id={self.project_id}, is_typing={self.is_typing})>"


class ReadStatus(Base):
    """消息已读状态模型"""
    __tablename__ = "read_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    read_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", backref="read_statuses")
    comment = relationship("Comment", backref="read_statuses")
    task = relationship("Task", backref="read_statuses")
    
    def __repr__(self):
        return f"<ReadStatus(id={self.id}, user_id={self.user_id}, comment_id={self.comment_id}, read_at={self.read_at})>"