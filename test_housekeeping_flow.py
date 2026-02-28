import requests
import json
import random
import string
import sqlite3

API = "http://127.0.0.1:5000"
DB_PATH = "data/users.db"

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def mark_verified(email):
    print(f"--- Manually Verifying {email} ---")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        print("✅ User manually verified in DB")
    except Exception as e:
        print(f"❌ DB Update Exception: {e}")

def register_user():
    print("--- Register User ---")
    username = f"user_{get_random_string(5)}"
    email = f"{username}@example.com"
    password = "password123"
    
    try:
        r = requests.post(f"{API}/signup", json={
            "name": "Test User",
            "username": username,
            "email": email,
            "password": password
        })
        if r.status_code == 201:
            print(f"✅ User Registered: {username}")
            mark_verified(email)
            return username, password
        else:
            print(f"❌ Registration Failed: {r.text}")
            return None, None
    except Exception as e:
        print(f"❌ Registration Exception: {e}")
        return None, None

def login_user(username, password):
    print("\n--- Login User ---")
    try:
        r = requests.post(f"{API}/login", json={"username": username, "password": password})
        if r.status_code == 200:
            token = r.json()["token"]
            print(f"✅ User Login Success. Token: {token[:20]}...")
            return token
        else:
            print(f"❌ User Login Failed: {r.text}")
            return None
    except Exception as e:
        print(f"❌ User Login Exception: {e}")
        return None

def get_services(token):
    print("\n--- Get Services ---")
    try:
        # Note: /housekeeping/services is likely public or requires token?
        # Let's try without token first as per frontend usually fetching public data
        r = requests.get(f"{API}/housekeeping/services")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"✅ Services: {json.dumps(r.json(), indent=2)}")
        else:
            print(f"❌ Failed: {r.text}")
            
            # If 401, try with token
            if r.status_code == 401 and token:
                print("Retrying with token...")
                headers = {"Authorization": f"Bearer {token}"}
                r = requests.get(f"{API}/housekeeping/services", headers=headers)
                print(f"Status with token: {r.status_code}")
                if r.status_code == 200:
                    print(f"✅ Services: {json.dumps(r.json(), indent=2)}")

    except Exception as e:
        print(f"❌ Exception: {e}")

def check_availability(token):
    print("\n--- Check Availability ---")
    if not token:
        print("Skipping (No Token)")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "service_type": "General Cleaning",
        "address": "123 Main St",
        "date": "2025-12-31",
        "time": "10:00"
    }
    try:
        # Note: The endpoint in api.js is /housekeeping/book but in controller it is /book inside housekeeping blueprint
        # so it is /housekeeping/book
        r = requests.post(f"{API}/housekeeping/book", json=data, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"✅ Availability: {json.dumps(r.json(), indent=2)}")
        elif r.status_code == 404:
             print(f"⚠️ No workers available (Expected if no workers registered): {r.text}")
        else:
            print(f"❌ Failed: {r.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    uname, pwd = register_user()
    if uname:
        token = login_user(uname, pwd)
        if token:
            get_services(token)
            check_availability(token)
