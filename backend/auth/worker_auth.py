import requests
from .auth_db import AuthDB
from cli import worker_service_selection

API = "http://127.0.0.1:5000"
TOKEN = None
WORKER_ID = None

def worker_signup():
    print("\n👷 Worker Signup")
    name = input("Name: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    email = input("Email: ").strip()
    service_type = input("Service Type (healthcare/housekeeping/car_service/loan_service/money_service): ").strip()
    
    auth_db = AuthDB()
    
    # Check if worker already exists
    cursor = auth_db.conn.cursor()
    cursor.execute("SELECT id FROM workers WHERE username=? OR email=?", (username, email))
    if cursor.fetchone():
        print("❌ Username or email already exists")
        return
    
    # Create worker
    worker_id = auth_db.create_worker(name, username, password, email, service_type)
    print(f"✅ Worker account created successfully!")
    print(f"🆔 Worker ID: {worker_id}")
    print("📧 Please verify your email (simulation)")

def worker_login():
    global TOKEN, WORKER_ID
    print("\n🔐 Worker Login")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    auth_db = AuthDB()
    worker_data, message = auth_db.authenticate_worker(username, password)
    
    if worker_data:
        TOKEN = auth_db.generate_token(worker_data)
        WORKER_ID = worker_data['id']
        print(f"✅ {message}")
        print(f"👷 Welcome, {worker_data['username']}!")
        print(f"🔧 Service Type: {worker_data.get('service_type', 'Not specified')}")
        return True
    else:
        print(f"❌ {message}")
        return False

def worker_menu():
    """Main worker menu - show services first"""
    while True:
        print("\n" + "="*50)
        print("👷 WORKER MENU")
        print("="*50)
        print("1. 📝 Signup")
        print("2. 🔐 Login")
        print("3. 🌐 Browse Services")
        print("4. ⬅️ Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            worker_signup()
        elif choice == "2":
            worker_login()
        elif choice == "3":
            # Show service selection without authentication
            worker_service_selection()
        elif choice == "4":
            return
        else:
            print("❌ Invalid choice")
