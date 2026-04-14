import requests

print("=== CHECKING ACTUAL SERVICE VALUES IN DATABASE ===")
print()

API_BASE = 'http://localhost:5000'

# Get all pending workers to see actual service values
response = requests.get(f'{API_BASE}/admin/workers/pending')
print(f"Getting all pending workers: Status {response.status_code}")

if response.status_code == 200:
    workers = response.json()
    print(f"Total pending workers: {len(workers)}")
    print()
    
    # Group by service values
    service_groups = {}
    for worker in workers:
        service = worker.get('service', 'unknown')
        if service not in service_groups:
            service_groups[service] = []
        service_groups[service].append(worker)
    
    print("Service values found:")
    for service, workers_list in service_groups.items():
        print(f"   '{service}': {len(workers_list)} workers")
        for worker in workers_list[:2]:  # Show first 2
            print(f"     - {worker.get('email')} (ID: {worker.get('id')})")
        if len(workers_list) > 2:
            print(f"     ... and {len(workers_list) - 2} more")
        print()
    
    # Now test different filter approaches
    print("Testing different filter approaches:")
    
    test_filters = [
        'housekeeping',
        'Housekeeping',
        '%housekeeping%',
        'housekeeping%',
    ]
    
    for filter_val in test_filters:
        response = requests.get(f'{API_BASE}/admin/workers/pending?service={filter_val}')
        if response.status_code == 200:
            filtered_workers = response.json()
            print(f"   Filter '{filter_val}': {len(filtered_workers)} workers")
        else:
            print(f"   Filter '{filter_val}': Error {response.status_code}")
    
    print()
    print("🔧 ANALYSIS:")
    print("   - Some workers have 'healthcare, housekeeping' (multiple services)")
    print("   - Some have 'housekeeping' (single service)")
    print("   - The filter needs to handle both cases")
    print()
    print("✅ SOLUTION:")
    print("   Change filter to: service ILIKE %housekeeping%")
    print("   This will match both 'housekeeping' and 'healthcare, housekeeping'")

else:
    print(f"Error: {response.json()}")
