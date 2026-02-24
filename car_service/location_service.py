"""
Location Service - Real-time GPS tracking and location management
Handles worker location updates, job tracking, and ETA calculations
"""

import sqlite3
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class LocationService:
    """Manages real-time location tracking for workers and jobs"""
    
    def __init__(self):
        self.avg_speed_kmh = 30  # Average speed for ETA calculation
    
    def update_worker_location(self, worker_id: int, latitude: float, longitude: float, 
                           worker_type: str = 'mechanic') -> Dict:
        """Update worker's current location"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            # Insert or update worker location
            cursor.execute("""
                INSERT OR REPLACE INTO mechanic_live_locations 
                (worker_id, latitude, longitude, last_updated, worker_type)
                VALUES (?, ?, ?, ?, ?)
            """, (worker_id, latitude, longitude, datetime.now(), worker_type))
            
            # Check if worker has active job
            cursor.execute("""
                SELECT id, user_lat, user_long, status
                FROM mechanic_jobs
                WHERE worker_id = ? AND status IN ('ACCEPTED', 'ON_THE_WAY', 'ARRIVED')
                ORDER BY id DESC
                LIMIT 1
            """, (worker_id,))
            
            active_job = cursor.fetchone()
            
            if active_job:
                job_id = active_job[0]
                user_lat = active_job[1]
                user_long = active_job[2]
                job_status = active_job[3]
                
                # Calculate distance to job
                distance = self.haversine_distance(
                    latitude, longitude, user_lat, user_long
                )
                
                # Calculate ETA
                eta_minutes = (distance / self.avg_speed_kmh) * 60
                
                # Update job tracking log
                cursor.execute("""
                    INSERT INTO job_tracking_logs 
                    (job_id, worker_id, latitude, longitude, distance_to_job, eta_minutes, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (job_id, worker_id, latitude, longitude, distance, eta_minutes, datetime.now()))
                
                # Check if worker arrived (within 50 meters)
                if distance <= 0.05 and job_status != 'ARRIVED':
                    self._mark_worker_arrived(job_id, worker_id)
                
                conn.commit()
                conn.close()
                
                return {
                    'success': True,
                    'job_id': job_id,
                    'distance_to_job': distance,
                    'eta_minutes': eta_minutes,
                    'status': job_status,
                    'arrived': distance <= 0.05
                }
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Location updated successfully',
                'active_job': None
            }
            
        except Exception as e:
            print(f"Error updating worker location: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_worker_live_location(self, worker_id: int) -> Optional[Dict]:
        """Get worker's current live location"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT worker_id, latitude, longitude, last_updated, worker_type
                FROM mechanic_live_locations
                WHERE worker_id = ?
                ORDER BY last_updated DESC
                LIMIT 1
            """, (worker_id,))
            
            location = cursor.fetchone()
            conn.close()
            
            if location:
                return dict(location)
            return None
            
        except Exception as e:
            print(f"Error getting worker location: {e}")
            return None
    
    def get_job_live_location(self, job_id: int) -> Optional[Dict]:
        """Get job's live tracking information"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get latest tracking data
            cursor.execute("""
                SELECT j.*, l.latitude, l.longitude, l.distance_to_job, l.eta_minutes, l.timestamp
                FROM mechanic_jobs j
                LEFT JOIN job_tracking_logs l ON j.id = l.job_id
                WHERE j.id = ?
                ORDER BY l.timestamp DESC
                LIMIT 1
            """, (job_id,))
            
            tracking_data = cursor.fetchone()
            conn.close()
            
            if tracking_data:
                return dict(tracking_data)
            return None
            
        except Exception as e:
            print(f"Error getting job location: {e}")
            return None
    
    def get_job_tracking_history(self, job_id: int) -> List[Dict]:
        """Get complete tracking history for a job"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT *
                FROM job_tracking_logs
                WHERE job_id = ?
                ORDER BY timestamp ASC
            """, (job_id,))
            
            history = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return history
            
        except Exception as e:
            print(f"Error getting tracking history: {e}")
            return []
    
    def calculate_eta(self, worker_lat: float, worker_long: float, 
                   user_lat: float, user_long: float) -> Dict:
        """Calculate ETA between worker and user location"""
        try:
            distance = self.haversine_distance(
                worker_lat, worker_long, user_lat, user_long
            )
            
            eta_minutes = (distance / self.avg_speed_kmh) * 60
            eta_seconds = eta_minutes * 60
            
            # Add traffic factor (simplified)
            traffic_factor = 1.2  # 20% buffer for traffic
            adjusted_eta_minutes = eta_minutes * traffic_factor
            
            return {
                'distance_km': distance,
                'eta_minutes': eta_minutes,
                'eta_seconds': eta_seconds,
                'adjusted_eta_minutes': adjusted_eta_minutes,
                'traffic_factor': traffic_factor
            }
            
        except Exception as e:
            print(f"Error calculating ETA: {e}")
            return {
                'distance_km': 0,
                'eta_minutes': 0,
                'eta_seconds': 0,
                'adjusted_eta_minutes': 0,
                'traffic_factor': 1.0
            }
    
    def get_nearby_workers(self, latitude: float, longitude: float, 
                         radius_km: float = 10.0, worker_type: str = 'mechanic') -> List[Dict]:
        """Get all workers within specified radius"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get workers within radius (simplified bounding box for performance)
            lat_delta = radius_km / 111.0  # Approximate km to degrees
            lon_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))
            
            cursor.execute("""
                SELECT w.*, l.latitude, l.longitude, l.last_updated
                FROM mechanics w
                JOIN mechanic_live_locations l ON w.id = l.worker_id
                WHERE w.approval_status = 'APPROVED'
                AND w.is_busy = 0
                AND w.online_status = 1
                AND l.latitude BETWEEN ? AND ?
                AND l.longitude BETWEEN ? AND ?
                AND l.last_updated > datetime('now', '-5 minutes')
            """, (
                latitude - lat_delta, latitude + lat_delta,
                longitude - lon_delta, longitude + lon_delta
            ))
            
            workers = []
            for row in cursor.fetchall():
                worker = dict(row)
                
                # Calculate exact distance
                distance = self.haversine_distance(
                    latitude, longitude,
                    worker['latitude'], worker['longitude']
                )
                
                if distance <= radius_km:
                    worker['distance_km'] = distance
                    workers.append(worker)
            
            # Sort by distance
            workers.sort(key=lambda x: x['distance_km'])
            
            conn.close()
            return workers
            
        except Exception as e:
            print(f"Error getting nearby workers: {e}")
            return []
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
              math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _mark_worker_arrived(self, job_id: int, worker_id: int):
        """Mark worker as arrived at job location"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE mechanic_jobs
                SET status = 'ARRIVED', arrived_at = ?
                WHERE id = ?
            """, (datetime.now(), job_id))
            
            conn.commit()
            conn.close()
            
            print(f"Worker {worker_id} arrived at job {job_id}")
            
        except Exception as e:
            print(f"Error marking arrival: {e}")
    
    def cleanup_old_locations(self, hours: int = 24):
        """Clean up old location data"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM mechanic_live_locations
                WHERE last_updated < datetime('now', '-{} hours')
            """.format(hours))
            
            cursor.execute("""
                DELETE FROM job_tracking_logs
                WHERE timestamp < datetime('now', '-{} hours')
            """.format(hours))
            
            conn.commit()
            conn.close()
            
            print(f"Cleaned up location data older than {hours} hours")
            
        except Exception as e:
            print(f"Error cleaning up locations: {e}")
    
    def get_worker_location_history(self, worker_id: int, hours: int = 24) -> List[Dict]:
        """Get worker's location history"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT *
                FROM job_tracking_logs
                WHERE worker_id = ?
                AND timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp ASC
            """.format(hours), (worker_id,))
            
            history = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return history
            
        except Exception as e:
            print(f"Error getting location history: {e}")
            return []


# Global instance
location_service = LocationService()
