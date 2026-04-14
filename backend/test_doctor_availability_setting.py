import requests

# Test setting availability for a doctor
def set_doctor_availability(doctor_id, date, time_slots):
    """Set availability for a specific doctor"""
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

# Example: Dr. Test Healthcare (ID: 6) sets availability for April 15
print("=== EXAMPLE: Doctor Setting Custom Availability ===")
print()

# Dr. Test Healthcare sets specific slots for April 15, 2026
success = set_doctor_availability(
    doctor_id=6,
    date="2026-04-15",
    time_slots=["01:00 PM", "02:00 PM", "03:00 PM"]  # Only 3 specific slots
)

if success:
    print("\n✅ Doctor successfully set custom availability!")
    print("   Patients will now only see these 3 slots for April 15")
else:
    print("\n❌ Failed to set availability")

print("\n" + "="*50)
print("HOW DOCTORS CAN SET AVAILABILITY:")
print("1. Login as healthcare worker")
print("2. Go to Availability tab in dashboard")
print("3. Select date and click on time slots")
print("4. Click 'Add Slot' to save availability")
print("5. Patients will only see the slots you set!")
print()
print("WORKER LOGIN CREDENTIALS:")
print("- Dr. Test Healthcare: doctor@expertease.com / 123456")
print("- Niharika Rothe: co2023.niharika.rothe@ves.ac.in / 123456")
print("- Aarohi Gate: aarohigate01@gmail.com / 123456")
print("- goat: pro@gmail.com / 123456")
