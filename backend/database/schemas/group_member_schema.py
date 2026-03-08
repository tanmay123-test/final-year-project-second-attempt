"""
Group Member Pydantic Schemas
Request and response models for group membership
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class GroupMemberRequest(BaseModel):
    """Request schema for group member operations"""
    group_id: int = Field(..., gt=0, description="Group ID")
    user_id: int = Field(..., gt=0, description="User ID")
    role: str = Field(..., description="Member role")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['member', 'admin', 'ai_assistant']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {allowed_roles}')
        return v

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

class GroupMembersListResponse(BaseModel):
    """Response schema for group members list"""
    members: List[GroupMemberResponse]
    total: int
    
    class Config:
        from_attributes = True

class MemberRoleUpdateRequest(BaseModel):
    """Request schema for updating member role"""
    role: str = Field(..., description="New role for member")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['member', 'admin', 'ai_assistant']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {allowed_roles}')
        return v
