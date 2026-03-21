"""
Consultation Session Database
Manages active consultation sessions, messages, calls, and real-time features
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Optional

load_dotenv()

class ConsultationSessionDB:
    def __init__(self):
        self.create_tables()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def create_tables(self):
        """Create all required tables for consultation sessions"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Consultation sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultation_sessions (
                    session_id SERIAL PRIMARY KEY,
                    request_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    expert_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ACTIVE',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_duration_seconds INTEGER DEFAULT 0,
                    resume_allowed BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Consultation messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultation_messages (
                    message_id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    sender_type TEXT NOT NULL,
                    sender_id INTEGER NOT NULL,
                    message_text TEXT,
                    message_type TEXT DEFAULT 'TEXT',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Consultation typing status table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultation_typing_status (
                    session_id INTEGER PRIMARY KEY,
                    user_typing BOOLEAN DEFAULT FALSE,
                    expert_typing BOOLEAN DEFAULT FALSE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Consultation calls table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultation_calls (
                    call_id SERIAL PRIMARY KEY,
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
                    image_id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    uploaded_by TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Consultation notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultation_notes (
                    note_id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    expert_id INTEGER NOT NULL,
                    note_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # Consultation Session Management
    def create_consultation_session(self, request_id: int, user_id: int, expert_id: int) -> int:
        """Create a new consultation session when request is accepted"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO consultation_sessions 
                (request_id, user_id, expert_id, status)
                VALUES (%s, %s, %s, 'ACTIVE')
                RETURNING session_id
            """, (request_id, user_id, expert_id))
            
            session_id = cursor.fetchone()[0]
            
            # Initialize typing status
            cursor.execute("""
                INSERT INTO consultation_typing_status (session_id)
                VALUES (%s)
            """, (session_id,))
            
            conn.commit()
            return session_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_active_consultation_session(self, expert_id: int) -> Optional[Dict]:
        """Get expert's current active consultation session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM consultation_sessions
                WHERE expert_id = %s AND status = 'ACTIVE'
            """, (expert_id,))
            
            row = cursor.fetchone()
            if row:
                session_dict = dict(row)
                # Get request details from expert_availability database
                try:
                    from .expert_availability_db import expert_availability_db
                    # expert_availability_db is already migrated to PostgreSQL
                    av_conn = expert_availability_db.get_conn()
                    av_cursor = av_conn.cursor()
                    av_cursor.execute("""
                        SELECT issue_description, area_of_expertise, user_id
                        FROM consultation_requests
                        WHERE request_id = %s
                    """, (session_dict['request_id'],))
                    request_row = av_cursor.fetchone()
                    if request_row:
                        session_dict['issue_description'] = request_row[0]
                        session_dict['area_of_expertise'] = request_row[1]
                        session_dict['user_id'] = request_row[2]
                    av_cursor.close()
                    av_conn.close()
                except Exception:
                    pass  # Ignore errors
                return session_dict
            return None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_session_status(self, session_id: int, status: str) -> bool:
        """Update consultation session status"""
        valid_statuses = ['ACTIVE', 'PAUSED', 'COMPLETED', 'DISCONNECTED']
        if status not in valid_statuses:
            return False
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            now = datetime.now()
            if status == 'COMPLETED':
                cursor.execute("""
                    UPDATE consultation_sessions 
                    SET status = %s, last_activity_at = %s, ended_at = %s
                    WHERE session_id = %s
                """, (status, now, now, session_id))
            else:
                cursor.execute("""
                    UPDATE consultation_sessions 
                    SET status = %s, last_activity_at = %s
                    WHERE session_id = %s
                """, (status, now, session_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_session_details(self, session_id: int) -> Optional[Dict]:
        """Get complete session details including messages, images, notes"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Get session info
            cursor.execute("""
                SELECT * FROM consultation_sessions
                WHERE session_id = %s
            """, (session_id,))
            
            session = cursor.fetchone()
            if not session:
                return None
            
            session_dict = dict(session)
            
            # Get request details from expert_availability database
            try:
                from .expert_availability_db import expert_availability_db
                av_conn = expert_availability_db.get_conn()
                av_cursor = av_conn.cursor()
                av_cursor.execute("""
                    SELECT issue_description, area_of_expertise, user_id
                    FROM consultation_requests
                    WHERE request_id = %s
                """, (session_dict['request_id'],))
                request_row = av_cursor.fetchone()
                if request_row:
                    session_dict['issue_description'] = request_row[0]
                    session_dict['area_of_expertise'] = request_row[1]
                    session_dict['user_id'] = request_row[2]
                av_cursor.close()
                av_conn.close()
            except Exception:
                pass  # Ignore errors
            
            # Get messages
            cursor.execute("""
                SELECT * FROM consultation_messages 
                WHERE session_id = %s 
                ORDER BY created_at ASC
            """, (session_id,))
            session_dict['messages'] = [dict(row) for row in cursor.fetchall()]
            
            # Get images
            cursor.execute("""
                SELECT * FROM consultation_images 
                WHERE session_id = %s 
                ORDER BY uploaded_at ASC
            """, (session_id,))
            session_dict['images'] = [dict(row) for row in cursor.fetchall()]
            
            # Get notes
            cursor.execute("""
                SELECT * FROM consultation_notes 
                WHERE session_id = %s 
                ORDER BY created_at ASC
            """, (session_id,))
            session_dict['notes'] = [dict(row) for row in cursor.fetchall()]
            
            # Get typing status
            cursor.execute("""
                SELECT * FROM consultation_typing_status 
                WHERE session_id = %s
            """, (session_id,))
            typing_status = cursor.fetchone()
            session_dict['typing_status'] = dict(typing_status) if typing_status else None
            
            # Get call info
            cursor.execute("""
                SELECT * FROM consultation_calls 
                WHERE session_id = %s 
                ORDER BY started_at DESC
            """, (session_id,))
            session_dict['calls'] = [dict(row) for row in cursor.fetchall()]
            
            return session_dict
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # Message Management
    def add_message(self, session_id: int, sender_type: str, sender_id: int, 
                    message_text: str, message_type: str = 'TEXT') -> int:
        """Add a message to consultation session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO consultation_messages 
                (session_id, sender_type, sender_id, message_text, message_type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING message_id
            """, (session_id, sender_type, sender_id, message_text, message_type))
            
            message_id = cursor.fetchone()[0]
            
            # Update last activity
            cursor.execute("""
                UPDATE consultation_sessions 
                SET last_activity_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            """, (session_id,))
            
            conn.commit()
            return message_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_session_messages(self, session_id: int, limit: int = 50) -> List[Dict]:
        """Get messages for a consultation session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM consultation_messages 
                WHERE session_id = %s 
                ORDER BY created_at ASC
                LIMIT %s
            """, (session_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def mark_messages_read(self, session_id: int, expert_id: int) -> int:
        """Mark messages as read for expert"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE consultation_messages 
                SET is_read = TRUE 
                WHERE session_id = %s AND sender_type = 'USER'
            """, (session_id,))
            
            count = cursor.rowcount
            conn.commit()
            return count
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # Typing Status Management
    def set_typing_status(self, session_id: int, user_typing: bool = None, expert_typing: bool = None):
        """Update typing status for consultation session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            if user_typing is not None and expert_typing is not None:
                cursor.execute("""
                    UPDATE consultation_typing_status 
                    SET user_typing = %s, expert_typing = %s, last_updated = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (user_typing, expert_typing, session_id))
            elif user_typing is not None:
                cursor.execute("""
                    UPDATE consultation_typing_status 
                    SET user_typing = %s, last_updated = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (user_typing, session_id))
            elif expert_typing is not None:
                cursor.execute("""
                    UPDATE consultation_typing_status 
                    SET expert_typing = %s, last_updated = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (expert_typing, session_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_typing_status(self, session_id: int) -> Optional[Dict]:
        """Get typing status for consultation session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM consultation_typing_status 
                WHERE session_id = %s
            """, (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # Call Management
    def start_call(self, session_id: int, started_by: str) -> int:
        """Start a voice call session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO consultation_calls 
                (session_id, started_by, call_status)
                VALUES (%s, %s, 'ACTIVE')
                RETURNING call_id
            """, (session_id, started_by))
            
            call_id = cursor.fetchone()[0]
            
            # Update last activity
            cursor.execute("""
                UPDATE consultation_sessions 
                SET last_activity_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            """, (session_id,))
            
            conn.commit()
            return call_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def end_call(self, call_id: int, session_id: int) -> bool:
        """End a voice call session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Get call start time to calculate duration
            cursor.execute("""
                SELECT started_at FROM consultation_calls 
                WHERE call_id = %s AND session_id = %s
            """, (call_id, session_id))
            call_start = cursor.fetchone()
            
            if call_start:
                start_time = call_start[0] # PostgreSQL returns datetime object
                if isinstance(start_time, str):
                    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                
                end_time = datetime.now()
                duration_seconds = int((end_time - start_time).total_seconds())
                
                cursor.execute("""
                    UPDATE consultation_calls 
                    SET ended_at = CURRENT_TIMESTAMP, call_duration_seconds = %s, call_status = 'ENDED'
                    WHERE call_id = %s AND session_id = %s
                """, (duration_seconds, call_id, session_id))
                
                cursor.execute("""
                    UPDATE consultation_sessions 
                    SET last_activity_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (session_id,))
                
                conn.commit()
                return True
            
            return False
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # Image Management
    def add_image(self, session_id: int, uploaded_by: str, file_path: str) -> int:
        """Add an image to consultation session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO consultation_images 
                (session_id, uploaded_by, file_path)
                VALUES (%s, %s, %s)
                RETURNING image_id
            """, (session_id, uploaded_by, file_path))
            
            image_id = cursor.fetchone()[0]
            
            # Update last activity
            cursor.execute("""
                UPDATE consultation_sessions 
                SET last_activity_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            """, (session_id,))
            
            conn.commit()
            return image_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_session_images(self, session_id: int) -> List[Dict]:
        """Get all images for a consultation session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM consultation_images 
                WHERE session_id = %s 
                ORDER BY uploaded_at ASC
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # Notes Management
    def add_note(self, session_id: int, expert_id: int, note_text: str) -> int:
        """Add a note to consultation session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO consultation_notes 
                (session_id, expert_id, note_text)
                VALUES (%s, %s, %s)
                RETURNING note_id
            """, (session_id, expert_id, note_text))
            
            note_id = cursor.fetchone()[0]
            
            # Update last activity
            cursor.execute("""
                UPDATE consultation_sessions 
                SET last_activity_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            """, (session_id,))
            
            conn.commit()
            return note_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_note(self, note_id: int, expert_id: int, note_text: str) -> bool:
        """Update an existing note"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE consultation_notes 
                SET note_text = %s, updated_at = CURRENT_TIMESTAMP
                WHERE note_id = %s AND expert_id = %s
            """, (note_text, note_id, expert_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_session_notes(self, session_id: int) -> List[Dict]:
        """Get all notes for a consultation session"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM consultation_notes 
                WHERE session_id = %s 
                ORDER BY created_at ASC
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # Timer Management
    def update_session_duration(self, session_id: int) -> bool:
        """Update cumulative session duration"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Get session start time
            cursor.execute("""
                SELECT started_at FROM consultation_sessions 
                WHERE session_id = %s AND status = 'ACTIVE'
            """, (session_id,))
            result = cursor.fetchone()
            
            if result:
                start_time = result[0]
                if isinstance(start_time, str):
                    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.now()
                duration_seconds = int((current_time - start_time).total_seconds())
                
                cursor.execute("""
                    UPDATE consultation_sessions 
                    SET total_duration_seconds = %s, last_activity_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (duration_seconds, session_id))
                
                conn.commit()
                return True
            
            return False
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_session_duration(self, session_id: int) -> int:
        """Get current session duration in seconds"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT started_at, total_duration_seconds FROM consultation_sessions 
                WHERE session_id = %s
            """, (session_id,))
            
            result = cursor.fetchone()
            if result and result[1]:  # total_duration_seconds exists
                return result[1]
            elif result:  # started_at exists but no duration yet
                start_time = result[0]
                if isinstance(start_time, str):
                    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                return int((datetime.now() - start_time).total_seconds())
            
            return 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

# Create database instance
consultation_session_db = ConsultationSessionDB()
