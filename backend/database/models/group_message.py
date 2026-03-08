"""
Group Message Model
SQLAlchemy model for group messages
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..ai_groups_base import Base, TimestampMixin

class GroupMessage(Base, TimestampMixin):
    """
    Group Messages table model
    """
    __tablename__ = "group_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("ai_groups.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, default="user_message")  # user_message, ai_response, system_insight
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    group = relationship("AIGroup", back_populates="messages")
    
    def __repr__(self):
        return f"<GroupMessage(id={self.id}, group_id={self.group_id}, type='{self.message_type}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        result = super().to_dict()
        result['group_name'] = self.group.name if self.group else None
        return result
