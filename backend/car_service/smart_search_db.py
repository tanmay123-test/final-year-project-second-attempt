"""
Smart Search Database
Handles mechanic locations, full-text search, and smart search data storage
"""

import os
import psycopg2
import psycopg2.extras
import math
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

load_dotenv()

class SmartSearchDB:
    def __init__(self):
        self._init_tables()
        self._init_fts()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def _init_tables(self):
        """Initialize smart search database tables"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Mechanic live locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanic_live_locations (
                    id SERIAL PRIMARY KEY,
                    mechanic_id INTEGER NOT NULL UNIQUE,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Mechanic skills mapping table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanic_skills (
                    id SERIAL PRIMARY KEY,
                    mechanic_id INTEGER NOT NULL,
                    skill_name TEXT NOT NULL,
                    confidence_score FLOAT DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Search cache table for performance
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    id SERIAL PRIMARY KEY,
                    user_lat FLOAT NOT NULL,
                    user_lon FLOAT NOT NULL,
                    required_skill TEXT NOT NULL,
                    search_radius_km FLOAT DEFAULT 5.0,
                    result_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def _init_fts(self):
        """Initialize full-text search for mechanic search in PostgreSQL"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Create content table for search
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanic_search_content (
                    id SERIAL PRIMARY KEY,
                    mechanic_id INTEGER NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    skills TEXT NOT NULL,
                    service_area TEXT DEFAULT 'Mumbai',
                    search_vector tsvector
                )
            """)
            
            # Create trigger to update search_vector
            cursor.execute("""
                CREATE OR REPLACE FUNCTION mechanic_search_vector_update() RETURNS trigger AS $$
                BEGIN
                    new.search_vector :=
                        setweight(to_tsvector('english', coalesce(new.name, '')), 'A') ||
                        setweight(to_tsvector('english', coalesce(new.skills, '')), 'B') ||
                        setweight(to_tsvector('english', coalesce(new.service_area, '')), 'C');
                    return new;
                END
                $$ LANGUAGE plpgsql;
            """)
            
            cursor.execute("""
                DROP TRIGGER IF EXISTS tsvectorupdate ON mechanic_search_content;
                CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
                ON mechanic_search_content FOR EACH ROW EXECUTE FUNCTION mechanic_search_vector_update();
            """)
            
            # Create GIN index for fast search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mechanic_search_vector ON mechanic_search_content USING GIN(search_vector);
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_mechanic_location(self, mechanic_id: int, latitude: float, longitude: float) -> bool:
        """Update mechanic's live location"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO mechanic_live_locations 
                (mechanic_id, latitude, longitude, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (mechanic_id) DO UPDATE SET
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                updated_at = EXCLUDED.updated_at
            """, (mechanic_id, latitude, longitude))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_mechanic_location(self, mechanic_id: int) -> Optional[Dict]:
        """Get mechanic's latest location"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM mechanic_live_locations 
                WHERE mechanic_id = %s 
                ORDER BY updated_at DESC 
                LIMIT 1
            """, (mechanic_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_mechanic_fts(self, mechanic_id: int, name: str, skills: str, service_area: str = "Mumbai"):
        """Update mechanic information in search content table"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO mechanic_search_content 
                (mechanic_id, name, skills, service_area)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (mechanic_id) DO UPDATE SET
                name = EXCLUDED.name,
                skills = EXCLUDED.skills,
                service_area = EXCLUDED.service_area
            """, (mechanic_id, name, skills, service_area))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def search_mechanics_fts(self, query: str) -> List[Dict]:
        """Search mechanics using PostgreSQL full-text search"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Format query for to_tsquery
            formatted_query = ' & '.join(query.split()) + ':*'
            
            cursor.execute("""
                SELECT id, mechanic_id, name, skills, service_area,
                       ts_rank(search_vector, to_tsquery('english', %s)) as rank
                FROM mechanic_search_content
                WHERE search_vector @@ to_tsquery('english', %s)
                ORDER BY rank DESC
            """, (formatted_query, formatted_query))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            # Fallback to ILIKE if FTS fails or for partial matches
            try:
                cursor.execute("""
                    SELECT id, mechanic_id, name, skills, service_area
                    FROM mechanic_search_content
                    WHERE name ILIKE %s OR skills ILIKE %s OR service_area ILIKE %s
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))
                return [dict(row) for row in cursor.fetchall()]
            except:
                return []
        finally:
            cursor.close()
            conn.close()
    
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
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Join with mechanics table (assuming it's in the same DB)
            cursor.execute("""
                SELECT m.*, mll.latitude, mll.longitude, mll.updated_at
                FROM mechanics m
                JOIN mechanic_live_locations mll ON m.id = mll.mechanic_id
                WHERE m.role = 'Mechanic' 
                AND m.is_online = TRUE 
                AND m.is_busy = FALSE
            """)
            
            nearby_mechanics = []
            current_time = datetime.now()
            
            for row in cursor.fetchall():
                mechanic = dict(row)
                
                # Check if location is recent (within 10 minutes)
                # PostgreSQL returns datetime object for updated_at
                location_time = mechanic['updated_at']
                if isinstance(location_time, str):
                    location_time = datetime.fromisoformat(location_time)
                
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
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def cache_search_results(self, user_lat: float, user_lon: float, 
                           required_skill: str, results: List[Dict], 
                           radius_km: float = 5.0, cache_minutes: int = 5):
        """Cache search results for performance"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            expires_at = datetime.now() + timedelta(minutes=cache_minutes)
            cursor.execute("""
                INSERT INTO search_cache 
                (user_lat, user_lon, required_skill, search_radius_km, result_json, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_lat, user_lon, required_skill, radius_km, json.dumps(results), expires_at))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_cached_results(self, user_lat: float, user_lon: float, 
                          required_skill: str, radius_km: float = 5.0) -> Optional[List[Dict]]:
        """Get cached search results if available"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT result_json, expires_at FROM search_cache
                WHERE user_lat = %s AND user_lon = %s AND required_skill = %s AND search_radius_km = %s
                AND expires_at > %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_lat, user_lon, required_skill, radius_km, datetime.now()))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['result_json'])
            return None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_cached_results_count(self) -> int:
        """Get count of cached search results"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM search_cache WHERE expires_at > CURRENT_TIMESTAMP")
            return cursor.fetchone()[0]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

# Global instance
smart_search_db = SmartSearchDB()
