import requests
import json

# Test freelance registration
url = "http://localhost:5000/worker/freelance/signup"

data = {
    "full_name": "Test Freelancer",
    "email": "testfreelancer@gmail.com",
    "phone": "1234567890",
    "skills": "Web Development",
    "skill_ids": [1],
    "hourly_rate": "50",
    "bio": "Test bio",
    "aadhaar": "123456789012"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
