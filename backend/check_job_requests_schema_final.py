import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'car_service', 'job_requests.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(job_requests)')
columns = cursor.fetchall()
print('job_requests table schema with NULL constraints:')
for col in columns:
    col_name, col_type, not_null, default_val = col
    if not_null == 0:  # NOT NULL constraint
        print(f'  ❌ {col_name}: {col_type} - NOT NULL (default: {default_val})')
    else:
        print(f'  ✅ {col_name}: {col_type} - NULL allowed')

conn.close()
