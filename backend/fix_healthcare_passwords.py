import os
import psycopg2
import bcrypt

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    # Set passwords for healthcare workers without passwords
    cursor.execute("SELECT id, full_name, email FROM workers WHERE service='healthcare' AND status='approved' AND password IS NULL")
    workers = cursor.fetchall()
    
    for worker in workers:
        worker_id, name, email = worker
        # Set a default password
        password = '123456'
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("UPDATE workers SET password = %s WHERE id = %s", (hashed_password, worker_id))
        print(f'Set password for {name} ({email})')
    
    conn.commit()
    print('All healthcare workers now have passwords!')
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
