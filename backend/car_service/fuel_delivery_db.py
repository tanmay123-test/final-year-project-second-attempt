"""
Fuel Delivery Agent Database Models
Handles fuel delivery agent registration, verification, and delivery management
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

class FuelDeliveryDB:
    def __init__(self):
        self._create_tables()
    
    def _create_tables(self):
        """Create all fuel delivery related tables"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Fuel Delivery Agents Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fuel_delivery_agents (
                    id SERIAL PRIMARY KEY,
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
            
            # Fuel Delivery Requests Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fuel_delivery_requests (
                    id SERIAL PRIMARY KEY,
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
                    otp TEXT,
                    assigned_at TIMESTAMP NULL,
                    completed_at TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Fuel Agent Activity Logs Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fuel_agent_activity_logs (
                    log_id SERIAL PRIMARY KEY,
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
                    location_id SERIAL PRIMARY KEY,
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
                    delivery_id SERIAL PRIMARY KEY,
                    agent_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    fuel_type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    earnings REAL NOT NULL,
                    status TEXT NOT NULL,
                    request_id INTEGER REFERENCES fuel_delivery_requests(id),
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id)
                )
            ''')

            # Fuel Delivery Proofs Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fuel_delivery_proofs (
                    proof_id SERIAL PRIMARY KEY,
                    request_id INTEGER NOT NULL,
                    image_path TEXT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (request_id) REFERENCES fuel_delivery_requests(id)
                )
            ''')
            
            # Fuel Agent Reviews Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fuel_agent_reviews (
                    review_id SERIAL PRIMARY KEY,
                    agent_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    request_id INTEGER,
                    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                    review_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES fuel_delivery_agents(id)
                )
            ''')
            
            # Fuel Agent Badges Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fuel_agent_badges (
                    id SERIAL PRIMARY KEY,
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
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def register_agent(self, agent_data):
        """Register new fuel delivery agent"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO fuel_delivery_agents 
                (name, email, phone_number, password_hash, city, vehicle_type, 
                 vehicle_number, service_area_city, service_area_location, service_area_km,
                 latitude, longitude, vehicle_photo_path, rc_book_photo_path, 
                 pollution_certificate_path, fuel_contract_path, employee_proof_path, 
                 govt_id_path, approval_status, online_status, is_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', 'OFFLINE', FALSE)
                RETURNING id
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
            
            agent_id = cursor.fetchone()[0]
            conn.commit()
            
            # Log registration activity
            self._log_activity_internal(agent_id, 'REGISTRATION', f'New agent registered: {agent_data["email"]}')
            
            return {'success': True, 'agent_id': agent_id}
            
        except Exception as e:
            conn.rollback()
            if 'email' in str(e):
                return {'success': False, 'error': 'Email already exists'}
            return {'success': False, 'error': f'Registration failed: {e}'}
        finally:
            cursor.close()
            conn.close()
    
    def authenticate_agent(self, email, password):
        """Authenticate fuel delivery agent"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT id, name, email, phone_number, city, vehicle_type, vehicle_number, password_hash, approval_status, is_verified, online_status, rating, total_deliveries
                FROM fuel_delivery_agents 
                WHERE email = %s
            ''', (email,))
            
            agent = cursor.fetchone()
            
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
        except Exception as e:
            print(f"DB Error: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def update_agent_status(self, agent_id, status):
        """Update agent online status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_agents 
                SET online_status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (status, agent_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            if success:
                self._log_activity_internal(agent_id, 'STATUS_CHANGE', f'Status changed to {status}')
            
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def update_agent_location(self, agent_id, latitude, longitude):
        """Update agent coordinates"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_agents
                SET latitude = %s, longitude = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (latitude, longitude, agent_id))
            
            # Also log in live locations table
            cursor.execute('''
                INSERT INTO fuel_agent_live_locations
                (agent_id, latitude, longitude, updated_at)
                VALUES (%s, %s, %s, %s)
            ''', (agent_id, latitude, longitude, datetime.now()))
            
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                self._log_activity_internal(agent_id, 'LOCATION_UPDATE', f'Updated location to {latitude},{longitude}')
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def get_agent_details(self, agent_id):
        """Get agent details"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT * FROM fuel_delivery_agents WHERE id = %s
            ''', (agent_id,))
            
            agent = cursor.fetchone()
            return dict(agent) if agent else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_available_agents(self, exclude_agent_id=None):
        """Get all APPROVED and ONLINE_AVAILABLE agents with basic metrics"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            query = """
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
            """
            params = []
            if exclude_agent_id:
                query += " AND a.id != %s"
                params.append(exclude_agent_id)
            
            query += " ORDER BY a.updated_at DESC LIMIT 100"
            
            cursor.execute(query, params)
            agents = [dict(row) for row in cursor.fetchall()]
            return agents
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_nearby_agents(self, user_lat, user_lon, radius_km=10):
        """Get nearby available agents using Haversine formula"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Using a subquery/CTE to calculate distance and filter in WHERE
            query = '''
                SELECT * FROM (
                    SELECT *, (
                        6371 * acos(
                            cos(radians(%s)) * cos(radians(latitude)) *
                            cos(radians(longitude) - radians(%s)) +
                            sin(radians(%s)) * sin(radians(latitude))
                        )
                    ) AS distance
                    FROM fuel_delivery_agents 
                    WHERE approval_status = 'APPROVED' 
                    AND online_status = 'ONLINE_AVAILABLE'
                ) AS agent_distances
                WHERE distance < %s
                ORDER BY distance
                LIMIT 10
            '''
            cursor.execute(query, (user_lat, user_lon, user_lat, radius_km))
            
            agents = [dict(row) for row in cursor.fetchall()]
            return agents
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def create_fuel_request(self, request_data):
        """Create new fuel delivery request"""
        import random
        otp = str(random.randint(1000, 9999))
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        
        # Get user details from users table if not provided
        user_name = request_data.get('user_name', 'User')
        user_phone = request_data.get('user_phone', 'N/A')
        
        try:
            cursor.execute('''
                INSERT INTO fuel_delivery_requests 
                (user_id, user_name, user_phone, fuel_type, quantity, latitude, 
                 longitude, address, priority_level, otp, agent_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                request_data['user_id'],
                user_name,
                user_phone,
                request_data['fuel_type'],
                request_data['quantity_liters'],
                request_data.get('latitude', 0.0),
                request_data.get('longitude', 0.0),
                request_data.get('address', 'Mumbai'),
                request_data.get('priority_level', 3),
                otp,
                request_data.get('agent_id'),
                'ASSIGNED' if request_data.get('agent_id') else 'WAITING_QUEUE'
            ))
            
            request_id = cursor.fetchone()[0]
            
            if request_data.get('agent_id'):
                # Update agent status to busy if auto-assigned
                cursor.execute('UPDATE fuel_delivery_agents SET online_status = \'BUSY\' WHERE id = %s', (request_data['agent_id'],))
            
            conn.commit()
            return {'success': True, 'request_id': request_id, 'otp': otp}
        except Exception as e:
            conn.rollback()
            print(f"Error creating fuel request: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def get_fuel_requests_queue(self, agent_lat=None, agent_lon=None):
        """Get fuel delivery requests queue"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT *
                FROM fuel_delivery_requests
                WHERE status = 'WAITING_QUEUE'
                ORDER BY priority_level DESC, created_at ASC
                LIMIT 20
            ''')
            
            requests = [dict(row) for row in cursor.fetchall()]
            return requests
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def assign_fuel_request(self, request_id, agent_id):
        """Assign fuel request to agent"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_requests 
                SET agent_id = %s, status = 'ASSIGNED', assigned_at = CURRENT_TIMESTAMP
                WHERE id = %s AND status = 'WAITING_QUEUE'
            ''', (agent_id, request_id))
            
            success = cursor.rowcount > 0
            if success:
                # Update agent status to busy
                cursor.execute('''
                    UPDATE fuel_delivery_agents 
                    SET online_status = 'BUSY', updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                ''', (agent_id,))
                
                self._log_activity_internal(agent_id, 'REQUEST_ASSIGNED', f'Assigned request {request_id}')
            
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def verify_otp(self, request_id, otp):
        """Verify OTP for fuel delivery request"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT otp FROM fuel_delivery_requests WHERE id = %s', (request_id,))
            result = cursor.fetchone()
            if result and result[0] == otp:
                return True
            return False
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def start_fuel_delivery(self, request_id, agent_id):
        """Start fuel delivery process"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_requests 
                SET status = 'IN_PROGRESS', agent_id = %s, assigned_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (agent_id, request_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def complete_fuel_delivery(self, request_id):
        """Complete fuel delivery process"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Get agent_id first to set them back to ONLINE_AVAILABLE
            cursor.execute('SELECT agent_id FROM fuel_delivery_requests WHERE id = %s', (request_id,))
            result = cursor.fetchone()
            agent_id = result[0] if result else None
            
            cursor.execute('''
                UPDATE fuel_delivery_requests 
                SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (request_id,))
            
            if agent_id:
                cursor.execute('UPDATE fuel_delivery_agents SET online_status = \'ONLINE_AVAILABLE\' WHERE id = %s', (agent_id,))
                
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def add_agent_review(self, agent_id, user_id, rating, review_text=None):
        """Add review for fuel agent"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO fuel_agent_reviews 
                (agent_id, user_id, rating, review_text)
                VALUES (%s, %s, %s, %s)
            ''', (agent_id, user_id, rating, review_text))
            
            # Update agent rating
            cursor.execute('''
                UPDATE fuel_delivery_agents 
                SET rating = (
                    SELECT AVG(rating) 
                    FROM fuel_agent_reviews 
                    WHERE agent_id = %s
                )
                WHERE id = %s
            ''', (agent_id, agent_id))
            
            conn.commit()
            # Check for badges
            self._check_and_award_badges_internal(agent_id)
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def get_agent_performance(self, agent_id):
        """Get agent performance metrics"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Get basic stats
            cursor.execute('''
                SELECT total_deliveries, rating, approval_status, is_verified
                FROM fuel_delivery_agents
                WHERE id = %s
            ''', (agent_id,))
            agent_stats = cursor.fetchone()
            if not agent_stats:
                return None
            
            # Get recent deliveries
            cursor.execute('''
                SELECT COUNT(*) as recent_deliveries
                FROM fuel_delivery_history
                WHERE agent_id = %s 
                AND completed_at >= CURRENT_TIMESTAMP - INTERVAL '30 days'
            ''', (agent_id,))
            recent_deliveries = cursor.fetchone()['recent_deliveries']
            
            # Get completion rate
            cursor.execute('''
                SELECT 
                    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as completion_rate
                FROM fuel_delivery_requests
                WHERE agent_id = %s
            ''', (agent_id,))
            completion_data = cursor.fetchone()
            completion_rate = float(completion_data['completion_rate'] or 0) if completion_data else 0
            
            # Review count
            cursor.execute('SELECT COUNT(*) as cnt FROM fuel_agent_reviews WHERE agent_id = %s', (agent_id,))
            review_count = cursor.fetchone()['cnt'] or 0
            
            # Avg delivery time (minutes) and on-time rate
            cursor.execute('''
                SELECT 
                    AVG(EXTRACT(EPOCH FROM (completed_at - assigned_at)) / 60) as avg_mins,
                    COUNT(CASE WHEN EXTRACT(EPOCH FROM (completed_at - assigned_at)) / 60 <= 35 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as on_time_pct
                FROM fuel_delivery_requests
                WHERE agent_id = %s AND status = 'COMPLETED' AND assigned_at IS NOT NULL AND completed_at IS NOT NULL
            ''', (agent_id,))
            delivery_stats = cursor.fetchone()
            avg_delivery_time = float(delivery_stats['avg_mins'] or 28) if delivery_stats else 28
            on_time_rate = float(delivery_stats['on_time_pct'] or 94) if delivery_stats else 94
            
            safety_score = 98.0 if agent_stats['is_verified'] else 95.0
            
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
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_agent_reviews(self, agent_id, limit=20):
        """Get customer reviews for agent"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT rev.review_id, rev.agent_id, rev.rating, rev.review_text, rev.created_at, r.address
                FROM fuel_agent_reviews rev
                LEFT JOIN fuel_delivery_requests r ON r.id = rev.request_id
                WHERE rev.agent_id = %s
                ORDER BY rev.created_at DESC
                LIMIT %s
            ''', (agent_id, limit))
            
            rows = cursor.fetchall()
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
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_agent_badges(self, agent_id):
        """Get agent badges"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT badge_type, earned_at
                FROM fuel_agent_badges
                WHERE agent_id = %s
                ORDER BY earned_at DESC
            ''', (agent_id,))
            
            badges = [dict(row) for row in cursor.fetchall()]
            return badges
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def _log_activity_internal(self, agent_id, activity_type, details):
        """Internal log agent activity"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO fuel_agent_activity_logs 
                (agent_id, activity_type, activity_details)
                VALUES (%s, %s, %s)
            ''', (agent_id, activity_type, details))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error in _log_activity: {e}")
        finally:
            cursor.close()
            conn.close()

    def _check_and_award_badges_internal(self, agent_id):
        """Internal check and award badges"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Get agent stats
            cursor.execute('''
                SELECT total_deliveries, rating
                FROM fuel_delivery_agents
                WHERE id = %s
            ''', (agent_id,))
            stats = cursor.fetchone()
            if not stats: return
            
            if stats['total_deliveries'] >= 100:
                self._award_badge_internal(agent_id, 'Fast Delivery')
            if stats['rating'] >= 4.5:
                self._award_badge_internal(agent_id, 'Top Rated Agent')
            if stats['total_deliveries'] >= 50:
                self._award_badge_internal(agent_id, 'Reliable Partner')
        except Exception as e:
            print(f"DB Error in _check_and_award_badges: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def _award_badge_internal(self, agent_id, badge_type):
        """Internal award badge to agent"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Check if badge already exists
            cursor.execute('''
                SELECT COUNT(*) FROM fuel_agent_badges
                WHERE agent_id = %s AND badge_type = %s
            ''', (agent_id, badge_type))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO fuel_agent_badges (agent_id, badge_type)
                    VALUES (%s, %s)
                ''', (agent_id, badge_type))
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error in _award_badge: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def close(self):
        """Close database connection (noop for this implementation)"""
        pass
    
    # Admin methods
    def get_agents_by_status(self, status):
        """Get all agents by approval status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT * FROM fuel_delivery_agents 
                WHERE approval_status = %s
                ORDER BY created_at DESC
            ''', (status,))
            
            agents = [dict(row) for row in cursor.fetchall()]
            return agents
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def update_agent_approval_status(self, agent_id, status):
        """Update agent approval status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_agents 
                SET approval_status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (status, agent_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def get_waiting_requests(self, limit=None):
        """Get waiting fuel delivery requests"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            query = '''
                SELECT * FROM fuel_delivery_requests 
                WHERE status = 'WAITING_QUEUE'
                ORDER BY priority_level DESC, created_at ASC
            '''
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            requests = [dict(row) for row in cursor.fetchall()]
            return requests
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_waiting_requests_count(self):
        """Get count of waiting requests"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM fuel_delivery_requests 
                WHERE status = 'WAITING_QUEUE'
            ''')
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"DB Error: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()
    
    def get_available_agents_count(self):
        """Get count of available agents"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM fuel_delivery_agents 
                WHERE online_status = 'ONLINE_AVAILABLE'
                AND approval_status = 'APPROVED'
            ''')
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"DB Error: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()
    
    def assign_request_to_agent(self, request_id, agent_id):
        """Assign fuel request to agent"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_requests 
                SET agent_id = %s, status = 'ASSIGNED', assigned_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (agent_id, request_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def unassign_request(self, request_id):
        """Unassign fuel request"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_requests 
                SET agent_id = NULL, status = 'WAITING_QUEUE', assigned_at = NULL
                WHERE id = %s
            ''', (request_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def get_active_delivery(self, agent_id):
        """Get active delivery for agent"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT * FROM fuel_delivery_requests 
                WHERE agent_id = %s 
                AND status IN ('ASSIGNED', 'IN_PROGRESS')
                LIMIT 1
            ''', (agent_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def log_agent_activity(self, agent_id, event_type, details=None):
        """Log agent activity wrapper"""
        self._log_activity_internal(agent_id, event_type, details)

# Create database instance
fuel_delivery_db = FuelDeliveryDB()
