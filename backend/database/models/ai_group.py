"""
AI Group Model
SQLAlchemy model for AI Groups functionality
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..ai_groups_base import Base, TimestampMixin

class AIGroup(Base, TimestampMixin):
    """
    AI Groups table model
    """
    __tablename__ = "ai_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    messages = relationship("GroupMessage", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AIGroup(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    def to_dict(self):
        """Convert to dictionary with relationships"""
        result = super().to_dict()
        result['members_count'] = len(self.members) if self.members else 0
        result['messages_count'] = len(self.messages) if self.messages else 0
        return result
