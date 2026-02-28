
import sys
import os
import jwt
import datetime
from config import JWT_SECRET, JWT_EXP_MINUTES

# Add project root to path
sys.path.append(os.getcwd())

from housekeeping.controllers.booking_controller import get_current_user
from user_db import UserDB
from worker_db import WorkerDB

# Mock request context
class MockRequest:
    def __init__(self, token):
        self.headers = {"Authorization": f"Bearer {token}"}

def generate_test_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXP_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def test_auth_logic():
    print("=== Testing Auth Logic for Sarthak ===")
    
    email = "sarthak@gmail.com"
    token = generate_test_token(email)
    print(f"Generated Token for {email}")
    
    # We need to mock 'request' in booking_controller
    # Since we can't easily inject it, we will replicate the logic here
    
    print("\nReplicating get_current_user logic:")
    
    user_db = UserDB()
    worker_db = WorkerDB()
    
    username = email # verify_token returns this
    
    print(f"Decoded Username: {username}")
    
    # 1. Check User DB
    print("Checking UserDB...")
    user_id = user_db.get_user_by_username(username)
    print(f"UserDB Result: {user_id}")
    
    if user_id:
        print("CRITICAL: Identified as USER!")
    else:
        print("UserDB check passed (None).")
        
    # 2. Check Worker DB
    print("Checking WorkerDB...")
    worker = worker_db.get_worker_by_email(username)
    if worker:
        print(f"WorkerDB Result: Found ID {worker['id']}")
        print("Identified as WORKER.")
    else:
        print("WorkerDB Result: None")
        
    if not user_id and worker:
        print("\nCONCLUSION: Auth logic is CORRECT. Should identify as Worker.")
    else:
        print("\nCONCLUSION: Auth logic is FLAWED.")

if __name__ == "__main__":
    test_auth_logic()
