#!/usr/bin/env python3
"""
Central Database Manager for All Services
Provides unified access to organized database structure
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    """Central database manager for all services"""
    
    def __init__(self, base_path=None):
        """Initialize database manager"""
        if base_path is None:
            # Use the absolute path to the backend/data directory
            base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "data"
        self.base_path = Path(base_path)
        
        # Database paths - Updated to match actual flat structure in backend/data
        self.databases = {
            'users': self.base_path / "users.db",
            'workers': self.base_path / "workers.db",
            'healthcare': self.base_path / "healthcare.db",
            'housekeeping': self.base_path / "housekeeping.db",
            'freelance': self.base_path / "freelance.db",
            'money_management': self.base_path / "money_management.db",
            'car_service': self.base_path / "car_profiles.db", # Use car_profiles.db for car service profile
            'mechanics': self.base_path / "car_mechanics.db",
            'fuel_delivery': self.base_path / "car_fuel_delivery.db",
            'tow_truck': self.base_path / "car_truck_operators.db"
        }
        
        # Ensure all databases exist
        self._ensure_databases_exist()
    
    def _ensure_databases_exist(self):
        """Ensure all database files exist"""
        for db_name, db_path in self.databases.items():
            if not db_path.exists():
                print(f"    Database {db_name} not found at {db_path}")
    
    @contextmanager
    def get_connection(self, db_type):
        """Get database connection with automatic cleanup"""
        if db_type not in self.databases:
            raise ValueError(f"Unknown database type: {db_type}")
        
        db_path = self.databases[db_type]
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    # User Management Methods
    def create_user(self, email, password, name, phone=None):
        """Create new user"""
        with self.get_connection('users') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (email, password, name, phone, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, password, name, phone, datetime.now(), datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_user(self, user_id=None, email=None):
        """Get user by ID or email"""
        with self.get_connection('users') as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            elif email:
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            else:
                raise ValueError("Either user_id or email must be provided")
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def authenticate_user(self, email, password):
        """Authenticate user"""
        with self.get_connection('users') as conn:
            cursor = conn.cursor()
            # Hash the password for comparison
            import hashlib
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, hashed_password))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        with self.get_connection('users') as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [datetime.now(), user_id]
            
            cursor.execute(f'''
                UPDATE users 
                SET {set_clause}, updated_at = ?
                WHERE id = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    # Worker Management Methods
    def create_worker(self, email, password, name, phone, service_type, worker_type):
        """Create new worker"""
        with self.get_connection('workers') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workers (email, password, name, phone, service_type, worker_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, password, name, phone, service_type, worker_type, datetime.now(), datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_worker(self, worker_id=None, email=None, service_type=None, worker_type=None):
        """Get worker by various criteria"""
        with self.get_connection('workers') as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM workers WHERE 1=1"
            params = []
            
            if worker_id:
                query += " AND id = ?"
                params.append(worker_id)
            if email:
                query += " AND email = ?"
                params.append(email)
            if service_type:
                query += " AND service_type = ?"
                params.append(service_type)
            if worker_type:
                query += " AND worker_type = ?"
                params.append(worker_type)
            
            cursor.execute(query, params)
            workers = cursor.fetchall()
            return [dict(worker) for worker in workers]
    
    def authenticate_worker(self, email, password):
        """Authenticate worker"""
        with self.get_connection('workers') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM workers WHERE email = ? AND password = ?', (email, password))
            worker = cursor.fetchone()
            return dict(worker) if worker else None
    
    def get_workers_by_service(self, service_type):
        """Get all workers for a specific service"""
        return self.get_worker(service_type=service_type)
    
    def get_workers_by_service_and_specialization(self, service_type, specialization):
        """Get workers by service type and specialization"""
        db_name = service_type
        with self.get_connection(db_name) as conn:
            cursor = conn.cursor()
            
            # Query workers by service type and specialization
            cursor.execute('''
                SELECT * FROM workers 
                WHERE service_type = ? AND specialization = ? AND worker_type = 'doctor'
                ORDER BY rating DESC, experience DESC
            ''', (service_type, specialization))
            
            workers = [dict(row) for row in cursor.fetchall()]
            return workers
    
    # Service-Specific Methods
    def create_booking(self, service_type, user_id, worker_id, booking_data):
        """Create booking for any service"""
        db_name = service_type
        with self.get_connection(db_name) as conn:
            cursor = conn.cursor()
            
            booking_json = json.dumps(booking_data) if isinstance(booking_data, dict) else booking_data
            
            cursor.execute(f'''
                INSERT INTO {service_type}_bookings 
                (user_id, worker_id, service_type, booking_data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, worker_id, service_type, booking_json, datetime.now(), datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_bookings(self, service_type, user_id=None, worker_id=None, status=None):
        """Get bookings for any service"""
        db_name = service_type
        with self.get_connection(db_name) as conn:
            cursor = conn.cursor()
            
            query = f"SELECT * FROM {service_type}_bookings WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            if worker_id:
                query += " AND worker_id = ?"
                params.append(worker_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            
            cursor.execute(query, params)
            bookings = cursor.fetchall()
            
            # Parse booking_data JSON
            result = []
            for booking in bookings:
                booking_dict = dict(booking)
                try:
                    booking_dict['booking_data'] = json.loads(booking_dict['booking_data'])
                except:
                    pass
                result.append(booking_dict)
            
            return result
    
    # Car Service Specific Methods
    def get_mechanics(self, **filters):
        """Get mechanics with optional filters"""
        return self.get_worker(service_type='car_service', worker_type='mechanic', **filters)
    
    def get_fuel_delivery_agents(self, **filters):
        """Get fuel delivery agents with optional filters"""
        return self.get_worker(service_type='car_service', worker_type='fuel_delivery', **filters)
    
    def get_tow_truck_operators(self, **filters):
        """Get tow truck operators with optional filters"""
        return self.get_worker(service_type='car_service', worker_type='tow_truck', **filters)
    
    def create_car_worker_record(self, worker_type, worker_id, worker_data):
        """Create record in car service worker-specific database"""
        db_name = worker_type  # mechanics, fuel_delivery, tow_truck
        
        if db_name not in self.databases:
            raise ValueError(f"Invalid car worker type: {worker_type}")
        
        with self.get_connection(db_name) as conn:
            cursor = conn.cursor()
            
            data_json = json.dumps(worker_data) if isinstance(worker_data, dict) else worker_data
            
            # Find appropriate table (this is simplified - you'd need to determine the correct table)
            table_name = f"{worker_type}_data"  # Example table name
            
            cursor.execute(f'''
                INSERT INTO {table_name} 
                (worker_id, {worker_type}_data, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (worker_id, data_json, 'active', datetime.now(), datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    # Analytics Methods
    def get_service_statistics(self, service_type):
        """Get statistics for a specific service"""
        with self.get_connection(service_type) as conn:
            cursor = conn.cursor()
            
            # Get booking statistics
            cursor.execute(f'''
                SELECT 
                    COUNT(*) as total_bookings,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_bookings,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bookings,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_bookings
                FROM {service_type}_bookings
            ''')
            
            booking_stats = cursor.fetchone()
            
            # Get worker statistics
            workers = self.get_workers_by_service(service_type)
            worker_stats = {
                'total_workers': len(workers),
                'verified_workers': len([w for w in workers if w.get('is_verified')]),
                'active_workers': len([w for w in workers if w.get('is_active')])
            }
            
            return {
                'bookings': dict(booking_stats),
                'workers': worker_stats,
                'service_type': service_type
            }
    
    # Health Check Methods
    def check_database_health(self):
        """Check health of all databases"""
        health_status = {}
        
        for db_name, db_path in self.databases.items():
            try:
                with self.get_connection(db_name) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    
                    health_status[db_name] = {
                        'status': 'healthy',
                        'tables': [table[0] for table in tables],
                        'size': os.path.getsize(db_path)
                    }
            except Exception as e:
                health_status[db_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return health_status

# Global instance
db_manager = DatabaseManager()

# Convenience functions for backward compatibility
def create_user(email, password, name, phone=None):
    return db_manager.create_user(email, password, name, phone)

def get_user(user_id=None, email=None):
    return db_manager.get_user(user_id, email)

def authenticate_user(email, password):
    return db_manager.authenticate_user(email, password)

def create_worker(email, password, name, phone, service_type, worker_type):
    return db_manager.create_worker(email, password, name, phone, service_type, worker_type)

def get_worker(worker_id=None, email=None, service_type=None, worker_type=None):
    return db_manager.get_worker(worker_id, email, service_type, worker_type)

def authenticate_worker(email, password):
    return db_manager.authenticate_worker(email, password)

if __name__ == "__main__":
    # Test database manager
    print("   Testing Database Manager...")
    
    # Check database health
    health = db_manager.check_database_health()
    print("\n  Database Health Status:")
    for db_name, status in health.items():
        print(f"  {db_name}: {status['status']}")
        if status['status'] == 'healthy':
            print(f"    Tables: {len(status['tables'])}")
            print(f"    Size: {status['size']} bytes")
    
    print("\n  Database Manager is ready!")
