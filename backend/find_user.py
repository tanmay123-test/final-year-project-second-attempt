from user_db import UserDB

def find_user():
    print("--- Finding a User ---")
    user_db = UserDB()
    conn = user_db.conn
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users LIMIT 1")
    user = cursor.fetchone()
    if user:
        print(f"User found: ID={user[0]}, Username={user[1]}")
    else:
        print("No user found")

if __name__ == "__main__":
    find_user()
