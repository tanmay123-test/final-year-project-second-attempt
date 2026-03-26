import os
import psycopg2
from dotenv import load_dotenv

def check_user():
    database_url = "postgresql://postgres.hfilbrunntrfpvxrbazy:Tan12may34567890@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
    if not database_url:
        print("DATABASE_URL not found in environment")
        return

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        email = 'tanmaybansode48@gmail.com'
        
        print(f"Checking for email: {email}")
        
        # Check mechanics table
        try:
            cur.execute("SELECT id, name, email, status, role, password_hash FROM mechanics WHERE email = %s", (email,))
            print('Mechanics table result:', cur.fetchone())
        except Exception as e:
            print(f"Error checking mechanics table: {e}")
            conn.rollback()

        # Check car_service_workers table
        try:
            cur.execute("SELECT id, name, email, status, role, password_hash FROM car_service_workers WHERE email = %s", (email,))
            print('Car service workers table result:', cur.fetchone())
        except Exception as e:
            print(f"Error checking car_service_workers table: {e}")
            conn.rollback()

        # Check workers table
        try:
            cur.execute("SELECT id, name, email, status, role FROM workers WHERE email = %s", (email,))
            print('Workers table result:', cur.fetchone())
        except Exception as e:
            print(f"Error checking workers table: {e}")
            conn.rollback()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    check_user()
