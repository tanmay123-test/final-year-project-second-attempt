import sqlite3
from config import WORKER_DB

def migrate():
    conn = sqlite3.connect(WORKER_DB)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN license_number TEXT")
        print("Added license_number column")
    except sqlite3.OperationalError as e:
        print(f"license_number column might already exist: {e}")
        
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN password TEXT")
        print("Added password column")
    except sqlite3.OperationalError as e:
        print(f"password column might already exist: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
