"""
Expert chat database for managing real-time messaging between users and experts.
"""
import sqlite3
import json
from datetime import datetime
from config import DATA_DIR
import os

os.makedirs(DATA_DIR, exist_ok=True)

EXPERT_CHAT_DB = os.path.join(DATA_DIR, "expert_chat.db")


class ExpertChatDB:
    def __init__(self):
        self.conn = sqlite3.connect(EXPERT_CHAT_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def get_conn(self):
        return sqlite3.connect(EXPERT_CHAT_DB)

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create chat_rooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                expert_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                room_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (session_id) REFERENCES expert_sessions (id),
                FOREIGN KEY (expert_id) REFERENCES experts (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create chat_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                file_url TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                FOREIGN KEY (room_id) REFERENCES chat_rooms (id)
            )
        """)
        
        # Create chat_participants table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                participant_id INTEGER NOT NULL,
                participant_type TEXT NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                is_online BOOLEAN DEFAULT 0,
                FOREIGN KEY (room_id) REFERENCES chat_rooms (id)
            )
        """)
        
        self.conn.commit()

    def create_chat_room(self, session_id, expert_id, user_id, room_name=None):
        cursor = self.conn.cursor()
        if not room_name:
            room_name = f"Expert Chat {session_id}"
        
        cursor.execute("""
            INSERT INTO chat_rooms (session_id, expert_id, user_id, room_name)
            VALUES (?, ?, ?, ?)
        """, (session_id, expert_id, user_id, room_name))
        self.conn.commit()
        
        room_id = cursor.lastrowid
        
        # Add participants
        self.add_participant(room_id, expert_id, "expert")
        self.add_participant(room_id, user_id, "user")
        
        return room_id

    def add_participant(self, room_id, participant_id, participant_type):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO chat_participants (room_id, participant_id, participant_type)
            VALUES (?, ?, ?)
        """, (room_id, participant_id, participant_type))
        self.conn.commit()

    def send_message(self, room_id, sender_id, sender_type, message, message_type="text", file_url=None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (room_id, sender_id, sender_type, message, message_type, file_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (room_id, sender_id, sender_type, message, message_type, file_url))
        self.conn.commit()
        return cursor.lastrowid

    def get_room_messages(self, room_id, limit=50, offset=0):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_messages 
            WHERE room_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        """, (room_id, limit, offset))
        messages = [dict(row) for row in cursor.fetchall()]
        return messages[::-1]  # Return in chronological order

    def get_chat_room(self, room_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT cr.*, e.worker_id, w.full_name as expert_name, u.name as user_name
            FROM chat_rooms cr
            JOIN experts e ON cr.expert_id = e.id
            JOIN workers w ON e.worker_id = w.id
            JOIN users u ON cr.user_id = u.id
            WHERE cr.id = ?
        """, (room_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_chat_rooms(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT cr.*, e.worker_id, w.full_name as expert_name, 
                   COUNT(cm.id) as unread_count
            FROM chat_rooms cr
            JOIN experts e ON cr.expert_id = e.id
            JOIN workers w ON e.worker_id = w.id
            LEFT JOIN chat_messages cm ON cr.id = cm.room_id 
                AND cm.sender_type = 'expert' AND cm.is_read = 0
            WHERE cr.user_id = ? AND cr.is_active = 1
            GROUP BY cr.id
            ORDER BY cr.created_at DESC
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_expert_chat_rooms(self, expert_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT cr.*, u.name as user_name, u.email as user_email,
                   COUNT(cm.id) as unread_count
            FROM chat_rooms cr
            JOIN users u ON cr.user_id = u.id
            LEFT JOIN chat_messages cm ON cr.id = cm.room_id 
                AND cm.sender_type = 'user' AND cm.is_read = 0
            WHERE cr.expert_id = ? AND cr.is_active = 1
            GROUP BY cr.id
            ORDER BY cr.created_at DESC
        """, (expert_id,))
        return [dict(row) for row in cursor.fetchall()]

    def mark_messages_read(self, room_id, participant_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE chat_messages 
            SET is_read = 1 
            WHERE room_id = ? AND sender_id != ? AND is_read = 0
        """, (room_id, participant_id))
        self.conn.commit()

    def update_participant_status(self, room_id, participant_id, is_online):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE chat_participants 
            SET is_online = ?, last_seen = CURRENT_TIMESTAMP
            WHERE room_id = ? AND participant_id = ?
        """, (is_online, room_id, participant_id))
        self.conn.commit()

    def get_room_participants(self, room_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT cp.*, 
                   CASE 
                       WHEN cp.participant_type = 'expert' THEN w.full_name
                       WHEN cp.participant_type = 'user' THEN u.name
                   END as participant_name
            FROM chat_participants cp
            LEFT JOIN experts e ON cp.participant_id = e.id AND cp.participant_type = 'expert'
            LEFT JOIN workers w ON e.worker_id = w.id
            LEFT JOIN users u ON cp.participant_id = u.id AND cp.participant_type = 'user'
            WHERE cp.room_id = ?
        """, (room_id,))
        return [dict(row) for row in cursor.fetchall()]

    def close_chat_room(self, room_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE chat_rooms 
            SET is_active = 0 
            WHERE id = ?
        """, (room_id,))
        self.conn.commit()

    def get_room_by_session(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_rooms 
            WHERE session_id = ? AND is_active = 1
        """, (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def search_messages(self, room_id, query):
        cursor = self.conn.cursor()
        pattern = f"%{query.strip()}%"
        cursor.execute("""
            SELECT * FROM chat_messages 
            WHERE room_id = ? AND message LIKE ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (room_id, pattern))
        return [dict(row) for row in cursor.fetchall()]


# Global instance
expert_chat_db = ExpertChatDB()
