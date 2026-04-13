import os
import psycopg2
import bcrypt

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    # Update existing user with bcrypt password
    username = 'bansode'
    password = '123456'
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f'Updating user: {username}')
    print(f'New hashed password: {hashed_password}')
    
    # Update the user
    cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, username))
    
    conn.commit()
    print('User updated successfully!')
    
    # Test the login
    cursor.execute("SELECT password, is_verified FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()
    if row:
        stored_password, is_verified = row
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        result = bcrypt.checkpw(password.encode('utf-8'), stored_password)
        print(f'Password verification test: {result}')
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
