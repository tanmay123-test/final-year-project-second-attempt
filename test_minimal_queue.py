#!/usr/bin/env python3
"""
Minimal test for new queue routes
"""

import requests

def test_minimal_queue():
    print("🔧 MINIMAL QUEUE TEST")
    print("="*50)
    
    # Test the queue service directly
    try:
        from car_service.fuel_request_queue_service import fuel_request_queue_service
        
        # Test the service directly
        result = fuel_request_queue_service.get_available_fuel_requests(1)
        print(f"Direct service test: {result.get('success', False)}")
        
        if result.get('success'):
            requests_data = result.get('requests', [])
            print(f"✅ Service found {len(requests_data)} requests")
            for req in requests_data[:2]:
                print(f"   {req.get('fuel_type', 'N/A')} - {req.get('quantity_liters', 0)}L")
                print(f"   Distance: {req.get('distance_km', 0)}km")
                print(f"   Score: {req.get('assignment_score', 0):.2f}")
        else:
            print("❌ Service returned no requests")
            
    except Exception as e:
        print(f"❌ Service error: {e}")
    
    print("\n🎯 MINIMAL TEST COMPLETE")

if __name__ == "__main__":
    test_minimal_queue()
