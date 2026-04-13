import os
import psycopg2
import bcrypt

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    # Create a test user with bcrypt password
    username = 'testuser'
    password = '123456'
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f'Creating test user: {username}')
    print(f'Hashed password: {hashed_password}')
    
    # Insert the user
    cursor.execute("""
        INSERT INTO users (username, name, email, password, is_verified) 
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (username) DO UPDATE SET 
        password = EXCLUDED.password,
        is_verified = EXCLUDED.is_verified
    """, (username, 'Test User', 'test@example.com', hashed_password, 1))
    
    conn.commit()
    print('Test user created successfully!')
    
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
