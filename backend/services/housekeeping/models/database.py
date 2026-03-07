import sqlite3
import os
from datetime import datetime
from config import HOUSEKEEPING_DB

class HousekeepingDatabase:
    def __init__(self, db_path=HOUSEKEEPING_DB):
        self.db_path = db_path
        self._create_tables()

    def get_conn(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        conn = self.get_conn()
        cursor = conn.cursor()

        # Services table (Categories)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            base_price REAL NOT NULL,
            description TEXT
        )
        """)

        # Seed default services if empty
        cursor.execute("SELECT count(*) FROM services")
        if cursor.fetchone()[0] == 0:
            default_services = [
                ("General Cleaning", 50.0, "Standard home cleaning service"),
                ("Deep Cleaning", 100.0, "Thorough deep cleaning service"),
                ("Bathroom Cleaning", 40.0, "Specialized bathroom cleaning"),
                ("Kitchen Cleaning", 60.0, "Intensive kitchen cleaning")
            ]
            cursor.executemany("INSERT INTO services (name, base_price, description) VALUES (?, ?, ?)", default_services)

        # Bookings table
        # user_id and worker_id are logical FKs to users.db and workers.db
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            worker_id INTEGER,
            service_type TEXT NOT NULL,
            address TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            price REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            rating INTEGER,
            review TEXT,
            home_size TEXT,
            add_ons TEXT,
            booking_type TEXT
        )
        """)
        # Migration: add user_hidden and user_accepted_at if missing
        try:
            cursor.execute("ALTER TABLE bookings ADD COLUMN user_hidden INTEGER DEFAULT 0")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE bookings ADD COLUMN user_accepted_at TEXT")
        except Exception:
            pass
        
        # Worker services configuration table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worker_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            price REAL NOT NULL,
            active INTEGER DEFAULT 1,
            UNIQUE(worker_id, service_id)
        )
        """)
        # Migration: add pricing_json if missing
        try:
            cursor.execute("ALTER TABLE worker_services ADD COLUMN pricing_json TEXT")
        except Exception:
            pass
        
        # Worker Status table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worker_status (
            worker_id INTEGER PRIMARY KEY,
            is_online INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Reminders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            booking_id INTEGER,
            reminder_type TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING', -- PENDING, SNOOZED, DISMISSED, SENT
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            snooze_until TEXT
        )
        """)
        
        conn.commit()
        conn.close()

    def _row_to_dict(self, row, cursor):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def set_worker_online(self, worker_id, is_online):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO worker_status (worker_id, is_online, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (worker_id, 1 if is_online else 0))
            conn.commit()
        finally:
            conn.close()

    def get_worker_online_status(self, worker_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT is_online FROM worker_status WHERE worker_id = ?", (worker_id,))
            row = cursor.fetchone()
            return bool(row[0]) if row else False # Default offline
        finally:
            conn.close()

    def create_booking(self, user_id, service_type, address, date, time, price, worker_id=None, status='PENDING'):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO bookings (user_id, service_type, address, booking_date, time_slot, price, status, worker_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, service_type, address, date, time, price, status, worker_id))
            booking_id = cursor.lastrowid
            conn.commit()
            return booking_id
        except Exception as e:
            print(f"Error creating booking: {e}")
            return None
        finally:
            conn.close()

    def create_booking_atomic(self, user_id, service_type, address, date, time, price, worker_id=None, status='PENDING', home_size=None, add_ons=None, booking_type=None):
        """
        Atomically create a booking, checking for conflicts if worker_id is provided.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            # If worker_id provided, check availability first
            if worker_id:
                query_check = """
                SELECT id FROM bookings 
                WHERE worker_id = ? AND booking_date = ? AND time_slot = ? 
                AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
                """
                cursor.execute(query_check, (worker_id, date, time))
                conflict = cursor.fetchone()
                if conflict:
                    return None, "Worker is already booked for this slot"

            cursor.execute("""
            INSERT INTO bookings (user_id, service_type, address, booking_date, time_slot, price, status, worker_id, home_size, add_ons, booking_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, service_type, address, date, time, price, status, worker_id, home_size, add_ons, booking_type))
            booking_id = cursor.lastrowid
            conn.commit()
            return booking_id, "Booking created"
        except Exception as e:
            return None, f"Database error: {str(e)}"
        finally:
            conn.close()

    def get_booking_by_id(self, booking_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return self._row_to_dict(row, cursor)
        return None

    def get_user_bookings(self, user_id, visible_only=True):
        conn = self.get_conn()
        cursor = conn.cursor()
        if visible_only:
            cursor.execute("SELECT * FROM bookings WHERE user_id = ? AND COALESCE(user_hidden, 0) = 0 ORDER BY created_at DESC", (user_id,))
        else:
            cursor.execute("SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_dict(row, cursor) for row in rows]

    def get_worker_bookings(self, worker_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE worker_id = ? ORDER BY booking_date DESC", (worker_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_dict(row, cursor) for row in rows]

    def get_available_bookings(self, service_type):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM bookings 
        WHERE status = 'PENDING' AND service_type = ? 
        ORDER BY booking_date ASC
        """, (service_type,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_dict(row, cursor) for row in rows]

    def update_booking_status(self, booking_id, status, worker_id=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            if worker_id and (status == 'ACCEPTED' or status == 'ASSIGNED'):
                cursor.execute("""
                UPDATE bookings 
                SET status = ?, worker_id = ? 
                WHERE id = ?
                """, (status, worker_id, booking_id))
            elif status == 'PENDING' and worker_id is None:
                 # Logic for resetting/reassigning failure
                 cursor.execute("""
                 UPDATE bookings
                 SET status = ?, worker_id = NULL
                 WHERE id = ?
                 """, (status, booking_id))
            elif status == 'COMPLETED':
                cursor.execute("""
                UPDATE bookings 
                SET status = ?, completed_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                """, (status, booking_id))
            else:
                cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating booking: {e}")
            return False
        finally:
            conn.close()

    def accept_booking_by_user(self, booking_id, user_id):
        """
        Mark a booking as accepted by the user and hide it from user's views.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE bookings
                SET user_hidden = 1, user_accepted_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (booking_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error accepting booking by user: {e}")
            return False
        finally:
            conn.close()

    def assign_worker_atomic(self, booking_id, worker_id, date, time, status='ASSIGNED'):
        """
        Atomically assign a worker to a booking if they are not already booked.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            # Check for conflict
            query_check = """
            SELECT id FROM bookings 
            WHERE worker_id = ? AND booking_date = ? AND time_slot = ? 
            AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
            AND id != ?
            """
            cursor.execute(query_check, (worker_id, date, time, booking_id))
            conflict = cursor.fetchone()
            
            if conflict:
                return False, "Worker is already booked for this slot"
            
            # Update booking
            query_update = """
            UPDATE bookings 
            SET status = ?, worker_id = ? 
            WHERE id = ?
            """
            cursor.execute(query_update, (status, worker_id, booking_id))
            
            if cursor.rowcount == 0:
                 return False, "Booking not found or update failed"
                 
            conn.commit()
            return True, "Worker assigned successfully"
        except Exception as e:
            print(f"Error in assign_worker_atomic: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            conn.close()

    def get_service_price(self, service_name):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT base_price FROM services WHERE name = ?", (service_name,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0.0

    def get_all_services(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM services")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_dict(row, cursor) for row in rows]

    # Worker Service Configuration
    def upsert_worker_services(self, worker_id, services):
        """
        Bulk upsert worker services.
        services: list of dicts {service_id: int, price: float, active: int}
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            for s in services:
                service_id = s.get('service_id')
                price = float(s.get('price', 0))
                active = 1 if s.get('active', 1) else 0
                pricing_json = s.get('pricing_json')
                cursor.execute("""
                    INSERT INTO worker_services (worker_id, service_id, price, active, pricing_json)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(worker_id, service_id) DO UPDATE SET
                        price=excluded.price,
                        active=excluded.active,
                        pricing_json=excluded.pricing_json
                """, (worker_id, service_id, price, active, pricing_json))
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB] upsert_worker_services error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_services_for_worker(self, worker_id):
        """
        Return list of services configured by the worker with pricing.
        [{id, name, description, price, active}]
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT s.id, s.name, s.description, ws.price, ws.active, ws.pricing_json
                FROM worker_services ws
                JOIN services s ON s.id = ws.service_id
                WHERE ws.worker_id = ?
                  AND ws.active = 1
                ORDER BY s.name ASC
            """, (worker_id,))
            rows = cursor.fetchall()
            return [
                {"id": r[0], "name": r[1], "description": r[2], "price": r[3], "active": bool(r[4]), "pricing_json": r[5]}
                for r in rows
            ]
        finally:
            conn.close()

    def get_all_services_with_base(self):
        """
        Return all services including base price with consistent keys.
        """
        base = self.get_all_services()
        # Normalize shape to include 'price' for UI defaults
        return [{"id": s["id"], "name": s["name"], "description": s["description"], "price": s["base_price"]} for s in base]

    def get_worker_service_price(self, worker_id, service_name):
        """
        Return worker-specific price for a given service name.
        Fallback to base price if worker has no override or not active.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, base_price FROM services WHERE name = ?", (service_name,))
            row = cursor.fetchone()
            if not row:
                return 0.0
            service_id, base_price = row[0], row[1]
            cursor.execute("""
                SELECT price FROM worker_services 
                WHERE worker_id = ? AND service_id = ? AND active = 1
            """, (worker_id, service_id))
            ws = cursor.fetchone()
            if ws:
                return ws[0]
            return base_price
        finally:
            conn.close()

    def worker_offers_service(self, worker_id, service_name):
        """
        Check if the worker has enabled a given service.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM services WHERE name = ?", (service_name,))
            row = cursor.fetchone()
            if not row:
                return False
            service_id = row[0]
            cursor.execute("""
                SELECT 1 FROM worker_services 
                WHERE worker_id = ? AND service_id = ? AND active = 1
            """, (worker_id, service_id))
            return cursor.fetchone() is not None
        finally:
            conn.close()


# Singleton instance
housekeeping_db = HousekeepingDatabase()
