"""
Tow Truck Driver Profile Database
Complete database operations for tow truck driver authentication and verification
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json

class TowTruckProfileDB:
    """Complete database operations for Tow Truck Driver Profiles"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default path in car_service directory
            self.db_path = os.path.join(os.path.dirname(__file__), "tow_truck_profiles.db")
        else:
            self.db_path = db_path
        
        self.init_database()
    
    def get_conn(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize tow truck profile tables"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # 1. Tow Driver Profiles Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tow_driver_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone_number TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                city TEXT NOT NULL,
                service_radius_km INTEGER DEFAULT 10,
                truck_type TEXT NOT NULL CHECK (truck_type IN ('FLATBED', 'WHEEL_LIFT', 'HEAVY_DUTY')),
                truck_registration_number TEXT NOT NULL UNIQUE,
                truck_model TEXT NOT NULL,
                truck_capacity TEXT NOT NULL CHECK (truck_capacity IN ('SMALL_CAR', 'SUV', 'HEAVY_VEHICLE')),
                insurance_expiry_date DATE NOT NULL,
                fitness_expiry_date DATE NOT NULL,
                approval_status TEXT DEFAULT 'PENDING_VERIFICATION' CHECK (approval_status IN ('PENDING_VERIFICATION', 'APPROVED', 'REJECTED', 'SUSPENDED')),
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                last_login TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES workers (id)
            )
        """)
        
        # 2. Tow Truck Documents Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tow_truck_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                document_type TEXT NOT NULL CHECK (document_type IN ('AADHAAR', 'PAN', 'DRIVING_LICENSE', 'VEHICLE_RC', 'INSURANCE', 'FITNESS_CERTIFICATE', 'TRUCK_FRONT', 'TRUCK_SIDE', 'TRUCK_NUMBER_PLATE')),
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verification_status TEXT DEFAULT 'PENDING' CHECK (verification_status IN ('PENDING', 'APPROVED', 'REJECTED')),
                admin_remark TEXT,
                expiry_date DATE,
                FOREIGN KEY (driver_id) REFERENCES tow_driver_profiles (id)
            )
        """)
        
        # 3. Fraud Detection Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tow_driver_fraud_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                incident_type TEXT NOT NULL CHECK (incident_type IN ('REPEATED_CANCELLATION', 'FAKE_EMERGENCY', 'MULTIPLE_DEVICE_LOGIN', 'DOCUMENT_MISMATCH')),
                incident_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (driver_id) REFERENCES tow_driver_profiles (id)
            )
        """)
        
        # Create indexes for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tow_driver_profiles_email ON tow_driver_profiles (email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tow_driver_profiles_status ON tow_driver_profiles (approval_status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tow_driver_documents_driver ON tow_truck_documents (driver_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tow_driver_documents_type ON tow_truck_documents (document_type)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tow_fraud_logs_driver ON tow_driver_fraud_logs (driver_id)")
        
        conn.commit()
        conn.close()
    
    # ==================== DRIVER PROFILE OPERATIONS ====================
    
    def create_tow_driver_profile(self, user_id: int, profile_data: Dict) -> int:
        """Create new tow truck driver profile"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO tow_driver_profiles 
                (user_id, full_name, email, phone_number, password_hash, city, service_radius_km,
                 truck_type, truck_registration_number, truck_model, truck_capacity,
                 insurance_expiry_date, fitness_expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                profile_data['full_name'],
                profile_data['email'],
                profile_data['phone_number'],
                profile_data['password_hash'],
                profile_data['city'],
                profile_data.get('service_radius_km', 10),
                profile_data['truck_type'],
                profile_data['truck_registration_number'],
                profile_data['truck_model'],
                profile_data['truck_capacity'],
                profile_data['insurance_expiry_date'],
                profile_data['fitness_expiry_date']
            ))
            
            profile_id = cur.lastrowid
            conn.commit()
            conn.close()
            
            return profile_id
        except Exception as e:
            print(f"Error creating tow driver profile: {e}")
            return 0
    
    def get_tow_driver_profile(self, driver_id: int = None, email: str = None) -> Optional[Dict]:
        """Get tow truck driver profile by ID or email"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        if driver_id:
            cur.execute("SELECT * FROM tow_driver_profiles WHERE id = ?", (driver_id,))
        elif email:
            cur.execute("SELECT * FROM tow_driver_profiles WHERE email = ?", (email,))
        else:
            conn.close()
            return None
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_tow_driver_profile(self, driver_id: int, updates: Dict) -> bool:
        """Update tow truck driver profile"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            # Build update query dynamically
            set_clauses = []
            params = []
            
            for key, value in updates.items():
                if key in ['full_name', 'phone_number', 'city', 'service_radius_km', 
                          'truck_type', 'truck_registration_number', 'truck_model', 
                          'truck_capacity', 'insurance_expiry_date', 'fitness_expiry_date',
                          'approval_status', 'admin_notes']:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            if set_clauses:
                params.append(driver_id)
                query = f"UPDATE tow_driver_profiles SET {', '.join(set_clauses)} WHERE id = ?"
                cur.execute(query, params)
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating tow driver profile: {e}")
            return False
    
    def authenticate_tow_driver(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate tow truck driver with email and password"""
        try:
            import bcrypt  # Import bcrypt for password verification
            
            profile = self.get_tow_driver_profile(email=email)
            
            if not profile:
                return None
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), profile['password_hash'].encode('utf-8')):
                return None
            
            # Check approval status
            if profile['approval_status'] != 'APPROVED':
                return None
            
            # Update last login
            self.update_tow_driver_profile(profile['id'], {'last_login': datetime.now().isoformat()})
            
            return profile
        except Exception as e:
            print(f"Error authenticating tow driver: {e}")
            return None
    
    def update_approval_status(self, driver_id: int, status: str, admin_notes: str = None) -> bool:
        """Update driver approval status"""
        updates = {'approval_status': status}
        
        if status == 'APPROVED':
            updates['approved_at'] = datetime.now().isoformat()
        
        if admin_notes:
            updates['admin_notes'] = admin_notes
        
        return self.update_tow_driver_profile(driver_id, updates)
    
    # ==================== DOCUMENT OPERATIONS ====================
    
    def upload_tow_driver_document(self, driver_id: int, document_type: str, 
                                  file_path: str, expiry_date: str = None) -> int:
        """Upload tow truck driver document"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO tow_truck_documents 
                (driver_id, document_type, file_path, expiry_date)
                VALUES (?, ?, ?, ?)
            """, (driver_id, document_type, file_path, expiry_date))
            
            doc_id = cur.lastrowid
            conn.commit()
            conn.close()
            
            return doc_id
        except Exception as e:
            print(f"Error uploading tow driver document: {e}")
            return 0
    
    def get_tow_driver_documents(self, driver_id: int) -> List[Dict]:
        """Get all documents for a tow truck driver"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM tow_truck_documents 
            WHERE driver_id = ? 
            ORDER BY uploaded_at DESC
        """, (driver_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def verify_document(self, document_id: int, status: str, admin_remark: str = None) -> bool:
        """Verify tow truck driver document"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE tow_truck_documents 
                SET verification_status = ?, admin_remark = ?
                WHERE id = ?
            """, (status, admin_remark, document_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error verifying document: {e}")
            return False
    
    def check_required_documents(self, driver_id: int) -> Dict:
        """Check if all required documents are uploaded and verified"""
        required_docs = [
            'AADHAAR', 'PAN', 'DRIVING_LICENSE', 'VEHICLE_RC', 
            'INSURANCE', 'FITNESS_CERTIFICATE', 'TRUCK_FRONT', 
            'TRUCK_SIDE', 'TRUCK_NUMBER_PLATE'
        ]
        
        documents = self.get_tow_driver_documents(driver_id)
        doc_status = {}
        
        for doc_type in required_docs:
            doc = next((d for d in documents if d['document_type'] == doc_type), None)
            doc_status[doc_type] = {
                'uploaded': doc is not None,
                'verified': doc is not None and doc['verification_status'] == 'APPROVED',
                'file_path': doc['file_path'] if doc else None,
                'expiry_date': doc['expiry_date'] if doc else None
            }
        
        return doc_status
    
    # ==================== EXPIRY MONITORING ====================
    
    def check_expiry_alerts(self, driver_id: int) -> List[Dict]:
        """Check for documents expiring soon"""
        documents = self.get_tow_driver_documents(driver_id)
        alerts = []
        
        for doc in documents:
            if doc['expiry_date'] and doc['verification_status'] == 'APPROVED':
                expiry_date = datetime.strptime(doc['expiry_date'], '%Y-%m-%d').date()
                today = datetime.now().date()
                days_until_expiry = (expiry_date - today).days
                
                if days_until_expiry <= 30:
                    alert_level = 'CRITICAL' if days_until_expiry <= 7 else 'WARNING'
                    alerts.append({
                        'document_type': doc['document_type'],
                        'days_until_expiry': days_until_expiry,
                        'alert_level': alert_level,
                        'expiry_date': doc['expiry_date']
                    })
        
        return alerts
    
    def suspend_expired_documents(self) -> List[int]:
        """Suspend drivers with expired documents"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Find drivers with expired documents
        cur.execute("""
            SELECT DISTINCT td.driver_id
            FROM tow_truck_documents td
            JOIN tow_driver_profiles tdp ON td.driver_id = tdp.id
            WHERE td.verification_status = 'APPROVED'
            AND td.expiry_date < date('now')
            AND tdp.approval_status = 'APPROVED'
        """)
        
        expired_drivers = [row['driver_id'] for row in cur.fetchall()]
        
        # Suspend expired drivers
        for driver_id in expired_drivers:
            self.update_approval_status(driver_id, 'SUSPENDED', 'Auto-suspended due to expired documents')
        
        conn.close()
        return expired_drivers
    
    # ==================== FRAUD DETECTION ====================
    
    def log_fraud_incident(self, driver_id: int, incident_type: str, incident_data: Dict) -> bool:
        """Log fraud incident for tow truck driver"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO tow_driver_fraud_logs 
                (driver_id, incident_type, incident_data)
                VALUES (?, ?, ?)
            """, (driver_id, incident_type, json.dumps(incident_data)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging fraud incident: {e}")
            return False
    
    def get_fraud_incidents(self, driver_id: int) -> List[Dict]:
        """Get fraud incidents for tow truck driver"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM tow_driver_fraud_logs 
            WHERE driver_id = ? 
            ORDER BY created_at DESC
        """, (driver_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def check_fraud_risk(self, driver_id: int) -> Dict:
        """Check fraud risk level for tow truck driver"""
        incidents = self.get_fraud_incidents(driver_id)
        
        # Calculate risk based on incident types and frequency
        risk_score = 0
        risk_factors = []
        
        incident_counts = {}
        for incident in incidents:
            incident_type = incident['incident_type']
            incident_counts[incident_type] = incident_counts.get(incident_type, 0) + 1
            
            # Risk scoring
            if incident_type == 'REPEATED_CANCELLATION':
                risk_score += incident_counts[incident_type] * 10
            elif incident_type == 'FAKE_EMERGENCY':
                risk_score += incident_counts[incident_type] * 25
            elif incident_type == 'MULTIPLE_DEVICE_LOGIN':
                risk_score += incident_counts[incident_type] * 15
            elif incident_type == 'DOCUMENT_MISMATCH':
                risk_score += incident_counts[incident_type] * 20
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'HIGH'
        elif risk_score >= 25:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'incident_counts': incident_counts,
            'total_incidents': len(incidents),
            'risk_factors': risk_factors
        }
    
    # ==================== COMPATIBILITY CHECKS ====================
    
    def check_vehicle_compatibility(self, driver_id: int, vehicle_type: str) -> bool:
        """Check if driver's truck is compatible with vehicle type"""
        profile = self.get_tow_driver_profile(driver_id)
        
        if not profile:
            return False
        
        truck_type = profile['truck_type']
        truck_capacity = profile['truck_capacity']
        
        # Compatibility matrix
        compatibility = {
            'FLATBED': ['SMALL_CAR', 'SUV', 'HEAVY_VEHICLE'],
            'WHEEL_LIFT': ['SMALL_CAR', 'SUV'],
            'HEAVY_DUTY': ['SUV', 'HEAVY_VEHICLE']
        }
        
        # Map vehicle types to capacities
        vehicle_capacity_map = {
            'SEDAN': 'SMALL_CAR',
            'HATCHBACK': 'SMALL_CAR',
            'MOTORCYCLE': 'SMALL_CAR',
            'SUV': 'SUV',
            'PICKUP': 'SUV',
            'TRUCK': 'HEAVY_VEHICLE',
            'BUS': 'HEAVY_VEHICLE',
            'VAN': 'SUV'
        }
        
        required_capacity = vehicle_capacity_map.get(vehicle_type, 'SMALL_CAR')
        
        return required_capacity in compatibility.get(truck_type, [])
    
    # ==================== ADMIN OPERATIONS ====================
    
    def get_pending_applications(self) -> List[Dict]:
        """Get all pending tow truck driver applications"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT tdp.*, w.username, w.email as worker_email
            FROM tow_driver_profiles tdp
            JOIN workers w ON tdp.user_id = w.id
            WHERE tdp.approval_status = 'PENDING_VERIFICATION'
            ORDER BY tdp.created_at DESC
        """)
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_approved_drivers(self) -> List[Dict]:
        """Get all approved tow truck drivers"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT tdp.*, w.username, w.email as worker_email
            FROM tow_driver_profiles tdp
            JOIN workers w ON tdp.user_id = w.id
            WHERE tdp.approval_status = 'APPROVED'
            ORDER BY tdp.approved_at DESC
        """)
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_driver_statistics(self) -> Dict:
        """Get tow truck driver statistics"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                approval_status,
                COUNT(*) as count
            FROM tow_driver_profiles
            GROUP BY approval_status
        """)
        
        status_counts = {row['approval_status']: row['count'] for row in cur.fetchall()}
        
        cur.execute("""
            SELECT 
                truck_type,
                COUNT(*) as count
            FROM tow_driver_profiles
            WHERE approval_status = 'APPROVED'
            GROUP BY truck_type
        """)
        
        truck_counts = {row['truck_type']: row['count'] for row in cur.fetchall()}
        
        conn.close()
        
        return {
            'status_counts': status_counts,
            'truck_counts': truck_counts,
            'total_drivers': sum(status_counts.values()),
            'approved_drivers': status_counts.get('APPROVED', 0)
        }

# Initialize database instance
tow_truck_profile_db = TowTruckProfileDB()
