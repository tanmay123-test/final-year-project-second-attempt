import requests
import json
import random
import string
import time

API = "http://127.0.0.1:5000"

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def register_worker():
    print("--- Register Housekeeping Worker ---")
    name = f"Worker {get_random_string(3)}"
    email = f"worker_{get_random_string(5)}@example.com"
    password = "password123"
    
    data = {
        "full_name": name,
        "email": email,
        "phone": "1234567890",
        "service": "housekeeping",
        "specialization": "General Cleaning",
        "experience": "5",
        "password": password
    }
    
    try:
        r = requests.post(f"{API}/worker/signup", json=data)
        if r.status_code == 201:
            worker_id = r.json().get("worker_id")
            print(f"✅ Worker Registered: {email} (ID: {worker_id})")
            return worker_id, email, password
        else:
            print(f"❌ Worker Registration Failed: {r.text}")
            return None, None, None
    except Exception as e:
        print(f"❌ Worker Registration Exception: {e}")
        return None, None, None

def login_worker(email, password, expect_failure=False):
    print(f"\n--- Login Worker ({email}) ---")
    try:
        r = requests.post(f"{API}/worker/login", json={"email": email, "password": password})
        if r.status_code == 200:
            if expect_failure:
                print(f"❌ Worker Login Succeeded (Unexpected): {r.json()}")
            else:
                token = r.json()["token"]
                print(f"✅ Worker Login Success. Token: {token[:20]}...")
            return r.json().get("token")
        else:
            if expect_failure:
                print(f"✅ Worker Login Failed (Expected): {r.text}")
            else:
                print(f"❌ Worker Login Failed: {r.text}")
            return None
    except Exception as e:
        print(f"❌ Worker Login Exception: {e}")
        return None

def approve_worker(worker_id):
    print(f"\n--- Approve Worker (ID: {worker_id}) ---")
    try:
        # Note: In a real scenario, this endpoint might be protected by admin auth
        # But looking at admin.py, it doesn't seem to enforce auth wrapper yet or we don't have admin login
        # Let's try calling it directly
        r = requests.post(f"{API}/admin/worker/approve/{worker_id}")
        if r.status_code == 200:
            print(f"✅ Worker Approved: {r.json()}")
            return True
        else:
            print(f"❌ Worker Approval Failed: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Worker Approval Exception: {e}")
        return False

def toggle_online_status(token):
    print("\n--- Toggle Online Status ---")
    if not token:
        print("Skipping (No Token)")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Check current status
        r = requests.get(f"{API}/housekeeping/worker/status", headers=headers)
        print(f"Current Status: {r.json()}")
        
        # Set to Online
        r = requests.post(f"{API}/housekeeping/worker/status", json={"is_online": True}, headers=headers)
        if r.status_code == 200:
             print(f"✅ Status Toggled to Online: {r.json()}")
        else:
             print(f"❌ Status Toggle Failed: {r.text}")

    except Exception as e:
        print(f"❌ Status Toggle Exception: {e}")

if __name__ == "__main__":
    worker_id, email, password = register_worker()
    if worker_id:
        # 1. Login should fail (Pending)
        login_worker(email, password, expect_failure=True)
        
        # 2. Approve Worker
        if approve_worker(worker_id):
            # 3. Login should succeed
            token = login_worker(email, password, expect_failure=False)
            
            # 4. Toggle Online
            if token:
                toggle_online_status(token)
