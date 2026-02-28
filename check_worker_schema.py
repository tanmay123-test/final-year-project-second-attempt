
import sqlite3
import os

db_path = 'd:/cdata13-04-2023/Downloads/ExpertEase/ExpertEase/data/workers.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(workers)')
columns = cursor.fetchall()
print("Workers Table Columns:")
for col in columns:
    print(col)

print("\nSample Data (First 3):")
cursor.execute('SELECT id, full_name, service, specialization FROM workers LIMIT 3')
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
