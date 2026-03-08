"""
AI Groups Dependencies
Common dependencies and utilities for AI Groups module
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..ai_groups_connection import get_db

def get_current_user_id(user_id: Optional[int] = None) -> int:
    """
    Dependency to get current user ID
    In a real application, this would validate JWT token or session
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    return user_id

def verify_group_membership(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db)
) -> bool:
    """
    Verify if user is a member of the group
    """
    from ..models.group_member import GroupMember
    
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this group"
        )
    
    return True

def verify_group_admin(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db)
) -> bool:
    """
    Verify if user is admin of the group
    """
    from ..models.group_member import GroupMember
    
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.role == 'admin'
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an admin of this group"
        )
    
    return True

class PaginationParams:
    """
    Common pagination parameters
    """
    def __init__(
        self,
        page: int = 1,
        per_page: int = 50,
        max_per_page: int = 1000
    ):
        self.page = max(1, page)
        self.per_page = min(max_per_page, max(1, per_page))
        self.offset = (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        return self.per_page
