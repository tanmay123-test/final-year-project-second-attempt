import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'data', 'workers.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('SELECT email FROM workers WHERE id=8')
row = c.fetchone()
if row:
    print(row[0])
else:
    print("Worker 8 not found")
conn.close()
