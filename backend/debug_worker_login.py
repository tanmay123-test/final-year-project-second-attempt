from worker_db import WorkerDB

# Test the worker login function directly
worker_db = WorkerDB()
email = 'co2023.niharika.rothe@ves.ac.in'
password = '123456'

print(f"Testing login for: {email}")
result = worker_db.verify_worker_login(email, password)
print(f"Result: {result}")

# Also test without password
result_no_password = worker_db.verify_worker_login(email)
print(f"Result without password: {result_no_password}")
