"""
Tow Truck Driver Database Module
Complete database operations for tow truck driver management system
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import json

class TowTruckDB:
    """Complete database operations for Tow Truck Driver System"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default path in car_service directory
            self.db_path = os.path.join(os.path.dirname(__file__), "tow_truck.db")
        else:
            self.db_path = db_path
        
        self.init_database()
    
    def get_conn(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize all tow truck tables"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # 1. Tow Driver Status Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tow_driver_status (
                driver_id INTEGER PRIMARY KEY,
                online_status TEXT DEFAULT 'OFFLINE' CHECK (online_status IN ('ONLINE', 'OFFLINE')),
                is_busy BOOLEAN DEFAULT FALSE,
                last_location_lat REAL,
                last_location_long REAL,
                priority_score REAL DEFAULT 0.0,
                truck_type TEXT DEFAULT 'FLATBED' CHECK (truck_type IN ('FLATBED', 'WHEEL_LIFT', 'HEAVY_DUTY')),
                last_status_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (driver_id) REFERENCES workers (id)
            )
        """)
        
        # 2. Tow Requests Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tow_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                assigned_driver_id INTEGER,
                vehicle_type TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                pickup_lat REAL NOT NULL,
                pickup_long REAL NOT NULL,
                drop_lat REAL NOT NULL,
                drop_long REAL NOT NULL,
                distance_km REAL,
                estimated_duration INTEGER,
                estimated_price_min REAL,
                estimated_price_max REAL,
                risk_level TEXT DEFAULT 'LOW' CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
                status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACCEPTED', 'ON_THE_WAY', 'ARRIVED', 'LOADING', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assigned_driver_id) REFERENCES workers (id)
            )
        """)
        
        # 3. Towing Proofs Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS towing_proofs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tow_request_id INTEGER NOT NULL,
                pickup_photo_path TEXT,
                vehicle_loaded_photo_path TEXT,
                drop_photo_path TEXT,
                damage_notes TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tow_request_id) REFERENCES tow_requests (id)
            )
        """)
        
        # 4. Tow Driver Earnings Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tow_driver_earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                tow_request_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                platform_commission REAL NOT NULL,
                driver_earning REAL NOT NULL,
                distance_km REAL NOT NULL,
                risk_bonus REAL DEFAULT 0.0,
                date DATE NOT NULL,
                FOREIGN KEY (driver_id) REFERENCES workers (id),
                FOREIGN KEY (tow_request_id) REFERENCES tow_requests (id)
            )
        """)
        
        # 5. Tow Driver Metrics Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tow_driver_metrics (
                driver_id INTEGER PRIMARY KEY,
                completion_rate REAL DEFAULT 0.0,
                on_time_rate REAL DEFAULT 0.0,
                acceptance_rate REAL DEFAULT 0.0,
                risk_handling_score REAL DEFAULT 0.0,
                trust_score REAL DEFAULT 0.0,
                total_tows INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (driver_id) REFERENCES workers (id)
            )
        """)
        
        # 6. Tow Driver Emergency Alerts Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tow_driver_emergency_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'RESOLVED')),
                FOREIGN KEY (driver_id) REFERENCES workers (id)
            )
        """)
        
        # Create indexes for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tow_requests_status ON tow_requests (status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tow_requests_driver ON tow_requests (assigned_driver_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tow_earnings_driver ON tow_driver_earnings (driver_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tow_earnings_date ON tow_driver_earnings (date)")
        
        conn.commit()
        conn.close()
    
    # ==================== TOW DRIVER STATUS OPERATIONS ====================
    
    def update_tow_driver_status(self, driver_id: int, online_status: str = None, 
                                is_busy: bool = None, lat: float = None, 
                                lng: float = None, truck_type: str = None) -> bool:
        """Update tow driver online status and location"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if online_status is not None:
                updates.append("online_status = ?")
                params.append(online_status)
            
            if is_busy is not None:
                updates.append("is_busy = ?")
                params.append(is_busy)
            
            if lat is not None:
                updates.append("last_location_lat = ?")
                params.append(lat)
            
            if lng is not None:
                updates.append("last_location_long = ?")
                params.append(lng)
            
            if truck_type is not None:
                updates.append("truck_type = ?")
                params.append(truck_type)
            
            if updates:
                updates.append("last_status_change = CURRENT_TIMESTAMP")
                params.append(driver_id)
                
                query = f"UPDATE tow_driver_status SET {', '.join(updates)} WHERE driver_id = ?"
                cur.execute(query, params)
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating tow driver status: {e}")
            return False
    
    def get_tow_driver_status(self, driver_id: int) -> Optional[Dict]:
        """Get tow driver current status"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT tds.*, w.username, w.email 
            FROM tow_driver_status tds
            JOIN workers w ON tds.driver_id = w.id
            WHERE tds.driver_id = ?
        """, (driver_id,))
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def calculate_tow_driver_priority_score(self, driver_id: int) -> float:
        """Calculate priority score based on metrics"""
        try:
            metrics = self.get_tow_driver_metrics(driver_id)
            if not metrics:
                return 0.0
            
            # Priority formula as specified
            priority = (metrics['completion_rate'] * 0.4) + \
                     (metrics['on_time_rate'] * 0.3) + \
                     (metrics['acceptance_rate'] * 0.3)
            
            # Update in database
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE tow_driver_status SET priority_score = ? WHERE driver_id = ?", 
                      (priority, driver_id))
            conn.commit()
            conn.close()
            
            return round(priority, 2)
        except Exception as e:
            print(f"Error calculating tow driver priority score: {e}")
            return 0.0
    
    # ==================== TOW REQUEST OPERATIONS ====================
    
    def create_tow_request(self, user_id: int, vehicle_type: str, issue_type: str,
                          pickup_lat: float, pickup_long: float, drop_lat: float, 
                          drop_long: float, distance: float, duration: int,
                          price_min: float, price_max: float, risk_level: str) -> int:
        """Create new tow request"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO tow_requests 
            (user_id, vehicle_type, issue_type, pickup_lat, pickup_long, 
             drop_lat, drop_long, distance_km, estimated_duration, 
             estimated_price_min, estimated_price_max, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, vehicle_type, issue_type, pickup_lat, pickup_long, 
               drop_lat, drop_long, distance, duration, price_min, price_max, risk_level))
        
        request_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return request_id
    
    def get_pending_tow_requests(self, driver_id: int = None, truck_type: str = None) -> List[Dict]:
        """Get pending tow requests with optional filtering"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        query = """
            SELECT tr.*, u.username as customer_name, u.email as customer_email
            FROM tow_requests tr
            JOIN users u ON tr.user_id = u.id
            WHERE tr.status = 'PENDING'
        """
        params = []
        
        if truck_type:
            # Filter by truck type compatibility
            if truck_type == 'HEAVY_DUTY':
                query += " AND tr.vehicle_type IN ('TRUCK', 'BUS', 'HEAVY_VEHICLE')"
            elif truck_type == 'FLATBED':
                query += " AND tr.vehicle_type IN ('SUV', 'SEDAN', 'HATCHBACK')"
            elif truck_type == 'WHEEL_LIFT':
                query += " AND tr.vehicle_type IN ('SEDAN', 'HATCHBACK', 'MOTORCYCLE')"
        
        query += " ORDER BY tr.created_at DESC"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def accept_tow_request(self, request_id: int, driver_id: int) -> bool:
        """Accept a tow request"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE tow_requests 
                SET assigned_driver_id = ?, status = 'ACCEPTED'
                WHERE id = ? AND status = 'PENDING'
            """, (driver_id, request_id))
            
            # Mark driver as busy
            self.update_tow_driver_status(driver_id, is_busy=True)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error accepting tow request: {e}")
            return False
    
    def update_tow_request_status(self, request_id: int, status: str, driver_id: int) -> bool:
        """Update tow request status through lifecycle"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE tow_requests 
                SET status = ? 
                WHERE id = ? AND assigned_driver_id = ?
            """, (status, request_id, driver_id))
            
            # If tow is completed, set completion time
            if status == 'COMPLETED':
                cur.execute("""
                    UPDATE tow_requests 
                    SET completed_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (request_id,))
                
                # Mark driver as not busy
                self.update_tow_driver_status(driver_id, is_busy=False)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating tow request status: {e}")
            return False
    
    def get_active_tow_operations(self, driver_id: int) -> List[Dict]:
        """Get tow driver's active towing operations"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT tr.*, u.username as customer_name, u.email as customer_email
            FROM tow_requests tr
            JOIN users u ON tr.user_id = u.id
            WHERE tr.assigned_driver_id = ? 
            AND tr.status IN ('ACCEPTED', 'ON_THE_WAY', 'ARRIVED', 'LOADING', 'IN_TRANSIT')
            ORDER BY tr.created_at DESC
        """, (driver_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== EARNINGS OPERATIONS ====================
    
    def add_tow_earning(self, driver_id: int, request_id: int, total_amount: float, 
                       distance_km: float, risk_bonus: float = 0.0) -> bool:
        """Add tow earning with commission calculation"""
        try:
            # Platform commission (20%)
            commission_rate = 0.20
            platform_commission = total_amount * commission_rate
            driver_earning = total_amount - platform_commission + risk_bonus
            
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO tow_driver_earnings 
                (driver_id, tow_request_id, total_amount, platform_commission, 
                 driver_earning, distance_km, risk_bonus, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (driver_id, request_id, total_amount, platform_commission, 
                   driver_earning, distance_km, risk_bonus, datetime.now().date()))
            
            conn.commit()
            conn.close()
            
            # Update metrics
            self.update_tow_completion_metrics(driver_id)
            return True
        except Exception as e:
            print(f"Error adding tow earning: {e}")
            return False
    
    def get_tow_driver_earnings(self, driver_id: int, period: str = 'all') -> Dict:
        """Get tow driver earnings with period filtering"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Date filtering
        date_filter = ""
        params = [driver_id]
        
        if period == 'today':
            date_filter = "AND date = CURRENT_DATE"
        elif period == 'week':
            date_filter = "AND date >= date('now', '-7 days')"
        elif period == 'month':
            date_filter = "AND date >= date('now', '-1 month')"
        
        cur.execute(f"""
            SELECT 
                SUM(total_amount) as total_earnings,
                SUM(platform_commission) as total_commission,
                SUM(driver_earning) as net_earnings,
                SUM(risk_bonus) as total_risk_bonus,
                SUM(distance_km) as total_distance,
                COUNT(*) as tow_count,
                AVG(driver_earning) as avg_earning,
                AVG(distance_km) as avg_distance
            FROM tow_driver_earnings 
            WHERE driver_id = ? {date_filter}
        """, params)
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else {
            'total_earnings': 0, 'total_commission': 0, 'net_earnings': 0,
            'total_risk_bonus': 0, 'total_distance': 0, 'tow_count': 0,
            'avg_earning': 0, 'avg_distance': 0
        }
    
    # ==================== METRICS OPERATIONS ====================
    
    def get_tow_driver_metrics(self, driver_id: int) -> Optional[Dict]:
        """Get tow driver performance metrics"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM tow_driver_metrics WHERE driver_id = ?
        """, (driver_id,))
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else {
            'completion_rate': 0.0, 'on_time_rate': 0.0, 'acceptance_rate': 0.0,
            'risk_handling_score': 0.0, 'trust_score': 0.0, 'total_tows': 0
        }
    
    def update_tow_completion_metrics(self, driver_id: int) -> None:
        """Update metrics after tow completion"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            # Calculate new metrics
            cur.execute("""
                SELECT 
                    COUNT(*) as total_tows,
                    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_tows,
                    SUM(CASE WHEN status = 'COMPLETED' AND 
                        julianday(completed_at) - julianday(created_at) <= estimated_duration THEN 1 ELSE 0 END) as on_time_tows,
                    SUM(CASE WHEN risk_level = 'HIGH' AND status = 'COMPLETED' THEN 1 ELSE 0 END) as high_risk_tows
                FROM tow_requests 
                WHERE assigned_driver_id = ?
            """, (driver_id,))
            
            row = cur.fetchone()
            total_tows = row['total_tows'] or 0
            completed_tows = row['completed_tows'] or 0
            on_time_tows = row['on_time_tows'] or 0
            high_risk_tows = row['high_risk_tows'] or 0
            
            # Calculate rates
            completion_rate = (completed_tows / total_tows * 100) if total_tows > 0 else 0
            on_time_rate = (on_time_tows / completed_tows * 100) if completed_tows > 0 else 0
            risk_handling_score = (high_risk_tows / completed_tows * 100) if completed_tows > 0 else 0
            
            # Update metrics
            cur.execute("""
                INSERT OR REPLACE INTO tow_driver_metrics 
                (driver_id, completion_rate, on_time_rate, risk_handling_score, total_tows, last_updated)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (driver_id, completion_rate, on_time_rate, risk_handling_score, total_tows))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating tow driver metrics: {e}")
    
    # ==================== EMERGENCY OPERATIONS ====================
    
    def create_tow_emergency_alert(self, driver_id: int, lat: float, lng: float) -> bool:
        """Create emergency SOS alert for tow driver"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO tow_driver_emergency_alerts 
                (driver_id, latitude, longitude)
                VALUES (?, ?, ?)
            """, (driver_id, lat, lng))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating tow emergency alert: {e}")
            return False
    
    def get_tow_emergency_alerts(self, driver_id: int) -> List[Dict]:
        """Get tow driver's emergency alerts"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM tow_driver_emergency_alerts 
            WHERE driver_id = ? 
            ORDER BY alert_time DESC
        """, (driver_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== TOWING PROOF OPERATIONS ====================
    
    def upload_towing_proof(self, request_id: int, pickup_path: str, 
                           loaded_path: str, drop_path: str, notes: str) -> bool:
        """Upload tow operation completion proof"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO towing_proofs 
                (tow_request_id, pickup_photo_path, vehicle_loaded_photo_path, drop_photo_path, damage_notes)
                VALUES (?, ?, ?, ?, ?)
            """, (request_id, pickup_path, loaded_path, drop_path, notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error uploading towing proof: {e}")
            return False
    
    def get_towing_proofs(self, request_id: int) -> List[Dict]:
        """Get proofs for a specific tow request"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM towing_proofs WHERE tow_request_id = ?
            ORDER BY uploaded_at DESC
        """, (request_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== EMERGENCY ZONE ANALYSIS ====================
    
    def get_emergency_zone_analysis(self) -> Dict:
        """Get current emergency zone demand analysis"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Count pending requests by risk level
        cur.execute("""
            SELECT 
                risk_level,
                COUNT(*) as pending_count,
                AVG(estimated_price_min) as avg_min_price,
                AVG(estimated_price_max) as avg_max_price,
                AVG(distance_km) as avg_distance
            FROM tow_requests 
            WHERE status = 'PENDING'
            GROUP BY risk_level
            ORDER BY pending_count DESC
        """)
        
        risk_demand = [dict(row) for row in cur.fetchall()]
        
        # Get online drivers count
        cur.execute("""
            SELECT COUNT(*) as online_count FROM tow_driver_status 
            WHERE online_status = 'ONLINE' AND is_busy = FALSE
        """)
        
        online_count = cur.fetchone()['online_count']
        
        # Get high incident zones (areas with most requests)
        cur.execute("""
            SELECT 
                CASE 
                    WHEN pickup_lat BETWEEN 19.0 AND 19.2 AND pickup_long BETWEEN 72.8 AND 73.0 THEN 'Eastern Express Highway'
                    WHEN pickup_lat BETWEEN 19.05 AND 19.15 AND pickup_long BETWEEN 72.82 AND 72.92 THEN 'Western Express Highway'
                    WHEN pickup_lat BETWEEN 19.07 AND 19.12 AND pickup_long BETWEEN 72.85 AND 72.90 THEN 'Bandra-Worli Sea Link'
                    ELSE 'Other Areas'
                END as zone,
                COUNT(*) as incident_count
            FROM tow_requests 
            WHERE status = 'PENDING' AND created_at >= datetime('now', '-2 hours')
            GROUP BY zone
            ORDER BY incident_count DESC
            LIMIT 5
        """)
        
        high_incident_zones = [dict(row) for row in cur.fetchall()]
        
        conn.close()
        
        return {
            'risk_demand': risk_demand,
            'online_drivers': online_count,
            'emergency_demand_level': self._calculate_emergency_demand_level(len(risk_demand)),
            'high_incident_zones': high_incident_zones,
            'heavy_vehicle_alert': self._check_heavy_vehicle_alert(risk_demand),
            'surge_pricing_active': self._check_surge_pricing(risk_demand)
        }
    
    def _calculate_emergency_demand_level(self, pending_requests_count: int) -> str:
        """Calculate emergency demand level"""
        if pending_requests_count >= 10:
            return 'HIGH'
        elif pending_requests_count >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _check_heavy_vehicle_alert(self, risk_demand: List[Dict]) -> int:
        """Check for heavy vehicle alerts"""
        heavy_count = 0
        for demand in risk_demand:
            if demand['risk_level'] == 'HIGH':
                heavy_count += demand['pending_count']
        return heavy_count
    
    def _check_surge_pricing(self, risk_demand: List[Dict]) -> bool:
        """Check if surge pricing is active"""
        high_risk_count = sum(demand['pending_count'] for demand in risk_demand if demand['risk_level'] == 'HIGH')
        return high_risk_count >= 3

# Initialize database instance
tow_truck_db = TowTruckDB()
