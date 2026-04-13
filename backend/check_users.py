import os
import psycopg2

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    # Check if users table exists and what columns it has
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position")
    columns = cursor.fetchall()
    print('Users table columns:')
    for col in columns:
        print(f'  {col[0]}: {col[1]}')
    
    # Check if there are any users
    cursor.execute("SELECT * FROM users LIMIT 5")
    users = cursor.fetchall()
    print(f'\nFound {len(users)} users:')
    for user in users:
        print(f'  {user}')
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
