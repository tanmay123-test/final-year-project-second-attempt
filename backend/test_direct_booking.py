#!/usr/bin/env python3
"""
Test script for direct booking functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.freelance.services.freelance_service import freelance_service
from services.freelance.models.database import freelance_db

def test_direct_booking():
    """Test direct booking functionality"""
    print("🧪 Testing Direct Booking Functionality...")
    
    try:
        # Test database connection
        conn = freelance_db.get_conn()
        print("✅ Database connection successful")
        
        # Test if freelance_bookings table exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'freelance_bookings'
        """)
        result = cursor.fetchone()
        if result:
            print("✅ freelance_bookings table exists")
        else:
            print("❌ freelance_bookings table not found")
            return False
        
        # Test service functions exist
        if hasattr(freelance_service, 'get_direct_bookings_by_client'):
            print("✅ get_direct_bookings_by_client function exists")
        else:
            print("❌ get_direct_bookings_by_client function missing")
            return False
            
        if hasattr(freelance_service, 'get_direct_bookings_by_freelancer'):
            print("✅ get_direct_bookings_by_freelancer function exists")
        else:
            print("❌ get_direct_bookings_by_freelancer function missing")
            return False
        
        cursor.close()
        conn.close()
        
        print("✅ All direct booking tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Direct booking test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_direct_booking()
    if success:
        print("\n🎉 Direct booking functionality is ready!")
        print("\n📋 Manual Testing Steps:")
        print("1. Start backend server: python app.py")
        print("2. Start frontend: npm run dev")
        print("3. Login as client and create a direct booking")
        print("4. Check the 'Direct Bookings' tab in Projects")
        print("5. Check browser console for debugging info")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
