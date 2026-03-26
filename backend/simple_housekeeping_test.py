#!/usr/bin/env python3
"""
Simple test for housekeeping database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.housekeeping.models.postgres_housekeeping_db import postgres_housekeeping_db

def simple_test():
    """Simple test of housekeeping database"""
    print("🧪 Simple Housekeeping Test...")
    
    try:
        # Initialize tables
        print("\n1. Creating tables...")
        postgres_housekeeping_db._create_tables()
        
        # Test connection
        print("\n2. Testing connection...")
        conn = postgres_housekeeping_db.get_conn()
        print(f"✅ Connected using: {type(conn).__name__}")
        conn.close()
        
        # Test basic query
        print("\n3. Testing basic query...")
        services = postgres_housekeeping_db.get_all_services_with_base()
        print(f"✅ Found {len(services)} services:")
        for service in services:
            print(f"   • {service['name']} - ₹{service['base_price']}")
        
        print("\n🎉 Housekeeping database is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n✅ Housekeeping service is ready!")
        print("\n📋 You can now:")
        print("1. Start the backend: python app.py")
        print("2. Access: http://localhost:5174/housekeeping/home")
    else:
        print("\n❌ Housekeeping setup failed")
