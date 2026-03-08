"""
AI Group Pydantic Schemas
Request and response models for AI Groups API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class CreateGroupRequest(BaseModel):
    """Request schema for creating a new AI group"""
    name: str = Field(..., min_length=1, max_length=100, description="Group name")
    description: Optional[str] = Field(None, max_length=500, description="Group description")
    category: str = Field(..., min_length=1, max_length=50, description="Group category")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Group name cannot be empty')
        return v.strip()
    
    @validator('category')
    def validate_category(cls, v):
        if not v or not v.strip():
            raise ValueError('Category cannot be empty')
        return v.strip()

class JoinGroupRequest(BaseModel):
    """Request schema for joining a group"""
    group_id: int = Field(..., gt=0, description="Group ID to join")
    user_id: int = Field(..., gt=0, description="User ID joining the group")
    role: Optional[str] = Field("member", description="Role in group")

class GroupResponse(BaseModel):
    """Response schema for group data"""
    id: int
    name: str
    description: Optional[str]
    category: str
    created_at: datetime
    members_count: int
    messages_count: int
    
    class Config:
        from_attributes = True

class GroupListResponse(BaseModel):
    """Response schema for group list"""
    groups: List[GroupResponse]
    total: int
    
    class Config:
        from_attributes = True

class GroupMemberResponse(BaseModel):
    """Response schema for group member"""
    id: int
    group_id: int
    user_id: int
    role: str
    joined_at: datetime
    group_name: Optional[str]
    
    class Config:
        from_attributes = True

class GroupMessageRequest(BaseModel):
    """Request schema for sending a message"""
    group_id: int = Field(..., gt=0, description="Group ID")
    user_id: int = Field(..., gt=0, description="User ID sending message")
    message: str = Field(..., min_length=1, max_length=2000, description="Message content")
    message_type: Optional[str] = Field("user_message", description="Type of message")
    
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
    """Response schema for message data"""
    id: int
    group_id: int
    user_id: int
    message: str
    message_type: str
    created_at: datetime
    group_name: Optional[str]
    
    class Config:
        from_attributes = True

class GroupDetailResponse(BaseModel):
    """Response schema for detailed group information"""
    group: GroupResponse
    members: List[GroupMemberResponse]
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True

class APIResponse(BaseModel):
    """Generic API response schema"""
    success: bool
    message: str
    data: Optional[dict] = None
    
    class Config:
        from_attributes = True
