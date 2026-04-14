import os
import psycopg2

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    # Check the exact email
    email = 'co2023.nihari.rothe@ves.ac.in'
    cursor.execute("SELECT id, full_name, email FROM workers WHERE email = %s", (email,))
    worker = cursor.fetchone()
    
    if worker:
        print(f"Found exact match: {worker}")
    else:
        print("No exact match found")
        # Check similar emails
        cursor.execute("SELECT id, full_name, email FROM workers WHERE email ILIKE '%niharika%' OR email ILIKE '%rothe%'")
        workers = cursor.fetchall()
        print(f"Found {len(workers)} similar workers:")
        for w in workers:
            print(f"  {w}")
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
