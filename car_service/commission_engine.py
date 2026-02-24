"""
Commission Engine - Automated payment and commission calculation system
Handles earnings, platform fees, and wallet management
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class CommissionEngine:
    """Manages commission calculation and payment processing"""
    
    def __init__(self):
        self.platform_commission_rate = 0.20  # 20% platform commission
        self.worker_earning_rate = 0.80      # 80% worker earnings
        self.min_base_cost = 100.0            # Minimum base cost
        self.emergency_surcharge = 1.5         # 50% emergency surcharge
        self.distance_rate_per_km = 10.0       # Rate per km for distance-based pricing
    
    def calculate_job_cost(self, distance_km: float, service_type: str, 
                        is_emergency: bool = False, base_cost: float = None) -> Dict:
        """Calculate total job cost"""
        try:
            # Use provided base cost or calculate default
            if base_cost is None:
                base_cost = self.min_base_cost + (distance_km * self.distance_rate_per_km)
            
            # Apply emergency surcharge
            if is_emergency:
                base_cost *= self.emergency_surcharge
            
            # Service type modifiers
            if service_type.upper() == 'TOW':
                base_cost *= 1.5  # Tow trucks cost more
            elif service_type.upper() == 'FUEL':
                base_cost *= 1.2  # Fuel delivery has moderate cost
            
            # Round to 2 decimal places
            total_cost = round(base_cost, 2)
            
            return {
                'base_cost': round(base_cost / (self.emergency_surcharge if is_emergency else 1), 2),
                'distance_cost': round(distance_km * self.distance_rate_per_km, 2),
                'emergency_surcharge': round(total_cost - (base_cost / (self.emergency_surcharge if is_emergency else 1)), 2) if is_emergency else 0,
                'total_cost': total_cost,
                'platform_commission': round(total_cost * self.platform_commission_rate, 2),
                'worker_earning': round(total_cost * self.worker_earning_rate, 2),
                'service_type': service_type,
                'is_emergency': is_emergency,
                'distance_km': round(distance_km, 2)
            }
            
        except Exception as e:
            print(f"Error calculating job cost: {e}")
            return {
                'total_cost': self.min_base_cost,
                'platform_commission': round(self.min_base_cost * self.platform_commission_rate, 2),
                'worker_earning': round(self.min_base_cost * self.worker_earning_rate, 2),
                'error': str(e)
            }
    
    def process_job_completion(self, job_id: int, worker_id: int, 
                           actual_cost: float = None) -> Dict:
        """Process payment and commission on job completion"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get job details
            cursor.execute("""
                SELECT * FROM mechanic_jobs
                WHERE id = ?
            """, (job_id,))
            
            job = cursor.fetchone()
            if not job:
                conn.close()
                return {'success': False, 'error': 'Job not found'}
            
            job_data = dict(job)
            
            # Calculate cost if not provided
            if actual_cost is None:
                cost_calc = self.calculate_job_cost(
                    job_data.get('distance_km', 0),
                    job_data.get('service_type', 'MECHANIC'),
                    job_data.get('is_emergency', False)
                )
                total_cost = cost_calc['total_cost']
            else:
                total_cost = actual_cost
            
            # Calculate commissions
            platform_commission = round(total_cost * self.platform_commission_rate, 2)
            worker_earning = round(total_cost * self.worker_earning_rate, 2)
            
            # Generate transaction IDs
            platform_tx_id = f"PF-{uuid.uuid4().hex[:12].upper()}"
            worker_tx_id = f"WR-{uuid.uuid4().hex[:12].upper()}"
            
            # Update worker wallet
            self._update_worker_wallet(worker_id, worker_earning, worker_tx_id, job_id)
            
            # Update platform wallet
            self._update_platform_wallet(platform_commission, platform_tx_id, job_id)
            
            # Record transaction logs
            self._record_transaction(job_id, worker_id, total_cost, 
                                platform_commission, worker_earning, 
                                platform_tx_id, worker_tx_id)
            
            # Update job payment status
            cursor.execute("""
                UPDATE mechanic_jobs
                SET total_cost = ?, platform_commission = ?, worker_earning = ?,
                    payment_status = 'PAID', paid_at = ?
                WHERE id = ?
            """, (total_cost, platform_commission, worker_earning, 
                   datetime.now(), job_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'job_id': job_id,
                'total_cost': total_cost,
                'platform_commission': platform_commission,
                'worker_earning': worker_earning,
                'platform_tx_id': platform_tx_id,
                'worker_tx_id': worker_tx_id,
                'paid_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error processing job completion: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_worker_wallet(self, worker_id: int, amount: float, 
                          transaction_id: str, job_id: int):
        """Update worker wallet balance"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            # Insert or update wallet
            cursor.execute("""
                INSERT INTO worker_wallet (worker_id, balance, last_updated)
                VALUES (?, ?, ?)
                ON CONFLICT(worker_id) DO UPDATE SET
                    balance = balance + ?,
                    last_updated = ?
            """, (worker_id, amount, datetime.now(), amount, datetime.now()))
            
            # Add wallet transaction
            cursor.execute("""
                INSERT INTO wallet_transactions 
                (worker_id, transaction_id, amount, transaction_type, 
                 reference_id, created_at)
                VALUES (?, ?, ?, 'EARNING', ?, ?)
            """, (worker_id, transaction_id, amount, job_id, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating worker wallet: {e}")
    
    def _update_platform_wallet(self, amount: float, transaction_id: str, job_id: int):
        """Update platform wallet balance"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            # Update platform wallet
            cursor.execute("""
                INSERT INTO platform_wallet (balance, last_updated)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    balance = balance + ?,
                    last_updated = ?
            """, (amount, datetime.now(), amount, datetime.now()))
            
            # Add platform transaction
            cursor.execute("""
                INSERT INTO platform_transactions 
                (transaction_id, amount, transaction_type, 
                 reference_id, created_at)
                VALUES (?, ?, 'COMMISSION', ?, ?)
            """, (transaction_id, amount, job_id, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating platform wallet: {e}")
    
    def _record_transaction(self, job_id: int, worker_id: int, total_cost: float,
                         platform_commission: float, worker_earning: float,
                         platform_tx_id: str, worker_tx_id: str):
        """Record complete transaction log"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO transaction_logs 
                (job_id, worker_id, total_cost, platform_commission, 
                 worker_earning, platform_tx_id, worker_tx_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (job_id, worker_id, total_cost, platform_commission,
                   worker_earning, platform_tx_id, worker_tx_id, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recording transaction: {e}")
    
    def get_worker_earnings(self, worker_id: int, days: int = 30) -> Dict:
        """Get worker earnings summary"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get wallet balance
            cursor.execute("""
                SELECT balance FROM worker_wallet WHERE worker_id = ?
            """, (worker_id,))
            
            wallet = cursor.fetchone()
            current_balance = wallet['balance'] if wallet else 0.0
            
            # Get recent earnings
            cursor.execute("""
                SELECT SUM(amount) as total_earnings,
                       COUNT(*) as transaction_count
                FROM wallet_transactions
                WHERE worker_id = ?
                AND transaction_type = 'EARNING'
                AND created_at > datetime('now', '-{} days')
            """.format(days), (worker_id,))
            
            earnings = cursor.fetchone()
            
            # Get job statistics
            cursor.execute("""
                SELECT COUNT(*) as completed_jobs,
                       SUM(worker_earning) as total_job_earnings,
                       AVG(worker_earning) as avg_earning_per_job
                FROM mechanic_jobs
                WHERE worker_id = ?
                AND status = 'COMPLETED'
                AND completion_time > datetime('now', '-{} days')
            """.format(days), (worker_id,))
            
            job_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'worker_id': worker_id,
                'current_balance': current_balance,
                'period_earnings': earnings['total_earnings'] or 0,
                'transaction_count': earnings['transaction_count'] or 0,
                'completed_jobs': job_stats['completed_jobs'] or 0,
                'total_job_earnings': job_stats['total_job_earnings'] or 0,
                'avg_earning_per_job': round(job_stats['avg_earning_per_job'] or 0, 2),
                'period_days': days
            }
            
        except Exception as e:
            print(f"Error getting worker earnings: {e}")
            return {'error': str(e)}
    
    def get_platform_revenue(self, days: int = 30) -> Dict:
        """Get platform revenue summary"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get platform wallet balance
            cursor.execute("""
                SELECT balance FROM platform_wallet WHERE id = 1
            """)
            
            wallet = cursor.fetchone()
            current_balance = wallet['balance'] if wallet else 0.0
            
            # Get recent revenue
            cursor.execute("""
                SELECT SUM(amount) as total_revenue,
                       COUNT(*) as transaction_count
                FROM platform_transactions
                WHERE transaction_type = 'COMMISSION'
                AND created_at > datetime('now', '-{} days')
            """.format(days), ())
            
            revenue = cursor.fetchone()
            
            # Get job statistics
            cursor.execute("""
                SELECT COUNT(*) as total_jobs,
                       SUM(total_cost) as total_job_value,
                       SUM(platform_commission) as total_commission,
                       AVG(platform_commission) as avg_commission_per_job
                FROM mechanic_jobs
                WHERE status = 'COMPLETED'
                AND completion_time > datetime('now', '-{} days')
            """.format(days), ())
            
            job_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'current_balance': current_balance,
                'period_revenue': revenue['total_revenue'] or 0,
                'transaction_count': revenue['transaction_count'] or 0,
                'total_jobs': job_stats['total_jobs'] or 0,
                'total_job_value': job_stats['total_job_value'] or 0,
                'total_commission': job_stats['total_commission'] or 0,
                'avg_commission_per_job': round(job_stats['avg_commission_per_job'] or 0, 2),
                'period_days': days
            }
            
        except Exception as e:
            print(f"Error getting platform revenue: {e}")
            return {'error': str(e)}
    
    def request_payout(self, worker_id: int, amount: float) -> Dict:
        """Process worker payout request"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check current balance
            cursor.execute("""
                SELECT balance FROM worker_wallet WHERE worker_id = ?
            """, (worker_id,))
            
            wallet = cursor.fetchone()
            current_balance = wallet['balance'] if wallet else 0.0
            
            if amount > current_balance:
                conn.close()
                return {
                    'success': False,
                    'error': 'Insufficient balance',
                    'requested_amount': amount,
                    'available_balance': current_balance
                }
            
            # Generate payout transaction
            payout_id = f"PO-{uuid.uuid4().hex[:12].upper()}"
            
            # Update wallet balance
            cursor.execute("""
                UPDATE worker_wallet
                SET balance = balance - ?, last_updated = ?
                WHERE worker_id = ?
            """, (amount, datetime.now(), worker_id))
            
            # Record payout transaction
            cursor.execute("""
                INSERT INTO wallet_transactions 
                (worker_id, transaction_id, amount, transaction_type, 
                 status, created_at)
                VALUES (?, ?, ?, 'PAYOUT', 'PENDING', ?)
            """, (worker_id, payout_id, amount, datetime.now()))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'payout_id': payout_id,
                'amount': amount,
                'remaining_balance': current_balance - amount,
                'status': 'PENDING'
            }
            
        except Exception as e:
            print(f"Error processing payout: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_transaction_history(self, worker_id: int = None, days: int = 30) -> List[Dict]:
        """Get transaction history"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if worker_id:
                cursor.execute("""
                    SELECT * FROM wallet_transactions
                    WHERE worker_id = ?
                    AND created_at > datetime('now', '-{} days')
                    ORDER BY created_at DESC
                """.format(days), (worker_id,))
            else:
                cursor.execute("""
                    SELECT * FROM platform_transactions
                    WHERE created_at > datetime('now', '-{} days')
                    ORDER BY created_at DESC
                """.format(days), ())
            
            transactions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return transactions
            
        except Exception as e:
            print(f"Error getting transaction history: {e}")
            return []


# Global instance
commission_engine = CommissionEngine()
