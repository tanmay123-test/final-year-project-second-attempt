#!/usr/bin/env python3

import sqlite3

def create_video_sessions_table():
    """Create video_sessions table manually"""
    
    conn = sqlite3.connect("data/expertease.db")
    cursor = conn.cursor()
    
    # Drop existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS video_sessions")
    
    # Create video_sessions table
    cursor.execute("""
        CREATE TABLE video_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER NOT NULL,
                room_id TEXT NOT NULL UNIQUE,
                doctor_otp TEXT NOT NULL,
                session_status TEXT DEFAULT 'created',
                started_at TIMESTAMP,
                ended_at TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ video_sessions table created successfully!")

if __name__ == "__main__":
    create_video_sessions_table()
