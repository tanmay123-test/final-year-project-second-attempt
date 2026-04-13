import os
import psycopg2

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    # Check both password columns
    cursor.execute("SELECT username, password, encrypted_password FROM users WHERE username='bansode'")
    user = cursor.fetchone()
    
    if user:
        username, password, encrypted_password = user
        print(f'Username: {username}')
        print(f'Password: {password}')
        print(f'Encrypted password: {encrypted_password}')
    else:
        print('User not found')
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
