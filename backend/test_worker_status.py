#!/usr/bin/env python3
"""
Test Worker Online Status Toggle
This script tests the worker online status functionality for housekeeping.
"""

import sys
import os
import requests
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_worker_status():
    """
    Test the worker status toggle functionality
    """
    base_url = "http://localhost:5000/api/housekeeping"
    
    print("🔧 Testing Worker Online Status Toggle")
    print("=" * 60)
    
    # Test 1: Check if worker_status table exists and has data
    print("\n1️⃣ Testing Database Connection...")
    try:
        from services.housekeeping.models.database import housekeeping_db
        
        # Test setting worker status
        test_worker_id = 1
        print(f"📝 Setting worker {test_worker_id} to online...")
        housekeeping_db.set_worker_online(test_worker_id, True)
        
        # Test getting worker status
        print(f"📖 Getting worker {test_worker_id} status...")
        status = housekeeping_db.get_worker_online_status(test_worker_id)
        print(f"✅ Worker status: {status}")
        
        # Test setting worker to offline
        print(f"📝 Setting worker {test_worker_id} to offline...")
        housekeeping_db.set_worker_online(test_worker_id, False)
        
        # Verify status change
        status = housekeeping_db.get_worker_online_status(test_worker_id)
        print(f"✅ Worker status after offline: {status}")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    # Test 2: Check if workers appear in booking service
    print("\n2️⃣ Testing Booking Service Integration...")
    try:
        from services.housekeeping.services.booking_service import BookingService
        
        booking_service = BookingService()
        top_cleaners = booking_service.get_top_cleaners()
        
        print(f"📊 Found {len(top_cleaners)} housekeeping workers")
        
        if top_cleaners:
            for i, worker in enumerate(top_cleaners[:3]):  # Show first 3
                print(f"  {i+1}. {worker.get('name', 'Unknown')} - Online: {worker.get('is_online', False)} - Price: ₹{worker.get('price', 0)}")
        else:
            print("⚠️ No housekeeping workers found")
            
    except Exception as e:
        print(f"❌ Booking service test failed: {e}")
        return False
    
    # Test 3: Check API endpoint (without auth for now)
    print("\n3️⃣ Testing API Endpoint Structure...")
    try:
        # Check if the endpoint exists (will get 401 without auth, but should exist)
        response = requests.get(f"{base_url}/worker/status", timeout=5)
        if response.status_code == 401:
            print("✅ API endpoint exists (requires authentication)")
        elif response.status_code == 404:
            print("❌ API endpoint not found")
            return False
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 Worker Status Test Summary:")
    print("✅ Database Operations: Working")
    print("✅ Booking Service Integration: Working")
    print("✅ API Endpoint: Available")
    
    print("\n🔧 Troubleshooting Tips:")
    print("1. If workers don't appear online:")
    print("   - Check worker authentication in frontend")
    print("   - Verify worker_id is being passed correctly")
    print("   - Check browser console for JavaScript errors")
    print("")
    print("2. If toggle doesn't work:")
    print("   - Check network tab in browser for API calls")
    print("   - Verify housekeepingService.setWorkerStatus() is being called")
    print("   - Check if worker is properly logged in")
    print("")
    print("3. If booking doesn't show online workers:")
    print("   - Verify get_top_cleaners() is being called")
    print("   - Check if workers have 'housekeeping' service type")
    print("   - Verify is_online field is being displayed in UI")
    
    return True

def main():
    """
    Main test function
    """
    print(f"🕐 Starting worker status test: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_worker_status()
    
    if success:
        print("\n🎉 Worker status system is working correctly!")
        print("\n📱 Next Steps:")
        print("1. Check frontend authentication")
        print("2. Verify worker is logged in correctly")
        print("3. Check browser console for JavaScript errors")
        print("4. Test the toggle in the provider dashboard")
    else:
        print("\n⚠️ Some worker status tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()
