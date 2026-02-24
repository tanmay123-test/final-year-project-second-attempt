"""
Live Tracking Engine (CLI Simulation)
Phase 8: Simulates mechanic movement and updates tracking data
"""

import threading
import time
import random
import math
import uuid
from datetime import datetime, timedelta
from typing import Dict, List
from dispatch_engine import Location, TrackingSession, dispatch_engine

class LiveTrackingEngine:
    """Simulates live tracking of mechanic movement"""
    
    def __init__(self):
        self.tracking_threads: Dict[str, threading.Thread] = {}
        self.tracking_active: Dict[str, bool] = {}
        
    def start_tracking(self, job_id: str, mechanic_id: int, 
                      start_location: Location, destination: Location):
        """Start live tracking for a job"""
        if job_id in self.tracking_active:
            return
        
        self.tracking_active[job_id] = True
        
        # Create tracking session
        tracking_session = TrackingSession(
            id=str(uuid.uuid4()),
            job_id=job_id,
            mechanic_id=mechanic_id,
            start_location=start_location,
            current_location=start_location,
            started_at=datetime.utcnow(),
            last_update=datetime.utcnow(),
            eta_minutes=0
        )
        
        dispatch_engine.tracking_sessions[job_id] = tracking_session
        
        # Start tracking simulation
        tracking_thread = threading.Thread(
            target=self._simulate_movement,
            args=(job_id, mechanic_id, start_location, destination),
            daemon=True
        )
        tracking_thread.start()
        self.tracking_threads[job_id] = tracking_thread
        
        dispatch_engine._log_job_event(
            job_id, "TRACKING_STARTED",
            f"Live tracking simulation started from {start_location.latitude:.4f},{start_location.longitude:.4f}"
        )
    
    def _simulate_movement(self, job_id: str, mechanic_id: int, 
                          start: Location, destination: Location):
        """Simulate mechanic movement towards destination"""
        tracking_session = dispatch_engine.tracking_sessions.get(job_id)
        if not tracking_session:
            return
        
        # Calculate total distance and steps
        total_distance = start.distance_to(destination)
        steps = max(20, int(total_distance * 10))  # More steps for longer distances
        
        current_lat = start.latitude
        current_lon = start.longitude
        
        for step in range(steps + 1):
            if not self.tracking_active.get(job_id, False):
                break
            
            # Calculate progress (0.0 to 1.0)
            progress = step / steps
            
            # Interpolate position
            current_lat = start.latitude + (destination.latitude - start.latitude) * progress
            current_lon = start.longitude + (destination.longitude - start.longitude) * progress
            
            # Add some randomness for realistic movement
            if step > 0 and step < steps:
                current_lat += random.uniform(-0.0001, 0.0001)
                current_lon += random.uniform(-0.0001, 0.0001)
            
            current_location = Location(current_lat, current_lon)
            
            # Update tracking session
            tracking_session.current_location = current_location
            tracking_session.last_update = datetime.utcnow()
            
            # Recalculate ETA
            remaining_distance = current_location.distance_to(destination)
            tracking_session.eta_minutes = int((remaining_distance / dispatch_engine.AVERAGE_SPEED_KMH) * 60)
            
            # Update mechanic location
            dispatch_engine.update_mechanic_location(mechanic_id, current_location)
            
            # Log tracking event
            self._log_tracking_event(job_id, mechanic_id, current_location, 
                                   remaining_distance, tracking_session.eta_minutes)
            
            # Check if arrived
            if remaining_distance <= (dispatch_engine.ARRIVAL_THRESHOLD_METERS / 1000.0):
                self._handle_arrival(job_id, mechanic_id)
                break
            
            # Sleep based on expected travel time
            sleep_time = (total_distance / dispatch_engine.AVERAGE_SPEED_KMH) * 3600 / steps
            time.sleep(max(0.1, min(2.0, sleep_time)))  # Between 0.1 and 2 seconds
    
    def _log_tracking_event(self, job_id: str, mechanic_id: int, 
                           location: Location, distance_km: float, eta_minutes: int):
        """Log tracking event to database"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO job_tracking_logs 
                (job_id, mechanic_id, latitude, longitude, eta_minutes, event_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (job_id, mechanic_id, location.latitude, location.longitude, 
                  eta_minutes, "LOCATION_UPDATE"))
            
            conn.commit()
            conn.close()
            
            # Print CLI update
            print(f"📍 TRACKING UPDATE: Job {job_id[:8]} | "
                  f"Mechanic {mechanic_id} | "
                  f"Location: {location.latitude:.4f},{location.longitude:.4f} | "
                  f"Distance: {distance_km:.2f}km | "
                  f"ETA: {eta_minutes}min")
            
        except Exception as e:
            print(f"⚠️ Tracking log error: {e}")
    
    def _handle_arrival(self, job_id: str, mechanic_id: int):
        """Handle mechanic arrival at destination"""
        job = dispatch_engine.active_jobs.get(job_id)
        if job:
            job.status = JobStatus.ARRIVED
            job.arrived_at = datetime.utcnow()
            
            dispatch_engine._log_job_event(
                job_id, "MECHANIC_ARRIVED",
                f"Mechanic {mechanic_id} arrived at destination"
            )
            
            print(f"🎉 ARRIVAL: Mechanic {mechanic_id} has arrived for job {job_id[:8]}")
        
        # Stop tracking
        self.stop_tracking(job_id)
    
    def stop_tracking(self, job_id: str):
        """Stop tracking for a job"""
        self.tracking_active[job_id] = False
        
        if job_id in self.tracking_threads:
            # Thread will terminate naturally
            del self.tracking_threads[job_id]
        
        dispatch_engine._log_job_event(
            job_id, "TRACKING_STOPPED",
            "Live tracking stopped"
        )
    
    def get_current_tracking(self, job_id: str) -> Dict:
        """Get current tracking information"""
        tracking_session = dispatch_engine.tracking_sessions.get(job_id)
        if not tracking_session:
            return {}
        
        job = dispatch_engine.active_jobs.get(job_id)
        if not job:
            return {}
        
        current_distance = tracking_session.current_location.distance_to(job.location)
        
        return {
            "job_id": job_id,
            "mechanic_id": tracking_session.mechanic_id,
            "current_location": {
                "latitude": tracking_session.current_location.latitude,
                "longitude": tracking_session.current_location.longitude
            },
            "destination": {
                "latitude": job.location.latitude,
                "longitude": job.location.longitude
            },
            "distance_km": current_distance,
            "eta_minutes": tracking_session.eta_minutes,
            "started_at": tracking_session.started_at.isoformat(),
            "last_update": tracking_session.last_update.isoformat()
        }
    
    def get_tracking_history(self, job_id: str, limit: int = 50) -> List[Dict]:
        """Get tracking history for a job"""
        try:
            from dispatch_database import dispatch_db
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT latitude, longitude, eta_minutes, event_type, logged_at
                FROM job_tracking_logs
                WHERE job_id = ?
                ORDER BY logged_at DESC
                LIMIT ?
            """, (job_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "latitude": row[0],
                    "longitude": row[1],
                    "eta_minutes": row[2],
                    "event_type": row[3],
                    "logged_at": row[4]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"⚠️ Error getting tracking history: {e}")
            return []

# Initialize tracking engine
tracking_engine = LiveTrackingEngine()
