from worker_db import WorkerDB

db = WorkerDB()
email = 'trunika24@gmail.com'
conn = db.get_conn()
cursor = conn.cursor()
cursor.execute("SELECT * FROM workers WHERE email = ?", (email,))
workers = cursor.fetchall()
print(f"Workers with email {email}: {len(workers)}")
for w in workers:
        # Access row fields by name if it's a sqlite3.Row or similar
        try:
            # Try to convert to dict (works for sqlite3.Row)
            w_dict = dict(w)
        except:
            # If it's a plain tuple, we need to know the column order or just print raw
            # Assuming typical order: id, name, email, ..., service_type, ...
            # Let's just print the tuple if dict fails
            w_dict = {'raw': str(w)}
            
        if 'raw' in w_dict:
             print(f"Worker (Tuple): {w_dict['raw']}")
        else:
             print(f"ID: {w_dict.get('id')}, Name: {w_dict.get('name')}, Email: {w_dict.get('email')}, Service: {w_dict.get('service_type')}")
