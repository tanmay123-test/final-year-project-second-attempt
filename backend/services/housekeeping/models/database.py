import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

class HousekeepingDatabase:
    def __init__(self):
        self._create_tables()

    def get_conn(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        conn.autocommit = False
        return conn

    def _create_tables(self):
        load_dotenv()
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            # Services table (Categories)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                base_price FLOAT NOT NULL,
                description TEXT
            )
            """)

            # Seed default services if empty
            cursor.execute("SELECT count(*) FROM services")
            if cursor.fetchone()[0] == 0:
                default_services = [
                    ("General Cleaning", 500.0, "Standard home cleaning service"),
                    ("Deep Cleaning", 1000.0, "Thorough deep cleaning service"),
                    ("Bathroom Cleaning", 400.0, "Specialized bathroom cleaning"),
                    ("Kitchen Cleaning", 600.0, "Intensive kitchen cleaning")
                ]
                psycopg2.extras.execute_batch(cursor, "INSERT INTO services (name, base_price, description) VALUES (%s, %s, %s)", default_services)

            # Bookings table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                worker_id INTEGER,
                service_type TEXT NOT NULL,
                address TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                price FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                rating INTEGER,
                review TEXT,
                home_size TEXT,
                add_ons TEXT,
                booking_type TEXT,
                user_hidden BOOLEAN DEFAULT FALSE,
                user_accepted_at TIMESTAMP,
                otp TEXT,
                started_at TEXT,
                retry_count INTEGER DEFAULT 0
            )
            """)
            
            # Worker services configuration table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker_services (
                id SERIAL PRIMARY KEY,
                worker_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                price FLOAT NOT NULL,
                active BOOLEAN DEFAULT TRUE,
                pricing_json TEXT,
                UNIQUE(worker_id, service_id)
            )
            """)
            
            # Worker Status table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker_status (
                worker_id INTEGER PRIMARY KEY,
                is_online BOOLEAN DEFAULT FALSE,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Reminders table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                booking_id INTEGER,
                reminder_type TEXT NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING', -- PENDING, SNOOZED, DISMISSED, SENT
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                snooze_until TEXT
            )
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def set_worker_online(self, worker_id, is_online):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO worker_status (worker_id, is_online, last_updated)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (worker_id) DO UPDATE SET
            is_online = EXCLUDED.is_online,
            last_updated = EXCLUDED.last_updated
            """, (worker_id, is_online))
            conn.commit()
        except Exception as e:
            print(f"DB Error set_worker_online: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_worker_online_status(self, worker_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT is_online FROM worker_status WHERE worker_id = %s", (worker_id,))
            row = cursor.fetchone()
            return bool(row[0]) if row else False
        except Exception as e:
            print(f"DB Error get_worker_online_status: {e}")
            return False
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def create_booking(self, user_id, service_type, address, date, time, price, worker_id=None, status='PENDING'):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO bookings (user_id, service_type, address, booking_date, time_slot, price, status, worker_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (user_id, service_type, address, date, time, price, status, worker_id))
            booking_id = cursor.fetchone()[0]
            conn.commit()
            return booking_id
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"Error creating booking: {e}")
            return None
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

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
                WHERE worker_id = %s AND booking_date = %s AND time_slot = %s 
                AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
                """
                cursor.execute(query_check, (worker_id, date, time))
                conflict = cursor.fetchone()
                if conflict:
                    return None, "Worker is already booked for this slot"

            cursor.execute("""
            INSERT INTO bookings (user_id, service_type, address, booking_date, time_slot, price, status, worker_id, home_size, add_ons, booking_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (user_id, service_type, address, date, time, price, status, worker_id, home_size, add_ons, booking_type))
            booking_id = cursor.fetchone()[0]
            conn.commit()
            return booking_id, "Booking created"
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            return None, f"Database error: {str(e)}"
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_booking_by_id(self, booking_id):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"DB Error: {e}")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_user_bookings(self, user_id, visible_only=True):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if visible_only:
                cursor.execute("SELECT * FROM bookings WHERE user_id = %s AND COALESCE(user_hidden, FALSE) = FALSE ORDER BY created_at DESC", (user_id,))
            else:
                cursor.execute("SELECT * FROM bookings WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"DB Error: {e}")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_worker_bookings(self, worker_id):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM bookings WHERE worker_id = %s ORDER BY booking_date DESC", (worker_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"DB Error: {e}")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_available_bookings(self, service_type):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
            SELECT * FROM bookings 
            WHERE status = 'PENDING' AND service_type = %s 
            ORDER BY booking_date ASC
            """, (service_type,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"DB Error: {e}")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def update_booking_status(self, booking_id, status, worker_id=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            if worker_id and (status == 'ACCEPTED' or status == 'ASSIGNED'):
                cursor.execute("""
                UPDATE bookings 
                SET status = %s, worker_id = %s 
                WHERE id = %s
                """, (status, worker_id, booking_id))
            elif status == 'PENDING' and worker_id is None:
                 cursor.execute("""
                 UPDATE bookings
                 SET status = %s, worker_id = NULL
                 WHERE id = %s
                 """, (status, booking_id))
            elif status == 'COMPLETED':
                cursor.execute("""
                UPDATE bookings 
                SET status = %s, completed_at = CURRENT_TIMESTAMP 
                WHERE id = %s
                """, (status, booking_id))
            else:
                cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", (status, booking_id))
            
            conn.commit()
            return True
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"Error updating booking: {e}")
            return False
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def accept_booking_by_user(self, booking_id, user_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE bookings
                SET user_hidden = TRUE, user_accepted_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
            """, (booking_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"Error accepting booking by user: {e}")
            return False
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def assign_worker_atomic(self, booking_id, worker_id, date, time, status='ASSIGNED'):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            query_check = """
            SELECT id FROM bookings 
            WHERE worker_id = %s AND booking_date = %s AND time_slot = %s 
            AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
            AND id != %s
            """
            cursor.execute(query_check, (worker_id, date, time, booking_id))
            conflict = cursor.fetchone()
            if conflict:
                return False, "Worker is already booked for this slot"
            query_update = """
            UPDATE bookings 
            SET status = %s, worker_id = %s 
            WHERE id = %s
            """
            cursor.execute(query_update, (status, worker_id, booking_id))
            if cursor.rowcount == 0:
                return False, "Booking not found or update failed"
            conn.commit()
            return True, "Worker assigned successfully"
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"Error in assign_worker_atomic: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_service_price(self, service_name):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT base_price FROM services WHERE name = %s", (service_name,))
            row = cursor.fetchone()
            return row[0] if row else 0.0
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"DB Error: {e}")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_all_services(self):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM services")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"DB Error: {e}")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    # Worker Service Configuration
    def upsert_worker_services(self, worker_id, services):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            for s in services:
                service_id = s.get('service_id')
                price = float(s.get('price', 0))
                active = bool(s.get('active', True))
                pricing_json = s.get('pricing_json')
                cursor.execute("""
                    INSERT INTO worker_services (worker_id, service_id, price, active, pricing_json)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT(worker_id, service_id) DO UPDATE SET
                        price=EXCLUDED.price,
                        active=EXCLUDED.active,
                        pricing_json=EXCLUDED.pricing_json
                """, (worker_id, service_id, price, active, pricing_json))
            conn.commit()
            return True
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"[DB] upsert_worker_services error: {e}")
            return False
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_services_for_worker(self, worker_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT s.id, s.name, s.description, ws.price, ws.active, ws.pricing_json
                FROM worker_services ws
                JOIN services s ON s.id = ws.service_id
                WHERE ws.worker_id = %s
                  AND ws.active = TRUE
                ORDER BY s.name ASC
            """, (worker_id,))
            rows = cursor.fetchall()
            return [
                {"id": r[0], "name": r[1], "description": r[2], "price": r[3], "active": bool(r[4]), "pricing_json": r[5]}
                for r in rows
            ]
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"DB Error: {e}")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_all_services_with_base(self):
        base = self.get_all_services()
        result = []
        for s in base:
            result.append({
                "id": s["id"],
                "name": s["name"],
                "description": s["description"],
                "price": s["base_price"],
                "available_count": 0
            })
        # If table was empty, seed defaults and retry
        if not result:
            self._seed_default_services()
            base = self.get_all_services()
            for s in base:
                result.append({
                    "id": s["id"],
                    "name": s["name"],
                    "description": s["description"],
                    "price": s["base_price"],
                    "available_count": 0
                })
        return result

    def _seed_default_services(self):
        """Ensure default services exist in the services table."""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            default_services = [
                ("General Cleaning", 500.0, "Standard home cleaning service"),
                ("Deep Cleaning", 1000.0, "Thorough deep cleaning service"),
                ("Bathroom Cleaning", 400.0, "Specialized bathroom cleaning"),
                ("Kitchen Cleaning", 600.0, "Intensive kitchen cleaning")
            ]
            for name, price, desc in default_services:
                cursor.execute("""
                    INSERT INTO services (name, base_price, description)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, (name, price, desc))
            conn.commit()
            print("[DB] Default services seeded successfully")
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"[DB] Error seeding services: {e}")
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def get_worker_service_price(self, worker_id, service_name):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, base_price FROM services WHERE name = %s", (service_name,))
            row = cursor.fetchone()
            if not row:
                return 0.0
            service_id, base_price = row[0], row[1]
            cursor.execute("""
                SELECT price FROM worker_services 
                WHERE worker_id = %s AND service_id = %s AND active = TRUE
            """, (worker_id, service_id))
            ws = cursor.fetchone()
            if ws:
                return ws[0]
            return base_price
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"DB Error: {e}")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    def worker_offers_service(self, worker_id, service_name):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT count(*) FROM worker_services WHERE worker_id = %s", (worker_id,))
            has_config = cursor.fetchone()[0] > 0
            if not has_config:
                return True
            cursor.execute("SELECT id FROM services WHERE name = %s", (service_name,))
            row = cursor.fetchone()
            if not row:
                return False
            service_id = row[0]
            cursor.execute("""
                SELECT 1 FROM worker_services 
                WHERE worker_id = %s AND service_id = %s AND active = TRUE
            """, (worker_id, service_id))
            return cursor.fetchone() is not None
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"DB Error: {e}")
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass


# Singleton instance
housekeeping_db = HousekeepingDatabase()
