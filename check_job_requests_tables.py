import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'car_service', 'job_requests.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables in job_requests.db:')
for table in tables:
    print(f'  {table[0]}')

conn.close()
