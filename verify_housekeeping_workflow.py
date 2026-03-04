
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from housekeeping.services.booking_service import BookingService
from user_db import UserDB
from worker_db import WorkerDB
from housekeeping.models.database import housekeeping_db

def verify_workflow():
    print("🚀 Starting Housekeeping Workflow Verification...")
    
    service = BookingService()
    user_db = UserDB()
    worker_db = WorkerDB()
    
    # 1. Setup Test Data
    print("\n1. Setting up test data...")
    # Create User
    user_email = f"test_user_{int(time.time())}@example.com"
    user_db.create_user("Test User", f"user_{int(time.time())}", "password123", user_email)
    user = user_db.get_user_by_email(user_email)
    # user is dict with 'email' and 'is_verified', need ID.
    # UserDB doesn't return ID in create_user or get_user_by_email easily directly...
    # Wait, get_user_by_email returns dict. get_user_by_username returns ID.
    user_id = user_db.get_user_by_username(f"user_{int(time.time())}")
    print(f"   Created User ID: {user_id}")
    
    # Create Worker
    worker_email = f"test_worker_{int(time.time())}@example.com"
    worker_id = worker_db.register_worker("Test Worker", worker_email, "1234567890", "housekeeping", "General Cleaning", 5)
    worker_db.approve_worker(worker_id)
    housekeeping_db.set_worker_online(worker_id, True)
    print(f"   Created Worker ID: {worker_id}")
    
    # 2. Create Booking Request
    print("\n2. Creating Booking Request...")
    result = service.create_booking_request(
        user_id, "General Cleaning", "123 Test St", "2025-12-25", "10:00 AM",
        worker_id=worker_id # Direct request
    )
    if result.get('success'):
        booking_id = result['booking_id']
        print(f"   ✅ Booking Created. ID: {booking_id}, Status: {result['status']}")
    else:
        print(f"   ❌ Failed to create booking: {result}")
        return

    # 3. Worker Accepts Booking
    print("\n3. Worker Accepting Booking...")
    success, msg, status = service.update_booking_status_by_worker(booking_id, worker_id, 'ACCEPTED')
    if success:
        print(f"   ✅ Booking Accepted. Status: {status}")
    else:
        print(f"   ❌ Failed to accept booking: {msg}")
        return

    # 4. Worker Starts Job
    print("\n4. Worker Starting Job...")
    success, msg, otp = service.start_job(booking_id, worker_id)
    if success:
        print(f"   ✅ Job Started. OTP Generated: {otp}")
        # Verify DB status
        booking = housekeeping_db.get_booking_by_id(booking_id)
        print(f"   🔍 DB Status: {booking['status']}, OTP: {booking['otp']}, Started At: {booking['started_at']}")
        if booking['status'] != 'IN_PROGRESS':
             print("   ❌ DB Status mismatch!")
             return
    else:
        print(f"   ❌ Failed to start job: {msg}")
        return

    # 5. Worker Completes Job (Wrong OTP)
    print("\n5. Worker Completing Job (Wrong OTP)...")
    success, msg = service.complete_job(booking_id, worker_id, "000000")
    if not success:
        print(f"   ✅ Failed as expected. Message: {msg}")
        booking = housekeeping_db.get_booking_by_id(booking_id)
        print(f"   🔍 Retry Count: {booking['retry_count']}")
        if booking['retry_count'] != 1:
            print("   ❌ Retry count did not increment!")
    else:
        print("   ❌ Job completed with wrong OTP!")
        return

    # 6. Worker Completes Job (Correct OTP)
    print("\n6. Worker Completing Job (Correct OTP)...")
    success, msg = service.complete_job(booking_id, worker_id, otp)
    if success:
        print(f"   ✅ Job Completed Successfully. Message: {msg}")
        booking = housekeeping_db.get_booking_by_id(booking_id)
        print(f"   🔍 DB Status: {booking['status']}")
        if booking['status'] != 'COMPLETED':
             print("   ❌ DB Status mismatch!")
             return
    else:
        print(f"   ❌ Failed to complete job: {msg}")
        return

    print("\n🎉 Verification Completed Successfully!")

if __name__ == "__main__":
    verify_workflow()
