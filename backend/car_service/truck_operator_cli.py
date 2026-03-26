"""
Truck Operator CLI Interface
Handles truck operator signup, login, and dashboard access
"""

import os
import requests
import time
from datetime import datetime

API = "http://127.0.0.1:5000"

def truck_operator_signup():
    """Truck operator signup process"""
    print("\n" + "="*60)
    print("  TRUCK OPERATOR SIGNUP")
    print("="*60)
    
    try:
        # Basic info
        name = input("  Enter full name: ").strip()
        email = input("  Enter email: ").strip()
        phone = input("  Enter phone: ").strip()
        password = input("  Enter password: ").strip()
        city_name = input("   Enter city name: ").strip()
        
        # Vehicle type dropdown
        print("\n  Vehicle Type:")
        print("1. Mini Truck")
        print("2. Medium Truck")
        print("3. Heavy Truck")
        print("4. Trailer")
        print("5. Tanker")
        
        while True:
            vehicle_choice = input("Select vehicle type (1-5): ").strip()
            if vehicle_choice == "1":
                vehicle_type = "Mini Truck"
                break
            elif vehicle_choice == "2":
                vehicle_type = "Medium Truck"
                break
            elif vehicle_choice == "3":
                vehicle_type = "Heavy Truck"
                break
            elif vehicle_choice == "4":
                vehicle_type = "Trailer"
                break
            elif vehicle_choice == "5":
                vehicle_type = "Tanker"
                break
            else:
                print("  Invalid choice. Please select 1-5.")
        
        # Truck details
        truck_registration = input("  Truck Registration Number: ").strip()
        truck_model = input("  Truck Model: ").strip()
        
        # Document paths
        print("\n  Document Uploads")
        print("Enter file paths for required documents:")
        
        license_path = input("Enter Driving license file path: ").strip()
        rc_book_path = input("Enter RC Book file path: ").strip()
        insurance_path = input("Enter Insurance file path: ").strip()
        
        # Validation
        if not all([name, email, phone, password, city_name, vehicle_type, truck_registration, truck_model]):
            print("  All required fields must be filled")
            return
        
        # Validate file paths exist
        for path, field_name in [(license_path, "License"), (rc_book_path, "RC Book"), (insurance_path, "Insurance")]:
            if path and not os.path.exists(path):
                print(f"  {field_name} file not found: {path}")
                return
        
        # Prepare data
        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "city": city_name,
            "vehicle_type": vehicle_type,
            "truck_registration": truck_registration,
            "truck_model": truck_model,
            "license_path": license_path,
            "rc_book_path": rc_book_path,
            "insurance_path": insurance_path
        }
        
        # Call API
        response = requests.post(f"{API}/api/car/truck-operator/signup", data=data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n  {result.get('message', 'Signup successful!')}")
            print(f"  Truck Operator ID: {result.get('operator_id')}")
            print("  You can now login to your truck operator dashboard")
        else:
            error = response.json().get("error", "Signup failed")
            print(f"  {error}")
        
    except Exception as e:
        print(f"  Signup error: {e}")

def truck_operator_login():
    """Truck operator login process"""
    print("\n" + "="*50)
    print("  TRUCK OPERATOR LOGIN")
    print("="*50)
    
    try:
        email = input("  Enter email: ").strip()
        password = input("  Enter password: ").strip()
        
        if not email or not password:
            print("  Email and password are required")
            return
        
        # Call API
        response = requests.post(f"{API}/api/car/truck-operator/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            result = response.json()
            operator = result.get("operator", {})
            token = result.get("token")
            
            print(f"\n  Login successful!")
            print(f"  Welcome, {operator.get('name', 'Operator')}!")
            print(f"   City: {operator.get('city', 'Unknown')}")
            print(f"  Vehicle Type: {operator.get('vehicle_type', 'Unknown')}")
            print(f"  Truck: {operator.get('truck_registration', 'Unknown')}")
            
            # Open truck operator dashboard
            truck_operator_dashboard(operator, token)
                
        elif response.status_code == 401:
            print("  Invalid email or password")
        elif response.status_code == 403:
            result = response.json()
            status = result.get("status", "PENDING")
            print(f"  {result.get('error', 'Account not approved')}")
            print(f"  Current status: {status}")
        else:
            error = response.json().get("error", "Login failed")
            print(f"  {error}")
            
    except Exception as e:
        print(f"  Login error: {e}")

def truck_operator_dashboard(operator, token):
    """Truck operator dashboard menu"""
    while True:
        print("\n" + "="*60)
        print("  TRUCK OPERATOR DASHBOARD")
        print("="*60)
        print(f"  {operator.get('name')}")
        print(f"  {operator.get('email')}")
        print(f"  {operator.get('phone')}")
        print(f"   City: {operator.get('city', 'Unknown')}")
        print(f"  Vehicle Type: {operator.get('vehicle_type', 'Unknown')}")
        print(f"  Truck: {operator.get('truck_registration', 'Unknown')}")
        print(f"  Model: {operator.get('truck_model', 'Unknown')}")
        print(f"  Status: {'ONLINE' if operator.get('is_online', 0) else 'OFFLINE'}")
        
        print("\nOptions:")
        print("1.   Go Online / Offline")
        print("2.   Transport Requests")
        print("3.   Active Jobs")
        print("4.   Earnings")
        print("5.   Performance")
        print("6.   Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            toggle_online_status(operator, token)
        elif choice == "2":
            print("  Transport Requests coming soon!")
            input("\nPress Enter to continue...")
        elif choice == "3":
            print("  Active Jobs coming soon!")
            input("\nPress Enter to continue...")
        elif choice == "4":
            print("  Earnings coming soon!")
            input("\nPress Enter to continue...")
        elif choice == "5":
            print("  Performance coming soon!")
            input("\nPress Enter to continue...")
        elif choice == "6":
            print("  Logged out successfully")
            return
        else:
            print("  Invalid choice")

def toggle_online_status(operator, token):
    """Toggle truck operator online/offline status"""
    try:
        current_status = operator.get('is_online', 0)
        new_status = 1 if current_status == 0 else 0
        
        response = requests.put(
            f"{API}/api/car/truck-operator/status",
            json={"is_online": bool(new_status)},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Status updated')}")
            
            # Update local operator data
            operator['is_online'] = new_status
            
            # Show note if it's a worker account
            if result.get('note'):
                print(f"   {result['note']}")
                
        else:
            error = response.json().get("error", "Failed to update status")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Status update error: {e}")
        input("\nPress Enter to continue...")

def truck_operator_menu():
    """Main truck operator menu"""
    while True:
        print("\n" + "="*50)
        print("  TRUCK OPERATOR")
        print("="*50)
        print("1.   Signup")
        print("2.   Login")
        print("3.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            truck_operator_signup()
        elif choice == "2":
            truck_operator_login()
        elif choice == "3":
            return
        else:
            print("  Invalid choice")
