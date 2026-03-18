"""
Active Fuel Delivery Engine - Phase 3 Implementation
"""

import sqlite3
import os
from datetime import datetime
from .fuel_delivery_db import fuel_delivery_db

class ActiveDeliveryService:
    def __init__(self):
        self.db = fuel_delivery_db
    
    def get_active_delivery(self, agent_id):
        """Get active delivery for an agent"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT r.*, u.name as user_name, u.phone_number as user_phone
                FROM fuel_delivery_requests r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.agent_id = ? AND r.status IN ('ASSIGNED', 'ARRIVING', 'DELIVERING')
                ORDER BY r.created_at DESC
                LIMIT 1
            ''', (agent_id,))
            
            delivery = cursor.fetchone()
            self.db.conn.commit()
            cursor.close()
            
            if delivery:
                return {
                    'request_id': delivery[0],
                    'user_id': delivery[1],
                    'user_name': delivery[7] if len(delivery) > 7 else 'N/A',
                    'user_phone': delivery[8] if len(delivery) > 8 else 'N/A',
                    'fuel_type': delivery[3],
                    'quantity_liters': delivery[4],
                    'delivery_latitude': delivery[5],
                    'delivery_longitude': delivery[6],
                    'delivery_address': delivery[7] if len(delivery) > 7 else 'N/A',
                    'status': delivery[2],
                    'created_at': delivery[8],
                    'assigned_at': delivery[9],
                    'delivery_started_at': delivery[10] if len(delivery) > 10 else None,
                    'completed_at': delivery[11] if len(delivery) > 11 else None
                }
            return None
            
        except Exception as e:
            return None
    
    def start_arrival(self, agent_id, request_id):
        """Agent starts navigation to delivery location"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE fuel_delivery_requests
                SET status = 'ARRIVING', updated_at = ?
                WHERE id = ? AND agent_id = ?
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_id, agent_id))
            
            self.db.conn.commit()
            cursor.close()
            
            # Log activity
            self._log_activity(agent_id, 'DELIVERY_ARRIVAL', {
                'request_id': request_id
            })
            
            return {'success': True, 'message': 'Navigation started'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def start_delivery(self, agent_id, request_id):
        """Agent starts fuel delivery"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE fuel_delivery_requests
                SET status = 'DELIVERING', delivery_started_at = ?
                WHERE id = ? AND agent_id = ?
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_id, agent_id))
            
            self.db.conn.commit()
            cursor.close()
            
            # Log activity
            self._log_activity(agent_id, 'DELIVERY_STARTED', {
                'request_id': request_id
            })
            
            return {'success': True, 'message': 'Delivery started'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def complete_delivery(self, agent_id, request_id, earnings_data=None):
        """Complete fuel delivery and calculate earnings"""
        try:
            cursor = self.db.conn.cursor()
            
            # Get delivery details (id is primary key of fuel_delivery_requests)
            cursor.execute('''
                SELECT * FROM fuel_delivery_requests
                WHERE id = ? AND agent_id = ?
            ''', (request_id, agent_id))
            
            delivery = cursor.fetchone()
            if not delivery:
                return {'success': False, 'error': 'Delivery not found'}
            
            # delivery columns: id, user_id, agent_id, user_name, user_phone, fuel_type, quantity, latitude, longitude, address, status, ...
            request_pk = delivery[0]
            user_id = delivery[1]
            fuel_type = delivery[5]
            quantity = delivery[6]
            
            # Calculate earnings
            fuel_cost = quantity * 100  # ₹100 per liter
            base_fee = 50  # ₹50 base fee
            emergency_fee = 0  # No emergency fee for normal delivery
            total_bill = fuel_cost + base_fee + emergency_fee
            agent_earning = total_bill * 0.70  # 70% commission
            platform_share = total_bill * 0.30  # 30% platform
            
            # Update delivery status
            cursor.execute('''
                UPDATE fuel_delivery_requests
                SET status = 'COMPLETED', completed_at = ?
                WHERE id = ? AND agent_id = ?
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_id, agent_id))
            
            # Add to delivery history (with request_id for join to get address later)
            cursor.execute('''
                INSERT INTO fuel_delivery_history
                (agent_id, user_id, fuel_type, quantity, earnings, status, completed_at, request_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (agent_id, user_id, fuel_type, quantity, agent_earning, 'COMPLETED', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_pk))
            
            # Update agent status to ONLINE_AVAILABLE
            cursor.execute('''
                UPDATE fuel_delivery_agents
                SET online_status = 'ONLINE_AVAILABLE', total_deliveries = total_deliveries + 1
                WHERE id = ?
            ''', (agent_id,))
            
            self.db.conn.commit()
            cursor.close()
            
            # Log activity
            self._log_activity(agent_id, 'DELIVERY_COMPLETED', {
                'request_id': request_id,
                'earnings': agent_earning,
                'total_bill': total_bill
            })
            
            return {
                'success': True,
                'message': 'Delivery completed successfully',
                'earnings': agent_earning,
                'total_bill': total_bill
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_agent_location(self, agent_id, latitude, longitude):
        """Update agent live location"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO fuel_agent_live_locations
                (agent_id, latitude, longitude, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, latitude, longitude, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            self.db.conn.commit()
            cursor.close()
            
            # Log activity
            self._log_activity(agent_id, 'LOCATION_UPDATED', {
                'latitude': latitude,
                'longitude': longitude
            })
            
            return {'success': True, 'message': 'Location updated'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def upload_delivery_proof(self, agent_id, request_id, proof_image_path):
        """Upload delivery proof image"""
        try:
            if not os.path.exists(proof_image_path):
                return {'success': False, 'error': 'Proof image not found'}
            
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO fuel_delivery_proofs
                (request_id, image_path, uploaded_at)
                VALUES (?, ?, ?)
            ''', (request_id, proof_image_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            self.db.conn.commit()
            cursor.close()
            
            # Log activity
            self._log_activity(agent_id, 'PROOF_UPLOADED', {
                'request_id': request_id,
                'proof_path': proof_image_path
            })
            
            return {'success': True, 'message': 'Proof uploaded successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _log_activity(self, agent_id, event_type, details=None):
        """Log agent activity"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO fuel_agent_activity_logs
                (agent_id, activity_type, activity_details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, event_type, str(details) if details else None, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            self.db.conn.commit()
            cursor.close()
        except Exception:
            pass  # Don't fail main flow due to logging errors

# Create service instance
active_delivery_service = ActiveDeliveryService()
