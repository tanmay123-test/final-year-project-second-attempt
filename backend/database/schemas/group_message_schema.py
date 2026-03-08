"""
Group Message Pydantic Schemas
Request and response models for group messages
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class SendMessageRequest(BaseModel):
    """Request schema for sending a message"""
    group_id: int = Field(..., gt=0, description="Group ID")
    user_id: int = Field(..., gt=0, description="User ID")
    message: str = Field(..., min_length=1, max_length=2000, description="Message content")
    message_type: Optional[str] = Field("user_message", description="Message type")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
    
    @validator('message_type')
    def validate_message_type(cls, v):
        allowed_types = ['user_message', 'ai_response', 'system_insight']
        if v not in allowed_types:
            raise ValueError(f'Message type must be one of: {allowed_types}')
        return v

class MessageResponse(BaseModel):
    """Response schema for message"""
    id: int
    group_id: int
    user_id: int
    message: str
    message_type: str
    created_at: datetime
    group_name: Optional[str]
    
    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    """Response schema for message list"""
    messages: List[MessageResponse]
    total: int
    page: int
    per_page: int
    
    class Config:
        from_attributes = True

class MessageFilterRequest(BaseModel):
    """Request schema for filtering messages"""
    group_id: int = Field(..., gt=0, description="Group ID")
    message_type: Optional[str] = Field(None, description="Filter by message type")
    limit: Optional[int] = Field(50, ge=1, le=1000, description="Number of messages to return")
    offset: Optional[int] = Field(0, ge=0, description="Number of messages to skip")
    
    @validator('message_type')
    def validate_message_type(cls, v):
        if v is not None:
            allowed_types = ['user_message', 'ai_response', 'system_insight']
            if v not in allowed_types:
                raise ValueError(f'Message type must be one of: {allowed_types}')
        return v
