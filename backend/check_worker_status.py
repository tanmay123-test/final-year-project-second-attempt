import sqlite3
import os

DB_PATH = os.path.join("data", "housekeeping.db")

def check_worker_status():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT worker_id, is_online FROM worker_status WHERE worker_id=8")
        status = cursor.fetchone()
        if status:
            print(f"Worker 8: Online={status[1]}")
        else:
            print("Worker 8 status not found in housekeeping.db")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_worker_status()
