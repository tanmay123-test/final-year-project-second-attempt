"""
Chat History Service
Manages conversation history for AI Financial Assistant
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatHistoryService:
    """
    Service for managing chat history with AI Financial Assistant
    """
    
    def __init__(self):
        self.db_path = 'expertease.db'
        
    def _init_database(self):
        """Initialize chat history database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create chat_history table for AI assistant
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_message TEXT,
                ai_response TEXT,
                message_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_history_user 
            ON chat_history(user_id)
            """)
            
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_history_created_at 
            ON chat_history(created_at)
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing chat history database: {str(e)}")
    
    def store_message(self, chat_id: int, user_id: int, message: str, message_type: str) -> int:
        """
        Store a message in chat history
        
        Args:
            chat_id: Chat session ID (0 for single chat)
            user_id: User ID
            message: Message content (user_message or ai_response)
            message_type: Type of message (user_message, ai_response)
            
        Returns:
            Message ID
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if message_type == "user_message":
                cursor.execute("""
                INSERT INTO chat_history (user_id, user_message, message_type, created_at)
                VALUES (?, ?, ?, ?)
                """, (user_id, message, message_type, datetime.utcnow()))
            else:
                cursor.execute("""
                INSERT INTO chat_history (user_id, ai_response, message_type, created_at)
                VALUES (?, ?, ?, ?)
                """, (user_id, message, message_type, datetime.utcnow()))
            
            message_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return message_id
            
        except Exception as e:
            print(f"Error storing message: {str(e)}")
            return 0
    
    def get_chat_history(self, chat_id: int, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chat history for a user
        
        Args:
            chat_id: Chat session ID (0 for single chat)
            user_id: User ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM chat_history 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """, (user_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                message = dict(row)
                # Format the message content
                if message['user_message']:
                    message['content'] = message['user_message']
                    message['sender'] = 'user'
                else:
                    message['content'] = message['ai_response']
                    message['sender'] = 'ai'
                
                messages.append(message)
            
            conn.close()
            
            # Return in chronological order (oldest first)
            return list(reversed(messages))
            
        except Exception as e:
            print(f"Error retrieving chat history: {str(e)}")
            return []
    
    def get_chat_statistics(self, chat_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get chat statistics for a user
        
        Args:
            chat_id: Chat session ID (0 for single chat)
            user_id: User ID
            
        Returns:
            Dictionary with chat statistics
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total messages
            cursor.execute("""
            SELECT COUNT(*) FROM chat_history WHERE user_id = ?
            """, (user_id,))
            total_messages = cursor.fetchone()[0]
            
            # User messages
            cursor.execute("""
            SELECT COUNT(*) FROM chat_history WHERE user_id = ? AND user_message IS NOT NULL
            """, (user_id,))
            user_messages = cursor.fetchone()[0]
            
            # AI responses
            cursor.execute("""
            SELECT COUNT(*) FROM chat_history WHERE user_id = ? AND ai_response IS NOT NULL
            """, (user_id,))
            ai_responses = cursor.fetchone()[0]
            
            # Message types distribution
            cursor.execute("""
            SELECT message_type, COUNT(*) FROM chat_history 
            WHERE user_id = ? GROUP BY message_type
            """, (user_id,))
            message_types = dict(cursor.fetchall())
            
            # Recent activity (last 7 days)
            cursor.execute("""
            SELECT COUNT(*) FROM chat_history 
            WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
            """, (user_id,))
            recent_messages = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_messages': total_messages,
                'user_messages': user_messages,
                'ai_responses': ai_responses,
                'message_types': message_types,
                'recent_messages_7_days': recent_messages,
                'engagement_score': min(100, (ai_responses / max(1, user_messages)) * 100)
            }
            
        except Exception as e:
            print(f"Error retrieving chat statistics: {str(e)}")
            return {}
    
    def search_messages(self, chat_id: int, user_id: int, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search messages in chat history
        
        Args:
            chat_id: Chat session ID (0 for single chat)
            user_id: User ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM chat_history 
            WHERE user_id = ? AND (
                user_message LIKE ? OR ai_response LIKE ?
            )
            ORDER BY created_at DESC
            LIMIT ?
            """, (user_id, f"%{query}%", f"%{query}%", limit))
            
            messages = []
            for row in cursor.fetchall():
                message = dict(row)
                if message['user_message']:
                    message['content'] = message['user_message']
                    message['sender'] = 'user'
                else:
                    message['content'] = message['ai_response']
                    message['sender'] = 'ai'
                
                messages.append(message)
            
            conn.close()
            return messages
            
        except Exception as e:
            print(f"Error searching messages: {str(e)}")
            return []
    
    def export_chat_history(self, chat_id: int, user_id: int, format: str = 'json') -> str:
        """
        Export chat history
        
        Args:
            chat_id: Chat session ID (0 for single chat)
            user_id: User ID
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported data as string
        """
        try:
            messages = self.get_chat_history(chat_id, user_id, limit=1000)
            
            if format.lower() == 'json':
                import json
                return json.dumps(messages, indent=2, default=str)
            elif format.lower() == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Header
                writer.writerow(['timestamp', 'sender', 'content', 'message_type'])
                
                # Data
                for msg in messages:
                    writer.writerow([
                        msg.get('created_at', ''),
                        msg.get('sender', ''),
                        msg.get('content', ''),
                        msg.get('message_type', '')
                    ])
                
                return output.getvalue()
            else:
                return "Unsupported format. Use 'json' or 'csv'."
                
        except Exception as e:
            print(f"Error exporting chat history: {str(e)}")
            return f"Error: {str(e)}"
    
    def clear_chat_history(self, chat_id: int, user_id: int) -> bool:
        """
        Clear chat history for a user
        
        Args:
            chat_id: Chat session ID (0 for single chat)
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            self._init_database()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            DELETE FROM chat_history WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error clearing chat history: {str(e)}")
            return False

# Singleton instance
chat_history_service = ChatHistoryService()
