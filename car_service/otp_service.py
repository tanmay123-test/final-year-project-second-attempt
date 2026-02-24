"""
OTP Service - Secure job verification system
Generates and verifies OTPs for job start confirmation
"""

import sqlite3
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional

class OTPService:
    """Manages OTP generation and verification for job security"""
    
    def __init__(self):
        self.otp_length = 4
        self.otp_validity_minutes = 10
    
    def generate_otp(self, job_id: int) -> Dict:
        """Generate OTP for job verification"""
        try:
            # Generate 4-digit OTP
            otp = ''.join(random.choices(string.digits, k=self.otp_length))
            
            # Calculate expiry time
            expires_at = datetime.now() + timedelta(minutes=self.otp_validity_minutes)
            
            # Store OTP in database
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO job_otps 
                (job_id, otp, generated_at, expires_at, is_used, attempts)
                VALUES (?, ?, ?, ?, 0, 0)
            """, (job_id, otp, datetime.now(), expires_at))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'otp': otp,
                'job_id': job_id,
                'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                'validity_minutes': self.otp_validity_minutes
            }
            
        except Exception as e:
            print(f"Error generating OTP: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_otp(self, job_id: int, input_otp: str) -> Dict:
        """Verify OTP for job"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get OTP record
            cursor.execute("""
                SELECT * FROM job_otps
                WHERE job_id = ?
                ORDER BY generated_at DESC
                LIMIT 1
            """, (job_id,))
            
            otp_record = cursor.fetchone()
            
            if not otp_record:
                conn.close()
                return {
                    'success': False,
                    'error': 'OTP not found for this job'
                }
            
            otp_data = dict(otp_record)
            
            # Check if OTP is already used
            if otp_data['is_used']:
                conn.close()
                return {
                    'success': False,
                    'error': 'OTP has already been used'
                }
            
            # Check if OTP is expired
            if datetime.now() > datetime.strptime(otp_data['expires_at'], '%Y-%m-%d %H:%M:%S'):
                conn.close()
                return {
                    'success': False,
                    'error': 'OTP has expired'
                }
            
            # Check attempts limit
            if otp_data['attempts'] >= 3:
                conn.close()
                return {
                    'success': False,
                    'error': 'Too many failed attempts. Please generate new OTP.'
                }
            
            # Increment attempts
            cursor.execute("""
                UPDATE job_otps
                SET attempts = attempts + 1
                WHERE job_id = ?
            """, (job_id,))
            
            # Verify OTP
            if input_otp == otp_data['otp']:
                # Mark OTP as used
                cursor.execute("""
                    UPDATE job_otps
                    SET is_used = 1, used_at = ?
                    WHERE job_id = ?
                """, (datetime.now(), job_id))
                
                # Update job status to WORKING
                cursor.execute("""
                    UPDATE mechanic_jobs
                    SET status = 'WORKING', work_started_at = ?
                    WHERE id = ?
                """, (datetime.now(), job_id))
                
                conn.commit()
                conn.close()
                
                return {
                    'success': True,
                    'message': 'OTP verified successfully',
                    'job_id': job_id,
                    'verified_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                conn.commit()
                conn.close()
                
                remaining_attempts = 3 - (otp_data['attempts'] + 1)
                return {
                    'success': False,
                    'error': f'Invalid OTP. {remaining_attempts} attempts remaining.',
                    'remaining_attempts': remaining_attempts
                }
            
        except Exception as e:
            print(f"Error verifying OTP: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_otp_status(self, job_id: int) -> Optional[Dict]:
        """Get OTP status for a job"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM job_otps
                WHERE job_id = ?
                ORDER BY generated_at DESC
                LIMIT 1
            """, (job_id,))
            
            otp_record = cursor.fetchone()
            conn.close()
            
            if otp_record:
                otp_data = dict(otp_record)
                
                # Check if expired
                is_expired = datetime.now() > datetime.strptime(otp_data['expires_at'], '%Y-%m-%d %H:%M:%S')
                
                return {
                    'job_id': otp_data['job_id'],
                    'generated_at': otp_data['generated_at'],
                    'expires_at': otp_data['expires_at'],
                    'is_used': bool(otp_data['is_used']),
                    'attempts': otp_data['attempts'],
                    'is_expired': is_expired,
                    'remaining_attempts': max(0, 3 - otp_data['attempts'])
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting OTP status: {e}")
            return None
    
    def can_generate_otp(self, job_id: int) -> Dict:
        """Check if new OTP can be generated for job"""
        try:
            otp_status = self.get_otp_status(job_id)
            
            if not otp_status:
                return {'can_generate': True, 'reason': 'No existing OTP'}
            
            # Can generate if existing OTP is used or expired
            if otp_status['is_used']:
                return {'can_generate': True, 'reason': 'Previous OTP was used'}
            
            if otp_status['is_expired']:
                return {'can_generate': True, 'reason': 'Previous OTP expired'}
            
            if otp_status['attempts'] >= 3:
                return {'can_generate': True, 'reason': 'Previous OTP exhausted attempts'}
            
            return {
                'can_generate': False,
                'reason': 'Active OTP exists',
                'remaining_attempts': otp_status['remaining_attempts'],
                'expires_at': otp_status['expires_at']
            }
            
        except Exception as e:
            print(f"Error checking OTP generation: {e}")
            return {'can_generate': False, 'error': str(e)}
    
    def invalidate_otp(self, job_id: int) -> Dict:
        """Invalidate OTP for a job"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE job_otps
                SET is_used = 1, used_at = ?
                WHERE job_id = ?
            """, (datetime.now(), job_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'OTP invalidated successfully'
            }
            
        except Exception as e:
            print(f"Error invalidating OTP: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_expired_otps(self, hours: int = 24):
        """Clean up expired OTP records"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM job_otps
                WHERE expires_at < datetime('now', '-{} hours')
            """.format(hours))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"Cleaned up {deleted_count} expired OTP records")
            
        except Exception as e:
            print(f"Error cleaning up OTPs: {e}")
    
    def get_otp_logs(self, job_id: int = None, worker_id: int = None, 
                     hours: int = 24) -> list:
        """Get OTP logs for monitoring"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT jo.*, mj.worker_id, mj.user_id
                FROM job_otps jo
                LEFT JOIN mechanic_jobs mj ON jo.job_id = mj.id
                WHERE jo.generated_at > datetime('now', '-{} hours')
            """.format(hours)
            
            params = []
            
            if job_id:
                query += " AND jo.job_id = ?"
                params.append(job_id)
            
            if worker_id:
                query += " AND mj.worker_id = ?"
                params.append(worker_id)
            
            query += " ORDER BY jo.generated_at DESC"
            
            cursor.execute(query, params)
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return logs
            
        except Exception as e:
            print(f"Error getting OTP logs: {e}")
            return []
    
    def resend_otp(self, job_id: int) -> Dict:
        """Resend OTP (generate new one)"""
        # Check if we can generate new OTP
        can_generate = self.can_generate_otp(job_id)
        
        if not can_generate['can_generate']:
            return {
                'success': False,
                'error': can_generate['reason']
            }
        
        # Invalidate existing OTP
        self.invalidate_otp(job_id)
        
        # Generate new OTP
        return self.generate_otp(job_id)


# Global instance
otp_service = OTPService()
