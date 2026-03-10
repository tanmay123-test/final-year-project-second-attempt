#!/usr/bin/env python3
import sqlite3
import os

db_path = os.path.join('data', 'money_service.db')

def check_schema():
    """Check the exact schema and column order"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get detailed table info
            cursor.execute("PRAGMA table_info(transactions)")
            columns = cursor.fetchall()
            
            print("=== TRANSACTIONS TABLE SCHEMA ===")
            for col in columns:
                print(f"Column {col[0]}: {col[1]} ({col[2]}) - NOT NULL: {col[3]}, DEFAULT: {col[4]}")
            
            print("\n=== SAMPLE DATA ===")
            cursor.execute("SELECT * FROM transactions LIMIT 3")
            rows = cursor.fetchall()
            
            for row in rows:
                print(f"Row: {row}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schema()
