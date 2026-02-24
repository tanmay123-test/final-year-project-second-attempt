"""
Fuel Delivery Agent Database Module
Complete database operations for fuel delivery agent management system
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import json

class FuelAgentDB:
    """Complete database operations for Fuel Delivery Agent System"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default path in car_service directory
            self.db_path = os.path.join(os.path.dirname(__file__), "fuel_agent.db")
        else:
            self.db_path = db_path
        
        self.init_database()
    
    def get_conn(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize all fuel agent tables"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # 1. Fuel Agent Status Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fuel_agent_status (
                agent_id INTEGER PRIMARY KEY,
                online_status TEXT DEFAULT 'OFFLINE' CHECK (online_status IN ('ONLINE', 'OFFLINE')),
                is_busy BOOLEAN DEFAULT FALSE,
                last_location_lat REAL,
                last_location_long REAL,
                priority_score REAL DEFAULT 0.0,
                last_status_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES workers (id)
            )
        """)
        
        # 2. Fuel Orders Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fuel_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                assigned_agent_id INTEGER,
                fuel_type TEXT NOT NULL CHECK (fuel_type IN ('PETROL', 'DIESEL')),
                quantity_liters REAL NOT NULL,
                location_lat REAL NOT NULL,
                location_long REAL NOT NULL,
                distance_km REAL,
                estimated_earning_min REAL,
                estimated_earning_max REAL,
                estimated_duration INTEGER,
                customer_rating REAL,
                status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACCEPTED', 'ON_THE_WAY', 'ARRIVED', 'DELIVERED', 'CANCELLED')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assigned_agent_id) REFERENCES workers (id)
            )
        """)
        
        # 3. Delivery Proofs Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS delivery_proofs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                fuel_meter_photo_path TEXT,
                delivery_confirmation_photo_path TEXT,
                delivery_notes TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES fuel_orders (id)
            )
        """)
        
        # 4. Fuel Agent Earnings Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fuel_agent_earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                order_id INTEGER NOT NULL,
                order_amount REAL NOT NULL,
                platform_commission REAL NOT NULL,
                agent_earning REAL NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES workers (id),
                FOREIGN KEY (order_id) REFERENCES fuel_orders (id)
            )
        """)
        
        # 5. Fuel Agent Metrics Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fuel_agent_metrics (
                agent_id INTEGER PRIMARY KEY,
                completion_rate REAL DEFAULT 0.0,
                on_time_rate REAL DEFAULT 0.0,
                acceptance_rate REAL DEFAULT 0.0,
                cancellation_rate REAL DEFAULT 0.0,
                trust_score REAL DEFAULT 0.0,
                total_deliveries INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES workers (id)
            )
        """)
        
        # 6. Fuel Agent Emergency Alerts Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fuel_agent_emergency_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'RESOLVED')),
                FOREIGN KEY (agent_id) REFERENCES workers (id)
            )
        """)
        
        # Create indexes for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_fuel_orders_status ON fuel_orders (status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_fuel_orders_agent ON fuel_orders (assigned_agent_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_fuel_earnings_agent ON fuel_agent_earnings (agent_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_fuel_earnings_date ON fuel_agent_earnings (date)")
        
        conn.commit()
        conn.close()
    
    # ==================== FUEL AGENT STATUS OPERATIONS ====================
    
    def update_fuel_agent_status(self, agent_id: int, online_status: str = None, 
                              is_busy: bool = None, lat: float = None, 
                              lng: float = None) -> bool:
        """Update fuel agent online status and location"""
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
            
            if updates:
                updates.append("last_status_change = CURRENT_TIMESTAMP")
                params.append(agent_id)
                
                query = f"UPDATE fuel_agent_status SET {', '.join(updates)} WHERE agent_id = ?"
                cur.execute(query, params)
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating fuel agent status: {e}")
            return False
    
    def get_fuel_agent_status(self, agent_id: int) -> Optional[Dict]:
        """Get fuel agent current status"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT fas.*, w.username, w.email 
            FROM fuel_agent_status fas
            JOIN workers w ON fas.agent_id = w.id
            WHERE fas.agent_id = ?
        """, (agent_id,))
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def calculate_fuel_agent_priority_score(self, agent_id: int) -> float:
        """Calculate priority score based on metrics"""
        try:
            metrics = self.get_fuel_agent_metrics(agent_id)
            if not metrics:
                return 0.0
            
            # Priority formula as specified
            priority = (metrics['completion_rate'] * 0.4) + \
                     (metrics['on_time_rate'] * 0.3) + \
                     (metrics['acceptance_rate'] * 0.3)
            
            # Update in database
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE fuel_agent_status SET priority_score = ? WHERE agent_id = ?", 
                      (priority, agent_id))
            conn.commit()
            conn.close()
            
            return round(priority, 2)
        except Exception as e:
            print(f"Error calculating fuel agent priority score: {e}")
            return 0.0
    
    # ==================== FUEL ORDER OPERATIONS ====================
    
    def create_fuel_order(self, user_id: int, fuel_type: str, quantity: float,
                        lat: float, lng: float, estimated_min: float, 
                        estimated_max: float, duration: int) -> int:
        """Create new fuel order request"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO fuel_orders 
            (user_id, fuel_type, quantity_liters, location_lat, location_long, 
             estimated_earning_min, estimated_earning_max, estimated_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, fuel_type, quantity, lat, lng, 
               estimated_min, estimated_max, duration))
        
        order_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return order_id
    
    def get_pending_fuel_orders(self, agent_id: int = None, fuel_type: str = None) -> List[Dict]:
        """Get pending fuel orders with optional filtering"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        query = """
            SELECT fo.*, u.username as customer_name, u.email as customer_email
            FROM fuel_orders fo
            JOIN users u ON fo.user_id = u.id
            WHERE fo.status = 'PENDING'
        """
        params = []
        
        if fuel_type:
            query += " AND fo.fuel_type = ?"
            params.append(fuel_type)
        
        query += " ORDER BY fo.created_at DESC"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def accept_fuel_order(self, order_id: int, agent_id: int) -> bool:
        """Accept a fuel order request"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE fuel_orders 
                SET assigned_agent_id = ?, status = 'ACCEPTED'
                WHERE id = ? AND status = 'PENDING'
            """, (agent_id, order_id))
            
            # Mark agent as busy
            self.update_fuel_agent_status(agent_id, is_busy=True)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error accepting fuel order: {e}")
            return False
    
    def update_fuel_order_status(self, order_id: int, status: str, agent_id: int) -> bool:
        """Update fuel order status through lifecycle"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE fuel_orders 
                SET status = ? 
                WHERE id = ? AND assigned_agent_id = ?
            """, (status, order_id, agent_id))
            
            # If order is delivered, set completion time
            if status == 'DELIVERED':
                cur.execute("""
                    UPDATE fuel_orders 
                    SET completed_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (order_id,))
                
                # Mark agent as not busy
                self.update_fuel_agent_status(agent_id, is_busy=False)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating fuel order status: {e}")
            return False
    
    def get_active_fuel_deliveries(self, agent_id: int) -> List[Dict]:
        """Get fuel agent's active deliveries"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT fo.*, u.username as customer_name, u.email as customer_email
            FROM fuel_orders fo
            JOIN users u ON fo.user_id = u.id
            WHERE fo.assigned_agent_id = ? 
            AND fo.status IN ('ACCEPTED', 'ON_THE_WAY', 'ARRIVED')
            ORDER BY fo.created_at DESC
        """, (agent_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== EARNINGS OPERATIONS ====================
    
    def add_fuel_earning(self, agent_id: int, order_id: int, order_amount: float) -> bool:
        """Add fuel delivery earning with commission calculation"""
        try:
            # Platform commission (20%)
            commission_rate = 0.20
            platform_commission = order_amount * commission_rate
            agent_earning = order_amount - platform_commission
            
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO fuel_agent_earnings 
                (agent_id, order_id, order_amount, platform_commission, agent_earning, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (agent_id, order_id, order_amount, platform_commission, 
                   agent_earning, datetime.now().date()))
            
            conn.commit()
            conn.close()
            
            # Update metrics
            self.update_delivery_completion_metrics(agent_id)
            return True
        except Exception as e:
            print(f"Error adding fuel earning: {e}")
            return False
    
    def get_fuel_agent_earnings(self, agent_id: int, period: str = 'all') -> Dict:
        """Get fuel agent earnings with period filtering"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Date filtering
        date_filter = ""
        params = [agent_id]
        
        if period == 'today':
            date_filter = "AND date = CURRENT_DATE"
        elif period == 'week':
            date_filter = "AND date >= date('now', '-7 days')"
        elif period == 'month':
            date_filter = "AND date >= date('now', '-1 month')"
        
        cur.execute(f"""
            SELECT 
                SUM(order_amount) as total_earnings,
                SUM(platform_commission) as total_commission,
                SUM(agent_earning) as net_earnings,
                COUNT(*) as delivery_count,
                AVG(agent_earning) as avg_earning
            FROM fuel_agent_earnings 
            WHERE agent_id = ? {date_filter}
        """, params)
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else {
            'total_earnings': 0, 'total_commission': 0, 
            'net_earnings': 0, 'delivery_count': 0, 'avg_earning': 0
        }
    
    # ==================== METRICS OPERATIONS ====================
    
    def get_fuel_agent_metrics(self, agent_id: int) -> Optional[Dict]:
        """Get fuel agent performance metrics"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM fuel_agent_metrics WHERE agent_id = ?
        """, (agent_id,))
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else {
            'completion_rate': 0.0, 'on_time_rate': 0.0, 
            'acceptance_rate': 0.0, 'cancellation_rate': 0.0,
            'trust_score': 0.0, 'total_deliveries': 0
        }
    
    def update_delivery_completion_metrics(self, agent_id: int) -> None:
        """Update metrics after delivery completion"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            # Calculate new metrics
            cur.execute("""
                SELECT 
                    COUNT(*) as total_deliveries,
                    SUM(CASE WHEN status = 'DELIVERED' THEN 1 ELSE 0 END) as completed_deliveries,
                    SUM(CASE WHEN status = 'DELIVERED' AND 
                        julianday(completed_at) - julianday(created_at) <= estimated_duration THEN 1 ELSE 0 END) as on_time_deliveries
                FROM fuel_orders 
                WHERE assigned_agent_id = ?
            """, (agent_id,))
            
            row = cur.fetchone()
            total_deliveries = row['total_deliveries'] or 0
            completed_deliveries = row['completed_deliveries'] or 0
            on_time_deliveries = row['on_time_deliveries'] or 0
            
            # Calculate rates
            completion_rate = (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
            on_time_rate = (on_time_deliveries / completed_deliveries * 100) if completed_deliveries > 0 else 0
            
            # Update metrics
            cur.execute("""
                INSERT OR REPLACE INTO fuel_agent_metrics 
                (agent_id, completion_rate, on_time_rate, total_deliveries, last_updated)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (agent_id, completion_rate, on_time_rate, total_deliveries))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating fuel agent metrics: {e}")
    
    # ==================== EMERGENCY OPERATIONS ====================
    
    def create_fuel_emergency_alert(self, agent_id: int, lat: float, lng: float) -> bool:
        """Create emergency SOS alert for fuel agent"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO fuel_agent_emergency_alerts 
                (agent_id, latitude, longitude)
                VALUES (?, ?, ?)
            """, (agent_id, lat, lng))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating fuel emergency alert: {e}")
            return False
    
    def get_fuel_emergency_alerts(self, agent_id: int) -> List[Dict]:
        """Get fuel agent's emergency alerts"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM fuel_agent_emergency_alerts 
            WHERE agent_id = ? 
            ORDER BY alert_time DESC
        """, (agent_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== DELIVERY PROOF OPERATIONS ====================
    
    def upload_delivery_proof(self, order_id: int, fuel_meter_path: str, 
                         delivery_photo_path: str, notes: str) -> bool:
        """Upload fuel delivery completion proof"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO delivery_proofs 
                (order_id, fuel_meter_photo_path, delivery_confirmation_photo_path, delivery_notes)
                VALUES (?, ?, ?, ?)
            """, (order_id, fuel_meter_path, delivery_photo_path, notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error uploading delivery proof: {e}")
            return False
    
    def get_delivery_proofs(self, order_id: int) -> List[Dict]:
        """Get proofs for a specific fuel order"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM delivery_proofs WHERE order_id = ?
            ORDER BY uploaded_at DESC
        """, (order_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== DEMAND ANALYSIS ====================
    
    def get_fuel_demand_analysis(self) -> Dict:
        """Get current fuel market demand analysis"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Count pending orders by fuel type
        cur.execute("""
            SELECT 
                fuel_type,
                COUNT(*) as pending_count,
                AVG(estimated_earning_min) as avg_min_earning,
                AVG(estimated_earning_max) as avg_max_earning,
                AVG(quantity_liters) as avg_quantity
            FROM fuel_orders 
            WHERE status = 'PENDING'
            GROUP BY fuel_type
            ORDER BY pending_count DESC
        """)
        
        fuel_demand = [dict(row) for row in cur.fetchall()]
        
        # Get online agents count
        cur.execute("""
            SELECT COUNT(*) as online_count FROM fuel_agent_status 
            WHERE online_status = 'ONLINE' AND is_busy = FALSE
        """)
        
        online_count = cur.fetchone()['online_count']
        
        conn.close()
        
        return {
            'fuel_demand': fuel_demand,
            'online_agents': online_count,
            'demand_level': self._calculate_fuel_demand_level(len(fuel_demand)),
            'peak_hour': self._is_peak_hour(),
            'fuel_shortage_alert': self._check_fuel_shortage(fuel_demand)
        }
    
    def _calculate_fuel_demand_level(self, pending_orders_count: int) -> str:
        """Calculate fuel demand level based on pending orders"""
        if pending_orders_count >= 15:
            return 'HIGH'
        elif pending_orders_count >= 8:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _is_peak_hour(self) -> bool:
        """Check if current time is peak delivery hour"""
        current_hour = datetime.now().hour
        return 7 <= current_hour <= 19  # Extended delivery hours
    
    def _check_fuel_shortage(self, fuel_demand: List[Dict]) -> bool:
        """Check for fuel shortage alerts"""
        # Check if petrol demand is unusually high
        petrol_demand = next((item for item in fuel_demand if item['fuel_type'] == 'PETROL'), None)
        
        if petrol_demand and petrol_demand['pending_count'] > 10:
            return True
        
        return False

# Initialize database instance
fuel_agent_db = FuelAgentDB()
