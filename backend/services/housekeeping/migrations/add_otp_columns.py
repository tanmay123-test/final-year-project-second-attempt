import sqlite3
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.append(project_root)

from config import HOUSEKEEPING_DB

def migrate_db():
    print(f"Migrating database at: {HOUSEKEEPING_DB}")
    conn = sqlite3.connect(HOUSEKEEPING_DB)
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'otp' not in columns:
            print("Adding 'otp' column...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN otp TEXT")
            
        if 'started_at' not in columns:
            print("Adding 'started_at' column...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN started_at TEXT")

        if 'retry_count' not in columns:
            print("Adding 'retry_count' column...")
            cursor.execute("ALTER TABLE bookings ADD COLUMN retry_count INTEGER DEFAULT 0")
            
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
