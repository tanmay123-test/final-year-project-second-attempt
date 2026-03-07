"""
Consultation Session Database
Manages active consultation sessions, messages, calls, and real-time features
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

# Database path
CONSULTATION_SESSION_DB = os.path.join(os.path.dirname(__file__), 'consultation_sessions.db')

class ConsultationSessionDB:
    def __init__(self):
        self.conn = sqlite3.connect(CONSULTATION_SESSION_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def get_conn(self):
        return sqlite3.connect(CONSULTATION_SESSION_DB, check_same_thread=False)
    
    def create_tables(self):
        """Create all required tables for consultation sessions"""
        cursor = self.conn.cursor()
        
        # Consultation sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultation_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                expert_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_duration_seconds INTEGER DEFAULT 0,
                resume_allowed BOOLEAN DEFAULT 1
            )
        """)
        
        # Consultation messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultation_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL,
                sender_id INTEGER NOT NULL,
                message_text TEXT,
                message_type TEXT DEFAULT 'TEXT',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0
            )
        """)
        
        # Consultation typing status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultation_typing_status (
                session_id INTEGER PRIMARY KEY,
                user_typing BOOLEAN DEFAULT 0,
                expert_typing BOOLEAN DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Consultation calls table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultation_calls (
                call_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                started_by TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                call_duration_seconds INTEGER DEFAULT 0,
                call_status TEXT NOT NULL DEFAULT 'INITIATED'
            )
        """)
        
        # Consultation images table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultation_images (
                image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                uploaded_by TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Consultation notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultation_notes (
                note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                expert_id INTEGER NOT NULL,
                note_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    # Consultation Session Management
    def create_consultation_session(self, request_id: int, user_id: int, expert_id: int) -> int:
        """Create a new consultation session when request is accepted"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO consultation_sessions 
            (request_id, user_id, expert_id, status)
            VALUES (?, ?, ?, 'ACTIVE')
        """, (request_id, user_id, expert_id))
        
        session_id = cursor.lastrowid
        self.conn.commit()
        
        # Initialize typing status
        cursor.execute("""
            INSERT INTO consultation_typing_status (session_id)
            VALUES (?)
        """, (session_id,))
        self.conn.commit()
        
        return session_id
    
    def get_active_consultation_session(self, expert_id: int) -> Optional[Dict]:
        """Get expert's current active consultation session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM consultation_sessions
            WHERE expert_id = ? AND status = 'ACTIVE'
        """, (expert_id,))
        
        row = cursor.fetchone()
        if row:
            session_dict = dict(row)
            # Get request details from expert_availability database
            try:
                from .expert_availability_db import expert_availability_db
                av_conn = expert_availability_db.conn.cursor()
                av_conn.execute("""
                    SELECT issue_description, area_of_expertise, user_id
                    FROM consultation_requests
                    WHERE request_id = ?
                """, (session_dict['request_id'],))
                request_row = av_conn.fetchone()
                if request_row:
                    session_dict['issue_description'] = request_row[0]
                    session_dict['area_of_expertise'] = request_row[1]
                    session_dict['user_id'] = request_row[2]
                av_conn.close()
            except Exception:
                pass  # Ignore errors
            return session_dict
        return None
    
    def update_session_status(self, session_id: int, status: str) -> bool:
        """Update consultation session status"""
        valid_statuses = ['ACTIVE', 'PAUSED', 'COMPLETED', 'DISCONNECTED']
        if status not in valid_statuses:
            return False
        
        cursor = self.conn.cursor()
        
        update_data = {"status": status, "last_activity_at": "CURRENT_TIMESTAMP"}
        if status == 'COMPLETED':
            update_data["ended_at"] = "CURRENT_TIMESTAMP"
        
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [session_id]
        
        cursor.execute(f"""
            UPDATE consultation_sessions 
            SET {set_clause}
            WHERE session_id = ?
        """, values)
        
        success = cursor.rowcount > 0
        self.conn.commit()
        return success
    
    def get_session_details(self, session_id: int) -> Optional[Dict]:
        """Get complete session details including messages, images, notes"""
        cursor = self.conn.cursor()
        
        # Get session info
        cursor.execute("""
            SELECT * FROM consultation_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        session = cursor.fetchone()
        if not session:
            return None
        
        session_dict = dict(session)
        
        # Get request details from expert_availability database
        try:
            from .expert_availability_db import expert_availability_db
            av_conn = expert_availability_db.conn.cursor()
            av_conn.execute("""
                SELECT issue_description, area_of_expertise, user_id
                FROM consultation_requests
                WHERE request_id = ?
            """, (session_dict['request_id'],))
            request_row = av_conn.fetchone()
            if request_row:
                session_dict['issue_description'] = request_row[0]
                session_dict['area_of_expertise'] = request_row[1]
                session_dict['user_id'] = request_row[2]
            av_conn.close()
        except Exception:
            pass  # Ignore errors
        
        # Get messages
        cursor.execute("""
            SELECT * FROM consultation_messages 
            WHERE session_id = ? 
            ORDER BY created_at ASC
        """, (session_id,))
        session_dict['messages'] = [dict(row) for row in cursor.fetchall()]
        
        # Get images
        cursor.execute("""
            SELECT * FROM consultation_images 
            WHERE session_id = ? 
            ORDER BY uploaded_at ASC
        """, (session_id,))
        session_dict['images'] = [dict(row) for row in cursor.fetchall()]
        
        # Get notes
        cursor.execute("""
            SELECT * FROM consultation_notes 
            WHERE session_id = ? 
            ORDER BY created_at ASC
        """, (session_id,))
        session_dict['notes'] = [dict(row) for row in cursor.fetchall()]
        
        # Get typing status
        cursor.execute("""
            SELECT * FROM consultation_typing_status 
            WHERE session_id = ?
        """, (session_id,))
        typing_status = cursor.fetchone()
        session_dict['typing_status'] = dict(typing_status) if typing_status else None
        
        # Get call info
        cursor.execute("""
            SELECT * FROM consultation_calls 
            WHERE session_id = ? 
            ORDER BY started_at DESC
        """, (session_id,))
        session_dict['calls'] = [dict(row) for row in cursor.fetchall()]
        
        return session_dict
    
    # Message Management
    def add_message(self, session_id: int, sender_type: str, sender_id: int, 
                    message_text: str, message_type: str = 'TEXT') -> int:
        """Add a message to consultation session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO consultation_messages 
            (session_id, sender_type, sender_id, message_text, message_type)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, sender_type, sender_id, message_text, message_type))
        
        message_id = cursor.lastrowid
        self.conn.commit()
        
        # Update last activity
        cursor.execute("""
            UPDATE consultation_sessions 
            SET last_activity_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()
        
        return message_id
    
    def get_session_messages(self, session_id: int, limit: int = 50) -> List[Dict]:
        """Get messages for a consultation session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM consultation_messages 
            WHERE session_id = ? 
            ORDER BY created_at ASC
            LIMIT ?
        """, (session_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_messages_read(self, session_id: int, expert_id: int) -> int:
        """Mark messages as read for expert"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE consultation_messages 
            SET is_read = 1 
            WHERE session_id = ? AND sender_type = 'USER'
        """, (session_id,))
        
        count = cursor.rowcount
        self.conn.commit()
        return count
    
    # Typing Status Management
    def set_typing_status(self, session_id: int, user_typing: bool = None, expert_typing: bool = None):
        """Update typing status for consultation session"""
        cursor = self.conn.cursor()
        
        update_fields = {}
        if user_typing is not None:
            update_fields["user_typing"] = user_typing
        if expert_typing is not None:
            update_fields["expert_typing"] = expert_typing
        
        if update_fields:
            set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
            values = list(update_fields.values()) + [session_id]
            
            cursor.execute(f"""
                UPDATE consultation_typing_status 
                SET {set_clause}, last_updated = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, values)
            self.conn.commit()
    
    def get_typing_status(self, session_id: int) -> Optional[Dict]:
        """Get typing status for consultation session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM consultation_typing_status 
            WHERE session_id = ?
        """, (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Call Management
    def start_call(self, session_id: int, started_by: str) -> int:
        """Start a voice call session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO consultation_calls 
            (session_id, started_by, call_status)
            VALUES (?, ?, 'ACTIVE')
        """, (session_id, started_by))
        
        call_id = cursor.lastrowid
        self.conn.commit()
        
        # Update last activity
        cursor.execute("""
            UPDATE consultation_sessions 
            SET last_activity_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()
        
        return call_id
    
    def end_call(self, call_id: int, session_id: int) -> bool:
        """End a voice call session"""
        cursor = self.conn.cursor()
        
        # Get call start time to calculate duration
        cursor.execute("""
            SELECT started_at FROM consultation_calls 
            WHERE call_id = ? AND session_id = ?
        """, (call_id, session_id))
        call_start = cursor.fetchone()
        
        if call_start:
            start_time = datetime.strptime(call_start[0], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.now()
            duration_seconds = int((end_time - start_time).total_seconds())
            
            cursor.execute("""
                UPDATE consultation_calls 
                SET ended_at = CURRENT_TIMESTAMP, call_duration_seconds = ?, call_status = 'ENDED'
                WHERE call_id = ? AND session_id = ?
            """, (duration_seconds, call_id, session_id))
            
            cursor.execute("""
                UPDATE consultation_sessions 
                SET last_activity_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))
            
            self.conn.commit()
            return True
        
        return False
    
    # Image Management
    def add_image(self, session_id: int, uploaded_by: str, file_path: str) -> int:
        """Add an image to consultation session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO consultation_images 
            (session_id, uploaded_by, file_path)
            VALUES (?, ?, ?)
        """, (session_id, uploaded_by, file_path))
        
        image_id = cursor.lastrowid
        self.conn.commit()
        
        # Update last activity
        cursor.execute("""
            UPDATE consultation_sessions 
            SET last_activity_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()
        
        return image_id
    
    def get_session_images(self, session_id: int) -> List[Dict]:
        """Get all images for a consultation session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM consultation_images 
            WHERE session_id = ? 
            ORDER BY uploaded_at ASC
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # Notes Management
    def add_note(self, session_id: int, expert_id: int, note_text: str) -> int:
        """Add a note to consultation session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO consultation_notes 
            (session_id, expert_id, note_text)
            VALUES (?, ?, ?)
        """, (session_id, expert_id, note_text))
        
        note_id = cursor.lastrowid
        self.conn.commit()
        
        # Update last activity
        cursor.execute("""
            UPDATE consultation_sessions 
            SET last_activity_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()
        
        return note_id
    
    def update_note(self, note_id: int, expert_id: int, note_text: str) -> bool:
        """Update an existing note"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE consultation_notes 
            SET note_text = ?, updated_at = CURRENT_TIMESTAMP
            WHERE note_id = ? AND expert_id = ?
        """, (note_text, note_id, expert_id))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        return success
    
    def get_session_notes(self, session_id: int) -> List[Dict]:
        """Get all notes for a consultation session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM consultation_notes 
            WHERE session_id = ? 
            ORDER BY created_at ASC
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # Timer Management
    def update_session_duration(self, session_id: int) -> bool:
        """Update cumulative session duration"""
        cursor = self.conn.cursor()
        
        # Get session start time
        cursor.execute("""
            SELECT started_at FROM consultation_sessions 
            WHERE session_id = ? AND status = 'ACTIVE'
        """, (session_id,))
        result = cursor.fetchone()
        
        if result:
            start_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()
            duration_seconds = int((current_time - start_time).total_seconds())
            
            cursor.execute("""
                UPDATE consultation_sessions 
                SET total_duration_seconds = ?, last_activity_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (duration_seconds, session_id))
            
            self.conn.commit()
            return True
        
        return False
    
    def get_session_duration(self, session_id: int) -> int:
        """Get current session duration in seconds"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT started_at, total_duration_seconds FROM consultation_sessions 
            WHERE session_id = ?
        """, (session_id,))
        
        result = cursor.fetchone()
        if result and result[1]:  # total_duration_seconds exists
            return result[1]
        elif result:  # started_at exists but no duration yet
            start_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            return int((datetime.now() - start_time).total_seconds())
        
        return 0

# Create database instance
consultation_session_db = ConsultationSessionDB()
