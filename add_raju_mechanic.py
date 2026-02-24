import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('car_service.db')
cursor = conn.cursor()

# Add Raju Mechanic as a worker
print("🔧 ADDING 'RAJU MECHANIC' TO DATABASE")
print("=" * 50)

# Insert into workers table (if it exists)
try:
    cursor.execute("""
        INSERT INTO workers (
            username, email, password, phone, address, city, 
            worker_type, specialization, experience_years, 
            rating, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "raju_mechanic",           # username
        "raju@mechanic.com",       # email
        "password123",              # password (hashed in real app)
        "9876543210",             # phone
        "123 Main Street, Delhi",    # address
        "Delhi",                  # city
        "MECHANIC",                # worker_type
        "General Repairs",          # specialization
        5,                         # experience_years
        4.5,                       # rating
        "ACTIVE",                  # status
        datetime.now().isoformat()  # created_at
    ))
    print("✅ Added to workers table")
except Exception as e:
    print(f"⚠️ Workers table error: {e}")

# Add to worker_metrics table
try:
    cursor.execute("""
        INSERT INTO worker_metrics (
            worker_id, total_jobs, completed_jobs, 
            cancelled_jobs, avg_rating, total_earnings,
            acceptance_rate, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        1,                          # worker_id
        25,                          # total_jobs
        23,                          # completed_jobs
        2,                           # cancelled_jobs
        4.5,                         # avg_rating
        15000.00,                    # total_earnings
        0.92,                         # acceptance_rate
        datetime.now().isoformat(),  # created_at
        datetime.now().isoformat()   # updated_at
    ))
    print("✅ Added to worker_metrics table")
except Exception as e:
    print(f"⚠️ Worker metrics error: {e}")

# Add live location for Raju
try:
    cursor.execute("""
        INSERT INTO mechanic_live_locations (
            worker_id, latitude, longitude, last_updated, 
            worker_type, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        1,                          # worker_id
        28.6139,                    # latitude (Delhi)
        77.2090,                     # longitude (Delhi)
        datetime.now().isoformat(),  # last_updated
        "MECHANIC",                  # worker_type
        datetime.now().isoformat()   # created_at
    ))
    print("✅ Added to mechanic_live_locations table")
except Exception as e:
    print(f"⚠️ Live location error: {e}")

# Commit changes
conn.commit()
conn.close()

print("\n🎉 'RAJU MECHANIC' added successfully!")
print("📊 Database Summary:")
print("   👨‍🔧 Worker ID: 1")
print("   📱 Phone: 9876543210")
print("   📍 Location: Delhi (28.6139, 77.2090)")
print("   ⭐ Rating: 4.5/5.0")
print("   🔧 Experience: 5 years")
print("   💰 Total Earnings: ₹15,000")
print("   📊 Jobs Completed: 23/25")

print("\n🚀 Now test the Uber-style dispatch:")
print("   1. Run: python cli.py")
print("   2. User → Car Services → Find Mechanics")
print("   3. Enter location and issue")
print("   4. See 'Raju Mechanic' in top candidates!")
