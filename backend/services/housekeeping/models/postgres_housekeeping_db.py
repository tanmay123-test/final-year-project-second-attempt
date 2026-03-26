"""
PostgreSQL Database for Housekeeping Service
This replaces the old SQLite version with proper PostgreSQL support
"""

import psycopg2
import psycopg2.extras
import os
from datetime import datetime
import logging

class PostgresHousekeepingDB:
    def __init__(self):
        # Use the same DATABASE_URL as other services
        self.database_url = os.environ.get('DATABASE_URL')
        self._tables_created = False

    def get_conn(self):
        """Get a new database connection"""
        try:
            if not self.database_url:
                # Fallback to SQLite if DATABASE_URL not set
                import sqlite3
                return sqlite3.connect("data/housekeeping.db")
            
            conn = psycopg2.connect(self.database_url, sslmode='require')
            conn.autocommit = False
            return conn
        except Exception as e:
            logging.error(f"Failed to connect to PostgreSQL: {e}")
            # Fallback to SQLite
            import sqlite3
            return sqlite3.connect("data/housekeeping.db")

    def _create_tables(self):
        """Create all necessary tables for housekeeping"""
        if self._tables_created:
            return
            
        conn = self.get_conn()
        cursor = conn.cursor()
        
        try:
            # Check if we're using PostgreSQL or SQLite
            is_postgresql = hasattr(conn, 'cursor') and 'psycopg2' in str(type(conn))
            
            if is_postgresql:
                self._create_postgres_tables(cursor)
            else:
                self._create_sqlite_tables(cursor)
            
            conn.commit()
            self._tables_created = True
            logging.info("Housekeeping tables created successfully")
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error creating housekeeping tables: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def _create_postgres_tables(self, cursor):
        """Create PostgreSQL tables"""
        # Services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS housekeeping_services (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                base_price DECIMAL(10,2) NOT NULL,
                duration_minutes INTEGER DEFAULT 60,
                category VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Other tables...
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS housekeeping_bookings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                worker_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                booking_date DATE NOT NULL,
                time_slot VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                total_amount DECIMAL(10,2) NOT NULL,
                address TEXT,
                phone VARCHAR(20),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default services
        cursor.execute("""
            INSERT INTO housekeeping_services (name, description, base_price, duration_minutes, category) 
            VALUES 
                ('Regular Cleaning', 'Basic house cleaning service', 500.00, 120, 'cleaning'),
                ('Deep Cleaning', 'Thorough deep cleaning service', 1200.00, 240, 'cleaning'),
                ('Kitchen Cleaning', 'Kitchen deep cleaning', 800.00, 180, 'cleaning')
            ON CONFLICT DO NOTHING
        """)

    def _create_sqlite_tables(self, cursor):
        """Create SQLite tables (fallback)"""
        # Services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS housekeeping_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                base_price REAL NOT NULL,
                duration_minutes INTEGER DEFAULT 60,
                category TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS housekeeping_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                worker_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                booking_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                total_amount REAL NOT NULL,
                address TEXT,
                phone TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default services
        cursor.execute("""
            INSERT OR IGNORE INTO housekeeping_services (name, description, base_price, duration_minutes, category) 
            VALUES 
                ('Regular Cleaning', 'Basic house cleaning service', 500.00, 120, 'cleaning'),
                ('Deep Cleaning', 'Thorough deep cleaning service', 1200.00, 240, 'cleaning'),
                ('Kitchen Cleaning', 'Kitchen deep cleaning', 800.00, 180, 'cleaning')
        """)

# Global instance (don't create tables on import)
postgres_housekeeping_db = PostgresHousekeepingDB()

def _row_to_dict(self, row, cursor):
    """Convert row to dictionary with column names"""
    if row is None:
        return None
    
    # Handle both PostgreSQL and SQLite
    if hasattr(cursor, 'description'):
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    else:
        # SQLite fallback
        return dict(zip(row.keys(), row)) if hasattr(row, 'keys') else {"data": row}

# Add method to class
PostgresHousekeepingDB._row_to_dict = _row_to_dict

# Additional methods for compatibility with existing booking service
def get_all_services_with_base(self):
    """Get all services with base pricing"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        # Check if we're using SQLite or PostgreSQL
        is_sqlite = not hasattr(conn, 'cursor') or 'psycopg2' not in str(type(conn))
        
        if is_sqlite:
            cursor.execute("""
                SELECT * FROM housekeeping_services 
                WHERE is_active = 1 
                ORDER BY category, name
            """)
        else:
            cursor.execute("""
                SELECT * FROM housekeeping_services 
                WHERE is_active = TRUE 
                ORDER BY category, name
            """)
        
        rows = cursor.fetchall()
        services = [self._row_to_dict(row, cursor) for row in rows]
        return services
    finally:
        cursor.close()
        conn.close()

def get_services_for_worker(self, worker_id):
    """Get services offered by a specific worker"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        # Check if we're using SQLite or PostgreSQL
        is_sqlite = not hasattr(conn, 'cursor') or 'psycopg2' not in str(type(conn))
        
        if is_sqlite:
            cursor.execute("""
                SELECT s.*, ws.price as worker_price, ws.is_available
                FROM housekeeping_services s
                LEFT JOIN housekeeping_worker_services ws ON s.id = ws.service_id AND ws.worker_id = ?
                WHERE s.is_active = 1
                ORDER BY s.category, s.name
            """, (worker_id,))
        else:
            cursor.execute("""
                SELECT s.*, ws.price as worker_price, ws.is_available
                FROM housekeeping_services s
                LEFT JOIN housekeeping_worker_services ws ON s.id = ws.service_id AND ws.worker_id = %s
                WHERE s.is_active = TRUE
                ORDER BY s.category, s.name
            """, (worker_id,))
        
        rows = cursor.fetchall()
        services = [self._row_to_dict(row, cursor) for row in rows]
        return services
    finally:
        cursor.close()
        conn.close()

def get_worker_online_status(self, worker_id):
    """Get worker's online status"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT is_available FROM housekeeping_worker_status 
            WHERE worker_id = %s
        """, (worker_id,))
        result = cursor.fetchone()
        return result[0] if result else False
    finally:
        cursor.close()
        conn.close()

# Add methods to the class
PostgresHousekeepingDB.get_all_services_with_base = get_all_services_with_base
PostgresHousekeepingDB.get_services_for_worker = get_services_for_worker
PostgresHousekeepingDB.get_worker_online_status = get_worker_online_status

def get_service_price(self, service_name):
    """Get base price for a service by name"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT base_price FROM housekeeping_services 
            WHERE name ILIKE %s AND is_active = TRUE
        """, (f"%{service_name}%",))
        result = cursor.fetchone()
        return result[0] if result else 500.0
    finally:
        cursor.close()
        conn.close()

def worker_offers_service(self, worker_id, service_name):
    """Check if worker offers a specific service"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM housekeeping_worker_services ws
            JOIN housekeeping_services s ON ws.service_id = s.id
            WHERE ws.worker_id = %s AND s.name ILIKE %s AND ws.is_available = TRUE
        """, (worker_id, f"%{service_name}%"))
        result = cursor.fetchone()
        return result[0] > 0
    finally:
        cursor.close()
        conn.close()

def create_booking_atomic(self, user_id, worker_id, service_id, booking_date, time_slot, total_amount, address=None, phone=None, notes=None):
    """Create a new booking atomically"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO housekeeping_bookings 
            (user_id, worker_id, service_id, booking_date, time_slot, total_amount, address, phone, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, worker_id, service_id, booking_date, time_slot, total_amount, address, phone, notes))
        booking_id = cursor.fetchone()[0]
        conn.commit()
        return booking_id, "Booking created successfully"
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cursor.close()
        conn.close()

def get_booking_by_id(self, booking_id):
    """Get booking details by ID"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.*, s.name as service_name, w.full_name as worker_name, u.name as user_name
            FROM housekeeping_bookings b
            JOIN housekeeping_services s ON b.service_id = s.id
            LEFT JOIN workers w ON b.worker_id = w.id
            LEFT JOIN users u ON b.user_id = u.id
            WHERE b.id = %s
        """, (booking_id,))
        result = cursor.fetchone()
        return self._row_to_dict(result, cursor) if result else None
    finally:
        cursor.close()
        conn.close()

def update_booking_status(self, booking_id, status, worker_id=None):
    """Update booking status"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        if worker_id:
            cursor.execute("""
                UPDATE housekeeping_bookings 
                SET status = %s, updated_at = CURRENT_TIMESTAMP, worker_id = %s
                WHERE id = %s
            """, (status, worker_id, booking_id))
        else:
            cursor.execute("""
                UPDATE housekeeping_bookings 
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (status, booking_id))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_bookings(self, user_id):
    """Get all bookings for a user"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.*, s.name as service_name, w.full_name as worker_name, w.phone as worker_phone
            FROM housekeeping_bookings b
            JOIN housekeeping_services s ON b.service_id = s.id
            LEFT JOIN workers w ON b.worker_id = w.id
            WHERE b.user_id = %s
            ORDER BY b.created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        return [self._row_to_dict(row, cursor) for row in rows]
    finally:
        cursor.close()
        conn.close()

def get_worker_bookings(self, worker_id):
    """Get all bookings for a worker"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.*, s.name as service_name, u.name as user_name, u.phone as user_phone
            FROM housekeeping_bookings b
            JOIN housekeeping_services s ON b.service_id = s.id
            LEFT JOIN users u ON b.user_id = u.id
            WHERE b.worker_id = %s
            ORDER BY b.created_at DESC
        """, (worker_id,))
        rows = cursor.fetchall()
        return [self._row_to_dict(row, cursor) for row in rows]
    finally:
        cursor.close()
        conn.close()

def set_worker_status(self, worker_id, is_available, location=None):
    """Set worker availability status"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO housekeeping_worker_status (worker_id, is_available, current_location)
            VALUES (%s, %s, %s)
            ON CONFLICT (worker_id) 
            DO UPDATE SET 
                is_available = EXCLUDED.is_available,
                current_location = COALESCE(EXCLUDED.current_location, housekeeping_worker_status.current_location),
                last_updated = CURRENT_TIMESTAMP
        """, (worker_id, is_available, location))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_worker_status(self, worker_id):
    """Get worker status"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        # Check if we're using SQLite or PostgreSQL
        is_sqlite = not hasattr(conn, 'cursor') or 'psycopg2' not in str(type(conn))
        
        if is_sqlite:
            cursor.execute("""
                SELECT is_available, current_location, last_updated 
                FROM housekeeping_worker_status 
                WHERE worker_id = ?
            """, (worker_id,))
        else:
            cursor.execute("""
                SELECT is_available, current_location, last_updated 
                FROM housekeeping_worker_status 
                WHERE worker_id = %s
            """, (worker_id,))
        
        result = cursor.fetchone()
        return self._row_to_dict(result, cursor) if result else None
    finally:
        cursor.close()
        conn.close()

def get_available_slots(self, service_name, date, worker_id=None):
    """Get available time slots for a service on a specific date"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        if worker_id:
            cursor.execute("""
                SELECT DISTINCT time_slot FROM housekeeping_time_slots
                WHERE worker_id = %s AND date = %s AND is_available = TRUE
                AND time_slot NOT IN (
                    SELECT time_slot FROM housekeeping_bookings 
                    WHERE worker_id = %s AND booking_date = %s AND status NOT IN ('CANCELLED', 'COMPLETED')
                )
                ORDER BY time_slot
            """, (worker_id, date, worker_id, date))
        else:
            # Get common available slots (9 AM to 8 PM)
            slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00', 
                    '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', 
                    '17:00-18:00', '18:00-19:00', '19:00-20:00']
            return slots
        
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    finally:
        cursor.close()
        conn.close()

def check_availability(self, worker_id, date, time_slot):
    """Check if a worker is available at a specific time"""
    conn = self.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM housekeeping_bookings 
            WHERE worker_id = %s AND booking_date = %s AND time_slot = %s 
            AND status NOT IN ('CANCELLED', 'COMPLETED')
        """, (worker_id, date, time_slot))
        result = cursor.fetchone()
        return result[0] == 0
    finally:
        cursor.close()
        conn.close()

# Add all methods to the class
PostgresHousekeepingDB.get_service_price = get_service_price
PostgresHousekeepingDB.worker_offers_service = worker_offers_service
PostgresHousekeepingDB.create_booking_atomic = create_booking_atomic
PostgresHousekeepingDB.get_booking_by_id = get_booking_by_id
PostgresHousekeepingDB.update_booking_status = update_booking_status
PostgresHousekeepingDB.get_user_bookings = get_user_bookings
PostgresHousekeepingDB.get_worker_bookings = get_worker_bookings
PostgresHousekeepingDB.set_worker_status = set_worker_status
PostgresHousekeepingDB.get_worker_status = get_worker_status
PostgresHousekeepingDB.get_available_slots = get_available_slots
PostgresHousekeepingDB.check_availability = check_availability
