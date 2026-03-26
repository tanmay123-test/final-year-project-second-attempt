#!/usr/bin/env python3
"""
Check database schema to fix the role column issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.freelance.models.database import freelance_db

def check_users_table():
    """Check the structure of the users table"""
    print("🔍 Checking users table structure...")
    
    try:
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        
        # Check if users table exists and get its columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        if columns:
            print("✅ Users table columns:")
            for col in columns:
                print(f"  • {col[0]} ({col[1]})")
        else:
            print("❌ Users table not found or no columns")
            
        # Check if there's a role-related column
        role_columns = [col for col in columns if 'role' in col[0].lower()]
        if role_columns:
            print(f"\n✅ Found role-related columns: {[col[0] for col in role_columns]}")
        else:
            print(f"\n❌ No role column found. Available columns: {[col[0] for col in columns]}")
            
        cursor.close()
        conn.close()
        
        return columns
        
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
        return []

if __name__ == "__main__":
    columns = check_users_table()
    
    print(f"\n🎯 Recommended fix:")
    if columns:
        print(f"Use one of these columns instead of 'role':")
        for col in columns:
            if any(keyword in col[0].lower() for keyword in ['role', 'type', 'user_type', 'account_type']):
                print(f"  • {col[0]}")
