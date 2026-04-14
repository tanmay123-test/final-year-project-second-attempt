import requests

# Test healthcare worker login
login_data = {
    'email': 'co2023.niharika.rothe@ves.ac.in',
    'password': '123456'
}

try:
    response = requests.post("http://localhost:5000/worker/healthcare/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
