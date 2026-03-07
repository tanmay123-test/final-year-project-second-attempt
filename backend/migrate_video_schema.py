#!/usr/bin/env python3
"""
Database migration script for video consultation features
Adds video_room, video_status, and prescription_file columns to appointments table
"""

import sqlite3
import os

def migrate_database():
    """Add missing video consultation columns to appointments table"""
    
    db_path = "data/expertease.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found at:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(appointments)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print("📋 Current columns:", columns)
        
        # Add video_room column if missing
        if 'video_room' not in columns:
            print("➕ Adding video_room column...")
            cursor.execute("ALTER TABLE appointments ADD COLUMN video_room TEXT")
            print("✅ video_room column added")
        else:
            print("✅ video_room column already exists")
        
        # Add video_status column if missing
        if 'video_status' not in columns:
            print("➕ Adding video_status column...")
            cursor.execute("ALTER TABLE appointments ADD COLUMN video_status TEXT DEFAULT 'ready'")
            print("✅ video_status column added")
        else:
            print("✅ video_status column already exists")
        
        # Add prescription_file column if missing
        if 'prescription_file' not in columns:
            print("➕ Adding prescription_file column...")
            cursor.execute("ALTER TABLE appointments ADD COLUMN prescription_file TEXT")
            print("✅ prescription_file column added")
        else:
            print("✅ prescription_file column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify schema
        cursor.execute("PRAGMA table_info(appointments)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print("\n📋 Updated columns:", new_columns)
        
        conn.close()
        
        print("\n🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Starting database migration for video consultation features...")
    print("=" * 60)
    
    success = migrate_database()
    
    if success:
        print("\n✅ Ready to start video consultation system!")
        print("You can now run: python app.py")
    else:
        print("\n❌ Migration failed. Please check the error above.")
