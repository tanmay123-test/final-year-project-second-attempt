print("=== QUICK HEALTHCARE TEST ===")
print()

# Test if server is running
try:
    import requests
    response = requests.get('http://localhost:5000/healthcare/doctors', timeout=3)
    if response.status_code == 200:
        data = response.json()
        doctors = data.get('doctors', [])
        print(f"✅ Server running - {len(doctors)} healthcare workers found")
        
        # Show first doctor
        if doctors:
            doctor = doctors[0]
            print(f"   Example: {doctor.get('full_name', 'N/A')} - {doctor.get('specialization', 'N/A')}")
        
        # Test availability
        response = requests.get('http://localhost:5000/healthcare/availability/6?date=2026-04-13', timeout=3)
        if response.status_code == 200:
            slots = response.json().get('available_slots', [])
            print(f"✅ Availability API working - {len(slots)} slots for doctor 6")
        else:
            print(f"❌ Availability API error: {response.status_code}")
            
    else:
        print(f"❌ Server error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")
    print("   Make sure the backend server is running on localhost:5000")

print()
print("=== WHAT TO CHECK ===")
print("1. Is backend server running? (python app.py)")
print("2. Can you see real doctors in frontend?")
print("3. Do time slots appear when you select a date?")
print("4. Does booking button work when you click it?")
print()
print("Please tell me which specific step is not working!")
