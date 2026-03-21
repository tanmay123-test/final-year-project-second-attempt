import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class CarProfileDB:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS car_profiles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    city TEXT NOT NULL,
                    address TEXT NOT NULL,
                    emergency_contact_name TEXT NOT NULL,
                    emergency_contact_phone TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_cars (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    fuel_type TEXT NOT NULL,
                    registration_number TEXT NOT NULL,
                    is_default INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def create_car_profile(self, user_id, city, address, emergency_name, emergency_phone):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            # PostgreSQL equivalent of INSERT OR REPLACE using ON CONFLICT
            cur.execute(
                """
                INSERT INTO car_profiles (user_id, city, address, emergency_contact_name, emergency_contact_phone)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    city = EXCLUDED.city,
                    address = EXCLUDED.address,
                    emergency_contact_name = EXCLUDED.emergency_contact_name,
                    emergency_contact_phone = EXCLUDED.emergency_contact_phone
                """,
                (user_id, city, address, emergency_name, emergency_phone),
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def get_car_profile(self, user_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM car_profiles WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def profile_exists(self, user_id):
        return self.get_car_profile(user_id) is not None

    def add_car(self, user_id, brand, model, year, fuel, reg, set_default=False):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            if set_default:
                cur.execute("UPDATE user_cars SET is_default=0 WHERE user_id=%s", (user_id,))
            
            cur.execute(
                """
                INSERT INTO user_cars (user_id, brand, model, year, fuel_type, registration_number, is_default)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (user_id, brand, model, year, fuel, reg, 1 if set_default else 0),
            )
            car_id = cur.fetchone()[0]
            conn.commit()
            return car_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def get_user_cars(self, user_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(
                "SELECT * FROM user_cars WHERE user_id=%s ORDER BY is_default DESC, created_at DESC",
                (user_id,),
            )
            rows = [dict(r) for r in cur.fetchall()]
            return rows
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def get_default_car(self, user_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(
                "SELECT * FROM user_cars WHERE user_id=%s AND is_default=1 ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            )
            row = cur.fetchone()
            if row:
                return dict(row)
            
            cur.execute(
                "SELECT * FROM user_cars WHERE user_id=%s ORDER BY created_at DESC LIMIT 1",
                (user_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def set_default_car(self, user_id, car_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            cur.execute("UPDATE user_cars SET is_default=0 WHERE user_id=%s", (user_id,))
            cur.execute("UPDATE user_cars SET is_default=1 WHERE id=%s AND user_id=%s", (car_id, user_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def get_car_by_id(self, car_id):
        """Get car information by car ID"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM user_cars WHERE id=%s", (car_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def update_profile(self, user_id, city, address, emergency_name, emergency_phone):
        """Update user car service profile"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE car_profiles 
                SET city=%s, address=%s, emergency_contact_name=%s, emergency_contact_phone=%s
                WHERE user_id=%s
                """,
                (city, address, emergency_name, emergency_phone, user_id)
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

car_profile_db = CarProfileDB()
