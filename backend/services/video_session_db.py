import sqlite3
import os
from datetime import datetime

class VideoSessionDB:
    def __init__(self):
        self.conn = sqlite3.connect("data/expertease.db", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create video_sessions table"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER NOT NULL,
                room_id TEXT NOT NULL UNIQUE,
                doctor_otp TEXT NOT NULL,
                session_status TEXT DEFAULT 'created',
                started_at TIMESTAMP,
                ended_at TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def create_video_session(self, appointment_id):
        """Create a new video session with OTP"""
        import random
        import string
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        room_id = f"appointment_{appointment_id}"
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO video_sessions (appointment_id, room_id, doctor_otp, session_status)
            VALUES (?, ?, ?, 'created')
        """, (appointment_id, room_id, otp))
        
        self.conn.commit()
        
        return {
            "session_id": cursor.lastrowid,
            "appointment_id": appointment_id,
            "room_id": room_id,
            "doctor_otp": otp,
            "session_status": "created"
        }
    
    def get_session_by_appointment(self, appointment_id):
        """Get video session by appointment ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM video_sessions 
            WHERE appointment_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (appointment_id,))
        
        session = cursor.fetchone()
        return dict(session) if session else None
    
    def verify_doctor_otp(self, appointment_id, otp):
        """Verify doctor OTP for starting call"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM video_sessions 
            WHERE appointment_id = ? AND doctor_otp = ? AND session_status = 'created'
        """, (appointment_id, otp))
        
        session = cursor.fetchone()
        return dict(session) if session else None
    
    def start_session(self, appointment_id):
        """Mark session as live"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE video_sessions 
            SET session_status = 'live', started_at = CURRENT_TIMESTAMP
            WHERE appointment_id = ?
        """, (appointment_id,))
        
        self.conn.commit()
        
        cursor.execute("""
            SELECT * FROM video_sessions 
            WHERE appointment_id = ?
        """, (appointment_id,))
        
        session = cursor.fetchone()
        return dict(session) if session else None
    
    def end_session(self, appointment_id):
        """End the video session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE video_sessions 
            SET session_status = 'ended', ended_at = CURRENT_TIMESTAMP
            WHERE appointment_id = ?
        """, (appointment_id,))
        
        self.conn.commit()
        
        cursor.execute("""
            SELECT * FROM video_sessions 
            WHERE appointment_id = ?
        """, (appointment_id,))
        
        session = cursor.fetchone()
        return dict(session) if session else None
    
    def get_session_by_room(self, room_id):
        """Get session by room ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM video_sessions 
            WHERE room_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (room_id,))
        
        session = cursor.fetchone()
        return dict(session) if session else None
    
    def update_appointment_status(self, appointment_id, status):
        """Update related appointment status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE appointments 
            SET status = ?
            WHERE id = ?
        """, (status, appointment_id))
        
        self.conn.commit()
    
    def get_active_sessions(self):
        """Get all active video sessions"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT vs.*, a.doctor_id, a.user_id, a.status as appointment_status
            FROM video_sessions vs
            JOIN appointments a ON vs.appointment_id = a.id
            WHERE vs.session_status IN ('created', 'live')
            ORDER BY vs.id DESC
        """)
        
        sessions = cursor.fetchall()
        return [dict(session) for session in sessions]
    
    def cleanup_old_sessions(self):
        """Clean up sessions older than 24 hours"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE video_sessions 
            SET session_status = 'ended', ended_at = CURRENT_TIMESTAMP
            WHERE session_status IN ('created', 'live') 
            AND id < (SELECT MAX(id) FROM video_sessions WHERE session_status IN ('created', 'live'))
        """)
        
        self.conn.commit()
        return cursor.rowcount

# Global instance
video_session_db = VideoSessionDB()
