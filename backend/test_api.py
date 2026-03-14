#!/usr/bin/env python3
import requests
import json

# Test the API endpoint directly
def test_api():
    try:
        # Test data with merchant
        data = {
            "category": "Food",
            "amount": 75.0,
            "description": "API Test",
            "merchant": "API Restaurant",
            "date": "2026-03-10",
            "type": "expense"
        }
        
        print("Testing API with merchant field...")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        # This will fail without auth, but we can see the error
        response = requests.post(
            "http://localhost:5000/api/money/transactions",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
