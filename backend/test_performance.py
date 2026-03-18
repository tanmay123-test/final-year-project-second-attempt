#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from car_service.job_requests_db import job_requests_db
from car_service.car_service_worker_db import car_service_worker_db

def test_performance():
    print("Testing performance endpoint...")
    
    # Get worker
    worker = car_service_worker_db.get_worker_by_email('co2023.shubhra.ausarmal@ves.ac.in')
    if not worker:
        print("❌ Worker not found")
        return
    
    print(f"✅ Worker found: ID={worker['id']}")
    
    # Get performance
    try:
        performance = job_requests_db.get_mechanic_performance(worker['id'])
        print(f"✅ Performance data: {performance}")
    except Exception as e:
        print(f"❌ Performance error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_performance()
