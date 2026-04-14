import requests

try:
    response = requests.get('http://localhost:5000/healthcare/doctors')
    print('Healthcare API Status:', response.status_code)
    data = response.json()
    print(f'Found {len(data.get("doctors", []))} doctors')
    print('✅ Server is running successfully!')
    
    # Test availability endpoint
    response = requests.get('http://localhost:5000/healthcare/availability/6?date=2026-04-13')
    print('Availability API Status:', response.status_code)
    slots = response.json().get('available_slots', [])
    print(f'Available slots for doctor 6: {len(slots)} slots')
    
except Exception as e:
    print(f'❌ Error: {e}')
