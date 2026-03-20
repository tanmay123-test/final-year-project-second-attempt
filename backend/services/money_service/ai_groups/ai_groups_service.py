"""
AI Groups Service
Business logic and service layer for AI Groups functionality
"""

from .ai_groups_engine import AIGroupsEngine
from datetime import datetime, timedelta
from typing import Dict, Any, List

class AIGroupsService:
    """Service class for AI Groups business logic"""
    
    def __init__(self):
        self.engine = AIGroupsEngine()
    
    def create_group(self, user_id: int, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new group with validation"""
        try:
            # Validate input
            validation_result = self._validate_group_data(group_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Create group
            group_id = self.engine.create_group(
                user_id=user_id,
                name=group_data['name'],
                description=group_data.get('description', ''),
                category=group_data['category']
            )
            
            # Add creator as admin
            self.engine.join_group(user_id, group_id, 'admin')
            
            return {
                'success': True,
                'message': 'Group created successfully',
                'group_id': group_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_available_groups(self, user_id: int = None, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get list of available groups with filtering"""
        try:
            category = filters.get('category') if filters else None
            groups = self.engine.list_groups(user_id, category)
            
            # Apply additional filters
            if filters:
                if 'search' in filters:
                    search_term = filters['search'].lower()
                    groups = [
                        group for group in groups 
                        if search_term in group['name'].lower() or 
                           search_term in (group.get('description', '')).lower()
                    ]
                
                if 'min_members' in filters:
                    min_members = filters['min_members']
                    groups = [
                        group for group in groups 
                        if group.get('members_count', 0) >= min_members
                    ]
            
            return {
                'success': True,
                'groups': groups,
                'total': len(groups)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def join_group(self, user_id: int, join_data: Dict[str, Any]) -> Dict[str, Any]:
        """User joins a group with role validation"""
        try:
            # Validate input
            if 'group_id' not in join_data:
                return {
                    'success': False,
                    'error': 'Group ID is required'
                }
            
            group_id = int(join_data['group_id'])
            role = join_data.get('role', 'member')
            
            # Validate role
            if role not in ['member', 'admin', 'ai_assistant']:
                return {
                    'success': False,
                    'error': 'Invalid role. Must be member, admin, or ai_assistant'
                }
            
            success = self.engine.join_group(user_id, group_id, role)
            
            if success:
                return {
                    'success': True,
                    'message': f'Joined group successfully as {role}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to join group'
                }
                
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_group_details(self, group_id: int, user_id: int = None) -> Dict[str, Any]:
        """Get comprehensive group details"""
        try:
            group_details = self.engine.get_group_details(group_id, user_id)
            
            # Enhance with additional data
            if group_details:
                # Add member statistics
                if 'members' in group_details:
                    admin_count = sum(1 for member in group_details['members'] if member.get('role') == 'admin')
                    member_count = len(group_details['members'])
                    
                    group_details['member_stats'] = {
                        'total_members': member_count,
                        'admin_count': admin_count,
                        'member_count': member_count - admin_count
                    }
                
                # Add message statistics
                if 'messages' in group_details:
                    today = datetime.now()
                    recent_messages = [
                        msg for msg in group_details['messages']
                        if self._is_recent_message(msg.get('created_at'), days=7)
                    ]
                    
                    group_details['message_stats'] = {
                        'total_messages': len(group_details['messages']),
                        'recent_messages_7_days': len(recent_messages),
                        'latest_message': group_details['messages'][0] if group_details['messages'] else None
                    }
            
            return {
                'success': True,
                'group': group_details
            }
            
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_message(self, user_id: int, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send message with validation and rate limiting including AI responses"""
        try:
            # Validate input
            validation_result = self._validate_message_data(message_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            group_id = int(message_data['group_id'])
            message = message_data['message']
            message_type = message_data.get('message_type', 'user_message')
            
            # Check rate limiting (max 10 messages per hour per user per group)
            if self._is_rate_limited(user_id, group_id):
                return {
                    'success': False,
                    'error': 'Rate limit exceeded. Maximum 10 messages per hour per group.'
                }
            
            message_id = self.engine.send_message(user_id, group_id, message, message_type)
            
            # Check if AI should respond
            ai_response = None
            try:
                # Import AI service for CLI
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                from ai.gemini_client import gemini_client
                
                # Check if AI should respond
                if gemini_client.should_respond_to_message(message):
                    # Generate AI response (synchronous for CLI)
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        ai_response_text = loop.run_until_complete(
                            gemini_client.generate_ai_response(message)
                        )
                        
                        # Store AI response
                        ai_response_id = self.engine.send_message(
                            user_id=-1,  # AI user ID
                            group_id=group_id,
                            message=ai_response_text,
                            message_type="ai_response"
                        )
                        
                        ai_response = {
                            'id': ai_response_id,
                            'message': ai_response_text,
                            'message_type': 'ai_response'
                        }
                        
                    finally:
                        loop.close()
                        
            except ImportError:
                # AI service not available, continue without AI response
                pass
            except Exception as e:
                # AI service error, continue without AI response
                print(f"AI Service Error: {e}")
                pass
            
            response_data = {
                'success': True,
                'message': 'Message sent successfully',
                'message_id': message_id,
                'timestamp': datetime.now().isoformat()
            }
            
            if ai_response:
                response_data['ai_response'] = ai_response
            
            return response_data
            
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_groups(self, user_id: int) -> Dict[str, Any]:
        """Get all groups for a user with enhanced data"""
        try:
            groups = self.engine.get_user_groups(user_id)
            
            # Add enhanced statistics
            for group in groups:
                # Get unread count (messages since last visit)
                group['unread_count'] = self._get_unread_count(group['id'], user_id)
                
                # Get activity level
                activity = self._calculate_activity_level(group['id'])
                group['activity_level'] = activity
                
                # Get user's role in each group
                group['user_role'] = self.engine.get_user_role(group['id'], user_id)
            
            return {
                'success': True,
                'groups': groups,
                'total': len(groups)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def leave_group(self, user_id: int, group_id: int) -> Dict[str, Any]:
        """User leaves a group with validation"""
        try:
            # Check if user is member
            if not self.engine.is_user_member(group_id, user_id):
                return {
                    'success': False,
                    'error': 'User is not a member of this group'
                }
            
            # Prevent last admin from leaving
            group_details = self.engine.get_group_details(group_id)
            if group_details:
                admin_count = sum(1 for member in group_details.get('members', []) 
                                if member.get('role') == 'admin')
                user_role = self.engine.get_user_role(group_id, user_id)
                
                if user_role == 'admin' and admin_count <= 1:
                    return {
                        'success': False,
                        'error': 'Cannot leave group. You are the last admin. Please promote another member to admin first.'
                    }
            
            success = self.engine.leave_group(user_id, group_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Left group successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to leave group'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_member_role(self, admin_user_id: int, group_id: int, target_user_id: int, new_role: str) -> Dict[str, Any]:
        """Update member role (admin only)"""
        try:
            # Validate new role
            if new_role not in ['member', 'admin', 'ai_assistant']:
                return {
                    'success': False,
                    'error': 'Invalid role. Must be member, admin, or ai_assistant'
                }
            
            success = self.engine.update_member_role(group_id, target_user_id, new_role, admin_user_id)
            
            if success:
                return {
                    'success': True,
                    'message': f'Member role updated to {new_role}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update member role'
                }
                
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_group(self, admin_user_id: int, group_id: int) -> Dict[str, Any]:
        """Delete group (admin only) with safety checks"""
        try:
            # Get group details for safety check
            group_details = self.engine.get_group_details(group_id)
            
            if not group_details:
                return {
                    'success': False,
                    'error': 'Group not found'
                }
            
            # Safety check: warn if group has more than 10 members
            member_count = len(group_details.get('members', []))
            if member_count > 10:
                return {
                    'success': False,
                    'error': f'Cannot delete group with {member_count} members. Please remove members first or consider archiving the group.'
                }
            
            success = self.engine.delete_group(group_id, admin_user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Group deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to delete group'
                }
                
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_group_analytics(self, group_id: int, user_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a group"""
        try:
            # Check if user is member
            if not self.engine.is_user_member(group_id, user_id):
                return {
                    'success': False,
                    'error': 'Access denied. User is not a member of this group.'
                }
            
            stats = self.engine.get_group_statistics(group_id)
            
            # Calculate additional metrics
            analytics = {
                'basic_stats': stats,
                'engagement_metrics': self._calculate_engagement_metrics(group_id),
                'growth_trends': self._calculate_growth_trends(group_id),
                'top_contributors': self._get_top_contributors(group_id),
                'activity_heatmap': self._generate_activity_heatmap(group_id)
            }
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # Helper methods
    def _validate_group_data(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate group creation data"""
        if 'name' not in group_data or not group_data['name'].strip():
            return {'valid': False, 'error': 'Group name is required'}
        
        if 'category' not in group_data or not group_data['category'].strip():
            return {'valid': False, 'error': 'Category is required'}
        
        name = group_data['name'].strip()
        if len(name) > 100:
            return {'valid': False, 'error': 'Group name must be 100 characters or less'}
        
        description = group_data.get('description', '').strip()
        if len(description) > 500:
            return {'valid': False, 'error': 'Description must be 500 characters or less'}
        
        return {'valid': True}
    
    def _validate_message_data(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate message data"""
        if 'group_id' not in message_data:
            return {'valid': False, 'error': 'Group ID is required'}
        
        if 'message' not in message_data or not message_data['message'].strip():
            return {'valid': False, 'error': 'Message cannot be empty'}
        
        message = message_data['message'].strip()
        if len(message) > 2000:
            return {'valid': False, 'error': 'Message must be 2000 characters or less'}
        
        return {'valid': True}
    
    def _is_rate_limited(self, user_id: int, group_id: int) -> bool:
        """Check if user is rate limited for messages"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        messages = self.engine.get_group_messages(
            group_id=group_id,
            limit=100  # Check last 100 messages
        )
        
        # Count messages from this user in the last hour
        recent_count = sum(1 for msg in messages 
                          if msg['user_id'] == user_id and 
                          self._is_recent_message(msg['created_at'], hours=1))
        
        return recent_count >= 10
    
    def _is_recent_message(self, message_time: str, days: int = None, hours: int = None) -> bool:
        """Check if message is recent"""
        try:
            if isinstance(message_time, str):
                message_time = datetime.fromisoformat(message_time.replace('Z', '+00:00'))
            
            now = datetime.now()
            
            if days:
                return (now - message_time).days <= days
            elif hours:
                return (now - message_time).total_seconds() <= hours * 3600
            else:
                return False
                
        except:
            return False
    
    def _get_unread_count(self, group_id: int, user_id: int) -> int:
        """Get unread message count (simplified - based on recent messages)"""
        messages = self.engine.get_group_messages(group_id, limit=50)
        
        # For now, count messages in last 24 hours as "unread"
        one_day_ago = datetime.now() - timedelta(days=1)
        unread_count = sum(1 for msg in messages 
                          if msg['user_id'] != user_id and 
                          self._is_recent_message(msg['created_at'], days=1))
        
        return unread_count
    
    def _calculate_engagement_metrics(self, group_id: int) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        stats = self.engine.get_group_statistics(group_id)
        
        total_messages = stats.get('messages_count', 0)
        total_members = stats.get('members_count', 1)
        
        if total_members == 0:
            return {'messages_per_member': 0, 'engagement_score': 0}
        
        messages_per_member = total_messages / total_members
        
        # Simple engagement score (0-100)
        engagement_score = min(100, (messages_per_member * 10))
        
        return {
            'messages_per_member': round(messages_per_member, 2),
            'engagement_score': round(engagement_score, 2)
        }
    
    def _calculate_growth_trends(self, group_id: int) -> Dict[str, Any]:
        """Calculate growth trends"""
        # This would require more detailed time-series data
        # For Phase 1, return basic trend info
        stats = self.engine.get_group_statistics(group_id)
        
        return {
            'member_growth': 'stable',  # Would calculate from historical data
            'message_growth': 'increasing',  # Would calculate from historical data
            'trend_period': 'last_30_days'  # Would be configurable
        }
    
    def _get_top_contributors(self, group_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top message contributors"""
        messages = self.engine.get_group_messages(group_id, limit=200)
        
        # Count messages per user
        user_counts = {}
        for msg in messages:
            user_id = msg['user_id']
            user_counts[user_id] = user_counts.get(user_id, 0) + 1
        
        # Sort and get top contributors
        top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {'user_id': user_id, 'message_count': count}
            for user_id, count in top_users
        ]
    
    def _generate_activity_heatmap(self, group_id: int) -> Dict[str, Any]:
        """Generate activity heatmap (simplified for Phase 1)"""
        stats = self.engine.get_group_statistics(group_id)
        
        recent_messages = stats.get('recent_messages_7_days', 0)
        
        # Simple activity level based on recent messages
        if recent_messages == 0:
            activity_level = 'low'
        elif recent_messages < 50:
            activity_level = 'medium'
        else:
            activity_level = 'high'
        
        return {
            'activity_level': activity_level,
            'recent_messages_7_days': recent_messages,
            'heatmap_data': f'Activity level: {activity_level}'  # Would be more detailed in Phase 2
        }
