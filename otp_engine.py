"""
OTP Lifecycle & Arrival Detection Engine
Phase 9: Handles arrival detection and OTP validation
"""

import random
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from dispatch_engine import JobStatus, dispatch_engine

class OTPEngine:
    """Manages OTP generation and validation for job completion"""
    
    def __init__(self):
        self.active_otp_sessions: Dict[str, Dict] = {}
        self.otp_expiry_minutes = 10
        
    def generate_otp(self, job_id: str, user_id: int, mechanic_id: int) -> str:
        """Generate 6-digit OTP for job verification"""
        otp_code = f"{random.randint(100000, 999999)}"
        session_id = str(uuid.uuid4())
        
        otp_session = {
            "id": session_id,
            "job_id": job_id,
            "user_id": user_id,
            "mechanic_id": mechanic_id,
            "otp_code": otp_code,
            "generated_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes),
            "verified": False,
            "verified_at": None
        }
        
        self.active_otp_sessions[session_id] = otp_session
        
        # Store in database
        self._store_otp_session(otp_session)
        
        dispatch_engine._log_job_event(
            job_id, "OTP_GENERATED",
            f"OTP {otp_code} generated for job verification"
        )
        
        print(f"🔐 OTP GENERATED: Job {job_id[:8]} | OTP: {otp_code} | Expires in {self.otp_expiry_minutes} minutes")
        
        return otp_code
    
    def verify_otp(self, job_id: str, otp_code: str) -> bool:
        """Verify OTP code for job"""
        # Find active OTP session for this job
        otp_session = None
        for session in self.active_otp_sessions.values():
            if session["job_id"] == job_id and not session["verified"]:
                otp_session = session
                break
        
        if not otp_session:
            print(f"❌ OTP VERIFICATION FAILED: No active OTP session for job {job_id[:8]}")
            return False
        
        # Check if OTP is expired
        if datetime.utcnow() > otp_session["expires_at"]:
            print(f"❌ OTP VERIFICATION FAILED: OTP expired for job {job_id[:8]}")
            return False
        
        # Check OTP code
        if otp_session["otp_code"] != otp_code:
            print(f"❌ OTP VERIFICATION FAILED: Invalid OTP for job {job_id[:8]}")
            return False
        
        # Mark as verified
        otp_session["verified"] = True
        otp_session["verified_at"] = datetime.utcnow()
        
        # Update database
        self._update_otp_verification(otp_session["id"])
        
        dispatch_engine._log_job_event(
            job_id, "OTP_VERIFIED",
            f"OTP {otp_code} successfully verified"
        )
        
        print(f"✅ OTP VERIFIED: Job {job_id[:8]} | OTP: {otp_code}")
        
        # Update job status to WORKING
        job = dispatch_engine.active_jobs.get(job_id)
        if job:
            job.status = JobStatus.WORKING
            job.started_work_at = datetime.utcnow()
            
            dispatch_engine._log_job_event(
                job_id, "WORK_STARTED",
                f"Work started for job {job_id[:8]}"
            )
            
            print(f"🔧 WORK STARTED: Job {job_id[:8]} - Mechanic can now begin service")
        
        return True
    
    def _store_otp_session(self, otp_session: Dict):
        """Store OTP session in database"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO otp_sessions 
                (id, job_id, user_id, mechanic_id, otp_code, generated_at, expires_at, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                otp_session["id"],
                otp_session["job_id"],
                otp_session["user_id"],
                otp_session["mechanic_id"],
                otp_session["otp_code"],
                otp_session["generated_at"].isoformat(),
                otp_session["expires_at"].isoformat(),
                int(otp_session["verified"])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error storing OTP session: {e}")
    
    def _update_otp_verification(self, session_id: str):
        """Update OTP verification in database"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE otp_sessions 
                SET verified = 1, verified_at = ?
                WHERE id = ?
            """, (datetime.utcnow().isoformat(), session_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Error updating OTP verification: {e}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired OTP sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.active_otp_sessions.items():
            if current_time > session["expires_at"]:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_otp_sessions[session_id]
        
        if expired_sessions:
            print(f"🧹 Cleaned up {len(expired_sessions)} expired OTP sessions")

class ArrivalDetectionEngine:
    """Handles arrival detection and OTP generation"""
    
    def __init__(self, otp_engine: OTPEngine):
        self.otp_engine = otp_engine
        self.arrival_check_threads: Dict[str, threading.Thread] = {}
        
    def check_arrival(self, job_id: str, mechanic_id: int):
        """Check if mechanic has arrived at destination"""
        job = dispatch_engine.active_jobs.get(job_id)
        mechanic = dispatch_engine.mechanics.get(mechanic_id)
        
        if not job or not mechanic or not mechanic.current_location:
            return False
        
        # Calculate distance to destination
        distance_km = mechanic.current_location.distance_to(job.location)
        distance_meters = distance_km * 1000
        
        # Check if within arrival threshold
        if distance_meters <= dispatch_engine.ARRIVAL_THRESHOLD_METERS:
            self._handle_arrival(job_id, mechanic_id)
            return True
        
        return False
    
    def _handle_arrival(self, job_id: str, mechanic_id: int):
        """Handle mechanic arrival"""
        job = dispatch_engine.active_jobs.get(job_id)
        if not job:
            return
        
        # Update job status
        job.status = JobStatus.ARRIVED
        job.arrived_at = datetime.utcnow()
        
        dispatch_engine._log_job_event(
            job_id, "MECHANIC_ARRIVED",
            f"Mechanic {mechanic_id} arrived at destination"
        )
        
        print(f"🎉 MECHANIC ARRIVED: Job {job_id[:8]} | Mechanic {mechanic_id}")
        
        # Generate OTP for user verification
        self.otp_engine.generate_otp(job_id, job.user_id, mechanic_id)
        
        # Start arrival monitoring
        self._start_arrival_monitoring(job_id, mechanic_id)
    
    def _start_arrival_monitoring(self, job_id: str, mechanic_id: int):
        """Start monitoring for arrival confirmation"""
        def monitor_arrival():
            # Wait for OTP verification (max 30 minutes)
            timeout_seconds = 30 * 60
            start_time = time.time()
            
            while time.time() - start_time < timeout_seconds:
                job = dispatch_engine.active_jobs.get(job_id)
                if job and job.status == JobStatus.WORKING:
                    # OTP verified, stop monitoring
                    break
                
                # Check if job was cancelled
                if job and job.status in [JobStatus.CANCELLED_BY_USER, JobStatus.CANCELLED_BY_MECHANIC]:
                    break
                
                time.sleep(10)  # Check every 10 seconds
            
            # Clean up monitoring thread
            if job_id in self.arrival_check_threads:
                del self.arrival_check_threads[job_id]
        
        thread = threading.Thread(target=monitor_arrival, daemon=True)
        thread.start()
        self.arrival_check_threads[job_id] = thread
    
    def manual_arrival_confirmation(self, job_id: str, mechanic_id: int) -> bool:
        """Allow mechanic to manually confirm arrival"""
        job = dispatch_engine.active_jobs.get(job_id)
        if not job:
            return False
        
        # Check if mechanic is close enough
        if not self.check_arrival(job_id, mechanic_id):
            print(f"❌ ARRIVAL CONFIRMATION FAILED: Mechanic too far from destination")
            return False
        
        # Generate OTP
        self.otp_engine.generate_otp(job_id, job.user_id, mechanic_id)
        
        print(f"✅ ARRIVAL CONFIRMED: Job {job_id[:8]} | OTP generated for user verification")
        
        return True
    
    def get_active_otp(self, job_id: str) -> Optional[Dict]:
        """Get active OTP session for a job"""
        for session in self.otp_engine.active_otp_sessions.values():
            if session["job_id"] == job_id and not session["verified"]:
                return {
                    "job_id": session["job_id"],
                    "generated_at": session["generated_at"].isoformat(),
                    "expires_at": session["expires_at"].isoformat(),
                    "time_remaining": max(0, (session["expires_at"] - datetime.utcnow()).total_seconds())
                }
        return None

# Initialize engines
otp_engine = OTPEngine()
arrival_engine = ArrivalDetectionEngine(otp_engine)
