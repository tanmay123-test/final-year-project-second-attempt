import sqlite3
import os
from datetime import datetime

class CarMechanicsDB:
    def __init__(self, db_path="car_mechanics.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Mechanics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                specialization TEXT NOT NULL,
                experience INTEGER NOT NULL,
                service_center TEXT NOT NULL,
                location TEXT NOT NULL,
                rating REAL DEFAULT 0.0,
                consultation_fee INTEGER DEFAULT 300,
                status TEXT DEFAULT 'pending',
                online_status TEXT DEFAULT 'offline',
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add online_status column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE mechanics ADD COLUMN online_status TEXT DEFAULT 'offline'")
        except:
            pass  # Column already exists
        
        # Car services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                estimated_duration TEXT NOT NULL,
                base_price INTEGER NOT NULL,
                category TEXT NOT NULL
            )
        """)
        
        # Car appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mechanic_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                user_email TEXT NOT NULL,
                user_phone TEXT NOT NULL,
                car_model TEXT,
                car_issue TEXT NOT NULL,
                service_type TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_status TEXT DEFAULT 'pending',
                payment_amount INTEGER DEFAULT 0,
                consultation_fee INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mechanic_id) REFERENCES mechanics (id)
            )
        """)
        
        # Insert default car services
        cursor.execute('''
            INSERT OR IGNORE INTO car_services (name, description, estimated_duration, base_price, category)
            VALUES 
                ('General Service', 'Complete car check-up and basic maintenance', '2-3 hours', 500, 'Maintenance'),
                ('Oil Change', 'Engine oil replacement and filter check', '30 minutes', 200, 'Maintenance'),
                ('Brake Service', 'Brake pads replacement and system check', '1-2 hours', 800, 'Repair'),
                ('Engine Diagnostics', 'Complete engine scanning and analysis', '1 hour', 300, 'Diagnostics'),
                ('Tire Service', 'Tire rotation, balancing and replacement', '1-2 hours', 400, 'Maintenance'),
                ('AC Service', 'Air conditioning system check and repair', '2-3 hours', 600, 'Repair'),
                ('Battery Service', 'Battery testing and replacement', '30 minutes', 250, 'Maintenance')
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Car mechanics database initialized")
    
    def get_mechanics(self, status='approved'):
        """Get all mechanics by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM mechanics WHERE status = ?', (status,))
        mechanics = cursor.fetchall()
        conn.close()
        return mechanics
    
    def get_mechanic_by_id(self, mechanic_id):
        """Get mechanic by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM mechanics WHERE id = ?', (mechanic_id,))
        mechanic = cursor.fetchone()
        conn.close()
        return mechanic
    
    def update_mechanic_status(self, mechanic_id, new_status: str):
        """Update mechanic approval status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE mechanics SET status = ? WHERE id = ?', (new_status, mechanic_id))
        conn.commit()
        conn.close()
        return True
    
    def get_car_services(self):
        """Get all available car services"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM car_services')
        services = cursor.fetchall()
        conn.close()
        return services
    
    def create_car_appointment(self, user_id, mechanic_id, user_name, user_email, user_phone,
                           car_model, car_issue, service_type, booking_date, time_slot, consultation_fee):
        """Create a car service appointment"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO car_appointments (user_id, mechanic_id, user_name, user_email, user_phone,
                                         car_model, car_issue, service_type, booking_date, time_slot, consultation_fee)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, mechanic_id, user_name, user_email, user_phone,
                   car_model, car_issue, service_type, booking_date, time_slot, consultation_fee))
            
            appointment_id = cursor.lastrowid
            conn.commit()
            return appointment_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_car_appointments(self, status=None):
        """Get car appointments with optional status filter"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT ca.*, m.name as mechanic_name, m.specialization as mechanic_specialization
                FROM car_appointments ca
                JOIN mechanics m ON ca.mechanic_id = m.id
                WHERE ca.status = ?
                ORDER BY ca.created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT ca.*, m.name as mechanic_name, m.specialization as mechanic_specialization
                FROM car_appointments ca
                JOIN mechanics m ON ca.mechanic_id = m.id
                ORDER BY ca.created_at DESC
            ''')
        
        appointments = cursor.fetchall()
        conn.close()
        return appointments
    
    def update_car_appointment_status(self, appointment_id, new_status):
        """Update appointment status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE car_appointments SET status = ? WHERE id = ?', (new_status, appointment_id))
        conn.commit()
        conn.close()
        return True
    
    def add_mechanic(self, name, email, phone, specialization, experience, 
                   service_center, location, rating, consultation_fee, status, password):
        """Add a new mechanic to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO mechanics 
                (name, email, phone, specialization, experience, service_center, 
                 location, rating, consultation_fee, status, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, phone, specialization, experience, service_center,
                   location, rating, consultation_fee, status, password))
            
            conn.commit()
            mechanic_id = cursor.lastrowid
            conn.close()
            return mechanic_id if mechanic_id else None
        except sqlite3.IntegrityError:
            conn.close()
            return None
        except Exception as e:
            conn.close()
            raise e
    
    def update_mechanic_online_status(self, mechanic_id, online_status):
        """Update mechanic online status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE mechanics 
                SET online_status = ? 
                WHERE id = ?
            ''', (online_status, mechanic_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e
    
    def get_online_mechanics(self):
        """Get all online mechanics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM mechanics WHERE online_status = ? AND status = ?', ('online', 'approved'))
        mechanics = cursor.fetchall()
        conn.close()
        return mechanics

# Initialize database instance
car_mechanics_db = CarMechanicsDB()
