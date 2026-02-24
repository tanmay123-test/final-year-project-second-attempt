#!/usr/bin/env python3
"""
Test Dispatch Imports
Test if all dispatch modules can be imported
"""

def test_imports():
    """Test importing all dispatch modules"""
    print("🧪 TESTING DISPATCH IMPORTS")
    print("=" * 40)
    
    try:
        print("1. Testing dispatch_engine...")
        from dispatch_engine import dispatch_engine, Location, ServiceType, JobStatus
        print("✅ dispatch_engine imported")
        
        print("2. Testing dispatch_database...")
        from dispatch_database import dispatch_db
        print("✅ dispatch_database imported")
        
        print("3. Testing offer_engine...")
        from offer_engine import offer_engine, sequential_offer_manager
        print("✅ offer_engine imported")
        
        print("4. Testing tracking_engine...")
        from tracking_engine import tracking_engine
        print("✅ tracking_engine imported")
        
        print("5. Testing otp_engine...")
        from otp_engine import otp_engine, arrival_engine
        print("✅ otp_engine imported")
        
        print("6. Testing commission_engine...")
        from commission_engine import commission_engine, completion_engine
        print("✅ commission_engine imported")
        
        print("7. Testing dispatch_api...")
        from dispatch_api import register_dispatch_endpoints
        print("✅ dispatch_api imported")
        
        print("8. Testing dispatch_integration...")
        from dispatch_integration import integrate_dispatch_system
        print("✅ dispatch_integration imported")
        
        print("\n🎉 All dispatch modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
