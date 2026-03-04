#!/usr/bin/env python3
"""
Debug available routes to see what's actually loaded
"""

import requests

def check_available_routes():
    print("🔧 CHECKING AVAILABLE ROUTES")
    print("="*50)
    
    base_url = "http://127.0.0.1:5000/api/fuel-delivery"
    
    # Test all possible routes
    routes_to_test = [
        "/status",
        "/requests", 
        "/queue/available",
        "/queue/assign",
        "/active-delivery/1",
        "/history/1",
        "/performance/1"
    ]
    
    for route in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}")
            print(f"GET {route}: {response.status_code}")
        except Exception as e:
            print(f"GET {route}: Error - {e}")
    
    print("\n" + "="*50)
    print("🎯 ROUTE CHECK COMPLETE")

if __name__ == "__main__":
    check_available_routes()
