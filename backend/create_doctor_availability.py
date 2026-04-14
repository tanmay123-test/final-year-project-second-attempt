from availability_db import AvailabilityDB

# Create availability for healthcare workers
availability_db = AvailabilityDB()

# Healthcare worker IDs
doctor_ids = [5, 6, 7, 12]  # Our healthcare workers

# Time slots
time_slots = ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', 
              '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM']

# Create availability for next 7 days
from datetime import datetime, timedelta

for doctor_id in doctor_ids:
    print(f"Creating availability for doctor {doctor_id}")
    for day_offset in range(2):
        date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        for time_slot in time_slots:
            try:
                availability_db.add_availability(doctor_id, date, time_slot)
                print(f"  Set availability for {date} at {time_slot}")
            except Exception as e:
                print(f"  Error setting availability for {date} at {time_slot}: {e}")

print("Availability created for all doctors!")
