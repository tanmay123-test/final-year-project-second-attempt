"""
AI Groups REST API
REST API endpoints for AI Groups functionality following existing patterns
"""

from flask import Flask, request, jsonify
from datetime import datetime
from typing import Dict, Any, List
from auth_utils import get_current_user_id as _get_current_user_id

class AIGroupsAPI:
    """API class for AI Groups following existing patterns"""
    
    def __init__(self, blueprint=None):
        self.blueprint = blueprint
        if blueprint:
            self.init_blueprint(blueprint)
    
    def init_blueprint(self, blueprint):
        """Initialize Blueprint with AI group API endpoints"""
        self.blueprint = blueprint
        self.register_routes()
    
    def register_routes(self):
        """Register all API routes"""
        
        @self.blueprint.route('/api/money/groups/create', methods=['POST'])
        def create_group_route():
            user_id = _get_current_user_id()
            if not user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            return jsonify(self.create_group(user_id))
            
        @self.blueprint.route('/api/money/groups/list', methods=['GET'])
        def list_groups_route():
            user_id = _get_current_user_id()
            return jsonify(self.list_groups(user_id))
            
        @self.blueprint.route('/api/money/groups/join', methods=['POST'])
        def join_group_route():
            user_id = _get_current_user_id()
            if not user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            return jsonify(self.join_group(user_id))

    def create_group(self, user_id: int) -> Dict[str, Any]:
        """Create a new AI group"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'category']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            name = data['name'].strip()
            description = data.get('description', '').strip()
            category = data['category'].strip()
            
            # Validate data
            if not name:
                return {
                    'success': False,
                    'error': 'Group name cannot be empty'
                }
            
            if not category:
                return {
                    'success': False,
                    'error': 'Category cannot be empty'
                }
            
            # Import engine and create group
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            group_id = engine.create_group(user_id, name, description, category)
            
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
    
    def list_groups(self, user_id: int = None) -> Dict[str, Any]:
        """Get list of all available groups"""
        try:
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            # Get query parameters
            category = request.args.get('category')
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            
            groups = engine.list_groups(user_id, category)
            
            # Apply pagination
            total = len(groups)
            paginated_groups = groups[offset:offset + limit]
            
            return {
                'success': True,
                'groups': paginated_groups,
                'total': total,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def join_group(self, user_id: int) -> Dict[str, Any]:
        """User joins a group"""
        try:
            data = request.get_json()
            
            if 'group_id' not in data:
                return {
                    'success': False,
                    'error': 'Missing group_id'
                }
            
            group_id = int(data['group_id'])
            role = data.get('role', 'member')
            
            # Validate role
            allowed_roles = ['member', 'admin', 'ai_assistant']
            if role not in allowed_roles:
                return {
                    'success': False,
                    'error': f'Role must be one of: {allowed_roles}'
                }
            
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            success = engine.join_group(user_id, group_id, role)
            
            if success:
                return {
                    'success': True,
                    'message': 'Joined group successfully'
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
    
    def get_group_details(self, user_id: int) -> Dict[str, Any]:
        """Get group details including members and messages"""
        try:
            group_id = int(request.args.get('group_id'))
            
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            group_details = engine.get_group_details(group_id, user_id)
            
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
    
    def send_message(self, user_id: int) -> Dict[str, Any]:
        """Send a message to a group"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['group_id', 'message']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            group_id = int(data['group_id'])
            message = data['message'].strip()
            message_type = data.get('message_type', 'user_message')
            
            # Validate message
            if not message:
                return {
                    'success': False,
                    'error': 'Message cannot be empty'
                }
            
            # Validate message type
            allowed_types = ['user_message', 'ai_response', 'system_insight']
            if message_type not in allowed_types:
                return {
                    'success': False,
                    'error': f'Message type must be one of: {allowed_types}'
                }
            
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            message_id = engine.send_message(user_id, group_id, message, message_type)
            
            return {
                'success': True,
                'message': 'Message sent successfully',
                'message_id': message_id
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
    
    def get_group_messages(self, user_id: int) -> Dict[str, Any]:
        """Get messages for a specific group"""
        try:
            group_id = int(request.args.get('group_id'))
            limit = int(request.args.get('limit', 50))
            message_type = request.args.get('message_type')
            
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            # Check if user is member
            if not engine.is_user_member(group_id, user_id):
                return {
                    'success': False,
                    'error': 'User is not a member of this group'
                }
            
            messages = engine.get_group_messages(group_id, limit, message_type)
            
            return {
                'success': True,
                'messages': messages,
                'total': len(messages)
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
    
    def get_group_members(self, user_id: int) -> Dict[str, Any]:
        """Get all members of a group"""
        try:
            group_id = int(request.args.get('group_id'))
            
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            # Check if user is member
            if not engine.is_user_member(group_id, user_id):
                return {
                    'success': False,
                    'error': 'User is not a member of this group'
                }
            
            members = engine.get_group_members(group_id)
            
            return {
                'success': True,
                'members': members,
                'total': len(members)
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
    
    def leave_group(self, user_id: int) -> Dict[str, Any]:
        """User leaves a group"""
        try:
            data = request.get_json()
            
            if 'group_id' not in data:
                return {
                    'success': False,
                    'error': 'Missing group_id'
                }
            
            group_id = int(data['group_id'])
            
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            success = engine.leave_group(user_id, group_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Left group successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Group membership not found'
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
    
    def get_user_groups(self, user_id: int) -> Dict[str, Any]:
        """Get all groups a user is a member of"""
        try:
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            groups = engine.get_user_groups(user_id)
            
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
    
    def get_group_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive group statistics"""
        try:
            group_id = int(request.args.get('group_id'))
            
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            # Check if user is member
            if not engine.is_user_member(group_id, user_id):
                return {
                    'success': False,
                    'error': 'User is not a member of this group'
                }
            
            stats = engine.get_group_statistics(group_id)
            
            return {
                'success': True,
                'statistics': stats
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
