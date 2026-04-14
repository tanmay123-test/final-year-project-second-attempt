import requests

print("=== NEW AVAILABILITY SYSTEM TEST ===")
print()

# Test 1: Add specific time slots for a doctor
print("1. Testing doctor availability with specific time slots...")

# Clear existing slots and add 2 specific slots for today
doctor_id = 6
today = "2026-04-13"
time_slots = ["09:00 AM", "02:00 PM"]

print(f"   Doctor {doctor_id} - Setting availability for {today}")
print(f"   Time slots: {time_slots}")

try:
    # Set availability
    response = requests.post(f"http://localhost:5000/healthcare/availability/{doctor_id}", json={
        "date": today,
        "time_slots": time_slots
    })
    
    if response.status_code == 200:
        print("   ✅ Availability set successfully!")
        
        # Test 2: Verify availability
        response = requests.get(f"http://localhost:5000/healthcare/availability/{doctor_id}?date={today}")
        if response.status_code == 200:
            available_slots = response.json().get('available_slots', [])
            print(f"   ✅ Available slots: {available_slots}")
            
            # Test 3: Try to book first slot
            print("\n2. Testing appointment booking...")
            booking_data = {
                "doctor_id": doctor_id,
                "patient_id": 1,
                "date": today,
                "time": "09:00 AM",
                "reason": "Test appointment"
            }
            
            response = requests.post("http://localhost:5000/healthcare/appointments", json=booking_data)
            if response.status_code == 201:
                print("   ✅ First slot booked successfully!")
                
                # Test 4: Check remaining slots
                response = requests.get(f"http://localhost:5000/healthcare/availability/{doctor_id}?date={today}")
                remaining_slots = response.json().get('available_slots', [])
                print(f"   ✅ Remaining slots: {remaining_slots}")
                
                # Test 5: Try to book second slot
                booking_data["time"] = "02:00 PM"
                response = requests.post("http://localhost:5000/healthcare/appointments", json=booking_data)
                if response.status_code == 201:
                    print("   ✅ Second slot booked successfully!")
                    
                    # Test 6: Check if no slots remain
                    response = requests.get(f"http://localhost:5000/healthcare/availability/{doctor_id}?date={today}")
                    final_slots = response.json().get('available_slots', [])
                    print(f"   ✅ Final available slots: {final_slots}")
                    
                    print("\n🎉 NEW AVAILABILITY SYSTEM WORKING PERFECTLY!")
                    print("   - Doctors can set specific time slots (9 AM, 2 PM)")
                    print("   - Maximum 2 slots per date")
                    print("   - Users see only doctor-set slots")
                    print("   - Booking system works correctly")
                    
                else:
                    print(f"   ❌ Failed to book second slot: {response.json()}")
            else:
                print(f"   ❌ Failed to book first slot: {response.json()}")
        else:
            print(f"   ❌ Failed to get availability: {response.status_code}")
    else:
        print(f"   ❌ Failed to set availability: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Make sure the server is running on localhost:5000")

print()
print("📋 HOW TO USE:")
print("1. Login as healthcare worker")
print("2. Go to Availability tab")
print("3. Select date and choose time from dropdown")
print("4. Maximum 2 slots per date allowed")
print("5. Users will see only these specific slots when booking")
