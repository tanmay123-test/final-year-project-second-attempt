"""
Smart Search Database
Handles mechanic locations, FTS5 search, and smart search data storage
"""

import os
import sqlite3
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), 'smart_search.db')

class SmartSearchDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        self._init_fts5()
    
    def _init_tables(self):
        """Initialize smart search database tables"""
        cursor = self.conn.cursor()
        
        # Mechanic live locations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_live_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mechanic_id INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mechanic_id) REFERENCES car_service_workers (id)
            )
        """)
        
        # Mechanic skills mapping table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mechanic_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                confidence_score REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mechanic_id) REFERENCES car_service_workers (id)
            )
        """)
        
        # Search cache table for performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_lat REAL NOT NULL,
                user_lon REAL NOT NULL,
                required_skill TEXT NOT NULL,
                search_radius_km REAL DEFAULT 5.0,
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        self.conn.commit()
    
    def _init_fts5(self):
        """Initialize FTS5 virtual table for mechanic search"""
        cursor = self.conn.cursor()
        
        # Create FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS mechanics_fts USING fts5(
                mechanic_id,
                name,
                skills,
                service_area,
                content='mechanic_fts_content',
                content_rowid='id'
            )
        """)
        
        # Create content table for FTS5
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_fts_content (
                id INTEGER PRIMARY KEY,
                mechanic_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                skills TEXT NOT NULL,
                service_area TEXT DEFAULT 'Mumbai'
            )
        """)
        
        self.conn.commit()
    
    def update_mechanic_location(self, mechanic_id: int, latitude: float, longitude: float) -> bool:
        """Update mechanic's live location"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO mechanic_live_locations 
            (mechanic_id, latitude, longitude, updated_at)
            VALUES (?, ?, ?, ?)
        """, (mechanic_id, latitude, longitude, datetime.now()))
        self.conn.commit()
        return True
    
    def get_mechanic_location(self, mechanic_id: int) -> Optional[Dict]:
        """Get mechanic's latest location"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM mechanic_live_locations 
            WHERE mechanic_id = ? 
            ORDER BY updated_at DESC 
            LIMIT 1
        """, (mechanic_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_mechanic_fts(self, mechanic_id: int, name: str, skills: str, service_area: str = "Mumbai"):
        """Update mechanic information in FTS5 table"""
        cursor = self.conn.cursor()
        
        # Update content table
        cursor.execute("""
            INSERT OR REPLACE INTO mechanic_fts_content 
            (mechanic_id, name, skills, service_area)
            VALUES (?, ?, ?, ?)
        """, (mechanic_id, name, skills, service_area))
        
        # Get the row ID
        cursor.execute("SELECT id FROM mechanic_fts_content WHERE mechanic_id = ?", (mechanic_id,))
        row = cursor.fetchone()
        row_id = row[0] if row else None
        
        if row_id:
            # Update FTS5 table
            cursor.execute("""
                INSERT OR REPLACE INTO mechanics_fts 
                (rowid, mechanic_id, name, skills, service_area)
                VALUES (?, ?, ?, ?, ?)
            """, (row_id, mechanic_id, name, skills, service_area))
        
        self.conn.commit()
    
    def search_mechanics_fts(self, query: str) -> List[Dict]:
        """Search mechanics using FTS5"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT mfc.*
            FROM mechanics_fts mft
            JOIN mechanic_fts_content mfc ON mft.mechanic_id = mfc.mechanic_id
            WHERE mechanics_fts MATCH ?
            ORDER BY rank
        """, (query,))
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        return results
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def get_nearby_mechanics(self, user_lat: float, user_lon: float, 
                           radius_km: float = 5.0) -> List[Dict]:
        """Get mechanics within specified radius"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT csw.*, mll.latitude, mll.longitude, mll.updated_at
            from services.car_service_workers csw
            JOIN mechanic_live_locations mll ON csw.id = mll.mechanic_id
            WHERE csw.role = 'Mechanic' 
            AND csw.is_online = 1 
            AND csw.is_busy = 0
        """)
        
        nearby_mechanics = []
        current_time = datetime.now()
        
        for row in cursor.fetchall():
            mechanic = dict(row)
            
            # Check if location is recent (within 10 minutes)
            location_time = datetime.fromisoformat(mechanic['updated_at'])
            if current_time - location_time > timedelta(minutes=10):
                continue
            
            # Calculate distance
            distance = self.calculate_distance(
                user_lat, user_lon, 
                mechanic['latitude'], mechanic['longitude']
            )
            
            # Filter by radius
            if distance <= radius_km:
                mechanic['distance_km'] = distance
                nearby_mechanics.append(mechanic)
        
        # Sort by distance
        nearby_mechanics.sort(key=lambda x: x['distance_km'])
        return nearby_mechanics
    
    def cache_search_results(self, user_lat: float, user_lon: float, 
                           required_skill: str, results: List[Dict], 
                           radius_km: float = 5.0, cache_minutes: int = 5):
        """Cache search results for performance"""
        cursor = self.conn.cursor()
        import json
        
        expires_at = datetime.now() + timedelta(minutes=cache_minutes)
        cursor.execute("""
            INSERT INTO search_cache 
            (user_lat, user_lon, required_skill, search_radius_km, result_json, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_lat, user_lon, required_skill, radius_km, json.dumps(results), expires_at))
        self.conn.commit()
    
    def get_cached_results(self, user_lat: float, user_lon: float, 
                          required_skill: str, radius_km: float = 5.0) -> Optional[List[Dict]]:
        """Get cached search results if available"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT result_json, expires_at FROM search_cache
            WHERE user_lat = ? AND user_lon = ? AND required_skill = ? AND search_radius_km = ?
            AND expires_at > ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_lat, user_lon, required_skill, radius_km, datetime.now()))
        
        row = cursor.fetchone()
        if row:
            import json
            return json.loads(row[0])
        return None
    
    def get_cached_results_count(self) -> int:
        """Get count of cached search results"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM search_cache WHERE expires_at > ?", (datetime.now(),))
        return cursor.fetchone()[0]

# Global instance
smart_search_db = SmartSearchDB()
