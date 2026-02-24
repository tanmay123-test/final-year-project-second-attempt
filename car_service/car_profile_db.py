import sqlite3
import os
from datetime import datetime

class CarProfileDB:
    def __init__(self, db_path="car_profiles.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Car profiles table - linked to main users (no FK constraint due to separate DB files)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                city TEXT NOT NULL,
                default_address TEXT NOT NULL,
                emergency_contact_name TEXT NOT NULL,
                emergency_contact_phone TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User cars table - multiple cars per user
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                car_brand TEXT NOT NULL,
                car_model TEXT NOT NULL,
                manufacturing_year INTEGER NOT NULL,
                fuel_type TEXT NOT NULL,
                registration_number TEXT NOT NULL,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Car profile database initialized")
    
    def check_car_profile_exists(self, user_id):
        """Check if user already has a car profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM car_profiles WHERE user_id = ?', (user_id,))
        profile = cursor.fetchone()
        conn.close()
        return profile is not None
    
    def create_car_profile(self, user_id, city, default_address, 
                          emergency_contact_name, emergency_contact_phone):
        """Create car profile for existing user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO car_profiles (user_id, city, default_address, 
                                     emergency_contact_name, emergency_contact_phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, city, default_address, emergency_contact_name, emergency_contact_phone))
            
            profile_id = cursor.lastrowid
            conn.commit()
            return profile_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_car_profile(self, user_id):
        """Get car profile for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM car_profiles WHERE user_id = ?', (user_id,))
        profile = cursor.fetchone()
        conn.close()
        return profile
    
    def add_user_car(self, user_id, car_brand, car_model, manufacturing_year, 
                    fuel_type, registration_number, is_default=False):
        """Add a car for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_cars (user_id, car_brand, car_model, manufacturing_year, 
                                     fuel_type, registration_number, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, car_brand, car_model, manufacturing_year, 
                   fuel_type, registration_number, is_default))
            
            car_id = cursor.lastrowid
            conn.commit()
            return car_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_user_cars(self, user_id):
        """Get all cars for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_cars WHERE user_id = ? ORDER BY is_default DESC, created_at DESC', (user_id,))
        cars = cursor.fetchall()
        conn.close()
        return cars

# Initialize database instance
car_profile_db = CarProfileDB()
