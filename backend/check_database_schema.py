import psycopg2
import psycopg2.extras
from database.database_manager import DatabaseManager

print("=== CHECKING DATABASE SCHEMA FOR WORKERS TABLE ===")
print()

try:
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Check the workers table structure
    cursor.execute("""
        SELECT column_name, column_default, is_nullable, data_type
        FROM information_schema.columns
        WHERE table_name = 'workers' AND column_name = 'status'
    """)
    
    status_column = cursor.fetchone()
    
    if status_column:
        print(f"Status column found:")
        print(f"  - Column Name: {status_column['column_name']}")
        print(f"  - Data Type: {status_column['data_type']}")
        print(f"  - Default Value: {status_column['column_default']}")
        print(f"  - Is Nullable: {status_column['is_nullable']}")
        
        if status_column['column_default']:
            print(f"\n⚠️  ISSUE FOUND: Default value is '{status_column['column_default']}'")
            print("   This might be causing automatic approval!")
        else:
            print(f"\n✅ No default value - should be NULL by default")
    else:
        print("❌ Status column not found in workers table!")
    
    # Check recent workers to see their status
    cursor.execute("""
        SELECT id, full_name, email, service, status, created_at
        FROM workers
        WHERE service = 'healthcare'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    recent_workers = cursor.fetchall()
    
    print(f"\nRecent healthcare workers:")
    for worker in recent_workers:
        print(f"  - {worker['full_name']} ({worker['email']})")
        print(f"    Status: {worker['status']}")
        print(f"    Created: {worker['created_at']}")
        print()
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

print("\n🔧 IF STATUS DEFAULT IS THE ISSUE:")
print("   Need to update database to remove default 'approved' value")
