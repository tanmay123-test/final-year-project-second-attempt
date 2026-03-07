from worker_db import WorkerDB

db = WorkerDB()
workers = db.get_all_workers()

print("Searching for 'goat' in worker names/emails...")
for w in workers:
    if 'goat' in w['name'].lower() or 'goat' in w['email'].lower():
        print(f"Found Worker: ID={w['id']}, Name={w['name']}, Email={w['email']}, Service={w['service']}")
