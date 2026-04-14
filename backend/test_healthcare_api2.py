import requests

try:
    response = requests.get("http://localhost:5000/healthcare/doctors")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data.get('doctors', []))} doctors")
    for doctor in data.get('doctors', [])[:3]:
        print(f"  - {doctor.get('full_name', 'N/A')} ({doctor.get('service', 'N/A')}) - {doctor.get('status', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")
