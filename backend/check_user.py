import sqlite3
import bcrypt

def check_and_create_user():
    # Connect to database
    conn = sqlite3.connect('data/users.db')
    cursor = conn.cursor()
    
    # Check if user niharika exists
    cursor.execute('SELECT username, email, is_verified, password FROM users WHERE username=? OR email=?', ('niharika', 'niharika'))
    user = cursor.fetchone()
    
    if user:
        print(f'User found: {user[0]} ({user[1]}) - Verified: {user[2]}')
        
        # Update password to "123"
        hashed_password = bcrypt.hashpw('123'.encode(), bcrypt.gensalt())
        cursor.execute('UPDATE users SET password=?, is_verified=1 WHERE username=?', (hashed_password, 'niharika'))
        conn.commit()
        print('Password updated to "123" and user verified')
    else:
        print('User niharika not found. Creating new user...')
        
        # Create new user
        hashed_password = bcrypt.hashpw('123'.encode(), bcrypt.gensalt())
        cursor.execute('''
            INSERT INTO users (name, username, email, password, is_verified)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Niharika', 'niharika', 'niharika@example.com', hashed_password, 1))
        conn.commit()
        print('New user created with username "niharika" and password "123"')
    
    # List all users
    cursor.execute('SELECT username, email, is_verified FROM users')
    users = cursor.fetchall()
    print(f'\nAll users in database ({len(users)}):')
    for user in users:
        print(f'  - {user[0]} ({user[1]}) - Verified: {user[2]}')
    
    conn.close()

if __name__ == '__main__':
    check_and_create_user()
