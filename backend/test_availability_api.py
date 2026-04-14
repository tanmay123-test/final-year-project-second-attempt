import requests

# Test availability for different doctors and dates
doctors = [5, 6, 7, 12]
dates = ['2026-04-13', '2026-04-14']

for doctor_id in doctors:
    print(f"\n=== Doctor {doctor_id} ===")
    for date in dates:
        try:
            response = requests.get(f'http://localhost:5000/healthcare/availability/{doctor_id}?date={date}')
            if response.status_code == 200:
                data = response.json()
                print(f"  {date}: {len(data.get('available_slots', []))} slots available")
                if data.get('available_slots'):
                    print(f"    First 3 slots: {data['available_slots'][:3]}")
            else:
                print(f"  {date}: Error {response.status_code}")
        except Exception as e:
            print(f"  {date}: Exception {e}")
