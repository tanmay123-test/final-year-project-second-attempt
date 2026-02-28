import requests
import sqlite3
import jwt
import datetime
import sys
import os

# Configuration
BASE_URL = "http://localhost:5000"
WORKER_ID = 8

# Add current directory to path so we can import modules
sys.path.append(os.getcwd())

try:
    from auth_utils import generate_token
    from config import USER_DB
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def get_any_user():
    try:
        # Connect to users.db
        print(f"📂 Connecting to DB: {USER_DB}")
        conn = sqlite3.connect(USER_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT username, id FROM users LIMIT 1")
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return user
        else:
            print("❌ No users found in users.db")
            # Create a dummy user
            conn = sqlite3.connect(USER_DB)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password, is_verified) VALUES (?, ?, ?, ?)", 
                           ("testuser", "test@example.com", "password", 1))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return ("testuser", user_id)
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)

def trigger_booking():
    user_info = get_any_user()
    if not user_info:
        print("❌ Could not get a user.")
        return

    username, user_id = user_info
    print(f"👤 Using user: {username} (ID: {user_id})")
    
    token = generate_token(username)
    # The generate_token function returns a string in Python < 3.10 but bytes in older PyJWT? 
    # auth_utils.py uses jwt.encode which returns string in newer versions.
    if isinstance(token, bytes):
        token = token.decode('utf-8')
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create booking payload
    # Worker 8 service needs to match. Let's assume Cleaning or verify.
    # I'll just try 'Cleaning' first.
    payload = {
        "service_type": "General Cleaning",
        "address": "123 Test St, Mumbai",
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.datetime.now().strftime("%I:%M %p"),
        "worker_id": WORKER_ID,
        "booking_type": "instant"
    }
    
    print(f"🚀 Sending booking request for Worker {WORKER_ID}...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/housekeeping/confirm-booking",
            json=payload,
            headers=headers
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ Booking created successfully!")
        else:
            print("❌ Failed to create booking")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    trigger_booking()
