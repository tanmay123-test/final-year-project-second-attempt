"""
Car Service Profile CLI Interface
Manage user profile and emergency contacts
"""

import requests
from .car_profile_db import car_profile_db

API = "http://127.0.0.1:5000"

def car_profile_screen(token):
    """Display and manage car service profile"""
    while True:
        print("\n" + "="*60)
        print("👤 CAR SERVICE PROFILE")
        print("="*60)
        
        # Get current profile
        try:
            response = requests.get(f"{API}/api/car/profile", headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                profile = response.json()
                display_profile(profile)
            else:
                print("❌ Failed to load profile")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        print("\nOptions:")
        print("1. ✏️ Edit Profile")
        print("2. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            edit_profile(token)
        elif choice == "2":
            return
        else:
            print("❌ Invalid choice")

def display_profile(profile):
    """Display user profile information"""
    print("\n📍 LOCATION")
    print("-" * 30)
    print(f"City: {profile.get('city', 'Not set')}")
    print(f"Address: {profile.get('address', 'Not set')}")
    
    print("\n🚨 EMERGENCY CONTACT")
    print("-" * 30)
    print(f"Name: {profile.get('emergency_contact_name', 'Not set')}")
    print(f"Phone: {profile.get('emergency_contact_phone', 'Not set')}")

def edit_profile(token):
    """Edit user profile information"""
    print("\n" + "="*60)
    print("✏️ EDIT PROFILE")
    print("="*60)
    
    print("Leave blank to keep current value")
    
    # Get current profile first
    try:
        response = requests.get(f"{API}/api/car/profile", headers={"Authorization": f"Bearer {token}"})
        current_profile = response.json() if response.status_code == 200 else {}
    except:
        current_profile = {}
    
    # Get new values
    city = input(f"City [{current_profile.get('city', '')}]: ").strip() or current_profile.get('city', '')
    address = input(f"Address [{current_profile.get('address', '')}]: ").strip() or current_profile.get('address', '')
    emergency_name = input(f"Emergency Contact Name [{current_profile.get('emergency_contact_name', '')}]: ").strip() or current_profile.get('emergency_contact_name', '')
    emergency_phone = input(f"Emergency Contact Phone [{current_profile.get('emergency_contact_phone', '')}]: ").strip() or current_profile.get('emergency_contact_phone', '')
    
    # Validate inputs
    if not city or not address or not emergency_name or not emergency_phone:
        print("❌ All fields are required")
        input("\nPress Enter to continue...")
        return
    
    # Update profile
    profile_data = {
        "city": city,
        "address": address,
        "emergency_contact_name": emergency_name,
        "emergency_contact_phone": emergency_phone
    }
    
    try:
        response = requests.put(
            f"{API}/api/car/profile",
            json=profile_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            print("✅ Profile updated successfully")
        else:
            print("❌ Failed to update profile")
            if response.status_code == 401:
                print("❌ Please login again")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")
