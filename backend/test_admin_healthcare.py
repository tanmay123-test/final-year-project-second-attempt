import requests

print('Testing fixed healthcare admin endpoints...')
API = "http://127.0.0.1:5000"

try:
    # Test pending workers
    print('\n1. Testing pending workers...')
    r = requests.get(f"{API}/admin/healthcare/workers/pending")
    data = r.json()
    print(f'Status: {r.status_code}')
    print(f'Data: {data}')
    print(f'Workers type: {type(data.get("workers", []))}')
    
    # Test approved workers
    print('\n2. Testing approved workers...')
    r = requests.get(f"{API}/admin/healthcare/workers/approved")
    data = r.json()
    print(f'Status: {r.status_code}')
    print(f'Data: {data}')
    
except Exception as e:
    print(f'Error: {e}')
