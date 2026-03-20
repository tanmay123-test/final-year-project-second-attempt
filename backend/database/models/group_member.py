"""
Group Member Model
SQLAlchemy model for group membership
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..ai_groups_base import Base, TimestampMixin

class GroupMember(Base, TimestampMixin):
    """
    Group Members table model
    """
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("ai_groups.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    role = Column(String(20), nullable=False, default="member")  # member, admin, ai_assistant
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    group = relationship("AIGroup", back_populates="members")
    
    def __repr__(self):
        return f"<GroupMember(id={self.id}, group_id={self.group_id}, user_id={self.user_id}, role='{self.role}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        result = super().to_dict()
        result['group_name'] = self.group.name if self.group else None
        return result
