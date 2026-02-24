"""
Commission & Completion Engine
Phase 11: Handles job completion, commission calculation, and payment processing
"""

from datetime import datetime
from typing import Dict, Tuple
from dispatch_engine import JobStatus, dispatch_engine

class CommissionEngine:
    """Handles commission calculation and payment processing"""
    
    def __init__(self):
        self.PLATFORM_COMMISSION_RATE = 0.20  # 20% platform commission
        self.MECHANIC_EARNINGS_RATE = 0.80    # 80% mechanic earnings
        self.EMERGENCY_BONUS_RATE = 0.25      # 25% bonus for emergency jobs
        self.BASE_FEE = 250.0                  # Base service fee
        self.PER_KM_RATE = 10.0                # Rate per kilometer
        
    def calculate_job_pricing(self, job_id: str) -> Dict:
        """Calculate complete pricing breakdown for a job"""
        job = dispatch_engine.active_jobs.get(job_id)
        if not job:
            return {}
        
        # Get mechanic location for distance calculation
        mechanic = dispatch_engine.mechanics.get(job.mechanic_id) if job.mechanic_id else None
        if not mechanic or not mechanic.current_location:
            return {}
        
        # Calculate distance
        distance_km = mechanic.current_location.distance_to(job.location)
        
        # Calculate base fee
        base_fee = self.BASE_FEE
        
        # Calculate distance fee
        distance_fee = distance_km * self.PER_KM_RATE
        
        # Calculate emergency bonus
        emergency_bonus = 0.0
        if job.urgency:
            emergency_bonus = (base_fee + distance_fee) * self.EMERGENCY_BONUS_RATE
        
        # Calculate total fee
        total_fee = base_fee + distance_fee + emergency_bonus
        
        # Calculate commission split
        platform_commission = total_fee * self.PLATFORM_COMMISSION_RATE
        mechanic_earnings = total_fee * self.MECHANIC_EARNINGS_RATE
        
        pricing = {
            "base_fee": round(base_fee, 2),
            "distance_fee": round(distance_fee, 2),
            "emergency_bonus": round(emergency_bonus, 2),
            "total_fee": round(total_fee, 2),
            "platform_commission": round(platform_commission, 2),
            "mechanic_earnings": round(mechanic_earnings, 2),
            "distance_km": round(distance_km, 2),
            "commission_rate": self.PLATFORM_COMMISSION_RATE,
            "earnings_rate": self.MECHANIC_EARNINGS_RATE
        }
        
        # Update job with pricing
        job.base_fee = pricing["base_fee"]
        job.distance_fee = pricing["distance_fee"]
        job.emergency_bonus = pricing["emergency_bonus"]
        job.total_fee = pricing["total_fee"]
        job.platform_commission = pricing["platform_commission"]
        job.mechanic_earnings = pricing["mechanic_earnings"]
        
        return pricing
    
    def process_completion(self, job_id: str) -> bool:
        """Process job completion and handle payments"""
        job = dispatch_engine.active_jobs.get(job_id)
        if not job:
            return False
        
        # Calculate pricing
        pricing = self.calculate_job_pricing(job_id)
        if not pricing:
            return False
        
        # Update job status
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        
        # Process commission
        commission_id = self._record_commission(job_id, pricing)
        
        # Update mechanic wallet
        self._update_mechanic_wallet(job.mechanic_id, pricing["mechanic_earnings"])
        
        # Update mechanic metrics
        self._update_mechanic_metrics(job.mechanic_id, pricing["mechanic_earnings"])
        
        # Set mechanic back to online
        mechanic = dispatch_engine.mechanics.get(job.mechanic_id)
        if mechanic:
            mechanic.status = MechanicStatus.ONLINE
        
        # Log completion
        dispatch_engine._log_job_event(
            job_id, "JOB_COMPLETED",
            f"Job completed. Total: ₹{pricing['total_fee']} | Mechanic: ₹{pricing['mechanic_earnings']} | Platform: ₹{pricing['platform_commission']}"
        )
        
        print(f"💰 JOB COMPLETED: Job {job_id[:8]}")
        print(f"   💸 Total Fee: ₹{pricing['total_fee']}")
        print(f"   🔧 Mechanic Earnings: ₹{pricing['mechanic_earnings']}")
        print(f"   🏢 Platform Commission: ₹{pricing['platform_commission']}")
        print(f"   📊 Distance: {pricing['distance_km']} km")
        
        return True
    
    def _record_commission(self, job_id: str, pricing: Dict) -> str:
        """Record commission transaction in database"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            commission_id = str(uuid.uuid4())
            job = dispatch_engine.active_jobs.get(job_id)
            
            cursor.execute("""
                INSERT INTO commission_tracking 
                (id, job_id, mechanic_id, total_amount, platform_commission, 
                 mechanic_earnings, commission_rate, processed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                commission_id,
                job_id,
                job.mechanic_id,
                pricing["total_fee"],
                pricing["platform_commission"],
                pricing["mechanic_earnings"],
                pricing["commission_rate"],
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return commission_id
            
        except Exception as e:
            print(f"⚠️ Error recording commission: {e}")
            return ""
    
    def _update_mechanic_wallet(self, mechanic_id: int, earnings: float):
        """Update mechanic wallet balance"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            # Update wallet
            cursor.execute("""
                UPDATE worker_wallet 
                SET current_balance = current_balance + ?,
                    total_earned = total_earned + ?,
                    last_updated = ?
                WHERE mechanic_id = ?
            """, (earnings, earnings, datetime.utcnow().isoformat(), mechanic_id))
            
            conn.commit()
            conn.close()
            
            print(f"💰 WALLET UPDATED: Mechanic {mechanic_id} +₹{earnings}")
            
        except Exception as e:
            print(f"⚠️ Error updating mechanic wallet: {e}")
    
    def _update_mechanic_metrics(self, mechanic_id: int, earnings: float):
        """Update mechanic performance metrics"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            # Get current metrics
            cursor.execute("""
                SELECT total_jobs, completed_jobs, total_earnings, average_rating
                FROM worker_metrics
                WHERE mechanic_id = ?
            """, (mechanic_id,))
            
            row = cursor.fetchone()
            if row:
                total_jobs, completed_jobs, total_earnings, avg_rating = row
                
                # Update metrics
                new_total_jobs = total_jobs + 1
                new_completed_jobs = completed_jobs + 1
                new_total_earnings = total_earnings + earnings
                
                # Calculate acceptance rate (simplified)
                acceptance_rate = new_completed_jobs / new_total_jobs if new_total_jobs > 0 else 0
                
                cursor.execute("""
                    UPDATE worker_metrics 
                    SET total_jobs = ?, completed_jobs = ?, total_earnings = ?,
                        acceptance_rate = ?, last_updated = ?
                    WHERE mechanic_id = ?
                """, (new_total_jobs, new_completed_jobs, new_total_earnings,
                      acceptance_rate, datetime.utcnow().isoformat(), mechanic_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error updating mechanic metrics: {e}")
    
    def get_mechanic_wallet(self, mechanic_id: int) -> Dict:
        """Get mechanic wallet information"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT current_balance, total_earned, total_withdrawn, last_updated
                FROM worker_wallet
                WHERE mechanic_id = ?
            """, (mechanic_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "mechanic_id": mechanic_id,
                    "current_balance": row[0],
                    "total_earned": row[1],
                    "total_withdrawn": row[2],
                    "last_updated": row[3]
                }
            
            return {"mechanic_id": mechanic_id, "current_balance": 0.0}
            
        except Exception as e:
            print(f"⚠️ Error getting mechanic wallet: {e}")
            return {"mechanic_id": mechanic_id, "current_balance": 0.0}
    
    def get_mechanic_metrics(self, mechanic_id: int) -> Dict:
        """Get mechanic performance metrics"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT total_jobs, completed_jobs, cancelled_jobs, average_rating,
                       total_earnings, acceptance_rate, fairness_score
                FROM worker_metrics
                WHERE mechanic_id = ?
            """, (mechanic_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "mechanic_id": mechanic_id,
                    "total_jobs": row[0],
                    "completed_jobs": row[1],
                    "cancelled_jobs": row[2],
                    "average_rating": row[3],
                    "total_earnings": row[4],
                    "acceptance_rate": row[5],
                    "fairness_score": row[6]
                }
            
            return {"mechanic_id": mechanic_id, "total_jobs": 0}
            
        except Exception as e:
            print(f"⚠️ Error getting mechanic metrics: {e}")
            return {"mechanic_id": mechanic_id, "total_jobs": 0}

class CompletionEngine:
    """Handles job completion workflow"""
    
    def __init__(self, commission_engine: CommissionEngine):
        self.commission_engine = commission_engine
    
    def complete_job(self, job_id: str, proof_notes: str = "") -> bool:
        """Complete a job with optional proof notes"""
        job = dispatch_engine.active_jobs.get(job_id)
        if not job:
            return False
        
        # Verify job is in working status
        if job.status != JobStatus.WORKING:
            print(f"❌ JOB COMPLETION FAILED: Job {job_id[:8]} not in WORKING status")
            return False
        
        # Add proof notes if provided
        if proof_notes:
            self._add_job_proof(job_id, proof_notes)
        
        # Process completion and commission
        success = self.commission_engine.process_completion(job_id)
        
        if success:
            # Stop tracking if active
            from tracking_engine import tracking_engine
            tracking_engine.stop_tracking(job_id)
            
            # Clean up OTP sessions
            from otp_engine import otp_engine
            otp_engine.cleanup_expired_sessions()
            
            print(f"✅ JOB COMPLETED SUCCESSFULLY: Job {job_id[:8]}")
        
        return success
    
    def _add_job_proof(self, job_id: str, proof_notes: str):
        """Add job proof notes"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            proof_id = str(uuid.uuid4())
            job = dispatch_engine.active_jobs.get(job_id)
            
            cursor.execute("""
                INSERT INTO job_proofs 
                (id, job_id, mechanic_id, proof_type, description, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                proof_id,
                job_id,
                job.mechanic_id,
                "COMPLETION_NOTES",
                proof_notes,
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error adding job proof: {e}")

# Initialize engines
commission_engine = CommissionEngine()
completion_engine = CompletionEngine(commission_engine)
