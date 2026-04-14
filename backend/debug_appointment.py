from appointment_db import AppointmentDB
from user_db import UserDB

# Test the appointment creation directly
appointment_db = AppointmentDB()
user_db = UserDB()

# Check if user exists
user = user_db.get_user_by_id(1)
print(f"User: {user}")

if user:
    # Try to create appointment
    try:
        appointment_id = appointment_db.book_clinic(
            user_id=1,
            worker_id=6,
            user_name=user.get('name', 'Test User'),
            symptoms="Regular checkup",
            date="2026-04-14",
            time_slot="10:00 AM"
        )
        print(f"Appointment created: {appointment_id}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
