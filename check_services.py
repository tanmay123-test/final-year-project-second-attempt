import sqlite3
import os

DB_PATH = os.path.join("data", "housekeeping.db")

def check_services():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM services")
        services = cursor.fetchall()
        print("Available Services:")
        for s in services:
            print(f"- {s[0]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_services()
