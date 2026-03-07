import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "car_profiles.db")

class CarProfileDB:
    def __init__(self):
        self._init_db()

    def _conn(self):
        return sqlite3.connect(DB_PATH)

    def _init_db(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS car_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        conn.close()

    def create_car_profile(self, user_id, city, address, emergency_name, emergency_phone):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO car_profiles (user_id, city, address, emergency_contact_name, emergency_contact_phone)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, city, address, emergency_name, emergency_phone),
        )
        conn.commit()
        conn.close()
        return True

    def get_car_profile(self, user_id):
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM car_profiles WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def profile_exists(self, user_id):
        return self.get_car_profile(user_id) is not None

    def add_car(self, user_id, brand, model, year, fuel, reg, set_default=False):
        conn = self._conn()
        cur = conn.cursor()
        if set_default:
            cur.execute("UPDATE user_cars SET is_default=0 WHERE user_id=?", (user_id,))
        cur.execute(
            """
            INSERT INTO user_cars (user_id, brand, model, year, fuel_type, registration_number, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, brand, model, year, fuel, reg, 1 if set_default else 0),
        )
        car_id = cur.lastrowid
        conn.commit()
        conn.close()
        return car_id

    def get_user_cars(self, user_id):
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM user_cars WHERE user_id=? ORDER BY is_default DESC, created_at DESC",
            (user_id,),
        )
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_default_car(self, user_id):
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM user_cars WHERE user_id=? AND is_default=1 ORDER BY created_at DESC LIMIT 1",
            (user_id,),
        )
        row = cur.fetchone()
        if row:
            conn.close()
            return dict(row)
        cur.execute(
            "SELECT * FROM user_cars WHERE user_id=? ORDER BY created_at DESC LIMIT 1",
            (user_id,),
        )
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def set_default_car(self, user_id, car_id):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("UPDATE user_cars SET is_default=0 WHERE user_id=?", (user_id,))
        cur.execute("UPDATE user_cars SET is_default=1 WHERE id=? AND user_id=?", (car_id, user_id))
        conn.commit()
        conn.close()
        return True

    def get_car_by_id(self, car_id):
        """Get car information by car ID"""
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_cars WHERE id=?", (car_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_profile(self, user_id, city, address, emergency_name, emergency_phone):
        """Update user car service profile"""
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE car_profiles 
            SET city=?, address=?, emergency_contact_name=?, emergency_contact_phone=?
            WHERE user_id=?
            """,
            (city, address, emergency_name, emergency_phone, user_id)
        )
        conn.commit()
        conn.close()
        return cur.rowcount > 0

car_profile_db = CarProfileDB()
