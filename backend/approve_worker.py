import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def approve_housekeeping_workers():
    """Approve all pending housekeeping workers"""
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get all pending housekeeping workers
        cursor.execute("""
            SELECT id, email, specialization, status 
            FROM workers 
            WHERE service = 'housekeeping' AND status = 'pending'
        """)
        
        pending_workers = cursor.fetchall()
        
        if not pending_workers:
            print("No pending housekeeping workers found.")
            return
        
        print(f"Found {len(pending_workers)} pending housekeeping workers:")
        for worker in pending_workers:
            print(f"  - ID: {worker['id']}, Email: {worker['email']}, Specialization: {worker['specialization']}")
        
        # Approve all pending workers
        cursor.execute("""
            UPDATE workers 
            SET status = 'approved' 
            WHERE service = 'housekeeping' AND status = 'pending'
        """)
        
        conn.commit()
        print(f"\n✅ Approved {len(pending_workers)} housekeeping workers!")
        
        # Show updated status
        cursor.execute("""
            SELECT id, email, specialization, status 
            FROM workers 
            WHERE service = 'housekeeping'
        """)
        
        all_workers = cursor.fetchall()
        print(f"\nAll housekeeping workers:")
        for worker in all_workers:
            status_emoji = "✅" if worker['status'] == 'approved' else "⏳"
            print(f"  {status_emoji} ID: {worker['id']}, Email: {worker['email']}, Status: {worker['status']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    approve_housekeeping_workers()
