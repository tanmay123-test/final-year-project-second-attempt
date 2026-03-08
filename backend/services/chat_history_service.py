"""
Chat History Service
Manages conversation history for AI Groups
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatHistoryService:
    """
    Service for managing chat history in AI Groups
    """
    
    def __init__(self):
        self.db_path = 'expertease.db'
        
    def _init_database(self):
        """Initialize chat history database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create chat_history table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_history_group_user 
            ON chat_history(group_id, user_id)
            """)
            
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_history_created_at 
            ON chat_history(created_at)
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing chat history database: {str(e)}")
    
    def store_message(self, group_id: int, user_id: int, message: str, message_type: str) -> int:
        """
        Store a message in chat history
        
        Args:
            group_id: Group ID
            user_id: User ID (use -1 for AI)
            message: Message content
            message_type: Type of message (user_message, ai_response, etc.)
            
        Returns:
            Message ID
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO chat_history (group_id, user_id, message, message_type, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (group_id, user_id, message, message_type, datetime.utcnow()))
            
            message_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return message_id
            
        except Exception as e:
            print(f"Error storing message: {str(e)}")
            return 0
    
    def get_chat_history(self, group_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chat history for a group
        
        Args:
            group_id: Group ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM chat_history 
            WHERE group_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """, (group_id, limit))
            
            # Convert to list of dictionaries
            columns = [description[0] for description in cursor.description]
            messages = []
            
            for row in cursor.fetchall():
                message_dict = dict(zip(columns, row))
                messages.append(message_dict)
            
            conn.close()
            return messages
            
        except Exception as e:
            print(f"Error getting chat history: {str(e)}")
            return []
    
    def get_user_messages(self, group_id: int, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get messages from a specific user in a group
        
        Args:
            group_id: Group ID
            user_id: User ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of user's messages
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM chat_history 
            WHERE group_id = ? AND user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """, (group_id, user_id, limit))
            
            # Convert to list of dictionaries
            columns = [description[0] for description in cursor.description]
            messages = []
            
            for row in cursor.fetchall():
                message_dict = dict(zip(columns, row))
                messages.append(message_dict)
            
            conn.close()
            return messages
            
        except Exception as e:
            print(f"Error getting user messages: {str(e)}")
            return []
    
    def get_ai_responses(self, group_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get AI responses in a group
        
        Args:
            group_id: Group ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of AI responses
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM chat_history 
            WHERE group_id = ? AND user_id = -1
            ORDER BY created_at DESC
            LIMIT ?
            """, (group_id, limit))
            
            # Convert to list of dictionaries
            columns = [description[0] for description in cursor.description]
            messages = []
            
            for row in cursor.fetchall():
                message_dict = dict(zip(columns, row))
                messages.append(message_dict)
            
            conn.close()
            return messages
            
        except Exception as e:
            print(f"Error getting AI responses: {str(e)}")
            return []
    
    def search_messages(self, group_id: int, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search messages in a group
        
        Args:
            group_id: Group ID
            query: Search query
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of matching messages
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM chat_history 
            WHERE group_id = ? AND (LOWER(message) LIKE ? OR LOWER(message_type) LIKE ?)
            ORDER BY created_at DESC
            LIMIT ?
            """, (group_id, f"%{query.lower()}%", f"%{query.lower()}%", limit))
            
            # Convert to list of dictionaries
            columns = [description[0] for description in cursor.description]
            messages = []
            
            for row in cursor.fetchall():
                message_dict = dict(zip(columns, row))
                messages.append(message_dict)
            
            conn.close()
            return messages
            
        except Exception as e:
            print(f"Error searching messages: {str(e)}")
            return []
    
    def clear_chat_history(self, group_id: int) -> bool:
        """
        Clear chat history for a group
        
        Args:
            group_id: Group ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            DELETE FROM chat_history WHERE group_id = ?
            """, (group_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error clearing chat history: {str(e)}")
            return False
    
    def get_chat_statistics(self, group_id: int) -> Dict[str, Any]:
        """
        Get chat statistics for a group
        
        Args:
            group_id: Group ID
            
        Returns:
            Dictionary with chat statistics
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total messages
            cursor.execute("""
            SELECT COUNT(*) as total_messages FROM chat_history WHERE group_id = ?
            """, (group_id,))
            total_messages = cursor.fetchone()[0]
            
            # User messages
            cursor.execute("""
            SELECT COUNT(*) as user_messages FROM chat_history 
            WHERE group_id = ? AND user_id != -1
            """, (group_id,))
            user_messages = cursor.fetchone()[0]
            
            # AI responses
            cursor.execute("""
            SELECT COUNT(*) as ai_responses FROM chat_history 
            WHERE group_id = ? AND user_id = -1
            """, (group_id,))
            ai_responses = cursor.fetchone()[0]
            
            # Most active users
            cursor.execute("""
            SELECT user_id, COUNT(*) as message_count FROM chat_history 
            WHERE group_id = ? AND user_id != -1
            GROUP BY user_id
            ORDER BY message_count DESC
            LIMIT 5
            """, (group_id,))
            
            active_users = []
            for row in cursor.fetchall():
                active_users.append({
                    "user_id": row[0],
                    "message_count": row[1]
                })
            
            conn.close()
            
            return {
                "total_messages": total_messages,
                "user_messages": user_messages,
                "ai_responses": ai_responses,
                "active_users": active_users,
                "group_id": group_id
            }
            
        except Exception as e:
            print(f"Error getting chat statistics: {str(e)}")
            return {}
    
    def export_chat_history(self, group_id: int, format: str = "json") -> Optional[str]:
        """
        Export chat history for a group
        
        Args:
            group_id: Group ID
            format: Export format (json, csv, txt)
            
        Returns:
            Exported data as string or None
        """
        try:
            messages = self.get_chat_history(group_id)
            
            if format.lower() == "json":
                import json
                return json.dumps(messages, indent=2, default=str)
            
            elif format.lower() == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow(["id", "group_id", "user_id", "message", "message_type", "created_at"])
                
                # Write data
                for msg in messages:
                    writer.writerow([
                        msg.get("id", ""),
                        msg.get("group_id", ""),
                        msg.get("user_id", ""),
                        msg.get("message", ""),
                        msg.get("message_type", ""),
                        msg.get("created_at", "")
                    ])
                
                return output.getvalue()
            
            elif format.lower() == "txt":
                lines = []
                for msg in messages:
                    timestamp = msg.get("created_at", "")
                    user_type = "AI" if msg.get("user_id") == -1 else f"User {msg.get('user_id', '')}"
                    lines.append(f"[{timestamp}] {user_type}: {msg.get('message', '')}")
                
                return "\n".join(lines)
            
            return None
            
        except Exception as e:
            print(f"Error exporting chat history: {str(e)}")
            return None

# Singleton instance for reuse
chat_history_service = ChatHistoryService()
