import os
import psycopg2

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    # Check healthcare workers and their passwords
    cursor.execute("SELECT id, full_name, email, service, status, password FROM workers WHERE service='healthcare' AND status='approved'")
    workers = cursor.fetchall()
    
    print(f'Found {len(workers)} approved healthcare workers:')
    for worker in workers:
        print(f'  ID: {worker[0]}, Name: {worker[1]}, Email: {worker[2]}, Has Password: {worker[5] is not None}')
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
