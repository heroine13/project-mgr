"""
评论相关CRUD操作
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_, or_
from datetime import datetime, timedelta
from app.models.comment import Comment, Mention, Reaction, TypingStatus, ReadStatus
from app.schemas.comment import (
    CommentCreate, CommentUpdate,
    MentionCreate, MentionUpdate,
    ReactionCreate,
    TypingStatusCreate,
    ReadStatusCreate
)


# ==================== Comment CRUD ====================

def create_comment(db: Session, comment_in: CommentCreate, user_id: int, project_id: int) -> Comment:
    """创建评论"""
    db_comment = Comment(
        **comment_in.dict(exclude_unset=True),
        user_id=user_id,
        project_id=project_id
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


def get_comment(db: Session, comment_id: int) -> Optional[Comment]:
    """获取评论"""
    return db.query(Comment).filter(Comment.id == comment_id).first()


def get_comments_by_task(
    db: Session, 
    task_id: int,
    skip: int = 0,
    limit: int = 100,
    include_replies: bool = True
) -> List[Comment]:
    """获取任务的评论列表"""
    query = db.query(Comment).filter(Comment.task_id == task_id)
    
    if not include_replies:
        # 只获取顶级评论（parent_id为None）
        query = query.filter(Comment.parent_id.is_(None))
    
    query = query.order_by(Comment.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def get_comments_by_project(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[Comment]:
    """获取项目的评论列表"""
    query = db.query(Comment).filter(Comment.project_id == project_id)
    
    if user_id:
        query = query.filter(Comment.user_id == user_id)
    
    query = query.order_by(Comment.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def get_recent_comments(
    db: Session,
    project_id: int,
    days: int = 7,
    limit: int = 50
) -> List[Comment]:
    """获取最近N天的评论"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    return db.query(Comment).filter(
        and_(
            Comment.project_id == project_id,
            Comment.created_at >= cutoff_date
        )
    ).order_by(Comment.created_at.desc()).limit(limit).all()


def update_comment(
    db: Session,
    db_comment: Comment,
    comment_in: CommentUpdate
) -> Comment:
    """更新评论"""
    update_data = comment_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_comment, field, value)
    
    db_comment.updated_at = datetime.utcnow()
    db_comment.is_edited = 1
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


def delete_comment(db: Session, comment_id: int) -> bool:
    """删除评论"""
    db_comment = get_comment(db, comment_id)
    if not db_comment:
        return False
    
    # 删除相关记录
    db.query(Mention).filter(Mention.comment_id == comment_id).delete()
    db.query(Reaction).filter(Reaction.comment_id == comment_id).delete()
    db.query(ReadStatus).filter(ReadStatus.comment_id == comment_id).delete()
    
    # 删除回复
    db.query(Comment).filter(Comment.parent_id == comment_id).delete()
    
    # 删除评论本身
    db.delete(db_comment)
    db.commit()
    
    return True


def get_comment_stats(db: Session, project_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
    """获取评论统计信息"""
    # 总评论数
    total_query = db.query(func.count(Comment.id)).filter(Comment.project_id == project_id)
    if user_id:
        total_query = total_query.filter(Comment.user_id == user_id)
    total_comments = total_query.scalar() or 0
    
    # 今日评论数
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_query = db.query(func.count(Comment.id)).filter(
        and_(
            Comment.project_id == project_id,
            Comment.created_at >= today_start
        )
    )
    if user_id:
        today_query = today_query.filter(Comment.user_id == user_id)
    today_comments = today_query.scalar() or 0
    
    # 未读提及数
    if user_id:
        unread_mentions_query = db.query(func.count(Mention.id)).filter(
            and_(
                Mention.mentioned_user_id == user_id,
                Mention.is_read == 0
            )
        )
        unread_mentions = unread_mentions_query.scalar() or 0
    else:
        unread_mentions = 0
    
    # 最近评论
    recent_comments = get_recent_comments(db, project_id, days=1, limit=5)
    
    return {
        "total_comments": total_comments,
        "today_comments": today_comments,
        "unread_mentions": unread_mentions,
        "recent_comments": recent_comments
    }


# ==================== Mention CRUD ====================

def create_mention(db: Session, mention_in: MentionCreate) -> Mention:
    """创建提及记录"""
    db_mention = Mention(**mention_in.dict())
    db.add(db_mention)
    db.commit()
    db.refresh(db_mention)
    return db_mention


def get_mention(db: Session, mention_id: int) -> Optional[Mention]:
    """获取提及记录"""
    return db.query(Mention).filter(Mention.id == mention_id).first()


def get_mentions_by_user(
    db: Session,
    user_id: int,
    is_read: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Mention]:
    """获取用户的提及记录"""
    query = db.query(Mention).filter(Mention.mentioned_user_id == user_id)
    
    if is_read is not None:
        query = query.filter(Mention.is_read == is_read)
    
    query = query.order_by(Mention.id.desc())
    
    return query.offset(skip).limit(limit).all()


def mark_mention_as_read(db: Session, mention_id: int) -> bool:
    """标记提及为已读"""
    db_mention = get_mention(db, mention_id)
    if not db_mention:
        return False
    
    db_mention.is_read = 1
    db_mention.read_at = datetime.utcnow()
    
    db.add(db_mention)
    db.commit()
    
    return True


def mark_all_mentions_as_read(db: Session, user_id: int) -> bool:
    """标记用户的所有提及为已读"""
    updated_count = db.query(Mention).filter(
        and_(
            Mention.mentioned_user_id == user_id,
            Mention.is_read == 0
        )
    ).update({"is_read": 1, "read_at": datetime.utcnow()})
    
    db.commit()
    return updated_count > 0


def delete_mention(db: Session, mention_id: int) -> bool:
    """删除提及记录"""
    db_mention = get_mention(db, mention_id)
    if not db_mention:
        return False
    
    db.delete(db_mention)
    db.commit()
    return True


# ==================== Reaction CRUD ====================

def create_reaction(db: Session, reaction_in: ReactionCreate, user_id: int) -> Reaction:
    """创建反应"""
    # 检查是否已存在相同反应
    existing = db.query(Reaction).filter(
        and_(
            Reaction.comment_id == reaction_in.comment_id,
            Reaction.user_id == user_id
        )
    ).first()
    
    if existing:
        # 如果已存在，更新反应类型
        existing.reaction_type = reaction_in.reaction_type
        existing.created_at = datetime.utcnow()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    # 创建新反应
    db_reaction = Reaction(
        **reaction_in.dict(),
        user_id=user_id
    )
    db.add(db_reaction)
    db.commit()
    db.refresh(db_reaction)
    return db_reaction


def get_reaction(db: Session, reaction_id: int) -> Optional[Reaction]:
    """获取反应"""
    return db.query(Reaction).filter(Reaction.id == reaction_id).first()


def get_reactions_by_comment(db: Session, comment_id: int) -> List[Reaction]:
    """获取评论的所有反应"""
    return db.query(Reaction).filter(Reaction.comment_id == comment_id).all()


def get_reaction_summary(db: Session, comment_id: int) -> Dict[str, Any]:
    """获取评论的反应统计"""
    reactions = get_reactions_by_comment(db, comment_id)
    
    summary = {}
    for reaction in reactions:
        if reaction.reaction_type not in summary:
            summary[reaction.reaction_type] = 0
        summary[reaction.reaction_type] += 1
    
    total = sum(summary.values())
    
    return {
        "total": total,
        "breakdown": summary,
        "reactions": reactions
    }


def delete_reaction(db: Session, comment_id: int, user_id: int) -> bool:
    """删除用户的反应"""
    deleted_count = db.query(Reaction).filter(
        and_(
            Reaction.comment_id == comment_id,
            Reaction.user_id == user_id
        )
    ).delete()
    
    db.commit()
    return deleted_count > 0


def toggle_reaction(db: Session, comment_id: int, user_id: int, reaction_type: str) -> Dict[str, Any]:
    """切换反应状态"""
    # 检查是否已存在
    existing = db.query(Reaction).filter(
        and_(
            Reaction.comment_id == comment_id,
            Reaction.user_id == user_id
        )
    ).first()
    
    if existing:
        if existing.reaction_type == reaction_type:
            # 如果相同反应，删除它
            delete_reaction(db, comment_id, user_id)
            return {"action": "removed", "reaction_type": reaction_type}
        else:
            # 如果不同反应，更新它
            existing.reaction_type = reaction_type
            existing.created_at = datetime.utcnow()
            db.add(existing)
            db.commit()
            return {"action": "updated", "reaction_type": reaction_type}
    else:
        # 创建新反应
        reaction_in = ReactionCreate(comment_id=comment_id, reaction_type=reaction_type)
        create_reaction(db, reaction_in, user_id)
        return {"action": "added", "reaction_type": reaction_type}


# ==================== TypingStatus CRUD ====================

def update_typing_status(
    db: Session,
    typing_in: TypingStatusCreate,
    user_id: int
) -> TypingStatus:
    """更新输入状态"""
    # 查找现有状态
    existing = db.query(TypingStatus).filter(
        and_(
            TypingStatus.project_id == typing_in.project_id,
            TypingStatus.user_id == user_id
        )
    ).first()
    
    if existing:
        # 更新现有状态
        existing.is_typing = typing_in.is_typing
        existing.task_id = typing_in.task_id
        existing.last_activity = datetime.utcnow()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # 创建新状态
        db_typing = TypingStatus(
            **typing_in.dict(),
            user_id=user_id,
            last_activity=datetime.utcnow()
        )
        db.add(db_typing)
        db.commit()
        db.refresh(db_typing)
        return db_typing


def get_active_typing_users(
    db: Session,
    project_id: int,
    task_id: Optional[int] = None
) -> List[TypingStatus]:
    """获取正在输入的用户"""
    query = db.query(TypingStatus).filter(
        and_(
            TypingStatus.project_id == project_id,
            TypingStatus.is_typing == 1
        )
    )
    
    if task_id:
        query = query.filter(TypingStatus.task_id == task_id)
    
    # 只显示最近30秒内的活动
    cutoff_time = datetime.utcnow() - timedelta(seconds=30)
    query = query.filter(TypingStatus.last_activity >= cutoff_time)
    
    return query.all()


def clear_typing_status(db: Session, user_id: int, project_id: int) -> bool:
    """清除用户的输入状态"""
    updated_count = db.query(TypingStatus).filter(
        and_(
            TypingStatus.user_id == user_id,
            TypingStatus.project_id == project_id
        )
    ).update({"is_typing": 0})
    
    db.commit()
    return updated_count > 0


# ==================== ReadStatus CRUD ====================

def mark_as_read(
    db: Session,
    read_in: ReadStatusCreate,
    user_id: int
) -> ReadStatus:
    """标记为已读"""
    # 查找现有记录
    if read_in.comment_id:
        existing = db.query(ReadStatus).filter(
            and_(
                ReadStatus.user_id == user_id,
                ReadStatus.comment_id == read_in.comment_id
            )
        ).first()
    elif read_in.task_id:
        existing = db.query(ReadStatus).filter(
            and_(
                ReadStatus.user_id == user_id,
                ReadStatus.task_id == read_in.task_id
            )
        ).first()
    else:
        # 至少需要comment_id或task_id之一
        raise ValueError("需要comment_id或task_id")
    
    if existing:
        # 更新现有记录
        existing.read_at = datetime.utcnow()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # 创建新记录
        db_read = ReadStatus(
            **read_in.dict(),
            user_id=user_id,
            read_at=datetime.utcnow()
        )
        db.add(db_read)
        db.commit()
        db.refresh(db_read)
        return db_read