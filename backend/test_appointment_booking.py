import requests

# Test appointment booking
appointment_data = {
    "doctor_id": 6,
    "patient_id": 1,
    "date": "2026-04-14",
    "time": "09:00 AM",
    "reason": "Regular checkup",
    "status": "pending"
}

try:
    response = requests.post("http://localhost:5000/healthcare/appointments", json=appointment_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
