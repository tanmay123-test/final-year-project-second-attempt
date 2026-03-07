#!/usr/bin/env python3
"""
Check all available fuel delivery routes
"""

import requests

API = "http://127.0.0.1:5000"

def check_routes():
    print('🔧 CHECKING AVAILABLE FUEL DELIVERY ROUTES')
    print('='*60)
    
    routes_to_test = [
        ('POST', '/api/fuel-delivery/status', 'Status Update'),
        ('GET', '/api/fuel-delivery/requests?agent_id=1', 'Get Requests'),
        ('POST', '/api/fuel-delivery/accept-request', 'Accept Request'),
        ('GET', '/api/fuel-delivery/demand-insights', 'Demand Insights'),
        ('POST', '/api/fuel-delivery/reject-request', 'Reject Request'),
    ]
    
    for method, route, description in routes_to_test:
        print(f'\n🔍 Testing {description}: {method} {route}')
        try:
            if method == 'POST':
                response = requests.post(f"{API}{route}", json={'test': 'data'})
            else:
                response = requests.get(f"{API}{route}")
            
            print(f'   Status: {response.status_code}')
            if response.status_code == 200:
                print(f'   ✅ Route exists and working')
            elif response.status_code == 404:
                print(f'   ❌ Route not found (404)')
            elif response.status_code == 405:
                print(f'   ⚠️ Route exists but wrong method (405)')
            else:
                print(f'   ⚠️ Route returned: {response.status_code}')
                
        except Exception as e:
            print(f'   ❌ Error: {e}')
    
    print('\n' + '='*60)
    print('🎯 ROUTE CHECK COMPLETE!')

if __name__ == "__main__":
    check_routes()
