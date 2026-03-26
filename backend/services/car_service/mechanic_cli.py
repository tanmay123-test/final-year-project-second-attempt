"""
Car Service Mechanic CLI Interface
Handles mechanic signup, login, and dashboard access
"""

import os
import requests
from datetime import datetime

API = "http://127.0.0.1:5000"

def mechanic_signup():
    """Mechanic signup process"""
    print("\n" + "="*60)
    print("  MECHANIC SIGNUP")
    print("="*60)
    
    try:
        # Basic info
        name = input("  Enter full name: ").strip()
        email = input("  Enter email: ").strip()
        phone = input("  Enter phone: ").strip()
        password = input("  Enter password: ").strip()
        age = input("  Enter age: ").strip()
        city = input("   Enter city: ").strip()
        experience = input("  Enter experience (years): ").strip()
        skills = input("  Enter skills (comma separated): ").strip()
        
        # Document paths
        print("\n  Document Uploads")
        print("Enter file paths for required documents:")
        
        aadhaar_path = input("Enter Aadhaar file path: ").strip()
        license_path = input("Enter Driving license file path: ").strip()
        certificate_path = input("Enter certificate file path (optional): ").strip() or None
        profile_photo_path = input("Enter profile photo path: ").strip()
        
        # Validation
        if not all([name, email, phone, password, age, city, experience, skills]):
            print("  All required fields must be filled")
            return
        
        # Validate file paths exist
        for path, field_name in [(aadhaar_path, "Aadhaar"), (license_path, "License"), 
                                 (certificate_path, "Certificate"), (profile_photo_path, "Profile photo")]:
            if path and not os.path.exists(path):
                print(f"  {field_name} file not found: {path}")
                return
        
        # Prepare data
        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "age": age,
            "city": city,
            "experience": experience,
            "skills": skills,
            "aadhaar_path": aadhaar_path,
            "license_path": license_path,
            "profile_photo_path": profile_photo_path
        }
        
        if certificate_path:
            data["certificate_path"] = certificate_path
        
        # Call API
        response = requests.post(f"{API}/api/car/mechanic/signup", data=data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n  {result.get('message', 'Signup successful!')}")
            print(f"  Mechanic ID: {result.get('mechanic_id')}")
            print("  You can now login to your mechanic dashboard")
        else:
            error = response.json().get("error", "Signup failed")
            print(f"  {error}")
        
    except Exception as e:
        print(f"  Signup error: {e}")

def mechanic_login():
    """Mechanic login process"""
    print("\n" + "="*50)
    print("  MECHANIC LOGIN")
    print("="*50)
    
    try:
        email = input("  Enter email: ").strip()
        password = input("  Enter password: ").strip()
        
        if not email or not password:
            print("  Email and password are required")
            return
        
        # Call API
        response = requests.post(f"{API}/api/car/mechanic/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            result = response.json()
            mechanic = result.get("mechanic", {})
            token = result.get("token")
            
            print(f"\n  Login successful!")
            print(f"  Welcome, {mechanic.get('name', 'Mechanic')}!")
            print(f"   City: {mechanic.get('city', 'Unknown')}")
            print(f"  Experience: {mechanic.get('experience', 0)} years")
            print(f"  Skills: {mechanic.get('skills', 'N/A')}")
            
            # Open mechanic dashboard
            mechanic_dashboard(mechanic, token)
                
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

def mechanic_dashboard(mechanic, token):
    """Mechanic dashboard menu"""
    while True:
        print("\n" + "="*60)
        print("  MECHANIC DASHBOARD")
        print("="*60)
        print(f"  {mechanic.get('name')}")
        print(f"  {mechanic.get('email')}")
        print(f"  {mechanic.get('phone')}")
        print(f"   {mechanic.get('city')}")
        print(f"  Experience: {mechanic.get('experience', 0)} years")
        print(f"  Skills: {mechanic.get('skills', 'N/A')}")
        print(f"  Status: {'ONLINE' if mechanic.get('is_online', 0) else 'OFFLINE'}")
        
        print("\nOptions:")
        print("1.   Go Online / Offline")
        print("2.   Job Requests (Transparent Queue)")
        print("3.   Active Jobs")
        print("4.   Earnings & Fairness Insights")
        print("5.   Performance, Safety & Support")
        print("6.   Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            toggle_online_status(mechanic, token)
        elif choice == "2":
            print("  Job Requests coming soon!")
            input("\nPress Enter to continue...")
        elif choice == "3":
            print("  Active Jobs coming soon!")
            input("\nPress Enter to continue...")
        elif choice == "4":
            print("  Earnings & Fairness Insights coming soon!")
            input("\nPress Enter to continue...")
        elif choice == "5":
            print("  Performance, Safety & Support coming soon!")
            input("\nPress Enter to continue...")
        elif choice == "6":
            print("  Logged out successfully")
            return
        else:
            print("  Invalid choice")

def toggle_online_status(mechanic, token):
    """Toggle mechanic online/offline status"""
    try:
        current_status = mechanic.get('is_online', 0)
        new_status = 1 if current_status == 0 else 0
        
        response = requests.put(
            f"{API}/api/car/mechanic/status",
            json={"is_online": bool(new_status)},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Status updated')}")
            
            # Update local mechanic data
            mechanic['is_online'] = new_status
            
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

def mechanic_menu():
    """Main mechanic menu"""
    while True:
        print("\n" + "="*50)
        print("  MECHANIC MENU")
        print("="*50)
        print("1.   Signup")
        print("2.   Login")
        print("3.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            mechanic_signup()
        elif choice == "2":
            mechanic_login()
        elif choice == "3":
            return
        else:
            print("  Invalid choice")
