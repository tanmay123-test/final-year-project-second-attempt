from worker_db import WorkerDB
import psycopg2
import psycopg2.extras

print("=== QUICK HEALTHCARE WORKER STATUS CHECK ===")
print()

try:
    worker_db = WorkerDB()
    
    # Get all healthcare workers
    conn = worker_db.get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute("""
        SELECT id, full_name, email, service, specialization, status, created_at
        FROM workers
        WHERE service = 'healthcare'
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    workers = cursor.fetchall()
    
    print(f"Found {len(workers)} healthcare workers:")
    print()
    
    for worker in workers:
        print(f"👨‍⚕️  {worker['full_name']}")
        print(f"   Email: {worker['email']}")
        print(f"   Status: {worker['status']}")
        print(f"   Specialization: {worker['specialization']}")
        print(f"   Created: {worker['created_at']}")
        print()
    
    # Check if any are auto-approved
    approved_workers = [w for w in workers if w['status'] == 'approved']
    pending_workers = [w for w in workers if w['status'] == 'pending']
    
    print(f"📊 SUMMARY:")
    print(f"   Total: {len(workers)}")
    print(f"   Approved: {len(approved_workers)}")
    print(f"   Pending: {len(pending_workers)}")
    
    if len(approved_workers) > 0:
        print(f"\n⚠️  ISSUE: {len(approved_workers)} workers are auto-approved!")
        for worker in approved_workers:
            print(f"   - {worker['full_name']} ({worker['email']})")
    
    if len(pending_workers) > 0:
        print(f"\n✅ GOOD: {len(pending_workers)} workers are pending approval")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
