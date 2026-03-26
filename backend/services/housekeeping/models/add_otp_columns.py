"""
Add OTP columns to bookings table for housekeeping service
"""
import sqlite3
import os

def add_otp_columns():
    # Path to housekeeping database
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'housekeeping.db')
    
    if not os.path.exists(db_path):
        print("❌ Housekeeping database not found at:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if otp column exists
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print("📋 Current columns:", columns)
        
        # Add missing columns
        if 'otp' not in columns:
            print("➕ Adding otp column...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN otp TEXT")
            print("✅ OTP column added")
        else:
            print("✅ OTP column already exists")
            
        if 'started_at' not in columns:
            print("➕ Adding started_at column...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN started_at TEXT")
            print("✅ started_at column added")
        else:
            print("✅ started_at column already exists")
            
        if 'retry_count' not in columns:
            print("➕ Adding retry_count column...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN retry_count INTEGER DEFAULT 0")
            print("✅ retry_count column added")
        else:
            print("✅ retry_count column already exists")
        
        conn.commit()
        conn.close()
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    add_otp_columns()
