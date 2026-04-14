import requests

print("=== TESTING CASE-INSENSITIVE FIX ===")
print()

API_BASE = 'http://localhost:5000'

test_filters = ['housekeeping', 'Housekeeping', 'HOUSEKEEPING']

for filter_val in test_filters:
    response = requests.get(f'{API_BASE}/admin/workers/pending?service={filter_val}')
    print(f"Filter '{filter_val}': Status {response.status_code}")
    
    if response.status_code == 200:
        workers = response.json()
        print(f"  Workers found: {len(workers)}")
        
        if workers:
            print("  Sample workers:")
            for worker in workers[:3]:
                print(f"    - {worker.get('email')} (Service: {worker.get('service')})")
    else:
        print(f"  Error: {response.json()}")
    print()

print("🎯 CASE-INSENSITIVE FILTER TEST COMPLETE!")
