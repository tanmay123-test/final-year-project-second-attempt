"""
Tow Truck User CLI Interface
"""

import requests
import time

API = "http://127.0.0.1:5000"

def tow_truck_user_interface(user_info):
    """User interface for requesting a tow truck"""
    print("\n" + "="*50)
    print("🚛 REQUEST TOW TRUCK")
    print("="*50)
    
    pickup = input("📍 Enter pickup location: ").strip()
    drop = input("🏁 Enter drop location: ").strip()
    
    print("\n🚗 Vehicle Type:")
    print("1. Small Car")
    print("2. SUV/Van")
    print("3. Heavy Vehicle")
    vehicle_choice = input("Select (1-3): ").strip()
    vehicle = {"1": "Small Car", "2": "SUV/Van", "3": "Heavy Vehicle"}.get(vehicle_choice, "Small Car")
    
    condition = input("🔧 Vehicle condition (e.g. Engine failure, Accident): ").strip()
    
    # Mock distance and earning
    distance = 15.5
    earning = 1200
    
    print(f"\n📏 Estimated Distance: {distance} km")
    print(f"💰 Estimated Cost: ₹{earning}")
    
    confirm = input("\nConfirm request? (y/N): ").strip().lower()
    if confirm != 'y':
        return
    
    response = requests.post(f"{API}/api/car/tow/create-request", json={
        "user_id": user_info['id'],
        "pickup": pickup,
        "drop": drop,
        "vehicle": vehicle,
        "condition": condition,
        "distance": distance,
        "earning": earning
    })
    
    if response.status_code == 200:
        res = response.json()
        request_id = res.get('request_id')
        print(f"\n✅ Request sent! ID: {request_id}")
        track_tow_status(request_id)
    else:
        print(f"❌ Error: {response.text}")

def track_tow_status(request_id):
    """Track tow request status"""
    print("\n⏳ Tracking status...")
    last_status = None
    
    while True:
        try:
            response = requests.get(f"{API}/api/car/tow/job-status/{request_id}")
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                otp = data.get('otp')
                
                if status != last_status:
                    print(f"\n🔔 Status Update: {status}")
                    if status == 'ACCEPTED' and otp:
                        print(f"🔒 YOUR OTP: {otp}")
                        print("⚠️ GIVE THIS OTP TO OPERATOR WHEN THEY ARRIVE")
                    last_status = status
                
                if status == 'COMPLETED':
                    print("\n✅ Towing completed!")
                    print("💰 PAYMENT REQUIRED")
                    print("1. 💳 Pay Now")
                    print("2. ⬅️ Back")
                    choice = input("\nSelect: ").strip()
                    if choice == "1":
                        print("Processing payment...")
                        time.sleep(2)
                        print("✅ Paid! Thank you.")
                    return
                
            time.sleep(5)
        except KeyboardInterrupt:
            return
        except Exception as e:
            print(f"Error: {e}")
            return
