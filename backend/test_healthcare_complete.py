print("=== COMPLETE HEALTHCARE SYSTEM TEST ===")
print()
print("Please start the server first: python app.py")
print("Then run this script again to test all functionality.")
print()

def test_healthcare_system():
    import requests
    
    print("🔍 Testing Healthcare System...")
    print()
    
    # Test 1: Get healthcare doctors
    try:
        response = requests.get('http://localhost:5000/healthcare/doctors')
        if response.status_code == 200:
            data = response.json()
            doctors = data.get('doctors', [])
            print(f"✅ Doctors API: Found {len(doctors)} healthcare workers")
            
            for i, doctor in enumerate(doctors[:2], 1):
                name = doctor.get('full_name', 'N/A')
                spec = doctor.get('specialization', 'N/A')
                print(f"   {i}. Dr. {name} ({spec})")
        else:
            print(f"❌ Doctors API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Get availability
    try:
        response = requests.get('http://localhost:5000/healthcare/availability/6?date=2026-04-13')
        if response.status_code == 200:
            data = response.json()
            slots = data.get('available_slots', [])
            print(f"✅ Availability API: {len(slots)} slots available")
        else:
            print(f"❌ Availability API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Availability error: {e}")
    
    # Test 3: Book appointment
    try:
        appointment_data = {
            "doctor_id": 6,
            "patient_id": 1,
            "date": "2026-04-13",
            "time": "09:00 AM",
            "reason": "Test appointment"
        }
        
        response = requests.post('http://localhost:5000/healthcare/appointments', json=appointment_data)
        if response.status_code == 201:
            print("✅ Booking API: Appointment created successfully")
        else:
            print(f"⚠️  Booking API: {response.status_code} - {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Booking error: {e}")
    
    print()
    print("🎯 FRONTEND TEST INSTRUCTIONS:")
    print("1. Go to: http://localhost:3000/healthcare/home")
    print("2. Check if you see real doctors (not dummy data)")
    print("3. Click 'Book Now' on any doctor")
    print("4. Select today's date (2026-04-13)")
    print("5. Check if time slots appear")
    print("6. Select a time slot and try to book")
    print()
    print("If any step fails, please tell me which one!")

if __name__ == "__main__":
    test_healthcare_system()
