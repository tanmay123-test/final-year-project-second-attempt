#!/usr/bin/env python3
"""
Test script for PostgreSQL Housekeeping Service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.housekeeping.models.postgres_housekeeping_db import postgres_housekeeping_db
from services.housekeeping.services.booking_service import BookingService

def test_postgres_housekeeping():
    """Test PostgreSQL housekeeping functionality"""
    print("🧪 Testing PostgreSQL Housekeeping Service...")
    
    try:
        # Initialize tables first
        print("\n1. Initializing database tables...")
        postgres_housekeeping_db._create_tables()
        
        # Test database connection
        print("\n2. Testing database connection...")
        conn = postgres_housekeeping_db.get_conn()
        conn.close()
        print("✅ Database connection successful")
        
        # Test services
        print("\n3. Testing services...")
        services = postgres_housekeeping_db.get_all_services_with_base()
        print(f"✅ Found {len(services)} services")
        for service in services[:3]:
            print(f"   • {service['name']} - ₹{service['base_price']}")
        
        # Test booking service
        print("\n4. Testing booking service...")
        booking_service = BookingService()
        
        # Test service types
        service_types = booking_service.get_service_types()
        print(f"✅ Found {len(service_types)} service types")
        
        # Test worker status
        print("\n5. Testing worker status...")
        test_worker_id = 1
        status = postgres_housekeeping_db.get_worker_status(test_worker_id)
        if status:
            print(f"✅ Worker {test_worker_id} status: {status}")
        else:
            print(f"ℹ️  Worker {test_worker_id} status not set (this is normal)")
        
        # Test available slots
        print("\n6. Testing available slots...")
        slots = postgres_housekeeping_db.get_available_slots("Regular Cleaning", "2024-01-01")
        print(f"✅ Found {len(slots)} available slots")
        
        print("\n🎉 PostgreSQL Housekeeping Service is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing PostgreSQL housekeeping: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_postgres_housekeeping()
    if success:
        print("\n📋 Next Steps:")
        print("1. Start the backend server: python app.py")
        print("2. Test the housekeeping API endpoints")
        print("3. Access: http://localhost:5174/housekeeping/home")
        print("4. Test: http://localhost:5174/worker/housekeeping/login")
    else:
        print("\n❌ PostgreSQL Housekeeping setup failed")
        sys.exit(1)
