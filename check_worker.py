import sqlite3
import os

DB_PATH = os.path.join("data", "workers.db")

def check_worker():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, service, specialization, clinic_location FROM workers WHERE id=8")
        worker = cursor.fetchone()
        if worker:
            print(f"Worker 8: Service={worker[1]}, Spec={worker[2]}, Location={worker[3]}")
        else:
            print("Worker 8 not found")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_worker()
