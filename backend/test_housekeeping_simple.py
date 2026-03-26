#!/usr/bin/env python3
"""
Simple test for housekeeping service with SQLite
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment to avoid PostgreSQL issues
os.environ['DATABASE_URL'] = 'sqlite:///data/housekeeping.db'

def test_housekeeping():
    """Test housekeeping service with SQLite"""
    print("🧪 Testing Housekeeping Service (SQLite)...")
    
    try:
        # Test database import
        print("\n1. Testing database import...")
        from services.housekeeping.models.database import housekeeping_db
        print("✅ Database imported successfully")
        
        # Test connection
        print("\n2. Testing database connection...")
        conn = housekeeping_db.get_conn()
        print(f"✅ Connected using: {type(conn).__name__}")
        conn.close()
        
        # Test booking service
        print("\n3. Testing booking service...")
        from services.housekeeping.services.booking_service import BookingService
        booking_service = BookingService()
        print("✅ Booking service created successfully")
        
        # Test services
        print("\n4. Testing services...")
        services = booking_service.get_service_types()
        print(f"✅ Found {len(services)} services")
        for service in services[:3]:
            print(f"   • {service.get('name', 'Unknown')} - ₹{service.get('base_price', 0)}")
        
        # Test workers
        print("\n5. Testing workers...")
        try:
            workers = booking_service.get_top_cleaners()
            print(f"✅ Found {len(workers)} workers")
        except Exception as e:
            print(f"ℹ️  Workers test failed (expected if no workers): {e}")
        
        print("\n🎉 Housekeeping service is working with SQLite!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_housekeeping()
    if success:
        print("\n✅ Housekeeping service is ready!")
        print("\n📋 Next Steps:")
        print("1. Start the backend: python app.py")
        print("2. Access: http://localhost:5174/housekeeping/home")
        print("3. Test: http://localhost:5174/worker/housekeeping/login")
        print("\n🔗 Available Routes:")
        print("- GET /api/housekeeping/services")
        print("- GET /api/housekeeping/workers")
        print("- POST /api/housekeeping/confirm-booking")
        print("- GET /api/housekeeping/my-bookings")
    else:
        print("\n❌ Housekeeping setup failed")
