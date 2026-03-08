"""
AI Groups Service
Business logic for AI Groups functionality
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

from ..models.ai_group import AIGroup
from ..models.group_member import GroupMember
from ..models.group_message import GroupMessage
from ..schemas.ai_group_schema import CreateGroupRequest, JoinGroupRequest
from ..schemas.group_message_schema import SendMessageRequest, MessageFilterRequest

class AIGroupsService:
    """
    Service class for AI Groups business logic
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_group(self, group_request: CreateGroupRequest) -> AIGroup:
        """
        Create a new AI group
        """
        try:
            # Check if group name already exists
            existing_group = self.db.query(AIGroup).filter(
                AIGroup.name == group_request.name
            ).first()
            
            if existing_group:
                raise ValueError(f"Group with name '{group_request.name}' already exists")
            
            # Create new group
            group = AIGroup(
                name=group_request.name,
                description=group_request.description,
                category=group_request.category
            )
            
            self.db.add(group)
            self.db.commit()
            self.db.refresh(group)
            
            return group
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create group: {str(e)}")
    
    def list_groups(
        self, 
        category: Optional[str] = None, 
        limit: int = 50, 
        offset: int = 0
    ) -> Tuple[List[AIGroup], int]:
        """
        Get list of all available groups
        """
        try:
            query = self.db.query(AIGroup)
            
            # Apply category filter if provided
            if category:
                query = query.filter(AIGroup.category == category)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            groups = query.order_by(desc(AIGroup.created_at)).offset(offset).limit(limit).all()
            
            return groups, total
            
        except Exception as e:
            raise ValueError(f"Failed to list groups: {str(e)}")
    
    def join_group(self, join_request: Dict[str, Any]) -> GroupMember:
        """
        User joins a group
        """
        try:
            # Check if group exists
            group = self.db.query(AIGroup).filter(
                AIGroup.id == join_request['group_id']
            ).first()
            
            if not group:
                raise ValueError("Group not found")
            
            # Check if user is already a member
            existing_member = self.db.query(GroupMember).filter(
                and_(
                    GroupMember.group_id == join_request['group_id'],
                    GroupMember.user_id == join_request['user_id']
                )
            ).first()
            
            if existing_member:
                raise ValueError("User is already a member of this group")
            
            # Create new member
            member = GroupMember(
                group_id=join_request['group_id'],
                user_id=join_request['user_id'],
                role=join_request.get('role', 'member')
            )
            
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)
            
            return member
            
        except ValueError:
            raise
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to join group: {str(e)}")
    
    def get_group_details(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Get group details including members and messages
        """
        try:
            # Get group
            group = self.db.query(AIGroup).filter(
                AIGroup.id == group_id
            ).first()
            
            if not group:
                return None
            
            # Get members
            members = self.db.query(GroupMember).filter(
                GroupMember.group_id == group_id
            ).order_by(GroupMember.joined_at).all()
            
            # Get recent messages (last 50)
            messages = self.db.query(GroupMessage).filter(
                GroupMessage.group_id == group_id
            ).order_by(desc(GroupMessage.created_at)).limit(50).all()
            
            return {
                'group': group,
                'members': members,
                'messages': messages
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get group details: {str(e)}")
    
    def send_message(self, message_request: SendMessageRequest) -> GroupMessage:
        """
        Send a message to a group
        """
        try:
            # Check if user is a member of the group
            member = self.db.query(GroupMember).filter(
                and_(
                    GroupMember.group_id == message_request.group_id,
                    GroupMember.user_id == message_request.user_id
                )
            ).first()
            
            if not member:
                raise ValueError("User is not a member of this group")
            
            # Create message
            message = GroupMessage(
                group_id=message_request.group_id,
                user_id=message_request.user_id,
                message=message_request.message,
                message_type=message_request.message_type
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            return message
            
        except ValueError:
            raise
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to send message: {str(e)}")
    
    def get_group_messages(
        self, 
        filter_request: MessageFilterRequest
    ) -> Tuple[List[GroupMessage], int]:
        """
        Get messages for a specific group with filtering
        """
        try:
            query = self.db.query(GroupMessage).filter(
                GroupMessage.group_id == filter_request.group_id
            )
            
            # Apply message type filter if provided
            if filter_request.message_type:
                query = query.filter(
                    GroupMessage.message_type == filter_request.message_type
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            messages = query.order_by(desc(GroupMessage.created_at)).offset(
                filter_request.offset
            ).limit(filter_request.limit).all()
            
            return messages, total
            
        except Exception as e:
            raise ValueError(f"Failed to get messages: {str(e)}")
    
    def get_group_members(self, group_id: int) -> List[GroupMember]:
        """
        Get all members of a group
        """
        try:
            members = self.db.query(GroupMember).filter(
                GroupMember.group_id == group_id
            ).order_by(GroupMember.joined_at).all()
            
            return members
            
        except Exception as e:
            raise ValueError(f"Failed to get group members: {str(e)}")
    
    def leave_group(self, group_id: int, user_id: int) -> bool:
        """
        User leaves a group
        """
        try:
            member = self.db.query(GroupMember).filter(
                and_(
                    GroupMember.group_id == group_id,
                    GroupMember.user_id == user_id
                )
            ).first()
            
            if not member:
                return False
            
            self.db.delete(member)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to leave group: {str(e)}")
    
    def update_member_role(
        self, 
        group_id: int, 
        user_id: int, 
        new_role: str
    ) -> bool:
        """
        Update member role (admin only)
        """
        try:
            member = self.db.query(GroupMember).filter(
                and_(
                    GroupMember.group_id == group_id,
                    GroupMember.user_id == user_id
                )
            ).first()
            
            if not member:
                return False
            
            member.role = new_role
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to update member role: {str(e)}")
    
    def get_user_groups(self, user_id: int) -> List[AIGroup]:
        """
        Get all groups a user is a member of
        """
        try:
            groups = self.db.query(AIGroup).join(GroupMember).filter(
                GroupMember.user_id == user_id
            ).order_by(desc(AIGroup.created_at)).all()
            
            return groups
            
        except Exception as e:
            raise ValueError(f"Failed to get user groups: {str(e)}")
    
    def delete_group(self, group_id: int, user_id: int) -> bool:
        """
        Delete a group (admin only)
        """
        try:
            # Check if user is admin of the group
            member = self.db.query(GroupMember).filter(
                and_(
                    GroupMember.group_id == group_id,
                    GroupMember.user_id == user_id,
                    GroupMember.role == 'admin'
                )
            ).first()
            
            if not member:
                raise ValueError("Only group admins can delete groups")
            
            # Delete group (cascade will handle members and messages)
            group = self.db.query(AIGroup).filter(
                AIGroup.id == group_id
            ).first()
            
            if not group:
                return False
            
            self.db.delete(group)
            self.db.commit()
            
            return True
            
        except ValueError:
            raise
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to delete group: {str(e)}")
