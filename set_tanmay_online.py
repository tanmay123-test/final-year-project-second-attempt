#!/usr/bin/env python3
"""
Check Tanmay's current status and set him online
"""
import sqlite3
import os

def check_tanmay_status():
    """Check Tanmay's current status in worker database"""
    print("🔍 CHECKING TANMAY'S CURRENT STATUS")
    print("=" * 50)
    
    try:
        # Check worker auth database
        db_path = 'car_service/worker_auth/car_worker_auth.db'
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Find Tanmay (Worker ID 3)
            cursor.execute("SELECT * FROM workers WHERE id = 3 OR username LIKE '%tanmay%'")
            tanmay = cursor.fetchone()
            
            if tanmay:
                print(f"✅ Found Tanmay (ID: {tanmay[0]}):")
                print(f"   Username: {tanmay[1]}")
                print(f"   Email: {tanmay[2]}")
                print(f"   Worker Type: {tanmay[4]}")
                print(f"   Status: {tanmay[5]}")
                print(f"   City: {tanmay[6]}")
                print(f"   Service Area: {tanmay[7]}")
                
                # Check if online_status column exists
                cursor.execute("PRAGMA table_info(workers)")
                columns = cursor.fetchall()
                has_online_status = any('online_status' in col[1] for col in columns)
                
                if has_online_status:
                    print(f"   Online Status: {tanmay[8] if len(tanmay) > 8 else 'offline'}")
                else:
                    print("   ⚠️ No online_status column found")
                    
            else:
                print("❌ Tanmay not found in worker database")
            
            conn.close()
        else:
            print("❌ Worker auth database not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def set_tanmay_online():
    """Set Tanmay's status to online"""
    print("\n🔧 SETTING TANMAY TO ONLINE")
    print("=" * 40)
    
    try:
        db_path = 'car_service/worker_auth/car_worker_auth.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if online_status column exists
        cursor.execute("PRAGMA table_info(workers)")
        columns = cursor.fetchall()
        has_online_status = any('online_status' in col[1] for col in columns)
        
        if not has_online_status:
            # Add online_status column
            cursor.execute("ALTER TABLE workers ADD COLUMN online_status TEXT DEFAULT 'offline'")
            print("✅ Added online_status column")
        
        # Set Tanmay to online and approved
        cursor.execute("""
            UPDATE workers 
            SET status = 'approved', online_status = 'online' 
            WHERE id = 3 OR username LIKE '%tanmay%'
        """)
        
        rows_updated = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_updated > 0:
            print(f"✅ Tanmay is now ONLINE and APPROVED!")
            print(f"📊 Updated {rows_updated} records")
        else:
            print("❌ Failed to update Tanmay's status")
            
    except Exception as e:
        print(f"❌ Error setting Tanmay online: {e}")

if __name__ == "__main__":
    check_tanmay_status()
    set_tanmay_online()
    print("\n🔍 VERIFYING AFTER UPDATE:")
    check_tanmay_status()
