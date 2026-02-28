import unittest
import os
import sqlite3
from unittest.mock import MagicMock, patch
from housekeeping.services.booking_service import BookingService
from housekeeping.models.database import HousekeepingDatabase

# Use a temporary file for testing
TEST_DB = 'test_housekeeping.db'

class TestBookingFlow(unittest.TestCase):
    def setUp(self):
        # Setup temporary DB
        self.db = HousekeepingDatabase(TEST_DB)
        self.booking_service = BookingService()
        self.booking_service.db = self.db # Inject test DB
        
        # Mock WorkerDB
        self.booking_service.worker_db = MagicMock()
        self.booking_service.worker_db.get_workers_by_specialization.return_value = [
            {'id': 1, 'name': 'Test Worker', 'location': 'Test City', 'specialization': 'General Cleaning'}
        ]
        self.booking_service.worker_db.get_workers_by_service.return_value = [
            {'id': 1, 'name': 'Test Worker', 'location': 'Test City', 'specialization': 'General Cleaning'}
        ]
        self.booking_service.worker_db.get_worker_by_id.return_value = {
            'id': 1, 'name': 'Test Worker', 'email': 'test@worker.com'
        }

    def tearDown(self):
        self.db.get_conn().close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_worker_online_status(self):
        worker_id = 1
        # Initially offline
        self.assertFalse(self.db.get_worker_online_status(worker_id))
        
        # Set online
        self.db.set_worker_online(worker_id, True)
        self.assertTrue(self.db.get_worker_online_status(worker_id))
        
        # Set offline
        self.db.set_worker_online(worker_id, False)
        self.assertFalse(self.db.get_worker_online_status(worker_id))

    def test_instant_booking_flow(self):
        worker_id = 1
        user_id = 100
        service_type = 'General Cleaning'
        date = '2026-03-01'
        time = '10:00'
        address = '123 Test St, Test City'
        
        # 1. Worker goes online
        self.db.set_worker_online(worker_id, True)
        
        # 2. User searches for online workers
        workers = self.booking_service.get_online_workers(service_type, date, time, address)
        self.assertEqual(len(workers), 1)
        self.assertEqual(workers[0]['id'], worker_id)
        
        # 3. User creates booking request (Instant)
        result = self.booking_service.create_booking_request(user_id, service_type, address, date, time, worker_id)
        booking_id = result['booking_id']
        self.assertIsNotNone(booking_id)
        self.assertEqual(result['status'], 'REQUESTED')
        
        # 4. User confirms booking (Payment)
        success, msg = self.booking_service.confirm_booking(booking_id)
        self.assertTrue(success)
        self.assertIn("request sent", msg)
        
        # 5. Check booking status
        booking = self.db.get_booking_by_id(booking_id)
        self.assertEqual(booking['status'], 'REQUESTED')
        self.assertEqual(booking['worker_id'], worker_id)
        
        # 6. Verify worker is now "booked" for that slot (should not be available for another booking)
        # Try to search again
        workers_after = self.booking_service.get_online_workers(service_type, date, time, address)
        self.assertEqual(len(workers_after), 0)
        
        # 7. Worker accepts booking
        self.db.update_booking_status(booking_id, 'ACCEPTED')
        booking = self.db.get_booking_by_id(booking_id)
        self.assertEqual(booking['status'], 'ACCEPTED')

    def test_conflicting_booking(self):
        worker_id = 1
        user_id_1 = 100
        user_id_2 = 101
        date = '2026-03-01'
        time = '10:00'
        
        self.db.set_worker_online(worker_id, True)
        
        # User 1 books
        res1 = self.booking_service.create_booking_request(user_id_1, 'General Cleaning', 'Addr1', date, time, worker_id)
        self.booking_service.confirm_booking(res1['booking_id'])
        
        # User 2 tries to book same worker same time
        # Search should return empty
        workers = self.booking_service.get_online_workers('General Cleaning', date, time, 'Addr2')
        self.assertEqual(len(workers), 0)
        
        # If they try to force create (direct API call)
        res2 = self.booking_service.create_booking_request(user_id_2, 'General Cleaning', 'Addr2', date, time, worker_id)
        
        # Creation should fail because worker is already booked
        self.assertEqual(res2['status'], 'FAILED')
        self.assertIn("Worker is already booked for this slot", res2['error'])

if __name__ == '__main__':
    unittest.main()
