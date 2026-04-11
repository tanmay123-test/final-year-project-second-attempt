import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE workers ADD COLUMN IF NOT EXISTS profile_photo_path TEXT")
    cursor.execute("ALTER TABLE workers ADD COLUMN IF NOT EXISTS aadhaar_path TEXT")
    cursor.execute("ALTER TABLE workers ADD COLUMN IF NOT EXISTS degree_certificate_path TEXT")
    cursor.execute("ALTER TABLE workers ADD COLUMN IF NOT EXISTS medical_license_path TEXT")
    conn.commit()
    print("Migration successful!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
