print("=== HEALTHCARE SYSTEM DIAGNOSTIC ===")
print()

# Check 1: Backend syntax
print("1. Checking backend syntax...")
try:
    import app
    print("   ✅ Backend syntax is OK")
except Exception as e:
    print(f"   ❌ Backend syntax error: {e}")

# Check 2: Database connection and healthcare workers
print("\n2. Checking healthcare workers in database...")
try:
    import os
    import psycopg2
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM workers WHERE service='healthcare' AND status='approved'")
    count = cursor.fetchone()[0]
    print(f"   ✅ Found {count} approved healthcare workers")
    
    if count > 0:
        cursor.execute("SELECT id, full_name, email FROM workers WHERE service='healthcare' AND status='approved' LIMIT 3")
        workers = cursor.fetchall()
        for worker in workers:
            print(f"      - {worker[1]} (ID: {worker[0]})")
    
    conn.close()
except Exception as e:
    print(f"   ❌ Database error: {e}")

# Check 3: Required files exist
print("\n3. Checking required files...")
import os
files_to_check = [
    '../frontend/src/services/healthcare/pages/BookAppointment.jsx',
    '../frontend/src/services/healthcare/pages/HealthcareDashboard.jsx',
    '../frontend/src/services/healthcare/worker_portal/WorkerDashboardPage.jsx',
    'app.py'
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"   ✅ {file_path}")
    else:
        print(f"   ❌ {file_path} missing")

# Check 4: API endpoints (if server is running)
print("\n4. Checking API endpoints...")
try:
    import requests
    response = requests.get('http://localhost:5000/healthcare/doctors', timeout=2)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ /healthcare/doctors working - {len(data.get('doctors', []))} doctors")
    else:
        print(f"   ❌ /healthcare/doctors returned {response.status_code}")
except:
    print("   ⚠️  Server not running or not accessible")

print("\n=== DIAGNOSTIC COMPLETE ===")
print("\nIf you see issues above, please tell me which specific problem you're experiencing!")
