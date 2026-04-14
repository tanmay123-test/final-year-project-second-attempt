import requests

response = requests.get('http://localhost:5000/healthcare/doctors')
data = response.json()
print('API Response structure:')
print(f'Keys: {list(data.keys())}')
print(f'Doctors array type: {type(data.get("doctors"))}')
print(f'Number of doctors: {len(data.get("doctors", []))}')
if data.get('doctors'):
    print('First doctor keys:', list(data['doctors'][0].keys()))
    print('First doctor sample:', data['doctors'][0])
