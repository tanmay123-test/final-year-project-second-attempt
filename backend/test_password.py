import os
import psycopg2
import bcrypt

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    # Check password format for a specific user
    cursor.execute("SELECT username, password, is_verified FROM users WHERE username='bansode'")
    user = cursor.fetchone()
    
    if user:
        username, password, is_verified = user
        print(f'Username: {username}')
        print(f'Password type: {type(password)}')
        print(f'Password: {password}')
        print(f'Is verified: {is_verified}')
        
        # Try to check password
        test_password = '123456'
        try:
            if isinstance(password, memoryview):
                password_bytes = password.tobytes()
            else:
                password_bytes = password
            
            result = bcrypt.checkpw(test_password.encode(), password_bytes)
            print(f'Password check result: {result}')
        except Exception as e:
            print(f'Password check error: {e}')
    else:
        print('User not found')
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
