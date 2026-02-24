"""
Dispatch System Integration
Main integration file to connect dispatch system with existing Flask app
"""

def integrate_dispatch_system(app):
    """Integrate the smart dispatch system with the main Flask app"""
    
    try:
        # Import and register dispatch endpoints
        from dispatch_api import register_dispatch_endpoints
        register_dispatch_endpoints(app)
        
        # Initialize dispatch system components
        from dispatch_engine import dispatch_engine
        from dispatch_database import dispatch_db
        from offer_engine import offer_engine, sequential_offer_manager
        from tracking_engine import tracking_engine
        from otp_engine import otp_engine, arrival_engine
        from commission_engine import commission_engine, completion_engine
        
        # Load mechanics from database into dispatch engine
        load_mechanics_into_engine()
        
        print("✅ Smart Dispatch System integrated successfully")
        print("🚗 Available endpoints:")
        print("   POST /api/dispatch/job/create")
        print("   GET /api/dispatch/job/status/<job_id>")
        print("   POST /api/dispatch/mechanic/offer/<offer_id>/respond")
        print("   PUT /api/dispatch/mechanic/location/update")
        print("   POST /api/dispatch/otp/verify")
        print("   POST /api/dispatch/job/complete")
        print("   GET /api/dispatch/mechanic/wallet/<mechanic_id>")
        print("   GET /api/dispatch/mechanic/metrics/<mechanic_id>")
        print("   GET /api/dispatch/admin/jobs/active")
        
        return True
        
    except ImportError as e:
        print(f"⚠️ Dispatch system import error: {e}")
        print("🔧 Make sure all dispatch files are present")
        return False
    except Exception as e:
        print(f"⚠️ Dispatch system integration error: {e}")
        return False

def load_mechanics_into_engine():
    """Load mechanics from database into dispatch engine"""
    try:
        from dispatch_database import dispatch_db
        from dispatch_engine import Mechanic, MechanicStatus, ServiceType
        from datetime import datetime
        import sqlite3
        
        conn = sqlite3.connect(dispatch_db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, phone, email, service_type, specialization, 
                   rating, experience_years, status, latitude, longitude
            FROM mechanics
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            (mechanic_id, name, phone, email, service_type, specialization,
             rating, experience_years, status, latitude, longitude) = row
            
            # Create mechanic object
            mechanic = Mechanic(
                id=mechanic_id,
                name=name,
                phone=phone,
                email=email,
                service_type=ServiceType(service_type),
                specialization=specialization,
                rating=rating,
                experience_years=experience_years,
                status=MechanicStatus(status)
            )
            
            # Set location if available
            if latitude and longitude:
                from dispatch_engine import Location
                mechanic.current_location = Location(latitude, longitude)
                mechanic.last_location_update = datetime.utcnow()
            
            # Add to dispatch engine
            dispatch_engine.mechanics[mechanic_id] = mechanic
        
        print(f"✅ Loaded {len(rows)} mechanics into dispatch engine")
        
    except Exception as e:
        print(f"⚠️ Error loading mechanics: {e}")

# Add this to your main app.py
"""
In your main app.py, add:

from dispatch_integration import integrate_dispatch_system

# After app initialization
app = Flask(__name__)
# ... your existing app setup ...

# Integrate dispatch system
success = integrate_dispatch_system(app)
if not success:
    print("⚠️ Dispatch system not available")
"""
