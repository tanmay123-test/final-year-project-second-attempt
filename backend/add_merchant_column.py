#!/usr/bin/env python3
import sqlite3
import os

# Database path
db_path = os.path.join('data', 'money_service.db')

def add_merchant_column():
    """Add merchant column to transactions table"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if merchant column already exists
            cursor.execute("PRAGMA table_info(transactions)")
            columns = [column[1] for column in cursor.fetchall()]
            
            print("Current columns:", columns)
            
            if 'merchant' not in columns:
                print("Adding merchant column...")
                cursor.execute("ALTER TABLE transactions ADD COLUMN merchant TEXT")
                conn.commit()
                print("✅ Merchant column added successfully!")
            else:
                print("✅ Merchant column already exists!")
                
            # Verify the column was added
            cursor.execute("PRAGMA table_info(transactions)")
            columns = [column[1] for column in cursor.fetchall()]
            print("Updated columns:", columns)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_merchant_column()
