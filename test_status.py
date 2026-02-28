import requests
import sqlite3
import os
import sys

# Add current directory to path so we can import worker_db
sys.path.append(os.getcwd())

from worker_db import WorkerDB

# Setup
API_URL = "http://127.0.0.1:5000"
worker_db = WorkerDB()

email = "test_housekeeper@example.com"
password = "password123"

# 1. Register Worker
print("Registering worker...")
try:
    # Check if exists first
    existing = worker_db.get_worker_by_email(email)
    if not existing:
        worker_db.register_worker("Test Worker", email, "1234567890", "housekeeping", "General Cleaning", 5, "NY", "LIC123", password)
        print("Registered.")
    else:
        print("Worker exists.")
except Exception as e:
    print(f"Registration error: {e}")

# 2. Approve Worker
print("Approving worker...")
worker = worker_db.get_worker_by_email(email)
if worker:
    worker_db.approve_worker(worker['id'])
    print(f"Approved worker {worker['id']}")
else:
    print("Worker not found")
    exit(1)

# 3. Login
print("Logging in...")
try:
    resp = requests.post(f"{API_URL}/worker/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        exit(1)

    data = resp.json()
    token = data['token']
    print(f"Login successful. Token: {token[:20]}...")

    # 4. Update Status
    print("Updating status to Online...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_URL}/housekeeping/worker/status", json={"is_online": True}, headers=headers)

    print(f"Update Status Code: {resp.status_code}")
    print(f"Update Response: {resp.text}")

    # 5. Check Status
    print("Checking status...")
    resp = requests.get(f"{API_URL}/housekeeping/worker/status", headers=headers)
    print(f"Get Status Code: {resp.status_code}")
    print(f"Get Response: {resp.text}")

except Exception as e:
    print(f"Request failed: {e}")
