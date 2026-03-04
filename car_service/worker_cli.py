"""
Car Service Worker CLI Interface
Handles worker signup, login, and dashboard access
"""

import os
import requests
from datetime import datetime

API = "http://127.0.0.1:5000"

def worker_menu():
    """Main worker menu"""
    while True:
        print("\n" + "="*50)
        print("👷 WORKER MENU")
        print("="*50)
        print("1. 📝 Signup")
        print("2. 🔐 Login")
        print("3. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            worker_signup()
        elif choice == "2":
            worker_login()
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")

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
            "2": "Fuel Delivery Agent", 
            "3": "Tow Truck Operator",
            "4": "Automobile Expert"
        }
        
        if role_choice not in roles:
            print("❌ Invalid role selection")
            return
        
        role = roles[role_choice]
        print(f"\n✅ Selected Role: {role}")
        
        # Basic info
        name = input("👤 Full Name: ").strip()
        phone = input("📱 Phone Number: ").strip()
        email = input("📧 Email: ").strip()
        password = input("🔒 Password: ").strip()
        age = input("🎂 Age: ").strip()
        city = input("🏙️ City: ").strip()
        address = input("📍 Address: ").strip()
        experience = input("💼 Experience (years): ").strip()
        skills = input("🔧 Skills (describe your expertise): ").strip()
        
        # Vehicle info (only for fuel agent and tow truck)
        vehicle_number = vehicle_model = loading_capacity = None
        if role in ["Fuel Delivery Agent", "Tow Truck Operator"]:
            print(f"\n🚗 Vehicle Information (Required for {role}):")
            vehicle_number = input("Vehicle Number: ").strip()
            vehicle_model = input("Vehicle Model: ").strip()
            loading_capacity = input("Loading Capacity: ").strip()
        
        # Document uploads
        print("\n📄 Document Uploads")
        print("Please upload the following documents:")
        print("(Files should be in uploads/workers/ folder)")
        
        profile_photo = input("Profile photo filename: ").strip()
        aadhaar_card = input("Aadhaar card filename: ").strip()
        driving_license = input("Driving license filename: ").strip()
        certificate = input("Certificate filename (optional): ").strip() or None
        vehicle_rc = input("Vehicle RC filename: ").strip() if role in ["Fuel Delivery Agent", "Tow Truck Operator"] else None
        truck_photos = input("Truck photos filename: ").strip() if role == "Tow Truck Operator" else None
        
        # Security declaration
        print("\n🔒 SECURITY DECLARATION")
        print("I confirm all documents are valid and I agree to platform policies")
        print("(Type YES in any case: yes, YES, Yes)")
        confirm = input("Type YES to continue: ").strip()
        
        if confirm.upper() != "YES":
            print("❌ Security declaration not accepted. Signup cancelled.")
            return
        
        # Prepare data
        data = {
            "name": name,
            "phone": phone,
            "email": email,
            "password": password,
            "role": role,
            "age": age,
            "city": city,
            "address": address,
            "experience": experience,
            "skills": skills,
            "security_declaration": "1"
        }
        
        if vehicle_number:
            data["vehicle_number"] = vehicle_number
            data["vehicle_model"] = vehicle_model
            data["loading_capacity"] = loading_capacity
        
        if certificate:
            data["certificate"] = certificate
        if vehicle_rc:
            data["vehicle_rc"] = vehicle_rc
        if truck_photos:
            data["truck_photos"] = truck_photos
        
        # For now, simulate file uploads with paths
        # In a real implementation, you'd handle file uploads properly
        files = {}
        if profile_photo:
            files["profile_photo"] = ("profile_photo.jpg", "dummy", "image/jpeg")
        if aadhaar_card:
            files["aadhaar_card"] = ("aadhaar.jpg", "dummy", "image/jpeg")
        if driving_license:
            files["driving_license"] = ("license.jpg", "dummy", "image/jpeg")
        if certificate:
            files["certificate"] = ("certificate.pdf", "dummy", "application/pdf")
        if vehicle_rc:
            files["vehicle_rc"] = ("vehicle_rc.jpg", "dummy", "image/jpeg")
        if truck_photos:
            files["truck_photos"] = ("truck.jpg", "dummy", "image/jpeg")
        
        # Call API
        response = requests.post(f"{API}/api/car/worker/signup", data=data, files=files)
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✅ {result.get('message', 'Signup successful!')}")
            print(f"📋 Worker ID: {result.get('worker_id')}")
            print("\n" + "="*60)
            print("⏳ APPROVAL STATUS")
            print("="*60)
            print("📝 Your account has been submitted for admin review")
            print("⏱️  Expected approval time: 2-24 hours")
            print("� You will receive a notification once approved")
            print("🔐 After approval, you can login and access your dashboard")
            print("\n📞 For urgent inquiries, contact support")
            print("="*60)
        else:
            error = response.json().get("error", "Signup failed")
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Signup error: {e}")

def worker_login():
    """Worker login process"""
    print("\n" + "="*50)
    print("🔐 WORKER LOGIN")
    print("="*50)
    
    try:
        email = input("� Email: ").strip()
        
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
            from fuel_delivery_cli import fuel_delivery_agent_signup, fuel_delivery_agent_login, fuel_delivery_agent_dashboard
            fuel_delivery_agent_menu()
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
    while True:
        print("\n" + "="*60)
        print("🔧 MECHANIC DASHBOARD")
        print("="*60)
        print(f"👤 {worker.get('name')}")
        print(f"📱 {worker.get('phone')}")
        print(f"🏙️ {worker.get('city')}")
        print("\nOptions:")
        print("1. 📋 View Jobs")
        print("2. 📊 My Stats")
        print("3. 👤 Profile")
        print("4. ⬅️ Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            print("🚧 Job management coming soon!")
        elif choice == "2":
            print("🚧 Statistics coming soon!")
        elif choice == "3":
            print("🚧 Profile management coming soon!")
        elif choice == "4":
            print("👋 Logged out successfully")
            return
        else:
            print("❌ Invalid choice")

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
    while True:
        print("\n" + "="*60)
        print("🚛 TOW TRUCK DASHBOARD")
        print("="*60)
        print(f"👤 {worker.get('name')}")
        print(f"🚗 Vehicle: {worker.get('vehicle_model', 'N/A')}")
        print(f"⚖️ Capacity: {worker.get('loading_capacity', 'N/A')}")
        print("\nOptions:")
        print("1. 📋 View Requests")
        print("2. 📍 Active Jobs")
        print("3. 👤 Profile")
        print("4. ⬅️ Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            print("🚧 Tow request management coming soon!")
        elif choice == "2":
            print("🚧 Active job tracking coming soon!")
        elif choice == "3":
            print("🚧 Profile management coming soon!")
        elif choice == "4":
            print("👋 Logged out successfully")
            return
        else:
            print("❌ Invalid choice")

def expert_dashboard(worker, token):
    """Automobile expert dashboard"""
    while True:
        print("\n" + "="*60)
        print("👨‍🔧 AUTOMOBILE EXPERT DASHBOARD")
        print("="*60)
        print(f"👤 {worker.get('name')}")
        print(f"💼 Experience: {worker.get('experience', 0)} years")
        print(f"🔧 Skills: {worker.get('skills', 'N/A')}")
        print("\nOptions:")
        print("1. 📋 Consultations")
        print("2. 💬 Messages")
        print("3. 👤 Profile")
        print("4. ⬅️ Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            print("🚧 Consultation management coming soon!")
        elif choice == "2":
            print("🚧 Message system coming soon!")
        elif choice == "3":
            print("🚧 Profile management coming soon!")
        elif choice == "4":
            print("👋 Logged out successfully")
            return
        else:
            print("❌ Invalid choice")
