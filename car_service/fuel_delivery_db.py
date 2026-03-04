"""
Fuel Delivery Agent Database Models
Handles fuel delivery agent registration, verification, and delivery management
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Database path
DB_PATH = 'fuel_delivery.db'

class FuelDeliveryDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create all fuel delivery related tables"""
        cursor = self.conn.cursor()
        
        # Fuel Delivery Agents Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_delivery_agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                city TEXT NOT NULL,
                vehicle_type TEXT NOT NULL CHECK (vehicle_type IN ('Bike', 'Van', 'Truck')),
                vehicle_number TEXT NOT NULL,
                vehicle_photo_path TEXT,
                rc_book_photo_path TEXT,
                pollution_certificate_path TEXT,
                fuel_contract_path TEXT,
                employee_proof_path TEXT,
                govt_id_path TEXT,
                safety_declaration_accepted BOOLEAN DEFAULT FALSE,
                is_verified BOOLEAN DEFAULT FALSE,
                approval_status TEXT DEFAULT 'PENDING' CHECK (approval_status IN ('PENDING', 'APPROVED', 'REJECTED')),
                online_status TEXT DEFAULT 'OFFLINE' CHECK (online_status IN ('OFFLINE', 'ONLINE_AVAILABLE', 'BUSY')),
                rating REAL DEFAULT 0.0,
                total_deliveries INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Fuel Delivery Requests Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_delivery_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                agent_id INTEGER,
                fuel_type TEXT NOT NULL CHECK (fuel_type IN ('Petrol', 'Diesel')),
                quantity_liters REAL NOT NULL,
                delivery_latitude REAL,
                delivery_longitude REAL,
                delivery_address TEXT,
                priority_level INTEGER DEFAULT 1 CHECK (priority_level BETWEEN 1 AND 5),
                status TEXT DEFAULT 'WAITING_QUEUE' CHECK (status IN ('WAITING_QUEUE', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id)
            )
        ''')
        
        # Fuel Delivery History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_delivery_history (
                delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                fuel_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                earnings REAL NOT NULL,
                status TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Fuel Agent Reviews Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_agent_reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Fuel Agent Badges Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_agent_badges (
                badge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                badge_type TEXT NOT NULL CHECK (badge_type IN ('Safe Fuel Handler', 'Fast Delivery', 'Top Rated Agent', 'Reliable Partner', 'Emergency Responder')),
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id)
            )
        ''')
        
        # Fuel Agent Activity Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_agent_activity_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id)
            )
        ''')
        
        # Fuel Agent Reports Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_agent_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                reporter_id INTEGER,
                report_type TEXT NOT NULL,
                report_details TEXT,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id),
                FOREIGN KEY (reporter_id) REFERENCES users(id)
            )
        ''')
        
        self.conn.commit()
        cursor.close()
    
    def register_agent(self, agent_data):
        """Register new fuel delivery agent"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO fuel_delivery_agents 
                (name, email, phone_number, password_hash, city, vehicle_type, 
                 vehicle_number, vehicle_photo_path, rc_book_photo_path, 
                 pollution_certificate_path, fuel_contract_path, employee_proof_path, 
                 govt_id_path, safety_declaration_accepted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_data['name'],
                agent_data['email'],
                agent_data['phone_number'],
                agent_data['password_hash'],
                agent_data['city'],
                agent_data['vehicle_type'],
                agent_data['vehicle_number'],
                agent_data.get('vehicle_photo_path'),
                agent_data.get('rc_book_photo_path'),
                agent_data.get('pollution_certificate_path'),
                agent_data.get('fuel_contract_path'),
                agent_data.get('employee_proof_path'),
                agent_data.get('govt_id_path'),
                agent_data.get('safety_declaration_accepted', False)
            ))
            
            agent_id = cursor.lastrowid
            self.conn.commit()
            
            # Log registration activity
            self._log_activity(agent_id, 'REGISTRATION', f'New agent registered: {agent_data["email"]}')
            
            return {'success': True, 'agent_id': agent_id}
            
        except sqlite3.IntegrityError as e:
            if 'email' in str(e):
                return {'success': False, 'error': 'Email already exists'}
            return {'success': False, 'error': 'Registration failed'}
        finally:
            cursor.close()
    
    def authenticate_agent(self, email, password):
        """Authenticate fuel delivery agent"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, email, password_hash, approval_status, is_verified, online_status, rating, total_deliveries
            FROM fuel_delivery_agents 
            WHERE email = ?
        ''', (email,))
        
        agent = cursor.fetchone()
        cursor.close()
        
        if agent and check_password_hash(agent['password_hash'], password):
            if agent['approval_status'] != 'APPROVED':
                return {'success': False, 'error': 'Account not approved. Please wait for admin verification.'}
            
            return {
                'success': True,
                'agent': {
                    'id': agent['id'],
                    'name': agent['name'],
                    'email': agent['email'],
                    'approval_status': agent['approval_status'],
                    'is_verified': agent['is_verified'],
                    'online_status': agent['online_status'],
                    'rating': agent['rating'],
                    'total_deliveries': agent['total_deliveries']
                }
            }
        
        return {'success': False, 'error': 'Invalid email or password'}
    
    def update_agent_status(self, agent_id, status):
        """Update agent online status"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE fuel_delivery_agents 
            SET online_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, agent_id))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        cursor.close()
        
        if success:
            self._log_activity(agent_id, 'STATUS_CHANGE', f'Status changed to {status}')
        
        return success
    
    def get_agent_details(self, agent_id):
        """Get agent details"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM fuel_delivery_agents WHERE id = ?
        ''', (agent_id,))
        
        agent = cursor.fetchone()
        cursor.close()
        return dict(agent) if agent else None
    
    def get_nearby_agents(self, user_lat, user_lon, radius_km=10):
        """Get nearby available agents using Haversine formula"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT *, (
                6371 * acos(
                    cos(radians(?)) * cos(radians(?)) *
                    cos(radians(?) - radians(?)) +
                    sin(radians(?)) * sin(radians(?) - radians(?))
                )
            ) AS distance
            FROM fuel_delivery_agents 
            WHERE approval_status = 'APPROVED' 
            AND online_status = 'ONLINE_AVAILABLE'
            HAVING distance < ?
            ORDER BY distance
            LIMIT 10
        ''', (user_lat, user_lat, user_lat, user_lon, user_lat, user_lon, radius_km))
        
        agents = []
        for row in cursor.fetchall():
            agent = dict(row)
            agents.append(agent)
        
        cursor.close()
        return agents
    
    def create_fuel_request(self, request_data):
        """Create new fuel delivery request"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO fuel_delivery_requests 
            (user_id, fuel_type, quantity_liters, delivery_latitude, 
             delivery_longitude, delivery_address, priority_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request_data['user_id'],
            request_data['fuel_type'],
            request_data['quantity_liters'],
            request_data.get('delivery_latitude'),
            request_data.get('delivery_longitude'),
            request_data.get('delivery_address'),
            request_data.get('priority_level', 1)
        ))
        
        request_id = cursor.lastrowid
        self.conn.commit()
        cursor.close()
        
        return {'success': True, 'request_id': request_id}
    
    def get_fuel_requests_queue(self, agent_lat=None, agent_lon=None):
        """Get fuel delivery requests queue"""
        cursor = self.conn.cursor()
        
        if agent_lat and agent_lon:
            # Get nearby requests
            cursor.execute('''
                SELECT r.*, u.name as user_name, u.phone_number as user_phone
                FROM fuel_delivery_requests r
                JOIN users u ON r.user_id = u.id
                WHERE r.status = 'WAITING_QUEUE'
                ORDER BY r.priority_level DESC, r.created_at ASC
                LIMIT 20
            ''')
        else:
            # Get all requests
            cursor.execute('''
                SELECT r.*, u.name as user_name, u.phone_number as user_phone
                FROM fuel_delivery_requests r
                JOIN users u ON r.user_id = u.id
                WHERE r.status = 'WAITING_QUEUE'
                ORDER BY r.priority_level DESC, r.created_at ASC
                LIMIT 20
            ''')
        
        requests = []
        for row in cursor.fetchall():
            request = dict(row)
            requests.append(request)
        
        cursor.close()
        return requests
    
    def assign_fuel_request(self, request_id, agent_id):
        """Assign fuel request to agent"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_requests 
                SET agent_id = ?, status = 'ASSIGNED', assigned_at = CURRENT_TIMESTAMP
                WHERE request_id = ? AND status = 'WAITING_QUEUE'
            ''', (agent_id, request_id))
            
            success = cursor.rowcount > 0
            if success:
                # Update agent status to busy
                cursor.execute('''
                    UPDATE fuel_delivery_agents 
                    SET online_status = 'BUSY', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (agent_id,))
                
                self._log_activity(agent_id, 'REQUEST_ASSIGNED', f'Assigned request {request_id}')
            
            self.conn.commit()
            cursor.close()
            return success
            
        except Exception as e:
            cursor.close()
            return False
    
    def complete_fuel_delivery(self, request_id, agent_id):
        """Complete fuel delivery"""
        cursor = self.conn.cursor()
        try:
            # Get request details
            cursor.execute('''
                SELECT fuel_type, quantity_liters, user_id
                FROM fuel_delivery_requests
                WHERE request_id = ? AND agent_id = ?
            ''', (request_id, agent_id))
            
            request = cursor.fetchone()
            if not request:
                cursor.close()
                return False
            
            # Calculate earnings (example: 10% of fuel cost)
            fuel_price = 100  # Base price per liter
            earnings = request['quantity_liters'] * fuel_price * 0.1
            
            # Update request status
            cursor.execute('''
                UPDATE fuel_delivery_requests 
                SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP
                WHERE request_id = ? AND agent_id = ?
            ''', (request_id, agent_id))
            
            # Add to history
            cursor.execute('''
                INSERT INTO fuel_delivery_history 
                (agent_id, user_id, fuel_type, quantity, earnings, status)
                VALUES (?, ?, ?, ?, ?, 'COMPLETED')
            ''', (agent_id, request['user_id'], request['fuel_type'], 
                   request['quantity_liters'], earnings))
            
            # Update agent stats
            cursor.execute('''
                UPDATE fuel_delivery_agents 
                SET total_deliveries = total_deliveries + 1,
                    online_status = 'ONLINE_AVAILABLE',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (agent_id,))
            
            self.conn.commit()
            cursor.close()
            
            self._log_activity(agent_id, 'DELIVERY_COMPLETED', f'Completed delivery {request_id}')
            return {'success': True, 'earnings': earnings}
            
        except Exception as e:
            cursor.close()
            return False
    
    def add_agent_review(self, agent_id, user_id, rating, review_text=None):
        """Add review for fuel agent"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO fuel_agent_reviews 
            (agent_id, user_id, rating, review_text)
            VALUES (?, ?, ?, ?)
        ''', (agent_id, user_id, rating, review_text))
        
        # Update agent rating
        cursor.execute('''
            UPDATE fuel_delivery_agents 
            SET rating = (
                SELECT AVG(rating) 
                FROM fuel_agent_reviews 
                WHERE agent_id = ?
            )
            WHERE id = ?
        ''', (agent_id, agent_id))
        
        self.conn.commit()
        cursor.close()
        
        # Check for badges
        self._check_and_award_badges(agent_id)
        return True
    
    def get_agent_performance(self, agent_id):
        """Get agent performance metrics"""
        cursor = self.conn.cursor()
        
        # Get basic stats
        cursor.execute('''
            SELECT total_deliveries, rating, approval_status, is_verified
            FROM fuel_delivery_agents
            WHERE id = ?
        ''', (agent_id,))
        
        agent_stats = cursor.fetchone()
        
        # Get recent deliveries
        cursor.execute('''
            SELECT COUNT(*) as recent_deliveries
            FROM fuel_delivery_history
            WHERE agent_id = ? 
            AND completed_at >= datetime('now', '-30 days')
        ''', (agent_id,))
        
        recent_deliveries = cursor.fetchone()['recent_deliveries']
        
        # Get completion rate
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*) as completion_rate
            FROM fuel_delivery_requests
            WHERE agent_id = ?
        ''', (agent_id,))
        
        completion_data = cursor.fetchone()
        completion_rate = completion_data['completion_rate'] if completion_data['completion_rate'] else 0
        
        cursor.close()
        
        return {
            'total_deliveries': agent_stats['total_deliveries'],
            'recent_deliveries': recent_deliveries,
            'rating': agent_stats['rating'],
            'completion_rate': completion_rate,
            'approval_status': agent_stats['approval_status'],
            'is_verified': agent_stats['is_verified']
        }
    
    def get_agent_badges(self, agent_id):
        """Get agent badges"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT badge_type, earned_at
            FROM fuel_agent_badges
            WHERE agent_id = ?
            ORDER BY earned_at DESC
        ''', (agent_id,))
        
        badges = []
        for row in cursor.fetchall():
            badges.append(dict(row))
        
        cursor.close()
        return badges
    
    def _log_activity(self, agent_id, activity_type, details):
        """Log agent activity"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO fuel_agent_activity_logs 
            (agent_id, activity_type, activity_details)
            VALUES (?, ?, ?)
        ''', (agent_id, activity_type, details))
        self.conn.commit()
        cursor.close()
    
    def _check_and_award_badges(self, agent_id):
        """Check and award badges based on performance"""
        cursor = self.conn.cursor()
        
        # Get agent stats
        cursor.execute('''
            SELECT total_deliveries, rating
            FROM fuel_delivery_agents
            WHERE id = ?
        ''', (agent_id,))
        
        stats = cursor.fetchone()
        
        # Check for badges
        if stats['total_deliveries'] >= 100:
            self._award_badge(agent_id, 'Fast Delivery')
        
        if stats['rating'] >= 4.5:
            self._award_badge(agent_id, 'Top Rated Agent')
        
        if stats['total_deliveries'] >= 50:
            self._award_badge(agent_id, 'Reliable Partner')
        
        cursor.close()
    
    def _award_badge(self, agent_id, badge_type):
        """Award badge to agent"""
        cursor = self.conn.cursor()
        # Check if badge already exists
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM fuel_agent_badges
            WHERE agent_id = ? AND badge_type = ?
        ''', (agent_id, badge_type))
        
        if cursor.fetchone()['count'] == 0:
            cursor.execute('''
                INSERT INTO fuel_agent_badges (agent_id, badge_type)
                VALUES (?, ?)
            ''', (agent_id, badge_type))
            self.conn.commit()
        
        cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Create database instance
fuel_delivery_db = FuelDeliveryDB()
