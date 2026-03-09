"""
Car Service Worker CLI Interface
Handles worker signup, login, and dashboard access
"""

import os
import requests
import time
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
    except Exception as e:
        print(f"❌ Error: {e}")
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
    print("5. 🚚 Truck Operator")
    print("6. ⬅️ Back")
    
    choice = input("\nSelect worker type (1-6): ").strip()
        
    if choice == "1":
        mechanic_signup()
    elif choice == "2":
        fuel_delivery_agent_menu()
    elif choice == "3":
        tow_truck_operator_signup()
    elif choice == "4":
        automobile_expert_signup()
    elif choice == "5":
        from .truck_operator_cli import truck_operator_signup
        truck_operator_signup()
    elif choice == "6":
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
        password = input("🔒 Password: ").strip()
        
        if not email or not password:
            print("❌ Email and password are required")
            return
        
        # Unified worker login (matches final-year-project- flow)
        response = requests.post(f"{API}/api/car/service/worker/login", json={
            "email": email,
            "password": password
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
                from fuel_delivery_cli import fuel_delivery_agent_dashboard
                fuel_delivery_agent_dashboard(worker, token)
            elif role == "Tow Truck Operator":
                tow_dashboard(worker, token)
            elif role == "Automobile Expert":
                expert_dashboard(worker, token)
            elif role == "Truck Operator":
                from .truck_operator_cli import truck_operator_dashboard
                truck_operator_dashboard(worker)
            else:
                print("🚧 Dashboard not available for this role yet")
                
        elif response.status_code == 401:
            print("❌ Invalid email or password")
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

# Placeholder functions for other worker types
def healthcare_worker_menu():
    while True:
        print("\n" + "="*60)
        print("🏥 HEALTHCARE WORKER")
        print("="*60)
        print("1. 📝 Signup")
        print("2. 🔐 Login")
        print("3. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        if choice == "1":
            healthcare_signup()
        elif choice == "2":
            healthcare_login()
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")
            time.sleep(1)

def housekeeping_worker_menu():
    print("🏠 Housekeeping worker signup - Coming soon!")
    time.sleep(1)

def resource_management_menu():
    print("📦 Resource management worker signup - Coming soon!")
    time.sleep(1)

def money_management_menu():
    while True:
        print("\n" + "="*60)
        print("💰 MONEY MANAGEMENT WORKER")
        print("="*60)
        print("1. 📝 Signup (Not required; user-only features)")
        print("2. ⬅️ Back")
        
        c = input("\nSelect option: ").strip()
        if c in ["2", ""]:
            return
        else:
            print("❌ Invalid choice")
            time.sleep(1)

def mechanic_signup():
    print("\n" + "="*60)
    print("🔧 Mechanic signup - Use unified car service worker signup from admin")
    time.sleep(1)

def tow_truck_operator_signup():
    print("🚛 Tow truck operator signup - Coming soon!")
    time.sleep(1)

def automobile_expert_signup():
    print("\n" + "="*60)
    print("🧠 Automobile expert signup - Use unified car service worker signup from admin")
    time.sleep(1)

def mechanic_dashboard(worker, token):
    print("🔧 Mechanic dashboard - Coming soon!")
    time.sleep(1)

def tow_dashboard(worker, token):
    print("🚛 Tow truck dashboard - Coming soon!")
    time.sleep(1)

def expert_dashboard(worker, token):
    print("\n" + "="*60)
    print("🧠 Expert dashboard - Coming soon!")
    time.sleep(1)

def healthcare_signup():
    print("\n" + "="*60)
    print("📝 HEALTHCARE WORKER SIGNUP")
    print("="*60)
    try:
        full_name = input("Full Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        specialization = input("Specialization: ").strip()
        experience = input("Experience (years): ").strip()
        clinic_location = input("Clinic Location (optional): ").strip()
        license_number = input("License Number (optional): ").strip()
        password = input("Password (optional): ").strip()
        
        payload = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "specialization": specialization,
            "experience": experience or "0",
            "clinic_location": clinic_location,
            "license_number": license_number,
            "password": password
        }
        r = requests.post(f"{API}/worker/healthcare/signup", json=payload)
        if r.status_code == 201:
            wid = r.json().get("worker_id")
            print(f"✅ Signup successful! Worker ID: {wid}")
            print("⏳ Await admin approval before login")
        else:
            try:
                print(f"❌ Signup failed: {r.json().get('error','Unknown error')}")
            except Exception:
                print(f"❌ Signup failed [{r.status_code}]")
    except Exception as e:
        print(f"❌ Error: {e}")
    input("\nPress Enter to continue...")

def healthcare_login():
    print("\n" + "="*60)
    print("🔐 HEALTHCARE WORKER LOGIN")
    print("="*60)
    try:
        email = input("Email: ").strip()
        r = requests.post(f"{API}/worker/login", json={"email": email})
        if r.status_code == 200:
            data = r.json()
            token = data.get("token")
            worker = {
                "id": data.get("worker_id"),
                "service": data.get("service"),
                "specialization": data.get("specialization"),
                "name": data.get("name")
            }
            print("\n✅ Login successful!")
            healthcare_worker_dashboard(worker, token)
        elif r.status_code == 403:
            print("⏳ Account pending admin approval")
        else:
            try:
                print(f"❌ Login failed: {r.json().get('error','Unknown error')}")
            except Exception:
                print(f"❌ Login failed [{r.status_code}]")
    except Exception as e:
        print(f"❌ Login error: {e}")
    time.sleep(1)

def healthcare_worker_dashboard(worker, token):
    wid = worker.get("id")
    while True:
        print("\n" + "="*60)
        print(f"🏥 HEALTHCARE DASHBOARD - {worker.get('name','Doctor')}")
        print("="*60)
        print("1. 📥 Pending Requests")
        print("2. 📅 Appointments")
        print("3. 📊 Dashboard Stats")
        print("4. 🎥 Video Appointments Ready")
        print("5. 🔮 Start Video Call")
        print("6. 🧹 End Video Call")
        print("7. ⬅️ Back")
        c = input("\nSelect option: ").strip()
        if c == "1":
            _hc_view_requests(wid)
        elif c == "2":
            _hc_view_appointments(wid)
        elif c == "3":
            _hc_dashboard_stats(wid)
        elif c == "4":
            _hc_video_ready()
        elif c == "5":
            _hc_start_video_call(wid)
        elif c == "6":
            _hc_end_video_call(wid)
        elif c == "7":
            return
        else:
            print("❌ Invalid choice")
        input("\nPress Enter to continue...")

def _hc_view_requests(worker_id):
    r = requests.get(f"{API}/worker/{worker_id}/requests")
    if r.status_code != 200:
        print("❌ Failed to fetch requests")
        return
    reqs = r.json().get("requests", [])
    if not reqs:
        print("📭 No pending requests")
        return
    for i, a in enumerate(reqs, 1):
        print(f"[{i}] ID:{a['id']} | {a['status']} | {a['booking_date']}")

def _hc_view_appointments(worker_id):
    r = requests.get(f"{API}/worker/{worker_id}/appointments")
    if r.status_code != 200:
        print("❌ Failed to fetch appointments")
        return
    appts = r.json().get("appointments", [])
    if not appts:
        print("📭 No appointments")
        return
    for i, a in enumerate(appts, 1):
        print(f"[{i}] ID:{a['id']} | {a['status']} | {a['booking_date']}")

def _hc_dashboard_stats(worker_id):
    r = requests.get(f"{API}/worker/{worker_id}/dashboard/stats")
    if r.status_code != 200:
        print("❌ Failed to fetch stats")
        return
    s = r.json()
    print(f"📥 Pending: {s.get('pending_requests',0)}")
    print(f"📅 Today: {s.get('today_appointments',0)}")
    print(f"✅ Accepted: {s.get('accepted_appointments',0)}")
    print(f"📊 Total: {s.get('total_appointments',0)}")

def _hc_video_ready():
    r = requests.get(f"{API}/worker/video_appointments")
    if r.status_code != 200:
        print("❌ Failed to fetch video appointments")
        return
    rows = r.json()
    if not rows:
        print("📭 No video consultations ready")
        return
    for i, apt in enumerate(rows, 1):
        print(f"[{i}] Appointment #{apt['id']} | {apt['user_name']} | {apt['status']}")

def _hc_start_video_call(worker_id):
    try:
        appointment_id = input("Appointment ID: ").strip()
        otp = input("OTP: ").strip()
        r = requests.post(f"{API}/video/start", json={"appointment_id": int(appointment_id), "otp": otp, "doctor_id": worker_id})
        if r.status_code == 200:
            print("✅ Video call started")
        else:
            try:
                print(f"❌ Error: {r.json().get('error','Unknown error')}")
            except Exception:
                print(f"❌ Failed [{r.status_code}]")
    except Exception as e:
        print(f"❌ Error: {e}")

def _hc_end_video_call(worker_id):
    try:
        appointment_id = input("Appointment ID: ").strip()
        r = requests.post(f"{API}/video/end", json={"appointment_id": int(appointment_id)})
        if r.status_code == 200:
            print("✅ Video call ended")
        else:
            try:
                print(f"❌ Error: {r.json().get('error','Unknown error')}")
            except Exception:
                print(f"❌ Failed [{r.status_code}]")
    except Exception as e:
        print(f"❌ Error: {e}")
