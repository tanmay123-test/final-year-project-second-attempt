import requests
import sqlite3
import os
import sys
import jwt
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:5000"
WORKER_ID = 8
SECRET_KEY = "super-secret-key"  # Matching app.py config

def generate_token(user_id, email, user_type='worker'):
    payload = {
        'username': email,
        'user_id': user_id,
        'email': email,
        'type': user_type,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def get_worker_email(worker_id):
    db_path = os.path.join(os.getcwd(), 'data', 'workers.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return None
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM workers WHERE id = ?", (worker_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def check_api_bookings():
    email = get_worker_email(WORKER_ID)
    if not email:
        print(f"❌ Worker {WORKER_ID} not found in DB")
        return

    print(f"👤 Worker Email: {email}")
    token = generate_token(WORKER_ID, email)
    headers = {'Authorization': f'Bearer {token}'}
    
    url = f"{BASE_URL}/api/housekeeping/my-bookings"
    print(f"🌍 Fetching: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            bookings = data.get('bookings', [])
            print(f"✅ Found {len(bookings)} bookings")
            if len(bookings) > 0:
                print("🔍 RAW JSON of first booking:")
                import json
                print(json.dumps(bookings[0], indent=2, default=str))
            
            # Filter for pending/requested
            pending = [b for b in bookings if b.get('status') in ['PENDING', 'ASSIGNED', 'REQUESTED']]
            print(f"📋 Pending/Requested: {len(pending)}")
            
            for b in pending:
                print(f"   - ID: {b.get('id')}, Status: {b.get('status')}, Service: {b.get('service_type')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    check_api_bookings()
