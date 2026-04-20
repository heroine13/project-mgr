"""
Issue CRUD Operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from datetime import datetime

from ..models.issue import Issue, IssueComment, IssueAttachment, IssueStatus, IssuePriority, IssueType
from ..schemas.issue import IssueCreate, IssueUpdate


# ============ Issue CRUD ============

def create_issue(db: Session, issue: IssueCreate, reporter_id: int) -> Issue:
    """Create a new issue"""
    db_issue = Issue(
        title=issue.title,
        description=issue.description,
        issue_type=IssueType(issue.issue_type.value),
        status=IssueStatus.OPEN,
        priority=IssuePriority(issue.priority.value),
        project_id=issue.project_id,
        task_id=issue.task_id,
        assignee_id=issue.assignee_id,
        reporter_id=reporter_id,
        labels=issue.labels,
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


def get_issue(db: Session, issue_id: int) -> Optional[Issue]:
    """Get issue by ID"""
    return db.query(Issue).filter(Issue.id == issue_id).first()


def get_issues(
    db: Session,
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    issue_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    reporter_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[Issue], int]:
    """Get issues with filters and pagination"""
    query = db.query(Issue)
    
    # Apply filters
    if project_id:
        query = query.filter(Issue.project_id == project_id)
    if status:
        query = query.filter(Issue.status == IssueStatus(status))
    if priority:
        query = query.filter(Issue.priority == IssuePriority(priority))
    if issue_type:
        query = query.filter(Issue.issue_type == IssueType(issue_type))
    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)
    if reporter_id:
        query = query.filter(Issue.reporter_id == reporter_id)
    if search:
        query = query.filter(
            or_(
                Issue.title.ilike(f"%{search}%"),
                Issue.description.ilike(f"%{search}%"),
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    issues = (
        query
        .order_by(Issue.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return issues, total


def update_issue(db: Session, issue_id: int, issue_update: IssueUpdate) -> Optional[Issue]:
    """Update an issue"""
    db_issue = get_issue(db, issue_id)
    if not db_issue:
        return None
    
    update_data = issue_update.model_dump(exclude_unset=True)
    
    # Handle enum conversions
    if "issue_type" in update_data and update_data["issue_type"]:
        update_data["issue_type"] = IssueType(update_data["issue_type"].value)
    if "status" in update_data and update_data["status"]:
        update_data["status"] = IssueStatus(update_data["status"].value)
    if "priority" in update_data and update_data["priority"]:
        update_data["priority"] = IssuePriority(update_data["priority"].value)
    
    # Handle resolved_at timestamp
    if update_data.get("is_resolved") and not db_issue.is_resolved:
        update_data["resolved_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_issue, field, value)
    
    db.commit()
    db.refresh(db_issue)
    return db_issue


def update_issue_status(db: Session, issue_id: int, status: str) -> Optional[Issue]:
    """Update issue status"""
    db_issue = get_issue(db, issue_id)
    if not db_issue:
        return None
    
    db_issue.status = IssueStatus(status)
    if status == "resolved":
        db_issue.is_resolved = True
        db_issue.resolved_at = datetime.utcnow()
    elif status == "reopened":
        db_issue.is_resolved = False
        db_issue.resolved_at = None
    
    db.commit()
    db.refresh(db_issue)
    return db_issue


def delete_issue(db: Session, issue_id: int) -> bool:
    """Delete an issue"""
    db_issue = get_issue(db, issue_id)
    if not db_issue:
        return False
    
    db.delete(db_issue)
    db.commit()
    return True


def get_issue_stats(db: Session, project_id: Optional[int] = None) -> dict:
    """Get issue statistics"""
    query = db.query(Issue)
    if project_id:
        query = query.filter(Issue.project_id == project_id)
    
    total = query.count()
    
    # Status counts
    open_count = query.filter(Issue.status == IssueStatus.OPEN).count()
    in_progress_count = query.filter(Issue.status == IssueStatus.IN_PROGRESS).count()
    resolved_count = query.filter(Issue.status == IssueStatus.RESOLVED).count()
    closed_count = query.filter(Issue.status == IssueStatus.CLOSED).count()
    
    # Priority counts
    priority_counts = {
        "low": query.filter(Issue.priority == IssuePriority.LOW).count(),
        "medium": query.filter(Issue.priority == IssuePriority.MEDIUM).count(),
        "high": query.filter(Issue.priority == IssuePriority.HIGH).count(),
        "critical": query.filter(Issue.priority == IssuePriority.CRITICAL).count(),
    }
    
    # Type counts
    type_counts = {
        "bug": query.filter(Issue.issue_type == IssueType.BUG).count(),
        "feature": query.filter(Issue.issue_type == IssueType.FEATURE).count(),
        "improvement": query.filter(Issue.issue_type == IssueType.IMPROVEMENT).count(),
        "question": query.filter(Issue.issue_type == IssueType.QUESTION).count(),
    }
    
    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress_count,
        "resolved": resolved_count,
        "closed": closed_count,
        "by_priority": priority_counts,
        "by_type": type_counts,
    }


# ============ Issue Comment CRUD ============

def create_issue_comment(
    db: Session,
    issue_id: int,
    user_id: int,
    content: str,
    mentioned_users: Optional[str] = None,
) -> IssueComment:
    """Create a new issue comment"""
    db_comment = IssueComment(
        issue_id=issue_id,
        user_id=user_id,
        content=content,
        mentioned_users=mentioned_users,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_issue_comments(
    db: Session,
    issue_id: int,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[IssueComment], int]:
    """Get comments for an issue"""
    query = db.query(IssueComment).filter(IssueComment.issue_id == issue_id)
    total = query.count()
    comments = (
        query
        .order_by(IssueComment.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return comments, total


def update_issue_comment(
    db: Session,
    comment_id: int,
    content: str,
) -> Optional[IssueComment]:
    """Update an issue comment"""
    db_comment = db.query(IssueComment).filter(IssueComment.id == comment_id).first()
    if not db_comment:
        return None
    
    db_comment.content = content
    db_comment.is_edited = True
    db_comment.edited_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_issue_comment(db: Session, comment_id: int) -> bool:
    """Delete an issue comment"""
    db_comment = db.query(IssueComment).filter(IssueComment.id == comment_id).first()
    if not db_comment:
        return False
    
    db.delete(db_comment)
    db.commit()
    return True


def add_reaction_to_comment(
    db: Session,
    comment_id: int,
    emoji: str,
    user_id: int,
) -> Optional[IssueComment]:
    """Add reaction to a comment"""
    import json
    
    db_comment = db.query(IssueComment).filter(IssueComment.id == comment_id).first()
    if not db_comment:
        return None
    
    # Parse existing reactions
    reactions = json.loads(db_comment.reactions) if db_comment.reactions else {}
    
    if emoji not in reactions:
        reactions[emoji] = []
    
    # Add user if not already reacted
    if user_id not in reactions[emoji]:
        reactions[emoji].append(user_id)
    
    db_comment.reactions = json.dumps(reactions)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def remove_reaction_from_comment(
    db: Session,
    comment_id: int,
    emoji: str,
    user_id: int,
) -> Optional[IssueComment]:
    """Remove reaction from a comment"""
    import json
    
    db_comment = db.query(IssueComment).filter(IssueComment.id == comment_id).first()
    if not db_comment:
        return None
    
    # Parse existing reactions
    reactions = json.loads(db_comment.reactions) if db_comment.reactions else {}
    
    if emoji in reactions and user_id in reactions[emoji]:
        reactions[emoji].remove(user_id)
        # Clean up empty emoji entries
        if not reactions[emoji]:
            del reactions[emoji]
    
    db_comment.reactions = json.dumps(reactions) if reactions else None
    db.commit()
    db.refresh(db_comment)
    return db_comment


# ============ Issue Attachment CRUD ============

def create_issue_attachment(
    db: Session,
    issue_id: int,
    user_id: int,
    filename: str,
    file_path: str,
    file_size: Optional[int] = None,
    mime_type: Optional[str] = None,
) -> IssueAttachment:
    """Create a new issue attachment"""
    db_attachment = IssueAttachment(
        issue_id=issue_id,
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment


def get_issue_attachments(
    db: Session,
    issue_id: int,
) -> List[IssueAttachment]:
    """Get attachments for an issue"""
    return (
        db.query(IssueAttachment)
        .filter(IssueAttachment.issue_id == issue_id)
        .order_by(IssueAttachment.created_at.desc())
        .all()
    )


def delete_issue_attachment(db: Session, attachment_id: int) -> bool:
    """Delete an issue attachment"""
    db_attachment = db.query(IssueAttachment).filter(IssueAttachment.id == attachment_id).first()
    if not db_attachment:
        return False
    
    db.delete(db_attachment)
    db.commit()
    return True