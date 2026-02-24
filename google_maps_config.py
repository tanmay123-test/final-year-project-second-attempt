"""
Google Maps Configuration
Add Google Maps API configuration to existing config
"""

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = "AIzaSyBkAGv8Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9Z9"  # Replace with your actual API key

# Google Maps API Settings
GOOGLE_MAPS_ENABLED = True
GOOGLE_MAPS_CACHE_TTL = 300  # 5 minutes cache
GOOGLE_MAPS_REQUEST_TIMEOUT = 10  # seconds

# Google Maps Pricing (for monitoring)
GOOGLE_MAPS_QUOTA_LIMIT = 100000  # Monthly quota limit
GOOGLE_MAPS_COST_PER_REQUEST = 0.005  # USD per request (approximate)

# Map Settings
DEFAULT_MAP_ZOOM = 15
DEFAULT_MAP_SIZE = "600x400"
DEFAULT_MAP_TYPE = "roadmap"

# Traffic Settings
TRAFFIC_ENABLED = True
TRAFFIC_UPDATE_INTERVAL = 300  # 5 minutes

# Geocoding Settings
GEOCODING_REGION = "in"  # India region bias
GEOCODING_LANGUAGE = "en"  # English language

# Directions Settings
DIRECTIONS_MODE = "driving"  # driving, walking, bicycling, transit
DIRECTIONS_ALTERNATIVES = True  # Get alternative routes
DIRECTIONS_OPTIMIZE = True  # Optimize waypoint order

# Static Map Settings
STATIC_MAP_STYLE = "roadmap"  # roadmap, satellite, hybrid, terrain
STATIC_MAP_MARKERS = {
    'user': {'color': 'red', 'size': 'mid', 'label': 'U'},
    'worker': {'color': 'blue', 'size': 'mid', 'label': 'W'},
    'job': {'color': 'green', 'size': 'mid', 'label': 'J'}
}

# Initialize Google Maps service if API key is provided
def initialize_google_maps():
    """Initialize Google Maps service with configuration"""
    if GOOGLE_MAPS_ENABLED and GOOGLE_MAPS_API_KEY and GOOGLE_MAPS_API_KEY != "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        try:
            from car_service.google_maps_service import initialize_google_maps
            return initialize_google_maps(GOOGLE_MAPS_API_KEY)
        except ImportError:
            print("⚠️ Google Maps service not available")
            return None
    else:
        print("⚠️ Google Maps API key not configured")
        return None

# API Usage Monitoring
def track_api_usage(api_endpoint: str, cost: float = 0):
    """Track Google Maps API usage for billing monitoring"""
    try:
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect('car_service.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO google_maps_usage 
            (api_endpoint, cost, timestamp)
            VALUES (?, ?, ?)
        """, (api_endpoint, cost, datetime.now()))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Failed to track API usage: {e}")

def get_api_usage_stats(days: int = 30) -> dict:
    """Get API usage statistics"""
    try:
        import sqlite3
        
        conn = sqlite3.connect('car_service.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_requests,
                SUM(cost) as total_cost,
                api_endpoint,
                DATE(timestamp) as date
            FROM google_maps_usage
            WHERE timestamp > datetime('now', '-{} days')
            GROUP BY api_endpoint, DATE(timestamp)
            ORDER BY date DESC
        """.format(days))
        
        stats = cursor.fetchall()
        conn.close()
        
        return {
            'period_days': days,
            'usage_data': stats,
            'total_requests': sum(row[0] for row in stats),
            'total_cost': sum(row[1] for row in stats)
        }
        
    except Exception as e:
        print(f"Failed to get API usage stats: {e}")
        return {}

# Create usage tracking table if not exists
def create_usage_tracking_table():
    """Create Google Maps usage tracking table"""
    try:
        import sqlite3
        
        conn = sqlite3.connect('car_service.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS google_maps_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_endpoint TEXT NOT NULL,
                cost REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Google Maps usage tracking table created")
        
    except Exception as e:
        print(f"Failed to create usage tracking table: {e}")

# Initialize on import
create_usage_tracking_table()
