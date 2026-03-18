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
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
                phone_number TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                city TEXT NOT NULL,
                vehicle_type TEXT NOT NULL CHECK (vehicle_type IN ('Bike', 'Van', 'Truck')),
                vehicle_number TEXT NOT NULL,
                service_area_city TEXT DEFAULT '',
                service_area_location TEXT DEFAULT '',
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
                latitude REAL DEFAULT 0.0,
                longitude REAL DEFAULT 0.0,
                service_area_km INTEGER DEFAULT 15,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        try:
            cursor.execute("PRAGMA table_info(fuel_delivery_agents)")
            existing_cols = {row[1] for row in cursor.fetchall()}
            if 'service_area_city' not in existing_cols:
                cursor.execute("ALTER TABLE fuel_delivery_agents ADD COLUMN service_area_city TEXT DEFAULT ''")
            if 'service_area_location' not in existing_cols:
                cursor.execute("ALTER TABLE fuel_delivery_agents ADD COLUMN service_area_location TEXT DEFAULT ''")
            if 'service_area_km' not in existing_cols:
                cursor.execute("ALTER TABLE fuel_delivery_agents ADD COLUMN service_area_km INTEGER DEFAULT 15")
            if 'latitude' not in existing_cols:
                cursor.execute("ALTER TABLE fuel_delivery_agents ADD COLUMN latitude REAL DEFAULT 0.0")
            if 'longitude' not in existing_cols:
                cursor.execute("ALTER TABLE fuel_delivery_agents ADD COLUMN longitude REAL DEFAULT 0.0")
            if 'safety_declaration_accepted' not in existing_cols:
                cursor.execute("ALTER TABLE fuel_delivery_agents ADD COLUMN safety_declaration_accepted BOOLEAN DEFAULT FALSE")
        except Exception:
            pass
        
        # Fuel Delivery Requests Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_delivery_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                agent_id INTEGER NULL,
                user_name TEXT NOT NULL,
                user_phone TEXT NOT NULL,
                fuel_type TEXT NOT NULL CHECK (fuel_type IN ('Petrol', 'Diesel')),
                quantity REAL NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT NOT NULL,
                status TEXT DEFAULT 'WAITING_QUEUE' CHECK (status IN ('WAITING_QUEUE', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
                priority_level INTEGER DEFAULT 3 CHECK (priority_level BETWEEN 1 AND 5),
                assigned_at TIMESTAMP NULL,
                completed_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        
        # Fuel Agent Live Locations Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_agent_live_locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
        try:
            cursor.execute("PRAGMA table_info(fuel_delivery_history)")
            hist_cols = {row[1] for row in cursor.fetchall()}
            if 'request_id' not in hist_cols:
                cursor.execute("ALTER TABLE fuel_delivery_history ADD COLUMN request_id INTEGER REFERENCES fuel_delivery_requests(id)")
        except Exception:
            pass

        # Fuel Delivery Proofs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_delivery_proofs (
                proof_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES fuel_delivery_requests(id)
            )
        ''')
        
        # Fuel Agent Reviews Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_agent_reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                request_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id)
            )
        ''')
        
        # Fuel Agent Badges Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_agent_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                badge_type TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id)
            )
        ''')
        
        # Fuel Agent Performance Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_agent_performance (
                agent_id INTEGER PRIMARY KEY,
                total_deliveries INTEGER DEFAULT 0,
                completed_deliveries INTEGER DEFAULT 0,
                cancelled_deliveries INTEGER DEFAULT 0,
                completion_rate REAL DEFAULT 0,
                average_rating REAL DEFAULT 0,
                total_earnings REAL DEFAULT 0,
                online_hours REAL DEFAULT 0,
                recent_deliveries INTEGER DEFAULT 0,
                fair_assignment_score REAL DEFAULT 50,
                level TEXT DEFAULT 'BRONZE',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id)
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
                 vehicle_number, service_area_city, service_area_location, service_area_km,
                 latitude, longitude, vehicle_photo_path, rc_book_photo_path, 
                 pollution_certificate_path, fuel_contract_path, employee_proof_path, 
                 govt_id_path, approval_status, online_status, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', 'OFFLINE', FALSE)
            ''', (
                agent_data['name'],
                agent_data['email'],
                agent_data['phone_number'],
                agent_data['password_hash'] if 'password_hash' in agent_data else agent_data['password'],
                agent_data['city'],
                agent_data['vehicle_type'],
                agent_data['vehicle_number'],
                agent_data.get('service_area_city', ''),
                agent_data.get('service_area_location', ''),
                agent_data.get('service_area_km', 15),
                agent_data.get('latitude', 0.0),
                agent_data.get('longitude', 0.0),
                agent_data.get('vehicle_photo_path'),
                agent_data.get('rc_book_photo_path'),
                agent_data.get('pollution_certificate_path'),
                agent_data.get('fuel_contract_path'),
                agent_data.get('employee_proof_path'),
                agent_data.get('govt_id_path')
            ))
            
            agent_id = cursor.lastrowid
            self.conn.commit()
            cursor.close()
            
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
            SELECT id, name, email, phone_number, city, vehicle_type, vehicle_number, password_hash, approval_status, is_verified, online_status, rating, total_deliveries
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
                    'phone_number': agent['phone_number'],
                    'city': agent['city'],
                    'vehicle_type': agent['vehicle_type'],
                    'vehicle_number': agent['vehicle_number'],
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
    
    def update_agent_location(self, agent_id, latitude, longitude):
        """Update agent coordinates"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE fuel_delivery_agents
            SET latitude = ?, longitude = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (latitude, longitude, agent_id))
        self.conn.commit()
        ok = cursor.rowcount > 0
        cursor.close()
        if ok:
            self._log_activity(agent_id, 'LOCATION_UPDATE', f'Updated location to {latitude},{longitude}')
        return ok
    
    def get_agent_details(self, agent_id):
        """Get agent details"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM fuel_delivery_agents WHERE id = ?
        ''', (agent_id,))
        
        agent = cursor.fetchone()
        cursor.close()
        return dict(agent) if agent else None
    
    def get_available_agents(self):
        """Get all APPROVED and ONLINE_AVAILABLE agents with basic metrics"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                a.id, 
                a.name, 
                a.vehicle_type, 
                a.latitude, 
                a.longitude, 
                a.service_area_km, 
                a.rating,
                COALESCE(p.completion_rate, 0) as completion_rate
            FROM fuel_delivery_agents a
            LEFT JOIN fuel_agent_performance p ON p.agent_id = a.id
            WHERE a.approval_status = 'APPROVED'
              AND a.online_status = 'ONLINE_AVAILABLE'
            ORDER BY a.updated_at DESC
            LIMIT 100
        """)
        agents = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return agents
    
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
        cursor.execute('''
            SELECT *
            FROM fuel_delivery_requests
            WHERE status = 'WAITING_QUEUE'
            ORDER BY priority_level DESC, created_at ASC
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
                COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as completion_rate
            FROM fuel_delivery_requests
            WHERE agent_id = ?
        ''', (agent_id,))
        
        completion_data = cursor.fetchone()
        completion_rate = float(completion_data['completion_rate'] or 0) if completion_data else 0
        
        # Review count
        cursor.execute('SELECT COUNT(*) as cnt FROM fuel_agent_reviews WHERE agent_id = ?', (agent_id,))
        review_count = cursor.fetchone()['cnt'] or 0
        
        # Avg delivery time (minutes) and on-time rate (deliveries under 35 min) from COMPLETED requests
        cursor.execute('''
            SELECT 
                AVG((julianday(completed_at) - julianday(assigned_at)) * 24 * 60) as avg_mins,
                COUNT(CASE WHEN (julianday(completed_at) - julianday(assigned_at)) * 24 * 60 <= 35 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as on_time_pct
            FROM fuel_delivery_requests
            WHERE agent_id = ? AND status = 'COMPLETED' AND assigned_at IS NOT NULL AND completed_at IS NOT NULL
        ''', (agent_id,))
        delivery_stats = cursor.fetchone()
        avg_delivery_time = float(delivery_stats['avg_mins'] or 28) if delivery_stats else 28
        on_time_rate = float(delivery_stats['on_time_pct'] or 94) if delivery_stats else 94
        
        # Safety score: default high; could be derived from incidents later
        safety_score = 98.0 if (agent_stats['is_verified']) else 95.0
        
        cursor.close()
        
        return {
            'total_deliveries': agent_stats['total_deliveries'],
            'recent_deliveries': recent_deliveries,
            'rating': float(agent_stats['rating'] or 0),
            'completion_rate': completion_rate,
            'approval_status': agent_stats['approval_status'],
            'is_verified': agent_stats['is_verified'],
            'review_count': review_count,
            'avg_delivery_time_minutes': round(avg_delivery_time, 0),
            'on_time_rate': round(on_time_rate, 1),
            'safety_score': safety_score,
        }
    
    def get_agent_reviews(self, agent_id, limit=20):
        """Get customer reviews for agent (for Performance & Safety screen)."""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT rev.review_id, rev.agent_id, rev.rating, rev.review_text, rev.created_at, r.address
                FROM fuel_agent_reviews rev
                LEFT JOIN fuel_delivery_requests r ON r.id = rev.request_id
                WHERE rev.agent_id = ?
                ORDER BY rev.created_at DESC
                LIMIT ?
            ''', (agent_id, limit))
        except Exception:
            cursor.execute('''
                SELECT review_id, agent_id, rating, review_text, created_at
                FROM fuel_agent_reviews
                WHERE agent_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (agent_id, limit))
        rows = cursor.fetchall()
        cursor.close()
        result = []
        for row in rows:
            r = dict(row)
            result.append({
                'review_id': r.get('review_id'),
                'rating': int(r.get('rating') or 0),
                'review_text': r.get('review_text') or '',
                'created_at': r.get('created_at'),
                'source': ((r.get('address') or 'Delivery').strip() or 'Delivery')[:80],
            })
        return result
    
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
    
    # Admin methods
    def get_agents_by_status(self, status):
        """Get all agents by approval status"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM fuel_delivery_agents 
            WHERE approval_status = ?
            ORDER BY created_at DESC
        ''', (status,))
        
        agents = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return agents
    
    def update_agent_status(self, agent_id, status):
        """Update agent approval status"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE fuel_delivery_agents 
            SET approval_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, agent_id))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        cursor.close()
        return success
    
    # Availability Engine Database Methods
    def update_agent_online_status(self, agent_id, online_status):
        """Update agent online status"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE fuel_delivery_agents 
            SET online_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (online_status, agent_id))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        cursor.close()
        return success
    
    def get_waiting_requests(self, limit=None):
        """Get waiting fuel delivery requests"""
        cursor = self.conn.cursor()
        query = '''
            SELECT * FROM fuel_delivery_requests 
            WHERE status = 'WAITING_QUEUE'
            ORDER BY priority_level DESC, created_at ASC
        '''
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query)
        requests = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return requests
    
    def get_waiting_requests_count(self):
        """Get count of waiting requests"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM fuel_delivery_requests 
            WHERE status = 'WAITING_QUEUE'
        ''')
        result = cursor.fetchone()
        cursor.close()
        return result['count'] if result else 0
    
    def get_available_agents(self, exclude_agent_id=None):
        """Get available agents (ONLINE_AVAILABLE)"""
        cursor = self.conn.cursor()
        query = '''
            SELECT id, name, rating, total_deliveries
            FROM fuel_delivery_agents 
            WHERE online_status = 'ONLINE_AVAILABLE'
            AND approval_status = 'APPROVED'
        '''
        params = []
        if exclude_agent_id:
            query += ' AND id != ?'
            params.append(exclude_agent_id)
        
        cursor.execute(query, params)
        agents = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return agents
    
    def get_available_agents_count(self):
        """Get count of available agents"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM fuel_delivery_agents 
            WHERE online_status = 'ONLINE_AVAILABLE'
            AND approval_status = 'APPROVED'
        ''')
        result = cursor.fetchone()
        cursor.close()
        return result['count'] if result else 0
    
    def assign_request_to_agent(self, request_id, agent_id):
        """Assign fuel request to agent"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE fuel_delivery_requests 
            SET agent_id = ?, status = 'ASSIGNED', assigned_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (agent_id, request_id))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        cursor.close()
        return success
    
    def unassign_request(self, request_id):
        """Unassign fuel request (set back to waiting)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE fuel_delivery_requests 
            SET agent_id = NULL, status = 'WAITING_QUEUE', assigned_at = NULL
            WHERE id = ?
        ''', (request_id,))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        cursor.close()
        return success
    
    def get_active_delivery(self, agent_id):
        """Get active delivery for agent"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM fuel_delivery_requests 
            WHERE agent_id = ? 
            AND status IN ('ASSIGNED', 'IN_PROGRESS')
            LIMIT 1
        ''', (agent_id,))
    
    def update_agent_location(self, agent_id, latitude, longitude):
        """Update agent live location"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO fuel_agent_live_locations
                (agent_id, latitude, longitude, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, latitude, longitude, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            self.conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            return False
    
    def log_agent_activity(self, agent_id, event_type, details=None):
        """Log agent activity"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO fuel_agent_activity_logs
                (agent_id, activity_type, activity_details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, event_type, str(details) if details else None, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            self.conn.commit()
            cursor.close()
        except Exception:
            pass  # Don't fail main flow due to logging errors

# Create database instance
fuel_delivery_db = FuelDeliveryDB()
