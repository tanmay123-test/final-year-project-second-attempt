"""
Tow Truck Operator Database
Manages tow truck operator authentication, profiles, and requests
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Optional

load_dotenv()

class TowTruckDB:
    def __init__(self):
        self.init_db()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def init_db(self):
        """Initialize tow truck operators database"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            # Create tow_truck_operators table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_truck_operators (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    city TEXT NOT NULL,
                    experience TEXT NOT NULL,
                    truck_type TEXT NOT NULL,
                    truck_registration TEXT NOT NULL,
                    truck_model TEXT NOT NULL,
                    truck_capacity TEXT NOT NULL,
                    license_path TEXT,
                    insurance_path TEXT,
                    fitness_cert_path TEXT,
                    pollution_cert_path TEXT,
                    is_online INTEGER DEFAULT 0,
                    approval_status TEXT DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create tow_requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_requests (
                    id SERIAL PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    customer_address TEXT NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    issue_description TEXT,
                    operator_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    amount REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (operator_id) REFERENCES tow_truck_operators(id)
                )
            ''')
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def register_operator(self, operator_data):
        """Register a new tow truck operator"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO tow_truck_operators 
                (name, email, phone, password_hash, city, experience, truck_type, 
                 truck_registration, truck_model, truck_capacity, license_path,
                 insurance_path, fitness_cert_path, pollution_cert_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                operator_data['name'],
                operator_data['email'],
                operator_data['phone'],
                operator_data['password_hash'],
                operator_data['city'],
                operator_data['experience'],
                operator_data['truck_type'],
                operator_data['truck_registration'],
                operator_data['truck_model'],
                operator_data['truck_capacity'],
                operator_data.get('license_path'),
                operator_data.get('insurance_path'),
                operator_data.get('fitness_cert_path'),
                operator_data.get('pollution_cert_path')
            ))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_operator_by_email(self, email):
        """Get operator by email"""
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM tow_truck_operators WHERE email = %s", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update_operator_status(self, operator_id, is_online):
        """Update operator online status"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE tow_truck_operators 
                SET is_online = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (1 if is_online else 0, operator_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

# Create singleton instance
tow_truck_db = TowTruckDB()