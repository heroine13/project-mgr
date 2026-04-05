"""
CRUD operations for User model
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.schemas.auth import UserCreate
from app.auth import hash_password

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    """Create new user"""
    hashed_password = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Update user"""
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in kwargs.items():
            if value is not None:
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete user (soft delete by setting is_active=False)"""
    db_user = get_user(db, user_id)
    if db_user:
        db_user.is_active = False
        db.commit()
        return True
    return False