"""
Tow Truck Operator CLI Interface
Handles tow truck operator signup, login, and dashboard access
"""

import os
import requests
import time
from datetime import datetime

API = "http://127.0.0.1:5000"

def tow_truck_operator_signup():
    """Tow truck operator signup process"""
    print("\n" + "="*60)
    print("🚛 TOW TRUCK OPERATOR SIGNUP")
    print("="*60)
    
    try:
        # Basic info
        name = input("👤 Enter full name: ").strip()
        email = input("📧 Enter email: ").strip()
        phone = input("📱 Enter phone: ").strip()
        password = input("🔒 Enter password: ").strip()
        city = input("🏙️ Enter city: ").strip()
        experience = input("💼 Enter experience (years): ").strip()
        
        # Truck type dropdown
        print("\n🚚 Truck Type:")
        print("1. Flatbed")
        print("2. Wheel Lift")
        print("3. Heavy Duty")
        print("4. Integrated")
        
        while True:
            truck_choice = input("Select truck type (1-4): ").strip()
            if truck_choice == "1":
                truck_type = "Flatbed"
                break
            elif truck_choice == "2":
                truck_type = "Wheel Lift"
                break
            elif truck_choice == "3":
                truck_type = "Heavy Duty"
                break
            elif truck_choice == "4":
                truck_type = "Integrated"
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
        
        # Truck details
        truck_registration = input("🔢 Truck Registration Number: ").strip()
        truck_model = input("🚗 Truck Model: ").strip()
        
        # Capacity
        print("\n📏 Truck Capacity:")
        print("1. Small Car")
        print("2. SUV/Van")
        print("3. Heavy Vehicle")
        print("4. Multiple Vehicles")
        
        while True:
            capacity_choice = input("Select capacity (1-4): ").strip()
            if capacity_choice == "1":
                truck_capacity = "Small Car"
                break
            elif capacity_choice == "2":
                truck_capacity = "SUV/Van"
                break
            elif capacity_choice == "3":
                truck_capacity = "Heavy Vehicle"
                break
            elif capacity_choice == "4":
                truck_capacity = "Multiple Vehicles"
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
        
        # Document paths
        print("\n📄 Document Uploads")
        print("Enter file paths for required documents:")
        
        license_path = input("Enter Driving license file path: ").strip()
        insurance_path = input("Enter Insurance file path: ").strip()
        fitness_cert_path = input("Enter Fitness Certificate file path: ").strip()
        pollution_cert_path = input("Enter Pollution Certificate file path: ").strip()
        
        # Validation
        if not all([name, email, phone, password, city, experience, truck_type, truck_registration, truck_model, truck_capacity]):
            print("❌ All required fields must be filled")
            return
        
        # Validate file paths exist
        for path, field_name in [(license_path, "License"), (insurance_path, "Insurance"), 
                                 (fitness_cert_path, "Fitness Certificate"), (pollution_cert_path, "Pollution Certificate")]:
            if path and not os.path.exists(path):
                print(f"❌ {field_name} file not found: {path}")
                return
        
        # Prepare data
        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "city": city,
            "experience": experience,
            "truck_type": truck_type,
            "truck_registration": truck_registration,
            "truck_model": truck_model,
            "truck_capacity": truck_capacity,
            "license_path": license_path,
            "insurance_path": insurance_path,
            "fitness_cert_path": fitness_cert_path,
            "pollution_cert_path": pollution_cert_path
        }
        
        # Call API
        response = requests.post(f"{API}/api/tow-truck/register", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ {result.get('message', 'Signup successful!')}")
            print(f"📋 Tow Truck Operator ID: {result.get('operator_id')}")
            print("🎉 You can now login to your tow truck dashboard")
        else:
            try:
                error = response.json().get("error", "Signup failed")
            except:
                error = f"Signup failed with status {response.status_code}"
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Signup error: {e}")

def tow_truck_operator_login():
    """Tow truck operator login process"""
    print("\n" + "="*50)
    print("🔐 TOW TRUCK OPERATOR LOGIN")
    print("="*50)
    
    try:
        email = input("📧 Enter email: ").strip()
        password = input("🔒 Enter password: ").strip()
        
        if not email or not password:
            print("❌ Email and password are required")
            return
        
        # Call API
        response = requests.post(f"{API}/api/tow-truck/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            result = response.json()
            operator = result.get("operator", {})
            token = result.get("token")
            
            print(f"\n✅ Login successful!")
            print(f"👤 Welcome, {operator.get('name', 'Operator')}!")
            print(f"🏙️ City: {operator.get('city', 'Unknown')}")
            print(f"💼 Experience: {operator.get('experience', 0)} years")
            print(f"🚚 Truck Type: {operator.get('truck_type', 'Unknown')}")
            print(f"🔢 Truck: {operator.get('truck_registration', 'Unknown')}")
            
            # Open tow truck operator dashboard
            tow_truck_operator_dashboard(operator, token)
                
        elif response.status_code == 401:
            print("❌ Invalid email or password")
        elif response.status_code == 403:
            result = response.json()
            status = result.get("status", "PENDING")
            print(f"❌ {result.get('error', 'Account not approved')}")
            print(f"📊 Current status: {status}")
        else:
            error = response.json().get("error", "Login failed")
            print(f"❌ {error}")
            
    except Exception as e:
        print(f"❌ Login error: {e}")

def tow_truck_operator_dashboard(operator, token):
    """Tow truck operator dashboard menu"""
    while True:
        print("\n" + "="*60)
        print("🚛 TOW TRUCK OPERATOR DASHBOARD")
        print("="*60)
        print(f"👤 {operator.get('name')}")
        print(f"📧 {operator.get('email')}")
        print(f"📱 {operator.get('phone')}")
        print(f"🏙️ City: {operator.get('city')}")
        print(f"💼 Experience: {operator.get('experience', 0)} years")
        print(f"🚚 Truck Type: {operator.get('truck_type', 'Unknown')}")
        print(f"🔢 Truck: {operator.get('truck_registration', 'Unknown')}")
        print(f"📏 Capacity: {operator.get('truck_capacity', 'Unknown')}")
        print(f"🟢 Status: {'ONLINE' if operator.get('is_online', 0) else 'OFFLINE'}")
        
        print("\nOptions:")
        print("1. 🟢 Go Online / Offline")
        print("2. 📋 Tow Requests")
        print("3. 🔧 Active Jobs")
        print("4. 💰 Earnings")
        print("5. 📊 Performance")
        print("6. 👋 Logout")
        
        choice = input("\nSelect option: ").strip()
        
        worker_id = operator.get('id')

        if choice == "1":
            print("\n1. 🟢 Go Online")
            print("2. 🔴 Go Offline")
            sub = input("Select: ").strip()
            
            if sub == "1":
                response = requests.post(f"{API}/api/car/tow/go-online", json={"worker_id": worker_id})
            else:
                response = requests.post(f"{API}/api/car/tow/go-offline", json={"worker_id": worker_id})
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result.get('message', 'Status updated successfully')}")
                # Update local state for display
                operator['is_online'] = 1 if sub == "1" else 0
            else:
                print(f"❌ Error: {response.text}")
            input("\nPress Enter to continue...")

        elif choice == "2":
            response = requests.get(f"{API}/api/car/tow/requests")
            if response.status_code == 200:
                data = response.json()
                if not data:
                    print("🚫 No requests available")
                else:
                    for r in data:
                        print(f"\n🚛 Request ID: {r['id']}")
                        print(f"📍 Pickup: {r['pickup']}")
                        print(f"🏁 Drop: {r['drop']}")
                        print(f"🚗 Vehicle: {r['vehicle']}")
                        print(f"📏 Distance: {r['distance']} km")
                        print(f"💰 ₹{r['earning']}")
                    
                    choice_req = input("\nEnter Request ID to accept (0 to skip): ").strip()
                    if choice_req != "0":
                        res = requests.post(f"{API}/api/car/tow/accept", json={
                            "worker_id": worker_id,
                            "request_id": int(choice_req)
                        })
                        if res.status_code == 200:
                            print("✅ Job accepted! Navigate to pickup location.")
                        else:
                            print(f"❌ Error: {res.text}")
            else:
                print(f"❌ Error: {response.text}")
            input("\nPress Enter to continue...")

        elif choice == "3":
            response = requests.get(f"{API}/api/car/tow/active-jobs?worker_id={worker_id}")
            if response.status_code == 200:
                data = response.json()
                print("\n🔧 ACTIVE JOBS")
                print("-" * 20)
                if not data:
                    print("📭 No active jobs at the moment")
                else:
                    for job in data:
                        print(f"🆔 Job ID: {job['id']}")
                        print(f"👤 User: {job['user']}")
                        print(f"📍 Pickup: {job['pickup']}")
                        print(f"🏁 Drop: {job['drop']}")
                        print(f"📊 Status: {job['status']}")
                        
                        if job['status'] == 'ACCEPTED':
                            print("\nOptions for this job:")
                            print("1. 🔑 Enter OTP from user to START")
                            print("2. ⬅️ Back")
                            sub_choice = input("Select: ").strip()
                            if sub_choice == "1":
                                otp = input("🔐 Enter 4-digit OTP: ").strip()
                                res = requests.post(f"{API}/api/car/tow/start", json={
                                    "worker_id": worker_id,
                                    "job_id": job['id'],
                                    "otp": otp
                                })
                                if res.status_code == 200:
                                    res_data = res.json()
                                    if res_data.get('success'):
                                        print("✅ OTP Verified! Job started.")
                                    else:
                                        print(f"❌ {res_data.get('error', 'Invalid OTP')}")
                                else:
                                    print("❌ Error starting job")
                        
                        elif job['status'] == 'IN_PROGRESS':
                            print("\nOptions for this job:")
                            print("1. ✅ Mark as COMPLETED")
                            print("2. ⬅️ Back")
                            sub_choice = input("Select: ").strip()
                            if sub_choice == "1":
                                res = requests.post(f"{API}/api/car/tow/complete", json={
                                    "worker_id": worker_id,
                                    "job_id": job['id']
                                })
                                if res.status_code == 200:
                                    print("✅ Job completed! Earnings updated.")
                                else:
                                    print("❌ Error completing job")
                        print("-" * 10)
            else:
                print(f"❌ Error: {response.text}")
            input("\nPress Enter to continue...")

        elif choice == "4":
            response = requests.get(f"{API}/api/car/tow/earnings?worker_id={worker_id}")
            if response.status_code == 200:
                data = response.json()
                print("\n💰 EARNINGS SUMMARY")
                print("-" * 20)
                print(f"Today: ₹{data.get('today', 0):.2f}")
                print(f"Total: ₹{data.get('total', 0):.2f}")
            else:
                print(f"❌ Error: {response.text}")
            input("\nPress Enter to continue...")

        elif choice == "5":
            response = requests.get(f"{API}/api/car/tow/performance?worker_id={worker_id}")
            if response.status_code == 200:
                data = response.json()
                print("\n📊 PERFORMANCE METRICS")
                print("-" * 20)
                print(f"Rating: ⭐ {data.get('rating', 5.0)}")
                print(f"Completed Jobs: {data.get('completed_jobs', 0)}")
                print(f"Completion Rate: 100%")
            else:
                print(f"❌ Error: {response.text}")
            input("\nPress Enter to continue...")

        elif choice == "6":
            print("👋 Logged out successfully")
            return
        else:
            print("❌ Invalid choice")

def toggle_online_status(operator, token):
    """Toggle tow truck operator online/offline status"""
    try:
        current_status = operator.get('is_online', 0)
        new_status = 1 if current_status == 0 else 0
        
        response = requests.put(
            f"{API}/api/tow-truck/status",
            json={
                "operator_id": operator.get('id'),
                "is_online": bool(new_status)
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ {result.get('message', 'Status updated')}")
            
            # Update local operator data
            operator['is_online'] = new_status
            
            # Show note if it's a worker account
            if result.get('note'):
                print(f"ℹ️ {result['note']}")
                
        else:
            error = response.json().get("error", "Failed to update status")
            print(f"❌ {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Status update error: {e}")
        input("\nPress Enter to continue...")

def tow_truck_operator_menu():
    """Main tow truck operator menu"""
    while True:
        print("\n" + "="*50)
        print("🚛 TOW TRUCK OPERATOR")
        print("="*50)
        print("1. 📝 Signup")
        print("2. 🔐 Login")
        print("3. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            tow_truck_operator_signup()
        elif choice == "2":
            tow_truck_operator_login()
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")
