
from user_db import UserDB

def check_user():
    db = UserDB()
    user = db.get_user_by_email('trunika24@gmail.com')
    if user:
        print(f"User found: {user['id']} - {user['username']}")
    else:
        print("User not found")

if __name__ == "__main__":
    check_user()
