"""
Active Fuel Delivery Engine - Phase 3 Implementation
"""

import os
from datetime import datetime
from .fuel_delivery_db import fuel_delivery_db

class ActiveDeliveryService:
    def __init__(self):
        self.db = fuel_delivery_db
    
    def get_active_delivery(self, agent_id):
        """Get active delivery for an agent"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT r.*, u.name as user_name, u.phone_number as user_phone
                FROM fuel_delivery_requests r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.agent_id = %s AND r.status IN ('ASSIGNED', 'ARRIVING', 'DELIVERING')
                ORDER BY r.created_at DESC
                LIMIT 1
            ''', (agent_id,))
            
            delivery = cursor.fetchone()
            conn.commit()
            
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
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()
    
    def start_arrival(self, agent_id, request_id):
        """Agent starts navigation to delivery location"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_requests
                SET status = 'ARRIVING', updated_at = %s
                WHERE id = %s AND agent_id = %s
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_id, agent_id))
            
            conn.commit()
            
            # Log activity
            self._log_activity(agent_id, 'DELIVERY_ARRIVAL', {
                'request_id': request_id
            })
            
            return {'success': True, 'message': 'Navigation started'}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def start_delivery(self, agent_id, request_id):
        """Agent starts fuel delivery"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE fuel_delivery_requests
                SET status = 'DELIVERING', delivery_started_at = %s
                WHERE id = %s AND agent_id = %s
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_id, agent_id))
            
            conn.commit()
            
            # Log activity
            self._log_activity(agent_id, 'DELIVERY_STARTED', {
                'request_id': request_id
            })
            
            return {'success': True, 'message': 'Delivery started'}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def complete_delivery(self, agent_id, request_id, earnings_data=None):
        """Complete fuel delivery and calculate earnings"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            # Get delivery details (id is primary key of fuel_delivery_requests)
            cursor.execute('''
                SELECT * FROM fuel_delivery_requests
                WHERE id = %s AND agent_id = %s
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
            fuel_cost = quantity * 100  #  100 per liter
            base_fee = 50  #  50 base fee
            emergency_fee = 0  # No emergency fee for normal delivery
            total_bill = fuel_cost + base_fee + emergency_fee
            agent_earning = total_bill * 0.70  # 70% commission
            platform_share = total_bill * 0.30  # 30% platform
            
            # Update delivery status
            cursor.execute('''
                UPDATE fuel_delivery_requests
                SET status = 'COMPLETED', completed_at = %s
                WHERE id = %s AND agent_id = %s
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_id, agent_id))
            
            # Add to delivery history (with request_id for join to get address later)
            cursor.execute('''
                INSERT INTO fuel_delivery_history
                (agent_id, user_id, fuel_type, quantity, earnings, status, completed_at, request_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (agent_id, user_id, fuel_type, quantity, agent_earning, 'COMPLETED', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_pk))
            
            # Update agent status to ONLINE_AVAILABLE
            cursor.execute('''
                UPDATE fuel_delivery_agents
                SET online_status = 'ONLINE_AVAILABLE', total_deliveries = total_deliveries + 1
                WHERE id = %s
            ''', (agent_id,))
            
            conn.commit()
            
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
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def update_agent_location(self, agent_id, latitude, longitude):
        """Update agent live location"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            # Use PostgreSQL UPSERT pattern (INSERT ... ON CONFLICT)
            cursor.execute('''
                INSERT INTO fuel_agent_live_locations
                (agent_id, latitude, longitude, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (agent_id) DO UPDATE SET
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                updated_at = EXCLUDED.updated_at
            ''', (agent_id, latitude, longitude, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            
            # Log activity
            self._log_activity(agent_id, 'LOCATION_UPDATED', {
                'latitude': latitude,
                'longitude': longitude
            })
            
            return {'success': True, 'message': 'Location updated'}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def upload_delivery_proof(self, agent_id, request_id, proof_image_path):
        """Upload delivery proof image"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            if not os.path.exists(proof_image_path):
                return {'success': False, 'error': 'Proof image not found'}
            
            cursor.execute('''
                INSERT INTO fuel_delivery_proofs
                (request_id, image_path, uploaded_at)
                VALUES (%s, %s, %s)
            ''', (request_id, proof_image_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            
            # Log activity
            self._log_activity(agent_id, 'PROOF_UPLOADED', {
                'request_id': request_id,
                'proof_path': proof_image_path
            })
            
            return {'success': True, 'message': 'Proof uploaded successfully'}
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()
    
    def _log_activity(self, agent_id, event_type, details=None):
        """Log agent activity"""
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO fuel_agent_activity_logs
                (agent_id, activity_type, activity_details, timestamp)
                VALUES (%s, %s, %s, %s)
            ''', (agent_id, event_type, str(details) if details else None, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
        except Exception:
            conn.rollback()
            pass  # Don't fail main flow due to logging errors
        finally:
            cursor.close()
            conn.close()

# Create service instance
active_delivery_service = ActiveDeliveryService()