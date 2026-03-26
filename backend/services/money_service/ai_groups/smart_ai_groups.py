"""
Smart AI Groups - Main Interface
Main interface for AI Groups functionality following existing patterns
"""

from .ai_groups_engine import AIGroupsEngine
from .ai_groups_service import AIGroupsService
from .ai_groups_api import AIGroupsAPI
from datetime import datetime

class SmartAIGroups:
    """Main interface for Smart AI Groups"""
    
    def __init__(self):
        self.engine = AIGroupsEngine()
        self.service = AIGroupsService()
        self.api = AIGroupsAPI()
    
    def show_menu(self, user_id):
        """Main menu for AI Groups"""
        while True:
            print(f"""
======================================================================
  SMART AI GROUPS
======================================================================
1.   Create New Group
2.   List All Groups
3.   Search Groups
4.   Join Group
5.   My Groups
6.   Group Chat
7.   Group Members
8.   Group Analytics
9.   Chat History
10.    Group Settings
11.    Back to Money Service

Select option: """)
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._create_group(user_id)
            elif choice == "2":
                self._list_all_groups(user_id)
            elif choice == "3":
                self._search_groups(user_id)
            elif choice == "4":
                self._join_group(user_id)
            elif choice == "5":
                self._my_groups(user_id)
            elif choice == "6":
                self._group_chat(user_id)
            elif choice == "7":
                self._group_members(user_id)
            elif choice == "8":
                self._group_analytics(user_id)
            elif choice == "9":
                self._view_chat_history(user_id)
            elif choice == "10":
                self._group_settings(user_id)
            elif choice == "11":
                return
            else:
                print("  Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def _create_group(self, user_id):
        """Create a new AI group"""
        print("\n" + "="*60)
        print("  CREATE NEW GROUP")
        print("="*60)
        
        try:
            # Get group details
            name = input("  Group name: ").strip()
            description = input("  Description (optional): ").strip()
            category = input("   Category: ").strip()
            
            # Validate input
            if not name:
                print("  Group name is required")
                return
            
            if not category:
                print("  Category is required")
                return
            
            # Create group
            result = self.service.create_group(user_id, {
                'name': name,
                'description': description,
                'category': category
            })
            
            if result['success']:
                print(f"\n  {result['message']}")
                print(f"  Group ID: {result['group_id']}")
                
                # Schedule welcome message
                self._schedule_welcome_message(result['group_id'], user_id, name)
            else:
                print(f"\n  {result['error']}")
                
        except Exception as e:
            print(f"\n  Error: {e}")
    
    def _list_all_groups(self, user_id):
        """List all available groups"""
        print("\n" + "="*60)
        print("  AVAILABLE GROUPS")
        print("="*60)
        
        try:
            # Get filter options
            print("\n  FILTER OPTIONS:")
            print("1.   All Groups")
            print("2.    By Category")
            print("3.   Search")
            
            filter_choice = input("\nSelect filter (1-3): ").strip()
            
            filters = {}
            if filter_choice == "2":
                category = input("   Enter category: ").strip()
                if category:
                    filters['category'] = category
            elif filter_choice == "3":
                search = input("  Search term: ").strip()
                if search:
                    filters['search'] = search
            
            # Get groups
            result = self.service.list_available_groups(user_id, filters)
            
            if result['success'] and result['groups']:
                self._display_groups_list(result['groups'])
            else:
                print(f"\n  No groups found")
                if result.get('error'):
                    print(f"  {result['error']}")
                    
        except Exception as e:
            print(f"\n  Error: {e}")
    
    def _search_groups(self, user_id):
        """Search for groups"""
        print("\n" + "="*60)
        print("  SEARCH GROUPS")
        print("="*60)
        
        try:
            search_term = input("  Enter search term: ").strip()
            
            if not search_term:
                print("  Search term is required")
                return
            
            filters = {'search': search_term}
            result = self.service.list_available_groups(user_id, filters)
            
            if result['success'] and result['groups']:
                print(f"\n  Found {len(result['groups'])} groups matching '{search_term}':")
                self._display_groups_list(result['groups'])
            else:
                print(f"\n  No groups found matching '{search_term}'")
                
        except Exception as e:
            print(f"\n  Error: {e}")
    
    def _join_group(self, user_id):
        """Join a group"""
        print("\n" + "="*60)
        print("  JOIN GROUP")
        print("="*60)
        
        try:
            # Show available groups
            result = self.service.list_available_groups(user_id)
            
            if not result['success'] or not result['groups']:
                print("  No available groups to join")
                return
            
            print("\n  AVAILABLE GROUPS:")
            self._display_groups_list(result['groups'][:10])  # Show first 10
            
            group_id = input("\n  Enter Group ID to join (or 'back'): ").strip()
            
            if group_id.lower() == 'back':
                return
            
            try:
                group_id = int(group_id)
                
                # Get role
                print("\n  SELECT ROLE:")
                print("1.   Member")
                print("2.   Admin")
                print("3.   AI Assistant")
                
                role_choice = input("Select role (1-3): ").strip()
                role_map = {'1': 'member', '2': 'admin', '3': 'ai_assistant'}
                role = role_map.get(role_choice, 'member')
                
                # Join group
                join_data = {
                    'group_id': group_id,
                    'role': role
                }
                
                result = self.service.join_group(user_id, join_data)
                
                if result['success']:
                    print(f"\n  {result['message']}")
                    print(f"  Role: {role}")
                    
                    # Schedule join notification
                    self._schedule_join_notification(group_id, user_id, role)
                else:
                    print(f"\n  {result['error']}")
                    
            except ValueError:
                print("  Invalid Group ID")
                
        except Exception as e:
            print(f"\n  Error: {e}")
    
    def _my_groups(self, user_id):
        """Show user's groups"""
        print("\n" + "="*60)
        print("  MY GROUPS")
        print("="*60)
        
        try:
            result = self.service.get_user_groups(user_id)
            
            if result['success'] and result['groups']:
                self._display_user_groups(result['groups'])
            else:
                print("  You haven't joined any groups yet")
                
        except Exception as e:
            print(f"\n  Error: {e}")
    
    def _group_chat(self, user_id):
        """Group chat interface"""
        print("\n" + "="*60)
        print("  GROUP CHAT")
        print("="*60)
        
        try:
            # Show user's groups
            result = self.service.get_user_groups(user_id)
            
            if not result['success'] or not result['groups']:
                print("  Join a group first to access chat")
                return
            
            print("\n  YOUR GROUPS:")
            for i, group in enumerate(result['groups'], 1):
                status = " " if group.get('unread_count', 0) > 0 else " "
                print(f"{i}. {status} {group['name']} ({group.get('unread_count', 0)} unread)")
            
            group_choice = input("\n  Select group (number or 'back'): ").strip()
            
            if group_choice.lower() == 'back':
                return
            
            try:
                choice = int(group_choice) - 1
                if 0 <= choice < len(result['groups']):
                    selected_group = result['groups'][choice]
                    self._enter_group_chat(user_id, selected_group)
                else:
                    print("  Invalid selection")
                    
            except ValueError:
                print("  Invalid selection")
                
        except Exception as e:
            print(f"\n  Error: {e}")
    
    def _enter_group_chat(self, user_id, group):
        """Enter chat interface for a specific group"""
        print(f"\n" + "="*60)
        print(f"  {group['name'].upper()} CHAT")
        print("="*60)
        
        print(f"  Members: {group.get('members_count', 0)}")
        print(f"  Messages: {group.get('messages_count', 0)}")
        print(f"  Your Role: {group.get('user_role', 'member')}")
        
        if group.get('unread_count', 0) > 0:
            print(f"  Unread: {group['unread_count']} messages")
        
        print("\n  CHAT OPTIONS:")
        print("1.   Send Message")
        print("2.   View Recent Messages")
        print("3.   View Members")
        print("4.    Back")
        
        try:
            while True:
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    self._send_chat_message(user_id, group['id'])
                elif choice == "2":
                    self._view_recent_messages(user_id, group['id'])
                elif choice == "3":
                    self._view_group_members(user_id, group['id'])
                elif choice == "4":
                    return
                else:
                    print("  Invalid choice")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    def _send_chat_message(self, user_id: int, group_id: int):
        """Send a chat message to the group"""
        try:
            message = input("\n  Enter your message: ").strip()
            
            if not message:
                print("  Message cannot be empty")
                return
            
            message_data = {
                'group_id': group_id,
                'message': message,
                'message_type': 'user_message'
            }
            
            result = self.service.send_message(user_id, message_data)
            
            if result['success']:
                print(f"\n  Message sent: {message}")
                
                # Check if AI responded
                ai_messages = [msg for msg in result.get('messages', []) 
                              if msg.get('user_id') == -1 and msg.get('group_id') == group_id]
                
                if ai_messages:
                    ai_response = ai_messages[-1]  # Get latest AI response
                    message_type = ai_response.get('message_type', 'ai_response')
                    
                    # Display AI response based on type
                    if message_type == 'ai_stock_comparison':
                        print(f"\n  Stock Comparison:")
                        print("-" * 50)
                        print(f"  {ai_response['message']}")
                        print("-" * 50)
                        print("  This is educational comparison only, not financial advice.")
                        print("  Data provided by stock APIs")
                    elif message_type == 'ai_stock_analysis':
                        print(f"\n  Stock Analysis:")
                        print("-" * 50)
                        print(f"  {ai_response['message']}")
                        print("-" * 50)
                        print("  This is educational analysis only, not financial advice.")
                        print("  Data provided by Finnhub API")
                    elif message_type == 'ai_portfolio_analysis':
                        print(f"\n  Portfolio Analysis:")
                        print("-" * 50)
                        print(f"  {ai_response['message']}")
                        print("-" * 50)
                        print("  This is educational analysis only, not financial advice.")
                        print("  Based on your portfolio data")
                    elif message_type == 'ai_knowledge_response':
                        print(f"\n  Knowledge Response:")
                        print("-" * 50)
                        print(f"  {ai_response['message']}")
                        print("-" * 50)
                        print("  Educational information from financial knowledge base")
                        print("  Powered by vector search")
                    elif message_type == 'ai_news_summary':
                        print(f"\n  News Summary:")
                        print("-" * 50)
                        print(f"  {ai_response['message']}")
                        print("-" * 50)
                        print("  Financial news summary and market analysis")
                        print("  Data from Finnhub News API")
                    else:
                        print(f"\n  AI Response:")
                        print("-" * 50)
                        print(f"{ai_response['message']}")
                        print("-" * 50)
                        print("  Remember: This is educational information only, not financial advice.")
                else:
                    # Check if message might trigger AI but didn't respond
                    if self._should_show_ai_hint(message):
                        print("\n  AI Assistant didn't respond. Try using financial keywords like:")
                        print("     'explain what is...'")
                        print("     'how does... work'")
                        print("     'what is a stock'")
                        print("     'analyze [company] stock'")
                        print("     'search for [industry] companies'")
                        print("     'what is diversification?'")
                        print("     'analyze my portfolio'")
                        print("     'what's happening in the market?'")
                        print("     'explain [financial concept]'")
            else:
                print(f"  {result['error']}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    def _should_show_ai_hint(self, message: str) -> bool:
        """Check if user might be expecting an AI response"""
        message_lower = message.lower()
        question_words = ['what', 'how', 'why', 'explain', 'tell me']
        return any(word in message_lower for word in question_words)
    
    def _view_recent_messages(self, user_id, group_id):
        """View recent messages"""
        try:
            limit = input("  Number of messages (default 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            messages = engine.get_group_messages(group_id, limit)
            
            if messages:
                print(f"\n  RECENT MESSAGES (Last {len(messages)}):")
                print("-" * 60)
                for msg in messages:
                    sender = f"User {msg['user_id']}"
                    msg_type = msg.get('message_type', 'user_message')
                    time = msg.get('created_at', '')[:19]  # Format datetime
                    
                    print(f"  {time}")
                    print(f"  {sender}")
                    print(f"  {msg['message'][:100]}{'...' if len(msg['message']) > 100 else ''}")
                    print("-" * 60)
            else:
                print("  No messages found")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    def _view_group_members(self, user_id, group_id):
        """View group members"""
        try:
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            members = engine.get_group_members(group_id)
            
            if members:
                print(f"\n  GROUP MEMBERS ({len(members)}):")
                print("-" * 60)
                for member in members:
                    role_emoji = {
                        'admin': ' ',
                        'member': ' ',
                        'ai_assistant': ' '
                    }.get(member.get('role', 'member'), ' ')
                    
                    joined = member.get('joined_at', '')[:10]
                    username = member.get('username', f"User {member['user_id']}")
                    
                    print(f"{role_emoji} {username} - {member['role']} (joined {joined})")
            else:
                print("  No members found")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    def _group_members(self, user_id):
        """View group members"""
        print("\n" + "="*60)
        print("  GROUP MEMBERS")
        print("="*60)
        
        try:
            # Show user's groups
            result = self.service.get_user_groups(user_id)
            
            if not result['success'] or not result['groups']:
                print("  Join a group first")
                return
            
            print("\n  YOUR GROUPS:")
            for i, group in enumerate(result['groups'], 1):
                print(f"{i}. {group['name']}")
            
            group_choice = input("\n  Select group (number or 'back'): ").strip()
            
            if group_choice.lower() == 'back':
                return
            
            try:
                choice = int(group_choice) - 1
                if 0 <= choice < len(result['groups']):
                    selected_group = result['groups'][choice]
                    self._view_group_members(user_id, selected_group['id'])
                else:
                    print("  Invalid selection")
                    
            except ValueError:
                print("  Invalid selection")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    def _group_analytics(self, user_id):
        """Show group analytics"""
        print("\n" + "="*60)
        print("  GROUP ANALYTICS")
        print("="*60)
        
        try:
            # Show user's groups
            result = self.service.get_user_groups(user_id)
            
            if not result['success'] or not result['groups']:
                print("  Join a group first to view analytics")
                return
            
            print("\n  YOUR GROUPS:")
            for i, group in enumerate(result['groups'], 1):
                print(f"{i}. {group['name']}")
            
            group_choice = input("\n  Select group (number or 'back'): ").strip()
            
            if group_choice.lower() == 'back':
                return
            
            try:
                choice = int(group_choice) - 1
                if 0 <= choice < len(result['groups']):
                    selected_group_id = result['groups'][choice]['id']
                    self._show_analytics(user_id, selected_group_id)
                else:
                    print("  Invalid selection")
                    
            except ValueError:
                print("  Invalid selection")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    def _show_analytics(self, user_id, group_id):
        """Show detailed analytics for a group"""
        try:
            result = self.service.get_group_analytics(group_id, user_id)
            
            if result['success']:
                analytics = result['analytics']
                
                print(f"\n  GROUP ANALYTICS:")
                print("-" * 60)
                
                # Basic stats
                basic = analytics.get('basic_stats', {})
                print(f"  Total Members: {basic.get('members_count', 0)}")
                print(f"  Total Messages: {basic.get('messages_count', 0)}")
                print(f"  Recent Activity (7 days): {basic.get('recent_messages_7_days', 0)}")
                
                # Engagement metrics
                engagement = analytics.get('engagement_metrics', {})
                print(f"  Messages per Member: {engagement.get('messages_per_member', 0)}")
                print(f"  Engagement Score: {engagement.get('engagement_score', 0)}/100")
                
                # Message types
                message_types = basic.get('message_types', {})
                print(f"\n  MESSAGE TYPES:")
                for msg_type, count in message_types.items():
                    print(f"   {msg_type}: {count}")
                
                # Top contributors
                contributors = analytics.get('top_contributors', [])
                if contributors:
                    print(f"\n  TOP CONTRIBUTORS:")
                    for i, contributor in enumerate(contributors[:5], 1):
                        print(f"   {i}. User {contributor['user_id']}: {contributor['message_count']} messages")
                
            else:
                print(f"  {result.get('error', 'Failed to load analytics')}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    def _group_settings(self, user_id):
        """Group settings management"""
        print("\n" + "="*60)
        print("   GROUP SETTINGS")
        print("="*60)
        
        print("   SETTINGS OPTIONS:")
        print("1.   Leave Group")
        print("2.   Manage Members")
        print("3.    Edit Group Info")
        print("4.   Group Analytics")
        print("5.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            self._leave_group_settings(user_id)
        elif choice == "2":
            self._manage_members_settings(user_id)
        elif choice == "3":
            self._edit_group_settings(user_id)
        elif choice == "4":
            self._group_analytics(user_id)
        elif choice == "5":
            return
        else:
            print("  Invalid choice")
    
    def _leave_group_settings(self, user_id):
        """Leave a group from settings"""
        try:
            # Show user's groups
            result = self.service.get_user_groups(user_id)
            
            if not result['success'] or not result['groups']:
                print("  No groups to leave")
                return
            
            print("\n  YOUR GROUPS:")
            for i, group in enumerate(result['groups'], 1):
                role = group.get('user_role', 'member')
                print(f"{i}. {group['name']} ({role})")
            
            group_choice = input("\n  Select group to leave (number or 'back'): ").strip()
            
            if group_choice.lower() == 'back':
                return
            
            try:
                choice = int(group_choice) - 1
                if 0 <= choice < len(result['groups']):
                    selected_group_id = result['groups'][choice]['id']
                    
                    confirm = input(f"\n   Leave '{result['groups'][choice]['name']}'? (yes/no): ").strip().lower()
                    
                    if confirm in ['yes', 'y']:
                        result = self.service.leave_group(user_id, selected_group_id)
                        
                        if result['success']:
                            print("  Left group successfully")
                        else:
                            print(f"  {result['error']}")
                    else:
                        print("  Cancelled")
                else:
                    print("  Invalid selection")
                    
            except ValueError:
                print("  Invalid selection")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    def _manage_members_settings(self, user_id):
        """Manage group members (admin only)"""
        print("\n  ADMIN-ONLY FEATURE")
        print("This feature is only available to group administrators")
        input("\nPress Enter to continue...")
    
    def _edit_group_settings(self, user_id):
        """Edit group information (admin only)"""
        print("\n  ADMIN-ONLY FEATURE")
        print("This feature is only available to group administrators")
        input("\nPress Enter to continue...")
    
    # Helper methods
    def _display_groups_list(self, groups):
        """Display list of groups"""
        if not groups:
            print("  No groups found")
            return
        
        print(f"\n  FOUND {len(groups)} GROUPS:")
        print("-" * 60)
        print(f"{'ID':<6} {'NAME':<25} {'CATEGORY':<15} {'MEMBERS':<10} {'MESSAGES':<10}")
        print("-" * 60)
        
        for group in groups:
            print(f"{group['id']:<6} {group['name']:<25} {group.get('category', 'N/A'):<15} "
                  f"{group.get('members_count', 0):<10} {group.get('messages_count', 0):<10}")
    
    def _display_user_groups(self, groups):
        """Display user's groups with enhanced info"""
        if not groups:
            print("  You haven't joined any groups yet")
            return
        
        print(f"\n  YOUR GROUPS ({len(groups)}):")
        print("-" * 60)
        
        for group in groups:
            unread = group.get('unread_count', 0)
            activity = group.get('activity_level', 'unknown')
            activity_emoji = {'high': ' ', 'medium': ' ', 'low': ' ', 'stable': ' '}.get(activity, ' ')
            
            print(f"\n  {group['name']}")
            print(f"     Role: {group.get('user_role', 'member')}")
            print(f"     Members: {group.get('members_count', 0)}")
            print(f"     Messages: {group.get('messages_count', 0)}")
            print(f"     Unread: {unread}")
            print(f"     Activity: {activity_emoji} {activity}")
    
    def _schedule_welcome_message(self, group_id: int, user_id: int, group_name: str):
        """Schedule a welcome message when group is created"""
        try:
            welcome_msg = f"  Welcome to '{group_name}'! This group has been created successfully."
            
            message_data = {
                'group_id': group_id,
                'message': welcome_msg,
                'message_type': 'system_insight'
            }
            
            self.service.send_message(user_id, message_data)
        except:
            pass  # Don't fail group creation if welcome message fails
    
    def _schedule_join_notification(self, group_id: int, user_id: int, role: str):
        """Schedule a join notification"""
        try:
            from .ai_groups_engine import AIGroupsEngine
            engine = AIGroupsEngine()
            
            group_details = engine.get_group_details(group_id)
            group_name = group_details.get('name', f'Group {group_id}')
            
            notification_msg = f"  A new member has joined '{group_name}' as {role}."
            
            message_data = {
                'group_id': group_id,
                'message': notification_msg,
                'message_type': 'system_insight'
            }
            
            self.service.send_message(user_id, message_data)
        except:
            pass  # Don't fail join if notification fails
