import os
import psycopg2

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    # Check healthcare workers
    cursor.execute("SELECT id, full_name, email, service, specialization, status FROM workers WHERE service='healthcare' AND status='approved'")
    workers = cursor.fetchall()
    
    print(f'Found {len(workers)} approved healthcare workers:')
    for worker in workers:
        print(f'  ID: {worker[0]}, Name: {worker[1]}, Email: {worker[2]}, Specialization: {worker[4]}')
    
    # Check all healthcare workers
    cursor.execute("SELECT id, full_name, email, service, specialization, status FROM workers WHERE service='healthcare'")
    all_workers = cursor.fetchall()
    
    print(f'\nFound {len(all_workers)} total healthcare workers:')
    for worker in all_workers:
        print(f'  ID: {worker[0]}, Name: {worker[1]}, Status: {worker[5]}')
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
