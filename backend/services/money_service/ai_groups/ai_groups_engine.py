"""
AI Groups Engine
Core engine for AI Groups functionality using existing database patterns
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

class AIGroupsEngine:
    """Main engine for AI Groups using existing database patterns"""
    
    def __init__(self):
        self.conn = sqlite3.connect('expertease.db')
        self.conn.row_factory = sqlite3.Row
        self.create_ai_groups_tables()
    
    def create_ai_groups_tables(self):
        """Create AI Groups tables following existing patterns"""
        cursor = self.conn.cursor()
        
        # AI Groups table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Group Members table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES ai_groups (id)
        )
        """)
        
        # Group Messages table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            message_type TEXT NOT NULL DEFAULT 'user_message',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES ai_groups (id)
        )
        """)
        
        self.conn.commit()
    
    def create_group(self, user_id: int, name: str, description: str, category: str) -> int:
        """Create a new AI group"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO ai_groups (name, description, category, created_at)
            VALUES (?, ?, ?, ?)
            """, (name, description, category, datetime.now()))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Failed to create group: {e}")
    
    def list_groups(self, user_id: int = None, category: str = None) -> List[Dict]:
        """Get list of AI groups"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM ai_groups"
        params = []
        
        if category:
            query += " WHERE category = ?"
            params.append(category)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        groups = [dict(row) for row in cursor.fetchall()]
        
        # Add member and message counts
        for group in groups:
            group['members_count'] = self.get_group_members_count(group['id'])
            group['messages_count'] = self.get_group_messages_count(group['id'])
            
            # Check if user is member
            if user_id:
                group['is_member'] = self.is_user_member(group['id'], user_id)
        
        return groups
    
    def join_group(self, user_id: int, group_id: int, role: str = "member") -> bool:
        """User joins a group"""
        cursor = self.conn.cursor()
        
        try:
            # Check if group exists
            cursor.execute("SELECT id FROM ai_groups WHERE id = ?", (group_id,))
            if not cursor.fetchone():
                raise ValueError("Group not found")
            
            # Check if already a member
            cursor.execute("""
            SELECT id FROM group_members 
            WHERE group_id = ? AND user_id = ?
            """, (group_id, user_id))
            
            if cursor.fetchone():
                raise ValueError("User is already a member of this group")
            
            # Add member
            cursor.execute("""
            INSERT INTO group_members (group_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
            """, (group_id, user_id, role, datetime.now()))
            
            self.conn.commit()
            return True
            
        except ValueError:
            raise
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Failed to join group: {e}")
    
    def get_group_details(self, group_id: int, user_id: int = None) -> Dict:
        """Get detailed group information"""
        cursor = self.conn.cursor()
        
        # Get group info
        cursor.execute("SELECT * FROM ai_groups WHERE id = ?", (group_id,))
        group = cursor.fetchone()
        
        if not group:
            raise ValueError("Group not found")
        
        group = dict(group)
        
        # Get members
        group['members'] = self.get_group_members(group_id)
        
        # Get recent messages
        group['messages'] = self.get_group_messages(group_id, limit=50)
        
        # Check user membership
        if user_id:
            group['user_role'] = self.get_user_role(group_id, user_id)
            group['is_member'] = self.is_user_member(group_id, user_id)
        
        return group
    
    def send_message(self, user_id: int, group_id: int, message: str, message_type: str = "user_message") -> int:
        """Send a message to a group"""
        cursor = self.conn.cursor()
        
        try:
            # Check if user is member
            if not self.is_user_member(group_id, user_id):
                raise ValueError("User is not a member of this group")
            
            cursor.execute("""
            INSERT INTO group_messages (group_id, user_id, message, message_type, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (group_id, user_id, message, message_type, datetime.now()))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except ValueError:
            raise
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Failed to send message: {e}")
    
    def get_group_messages(self, group_id: int, limit: int = 100, message_type: str = None) -> List[Dict]:
        """Get messages for a group"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM group_messages WHERE group_id = ?"
        params = [group_id]
        
        if message_type:
            query += " AND message_type = ?"
            params.append(message_type)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_group_members(self, group_id: int) -> List[Dict]:
        """Get all members of a group"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT gm.*, u.username as username 
        FROM group_members gm
        LEFT JOIN users u ON gm.user_id = u.id
        WHERE gm.group_id = ?
        ORDER BY gm.joined_at ASC
        """, (group_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_user_groups(self, user_id: int) -> List[Dict]:
        """Get all groups a user is a member of"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT ag.*, gm.role as user_role, gm.joined_at as joined_at
        FROM ai_groups ag
        JOIN group_members gm ON ag.id = gm.group_id
        WHERE gm.user_id = ?
        ORDER BY gm.joined_at DESC
        """, (user_id,))
        
        groups = [dict(row) for row in cursor.fetchall()]
        
        # Add counts
        for group in groups:
            group['members_count'] = self.get_group_members_count(group['id'])
            group['messages_count'] = self.get_group_messages_count(group['id'])
        
        return groups
    
    def leave_group(self, user_id: int, group_id: int) -> bool:
        """User leaves a group"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
            DELETE FROM group_members 
            WHERE group_id = ? AND user_id = ?
            """, (group_id, user_id))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Failed to leave group: {e}")
    
    def update_member_role(self, group_id: int, user_id: int, new_role: str, admin_user_id: int) -> bool:
        """Update member role (admin only)"""
        cursor = self.conn.cursor()
        
        try:
            # Check if requester is admin
            if self.get_user_role(group_id, admin_user_id) != 'admin':
                raise ValueError("Only group admins can update member roles")
            
            cursor.execute("""
            UPDATE group_members 
            SET role = ?
            WHERE group_id = ? AND user_id = ?
            """, (new_role, group_id, user_id))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except ValueError:
            raise
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Failed to update member role: {e}")
    
    def delete_group(self, group_id: int, admin_user_id: int) -> bool:
        """Delete a group (admin only)"""
        cursor = self.conn.cursor()
        
        try:
            # Check if user is admin
            if self.get_user_role(group_id, admin_user_id) != 'admin':
                raise ValueError("Only group admins can delete groups")
            
            # Delete group (cascade will handle members and messages)
            cursor.execute("DELETE FROM ai_groups WHERE id = ?", (group_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except ValueError:
            raise
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Failed to delete group: {e}")
    
    # Helper methods
    def is_user_member(self, group_id: int, user_id: int) -> bool:
        """Check if user is a member of group"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT id FROM group_members 
        WHERE group_id = ? AND user_id = ?
        """, (group_id, user_id))
        
        return cursor.fetchone() is not None
    
    def get_user_role(self, group_id: int, user_id: int) -> str:
        """Get user's role in group"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT role FROM group_members 
        WHERE group_id = ? AND user_id = ?
        """, (group_id, user_id))
        
        result = cursor.fetchone()
        return result['role'] if result else None
    
    def get_group_members_count(self, group_id: int) -> int:
        """Get number of members in group"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT COUNT(*) as count FROM group_members 
        WHERE group_id = ?
        """, (group_id,))
        
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def get_group_messages_count(self, group_id: int) -> int:
        """Get number of messages in group"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT COUNT(*) as count FROM group_messages 
        WHERE group_id = ?
        """, (group_id,))
        
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def get_group_statistics(self, group_id: int) -> Dict:
        """Get comprehensive group statistics"""
        cursor = self.conn.cursor()
        
        # Basic stats
        members_count = self.get_group_members_count(group_id)
        messages_count = self.get_group_messages_count(group_id)
        
        # Message type breakdown
        cursor.execute("""
        SELECT message_type, COUNT(*) as count 
        FROM group_messages 
        WHERE group_id = ?
        GROUP BY message_type
        """, (group_id,))
        
        message_types = dict(cursor.fetchall())
        
        # Member role breakdown
        cursor.execute("""
        SELECT role, COUNT(*) as count 
        FROM group_members 
        WHERE group_id = ?
        GROUP BY role
        """, (group_id,))
        
        member_roles = dict(cursor.fetchall())
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        cursor.execute("""
        SELECT COUNT(*) as count 
        FROM group_messages 
        WHERE group_id = ? AND created_at >= ?
        """, (group_id, seven_days_ago))
        
        recent_activity = cursor.fetchone()
        
        return {
            'members_count': members_count,
            'messages_count': messages_count,
            'message_types': message_types,
            'member_roles': member_roles,
            'recent_messages_7_days': recent_activity['count'] if recent_activity else 0
        }
