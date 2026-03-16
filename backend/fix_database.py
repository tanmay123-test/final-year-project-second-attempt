import sqlite3
from worker_db import WorkerDB
from config import WORKER_DB

def fix_database():
    """Fix database issues with worker data"""
    conn = sqlite3.connect(WORKER_DB)
    cursor = conn.cursor()

    print('=== FIXING DATABASE ISSUES ===')

    # Fix worker 1 - has multiple services and wrong status
    cursor.execute("UPDATE workers SET service = 'housekeeping', status = 'pending' WHERE id = 1")
    print('Fixed worker 1: Set service to housekeeping, status to pending')

    # Fix worker 2 - has multiple services  
    cursor.execute("UPDATE workers SET service = 'housekeeping' WHERE id = 2")
    print('Fixed worker 2: Set service to housekeeping only')

    conn.commit()

    # Check updated data
    print('\n=== UPDATED WORKER DATA ===')
    cursor.execute('SELECT id, full_name, email, service, specialization, status, hourly_rate FROM workers LIMIT 5')
    workers = cursor.fetchall()
    for worker in workers:
        print(f'ID: {worker[0]}, Name: {worker[1]}, Email: {worker[2]}, Service: {worker[3]}, Status: {worker[4]}, Rate: {worker[5]}')

    conn.close()

if __name__ == "__main__":
    fix_database()
