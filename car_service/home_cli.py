from .car_profile_db import car_profile_db
from .booking_db import booking_db

def show_car_home(user_id):
    profile = car_profile_db.get_car_profile(user_id)
    if not profile:
        print("No car service profile found. Please setup your profile first.")
        input("\nPress Enter to continue...")
        return
    car = car_profile_db.get_default_car(user_id)
    
    print("\n" + "="*50)
    print("🚗 CAR SERVICE HOME")
    print("="*50)
    print("\n🚨 PANIC EMERGENCY")
    print("----------------------------------------")
    print("Emergency Contact:")
    print(f"Name: {profile.get('emergency_contact_name', '')}")
    print(f"Phone: {profile.get('emergency_contact_phone', '')}")
    print("\nEmergency Services:")
    print("1. 🚛 Tow Truck")
    print("2. ⛽ Fuel Delivery")
    print("3. 🔧 Mechanic Emergency")
    choice = input("\nSelect emergency option or press Enter to skip: ").strip()
    if choice in ["1", "2", "3"]:
        print("\nSearching nearest service...")
        print("(This will use Smart Dispatch Engine later)")
    print("\n\n📍 LOCATION")
    print("----------------------------------------")
    print(f"City: {profile.get('city', '')}")
    print(f"Address: {profile.get('address', '')}")
    print("\n\n🚗 DEFAULT CAR")
    print("----------------------------------------")
    if car:
        print(f"Brand: {car.get('brand', '')}")
        print(f"Model: {car.get('model', '')}")
        print(f"Year: {car.get('year', '')}")
        print(f"Fuel Type: {car.get('fuel_type', '')}")
        print(f"Registration Number: {car.get('registration_number', '')}")
    else:
        print("No cars found. Please add car first.")
    
    print("\n\n📅 ACTIVE JOB")
    print("----------------------------------------")
    
    # Get active job
    active_job = booking_db.get_active_job(user_id)
    if active_job:
        status_emoji = {
            'SEARCHING': '🔍',
            'ACCEPTED': '✅',
            'ARRIVING': '🚗',
            'WORKING': '🔧'
        }.get(active_job['status'], '📋')
        
        print(f"Job ID: {active_job['id']}")
        print(f"Issue: {active_job['issue']}")
        print(f"Status: {status_emoji} {active_job['status']}")
        print(f"Mechanic: {active_job['mechanic_name']}")
        print(f"Created: {active_job['created_at']}")
        
        if active_job['status'] == 'ACCEPTED':
            print(f"⏰ Accepted at: {active_job.get('accepted_at', 'Pending')}")
        elif active_job['status'] == 'ARRIVING':
            print(f"📍 Mechanic arriving in 15 minutes")
        elif active_job['status'] == 'WORKING':
            print(f"🔧 Work in progress since {active_job.get('started_at', 'Pending')}")
    else:
        print("No active jobs")
    
    input("\nPress Enter to continue...")
