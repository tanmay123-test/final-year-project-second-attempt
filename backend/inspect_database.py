#!/usr/bin/env python3
"""
Database Inspector - View mechanics and workers in database
"""

import sqlite3
import os

def inspect_database():
    """Inspect database for mechanic entries"""
    db_path = 'car_service.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 DATABASE INSPECTOR - MECHANICS & WORKERS")
        print("=" * 60)
        
        # Show all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n🗄️ Available Tables ({len(tables)}):")
        for table in tables:
            print(f"  📋 {table[0]}")
        
        # Check mechanic-related tables
        mechanic_tables = []
        for table in tables:
            table_name = table[0].lower()
            if 'mechanic' in table_name or 'worker' in table_name:
                mechanic_tables.append(table[0])
        
        print(f"\n🔧 Mechanic/Worker Related Tables:")
        for table in mechanic_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table[0]}: {count} records")
            
            # Show sample data
            if count > 0:
                try:
                    cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3")
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                    
                    print(f"    📋 Columns: {', '.join(columns[:5])}")
                    for row in rows:
                        print(f"    📄 Sample: {row[:3]}")
                except Exception as e:
                    print(f"    ⚠️ Could not show sample: {e}")
        
        # Specific mechanic tables to check
        key_tables = ['mechanics', 'workers', 'car_mechanics', 'service_workers']
        
        print(f"\n🔍 KEY MECHANIC TABLES:")
        for table in key_tables:
            if table in [t[0] for t in tables]:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  📋 {table}: {count} records")
                
                if count > 0:
                    try:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                        columns = [description[0] for description in cursor.description]
                        rows = cursor.fetchall()
                        
                        print(f"    📊 Columns: {', '.join(columns)}")
                        for i, row in enumerate(rows, 1):
                            print(f"    {i}. {row}")
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
                else:
                    print(f"    📭 No records found")
            else:
                print(f"  ❌ {table}: Table not found")
        
        # Check dispatch tables
        dispatch_tables = ['mechanic_live_locations', 'worker_metrics', 'mechanic_jobs']
        
        print(f"\n🚀 DISPATCH SYSTEM TABLES:")
        for table in dispatch_tables:
            if table in [t[0] for t in tables]:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: {count} records")
            else:
                print(f"  ❌ {table}: Table not found")
        
        conn.close()
        
        print(f"\n💡 TO ADD MECHANICS:")
        print(f"   1. Use CLI: User → Worker → Signup → Mechanic")
        print(f"   2. Use API: POST /api/car/worker/signup")
        print(f"   3. Use Web: Register through web interface")
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")

if __name__ == "__main__":
    inspect_database()
