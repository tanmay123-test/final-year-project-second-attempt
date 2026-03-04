import requests

# Test the fixed queue endpoint
print('🔧 TESTING FIXED QUEUE ENDPOINT')
print('='*50)

try:
    response = requests.get('http://127.0.0.1:5000/api/fuel-delivery/queue/available?agent_id=1')
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            requests_data = result.get('requests', [])
            print(f'✅ Found {len(requests_data)} requests')
            for req in requests_data[:2]:
                print(f'   {req.get("fuel_type", "N/A")} - {req.get("quantity_liters", 0)}L')
                print(f'   Distance: {req.get("distance_km", 0)}km, ETA: {req.get("eta_minutes", 0)}min')
                print(f'   Score: {req.get("assignment_score", 0):.2f}')
        else:
            print('❌ No requests found')
    else:
        print(f'❌ Failed: {response.text[:200]}')
        
except Exception as e:
    print(f'Error: {e}')
