
import sqlite3
db_path = 'd:/cdata13-04-2023/Downloads/ExpertEase/ExpertEase/data/workers.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT * FROM workers WHERE id=22')
row = cursor.fetchone()
print(row)
conn.close()
