import requests

print("=== CLEAR AND RESET AVAILABILITY ===")
print()

doctor_id = 6
today = "2026-04-13"
time_slots = ["09:00 AM", "02:00 PM"]

print(f"Clearing all existing slots for Doctor {doctor_id} on {today}")
print(f"Setting new slots: {time_slots}")
print()

try:
    # Step 1: Clear all slots by setting empty array
    response = requests.post(f"http://localhost:5000/healthcare/availability/{doctor_id}", json={
        "date": today,
        "time_slots": []
    })
    
    if response.status_code == 200:
        print("✅ Cleared all existing slots")
        
        # Step 2: Set new specific slots
        response = requests.post(f"http://localhost:5000/healthcare/availability/{doctor_id}", json={
            "date": today,
            "time_slots": time_slots
        })
        
        if response.status_code == 200:
            print("✅ Set new specific slots")
            
            # Step 3: Verify the availability
            response = requests.get(f"http://localhost:5000/healthcare/availability/{doctor_id}?date={today}")
            if response.status_code == 200:
                available_slots = response.json().get('available_slots', [])
                print(f"✅ Available slots: {available_slots}")
                
                if set(available_slots) == set(time_slots):
                    print("🎉 PERFECT! Only the 2 specific slots are available")
                    
                    # Test booking
                    print("\nTesting booking system...")
                    booking_data = {
                        "doctor_id": doctor_id,
                        "patient_id": 1,
                        "date": today,
                        "time": "09:00 AM",
                        "reason": "Test appointment"
                    }
                    
                    response = requests.post("http://localhost:5000/healthcare/appointments", json=booking_data)
                    if response.status_code == 201:
                        print("✅ Successfully booked 09:00 AM slot")
                        
                        # Check remaining slots
                        response = requests.get(f"http://localhost:5000/healthcare/availability/{doctor_id}?date={today}")
                        remaining = response.json().get('available_slots', [])
                        print(f"✅ Remaining slots: {remaining}")
                        
                        if remaining == ["02:00 PM"]:
                            print("🎉 BOOKING SYSTEM WORKING PERFECTLY!")
                        else:
                            print(f"❌ Expected ['02:00 PM'], got {remaining}")
                    else:
                        print(f"❌ Booking failed: {response.json()}")
                else:
                    print(f"❌ Expected {time_slots}, got {available_slots}")
            else:
                print(f"❌ Failed to get availability: {response.status_code}")
        else:
            print(f"❌ Failed to set slots: {response.status_code}")
    else:
        print(f"❌ Failed to clear slots: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
