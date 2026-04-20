"""
Issue API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueListResponse,
    IssueStatusUpdate,
    IssueAssigneeUpdate,
    IssueStatsResponse,
    IssueCommentCreate,
    IssueCommentUpdate,
    IssueCommentResponse,
    IssueCommentListResponse,
    IssueWithComments,
)
from ...crud import issue as crud_issue

router = APIRouter()


# ============ Issue Endpoints ============

@router.post("/", response_model=IssueResponse, status_code=201)
def create_issue(
    issue: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new issue"""
    return crud_issue.create_issue(db, issue, current_user.id)


@router.get("/", response_model=IssueListResponse)
def get_issues(
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    issue_type: Optional[str] = Query(None),
    assignee_id: Optional[int] = Query(None),
    reporter_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get issues with filters and pagination"""
    skip = (page - 1) * page_size
    issues, total = crud_issue.get_issues(
        db,
        project_id=project_id,
        status=status,
        priority=priority,
        issue_type=issue_type,
        assignee_id=assignee_id,
        reporter_id=reporter_id,
        search=search,
        skip=skip,
        limit=page_size,
    )
    
    pages = (total + page_size - 1) // page_size
    
    return IssueListResponse(
        total=total,
        items=issues,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/stats", response_model=IssueStatsResponse)
def get_issue_stats(
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get issue statistics"""
    stats = crud_issue.get_issue_stats(db, project_id)
    return IssueStatsResponse(**stats)


@router.get("/{issue_id}", response_model=IssueWithComments)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get issue by ID with comments"""
    db_issue = crud_issue.get_issue(db, issue_id)
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return db_issue


@router.put("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an issue"""
    db_issue = crud_issue.update_issue(db, issue_id, issue_update)
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return db_issue


@router.patch("/{issue_id}/status", response_model=IssueResponse)
def update_issue_status(
    issue_id: int,
    status_update: IssueStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update issue status"""
    db_issue = crud_issue.update_issue_status(db, issue_id, status_update.status.value)
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return db_issue


@router.patch("/{issue_id}/assignee", response_model=IssueResponse)
def update_issue_assignee(
    issue_id: int,
    assignee_update: IssueAssigneeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update issue assignee"""
    db_issue = crud_issue.get_issue(db, issue_id)
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    db_issue.assignee_id = assignee_update.assignee_id
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.delete("/{issue_id}", status_code=204)
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an issue"""
    success = crud_issue.delete_issue(db, issue_id)
    if not success:
        raise HTTPException(status_code=404, detail="Issue not found")
    return None


# ============ Issue Comment Endpoints ============

@router.post("/{issue_id}/comments", response_model=IssueCommentResponse, status_code=201)
def create_issue_comment(
    issue_id: int,
    comment: IssueCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new comment for an issue"""
    # Verify issue exists
    db_issue = crud_issue.get_issue(db, issue_id)
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    return crud_issue.create_issue_comment(
        db, issue_id, current_user.id, comment.content, comment.mentioned_users
    )


@router.get("/{issue_id}/comments", response_model=IssueCommentListResponse)
def get_issue_comments(
    issue_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comments for an issue"""
    skip = (page - 1) * page_size
    comments, total = crud_issue.get_issue_comments(db, issue_id, skip, page_size)
    
    return IssueCommentListResponse(
        total=total,
        items=comments,
    )


@router.put("/comments/{comment_id}", response_model=IssueCommentResponse)
def update_issue_comment(
    comment_id: int,
    comment_update: IssueCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a comment"""
    db_comment = crud_issue.update_issue_comment(db, comment_id, comment_update.content)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.delete("/comments/{comment_id}", status_code=204)
def delete_issue_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment"""
    success = crud_issue.delete_issue_comment(db, comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return None


# ============ Issue Reaction Endpoints ============

@router.post("/comments/{comment_id}/reactions/{emoji}")
def add_reaction(
    comment_id: int,
    emoji: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add reaction to a comment"""
    db_comment = crud_issue.add_reaction_to_comment(db, comment_id, emoji, current_user.id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"status": "success", "reactions": db_comment.reactions}


@router.delete("/comments/{comment_id}/reactions/{emoji}")
def remove_reaction(
    comment_id: int,
    emoji: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove reaction from a comment"""
    db_comment = crud_issue.remove_reaction_from_comment(db, comment_id, emoji, current_user.id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"status": "success", "reactions": db_comment.reactions}