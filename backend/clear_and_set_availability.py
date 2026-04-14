import requests

# Clear existing availability and set new specific slots
def clear_and_set_availability(doctor_id, date, time_slots):
    """Clear existing availability and set new specific slots"""
    # The POST endpoint already clears existing slots and sets new ones
    data = {
        "date": date,
        "time_slots": time_slots
    }
    
    try:
        response = requests.post(f"http://localhost:5000/healthcare/availability/{doctor_id}", json=data)
        print(f"Doctor {doctor_id} - Setting availability for {date}:")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"  Error: {e}")
        return False

# Clear all availability for April 15 and set only 3 specific slots
print("=== CLEARING AND SETTING SPECIFIC AVAILABILITY ===")
print()

success = clear_and_set_availability(
    doctor_id=6,
    date="2026-04-15",
    time_slots=["01:00 PM", "02:00 PM", "03:00 PM"]  # Only these 3 slots
)

if success:
    print("\n✅ Availability updated!")
    
    # Verify the new availability
    response = requests.get(f"http://localhost:5000/healthcare/availability/6?date=2026-04-15")
    print(f"\nVerified available slots: {response.json()}")
else:
    print("\n❌ Failed to update availability")
