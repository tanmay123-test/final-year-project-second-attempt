"""
Worker CLI Interface
Handles worker signup, login, and role-based routing
"""

import os
import requests
import time
from werkzeug.security import check_password_hash

API = "http://127.0.0.1:5000"

def healthcare_worker_menu():
    """Healthcare worker menu"""
    print("🏥 Healthcare worker coming soon!")

def housekeeping_worker_menu():
    """Housekeeping worker menu"""
    print("🏠 Housekeeping worker coming soon!")

def resource_management_menu():
    """Resource management menu"""
    print("📦 Resource management coming soon!")

def money_management_menu():
    """Money management menu"""
    print("💰 Money management coming soon!")

def mechanic_signup():
    """Mechanic signup process"""
    print("🔧 Mechanic signup - Please use mechanic CLI")

def tow_truck_operator_signup():
    """Tow truck operator signup process"""
    print("🚛 Tow truck operator signup - Please use tow truck CLI")

def automobile_expert_signup():
    """Automobile expert signup process"""
    print("🧠 Automobile expert signup - Please use automobile expert CLI")

def worker_signup():
    """Worker signup process"""
    print("\n" + "="*60)
    print("📝 WORKER SIGNUP")
    print("="*60)
    
    try:
        # Role selection first
        print("\n🎯 Select Worker Type:")
        print("1. 🏥 Healthcare")
        print("2. 🏠 Housekeeping")
        print("3. 📦 Resource Management")
        print("4. 🚗 Car Services")
        print("5. 💰 Money Management")
        
        choice = input("\nSelect service (1-5): ").strip()
        
        if choice == "1":
            healthcare_worker_menu()
        elif choice == "2":
            housekeeping_worker_menu()
        elif choice == "3":
            resource_management_menu()
        elif choice == "4":
            car_service_worker_menu()
        elif choice == "5":
            money_management_menu()
        else:
            print("❌ Invalid choice")
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ Signup error: {e}")

def car_service_worker_menu():
    """Car service worker submenu"""
    print("\n" + "="*60)
    print("🚗 CAR SERVICE WORKER")
    print("="*60)
    print("1. 🔧 Mechanic")
    print("2. ⛽ Fuel Delivery Agent")
    print("3. 🚛 Tow Truck Operator")
    print("4. 🧠 Automobile Expert")
    print("5. ⬅️ Back")
    
    choice = input("\nSelect worker type (1-4): ").strip()
        
        if choice == "1":
            mechanic_signup()
        elif choice == "2":
            fuel_delivery_agent_menu()
        elif choice == "3":
            tow_truck_operator_signup()
        elif choice == "4":
            automobile_expert_signup()
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice")
            time.sleep(1)

def fuel_delivery_agent_menu():
    """Fuel delivery agent main menu"""
    while True:
        print("\n" + "="*60)
        print("⛽ FUEL DELIVERY AGENT")
        print("="*60)
        print("1. 📝 Signup")
        print("2. 🔐 Login")
        print("3. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            from fuel_delivery_cli import fuel_delivery_agent_signup
            fuel_delivery_agent_signup()
        elif choice == "2":
            from fuel_delivery_cli import fuel_delivery_agent_login
            fuel_delivery_agent_login()
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")
            time.sleep(1)

def worker_login():
    """Worker login process"""
    print("\n" + "="*50)
    print("🔐 WORKER LOGIN")
    print("="*50)
    
    try:
        email = input("📧 Email: ").strip()
        
        if not email:
            print("❌ Email is required")
            return
        
        # Call API with email only
        response = requests.post(f"{API}/api/car/worker/login", json={
            "email": email
        })
        
        if response.status_code == 200:
            result = response.json()
            worker = result.get("worker", {})
            token = result.get("token")
            
            print(f"\n✅ Login successful!")
            print(f"👤 Welcome, {worker.get('name', 'Worker')}!")
            print(f"🎯 Role: {worker.get('role', 'Unknown')}")
            print(f"🏙️ City: {worker.get('city', 'Unknown')}")
            print(f"💼 Experience: {worker.get('experience', 0)} years")
            
            # Redirect to role-specific dashboard
            role = worker.get('role')
            if role == "Mechanic":
                mechanic_dashboard(worker, token)
            elif role == "Fuel Delivery Agent":
                fuel_dashboard(worker, token)
            elif role == "Tow Truck Operator":
                tow_dashboard(worker, token)
            elif role == "Automobile Expert":
                expert_dashboard(worker, token)
            else:
                print("🚧 Dashboard not available for this role yet")
                
        elif response.status_code == 401:
            print("❌ Invalid email")
        elif response.status_code == 403:
            result = response.json()
            status = result.get("status", "PENDING")
            print("\n" + "="*60)
            print("⏳ ACCOUNT PENDING APPROVAL")
            print("="*60)
            print("📝 Your account is still under admin review")
            print("⏱️  Expected approval time: 2-24 hours")
            print("📧 You will receive a notification once approved")
            print("📊 Current status: " + status)
            print("\n🔐 Please try logging in again after approval")
            print("📞 For urgent inquiries, contact support")
            print("="*60)
        else:
            error = response.json().get("error", "Login failed")
            print(f"❌ {error}")
            
    except Exception as e:
        print(f"❌ Login error: {e}")

def mechanic_dashboard(worker, token):
    """Mechanic dashboard"""
    print("🔧 Mechanic dashboard - Please use mechanic CLI")

def fuel_dashboard(worker, token):
    """Fuel delivery agent dashboard"""
    # Import and use our comprehensive fuel delivery CLI
    from fuel_delivery_cli import fuel_delivery_agent_dashboard
    
    # Get agent details from worker data
    agent_info = {
        'id': worker.get('worker_id'),
        'name': worker.get('name'),
        'email': worker.get('email'),
        'vehicle_type': worker.get('vehicle_model'),
        'vehicle_number': worker.get('vehicle_number'),
        'online_status': 'OFFLINE',  # Would need to get from API
        'rating': 0.0,  # Would need to get from API
        'total_deliveries': 0  # Would need to get from API
    }
    
    fuel_delivery_agent_dashboard(agent_info)

def tow_dashboard(worker, token):
    """Tow truck operator dashboard"""
    print("🚛 Tow truck dashboard - Please use tow truck CLI")

def expert_dashboard(worker, token):
    """Automobile expert dashboard"""
    print("🧠 Automobile expert dashboard - Please use automobile expert CLI")
