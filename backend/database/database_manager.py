#!/usr/bin/env python3
"""
Central Database Manager for All Services (PostgreSQL Version)
Provides unified access to PostgreSQL database
"""

import psycopg2
import psycopg2.extras
import json
import os
from datetime import datetime
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """Central database manager for all services using PostgreSQL"""
    
    def __init__(self):
        """Initialize database manager"""
        self.db_url = os.environ.get('DATABASE_URL')
        if not self.db_url:
            print("  WARNING: DATABASE_URL not found in environment")
    
    @contextmanager
    def get_connection(self, db_type=None):
        """Get PostgreSQL database connection with automatic cleanup"""
        if not self.db_url:
            raise ValueError("DATABASE_URL not set in environment")
            
        conn = psycopg2.connect(self.db_url, sslmode='require')
        try:
            yield conn
        finally:
            conn.close()
    
    # User Management Methods
    def create_user(self, email, password, name, phone=None):
        """Create new user in public.users table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (email, password, name, phone, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (email, password, name, phone, datetime.now(), datetime.now()))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
    
    def get_user(self, user_id=None, email=None):
        """Get user by ID or email"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            if user_id:
                cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            elif email:
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            else:
                raise ValueError("Either user_id or email must be provided")
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def authenticate_user(self, email, password):
        """Authenticate user (this logic depends on your password hashing strategy)"""
        # Note: Usually bcrypt is used, but keeping original structure for now
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            if user:
                # Assuming password comparison is handled by the caller or add logic here
                return dict(user)
            return None
    
    # Worker Management Methods
    def create_worker(self, email, password, name, phone, service_type, worker_type):
        """Create new worker in public.workers table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workers (email, password, full_name, phone, service, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (email, password, name, phone, service_type, 'pending', datetime.now(), datetime.now()))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
    
    def get_worker(self, worker_id=None, email=None, service_type=None, worker_type=None):
        """Get worker by various criteria"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            query = "SELECT * FROM workers WHERE 1=1"
            params = []
            
            if worker_id:
                query += " AND id = %s"
                params.append(worker_id)
            if email:
                query += " AND email = %s"
                params.append(email)
            if service_type:
                query += " AND service LIKE %s"
                params.append(f'%{service_type}%')
            # worker_type might map to specialization or status in your actual schema
            
            cursor.execute(query, params)
            workers = cursor.fetchall()
            return [dict(worker) for worker in workers]
    
    def authenticate_worker(self, email, password):
        """Authenticate worker"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute('SELECT * FROM workers WHERE email = %s', (email,))
            worker = cursor.fetchone()
            if worker:
                return dict(worker)
            return None
    
    def get_workers_by_service(self, service_type):
        """Get all workers for a specific service"""
        return self.get_worker(service_type=service_type)
    
    def get_workers_by_service_and_specialization(self, service_type, specialization):
        """Get workers by service type and specialization"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute('''
                SELECT * FROM workers 
                WHERE service LIKE %s AND specialization = %s AND status = 'approved'
                ORDER BY rating DESC, experience DESC
            ''', (f'%{service_type}%', specialization))
            
            workers = [dict(row) for row in cursor.fetchall()]
            return workers
    
    # Service-Specific Methods
    def create_booking(self, service_type, user_id, worker_id, booking_data):
        """Create booking in appropriate table"""
        # Map service_type to table name
        table_name = f"{service_type}_bookings"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            booking_json = json.dumps(booking_data) if isinstance(booking_data, dict) else booking_data
            
            cursor.execute(f'''
                INSERT INTO {table_name} 
                (user_id, worker_id, status, booking_data, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (user_id, worker_id, 'pending', booking_json, datetime.now(), datetime.now()))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
    
    def get_bookings(self, service_type, user_id=None, worker_id=None, status=None):
        """Get bookings from appropriate table"""
        table_name = f"{service_type}_bookings"
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            query = f"SELECT * FROM {table_name} WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            if worker_id:
                query += " AND worker_id = %s"
                params.append(worker_id)
            if status:
                query += " AND status = %s"
                params.append(status)
            
            cursor.execute(query, params)
            bookings = cursor.fetchall()
            
            result = []
            for booking in bookings:
                booking_dict = dict(booking)
                if isinstance(booking_dict.get('booking_data'), str):
                    try:
                        booking_dict['booking_data'] = json.loads(booking_dict['booking_data'])
                    except:
                        pass
                result.append(booking_dict)
            
            return result
    
    # Health Check Methods
    def check_database_health(self):
        """Check health of PostgreSQL connection and tables"""
        health_status = {}
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                tables = [table[0] for table in cursor.fetchall()]
                
                health_status['postgres'] = {
                    'status': 'healthy',
                    'tables': tables,
                    'url_configured': True if self.db_url else False
                }
        except Exception as e:
            health_status['postgres'] = {
                'status': 'error',
                'error': str(e),
                'url_configured': True if self.db_url else False
            }
        
        return health_status

# Global instance
db_manager = DatabaseManager()

# Convenience functions
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
