import unittest
import os
import sqlite3
import json
from unittest.mock import MagicMock, patch
from housekeeping.services.booking_service import BookingService
from housekeeping.models.database import HousekeepingDatabase

# Use a temporary file for testing
TEST_DB = 'test_housekeeping_complete.db'

class TestCompleteBookingFlow(unittest.TestCase):
    def setUp(self):
        # Setup temporary DB
        self.db = HousekeepingDatabase(TEST_DB)
        self.booking_service = BookingService()
        self.booking_service.db = self.db # Inject test DB
        
        # Mock WorkerDB
        self.booking_service.worker_db = MagicMock()
        
        # Mock workers
        self.worker1 = {'id': 1, 'name': 'Worker 1', 'location': 'Test City', 'specialization': 'General Cleaning'}
        self.worker2 = {'id': 2, 'name': 'Worker 2', 'location': 'Test City', 'specialization': 'General Cleaning'}
        
        self.booking_service.worker_db.get_workers_by_specialization.return_value = [self.worker1, self.worker2]
        self.booking_service.worker_db.get_workers_by_service.return_value = [self.worker1, self.worker2]
        
        def get_worker_by_id(worker_id):
            if worker_id == 1: return self.worker1
            if worker_id == 2: return self.worker2
            return None
        self.booking_service.worker_db.get_worker_by_id.side_effect = get_worker_by_id

    def tearDown(self):
        self.db.get_conn().close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_new_fields_persistence(self):
        """Test that home_size, add_ons, and booking_type are saved correctly"""
        user_id = 101
        service_type = 'General Cleaning'
        date = '2026-03-10'
        time = '10:00'
        address = '123 Test St'
        home_size = '2 BHK'
        add_ons = json.dumps(['balcony', 'terrace'])
        booking_type = 'schedule'
        
        # Create booking
        result = self.booking_service.create_booking_request(
            user_id, service_type, address, date, time, 
            worker_id=None, 
            home_size=home_size, 
            add_ons=add_ons, 
            booking_type=booking_type
        )
        
        booking_id = result['booking_id']
        self.assertIsNotNone(booking_id)
        
        # Verify DB record
        booking = self.db.get_booking_by_id(booking_id)
        self.assertEqual(booking['home_size'], home_size)
        self.assertEqual(booking['add_ons'], add_ons)
        self.assertEqual(booking['booking_type'], booking_type)

    def test_scheduled_booking_auto_assignment(self):
        """Test auto-assignment for scheduled bookings"""
        user_id = 102
        date = '2026-03-11'
        time = '14:00'
        
        # Set workers online
        self.db.set_worker_online(1, True)
        self.db.set_worker_online(2, True)
        
        # Create scheduled booking request
        result = self.booking_service.create_booking_request(
            user_id, 'General Cleaning', 'Test City', date, time, 
            worker_id=None, booking_type='schedule'
        )
        booking_id = result['booking_id']
        
        # Confirm booking (trigger assignment)
        success, msg = self.booking_service.confirm_booking(booking_id)
        self.assertTrue(success)
        
        # Verify a worker was assigned
        booking = self.db.get_booking_by_id(booking_id)
        self.assertEqual(booking['status'], 'ASSIGNED')
        self.assertIn(booking['worker_id'], [1, 2])
        assigned_worker_id = booking['worker_id']
        
        print(f"Assigned Worker: {assigned_worker_id}")

    def test_worker_decline_reassignment(self):
        """Test reassignment when a worker declines"""
        user_id = 103
        date = '2026-03-12'
        time = '09:00'
        
        # Set workers online
        self.db.set_worker_online(1, True)
        self.db.set_worker_online(2, True)
        
        # Create booking
        result = self.booking_service.create_booking_request(
            user_id, 'General Cleaning', 'Test City', date, time, 
            worker_id=None, booking_type='schedule'
        )
        booking_id = result['booking_id']
        self.booking_service.confirm_booking(booking_id)
        
        # Get assigned worker
        booking = self.db.get_booking_by_id(booking_id)
        first_worker_id = booking['worker_id']
        self.assertIsNotNone(first_worker_id)
        
        # Worker declines
        # Assuming update_status handles reassignment logic or we call reassign_worker directly
        # In controller: status == 'DECLINED' calls reassign_worker
        success, msg = self.booking_service.reassign_worker(booking_id, first_worker_id)
        self.assertTrue(success)
        
        # Verify new assignment
        booking = self.db.get_booking_by_id(booking_id)
        new_worker_id = booking['worker_id']
        self.assertNotEqual(new_worker_id, first_worker_id)
        self.assertIn(new_worker_id, [1, 2])
        self.assertEqual(booking['status'], 'ASSIGNED')
        
        print(f"Reassigned from {first_worker_id} to {new_worker_id}")

    def test_instant_booking_flow(self):
        """Test instant booking with specific worker"""
        user_id = 104
        date = '2026-03-13'
        time = '11:00'
        target_worker_id = 1
        
        self.db.set_worker_online(target_worker_id, True)
        
        # Create instant booking
        result = self.booking_service.create_booking_request(
            user_id, 'General Cleaning', 'Test City', date, time, 
            worker_id=target_worker_id, booking_type='instant'
        )
        booking_id = result['booking_id']
        
        # Confirm
        success, msg = self.booking_service.confirm_booking(booking_id)
        self.assertTrue(success)
        
        # Verify status is REQUESTED (waiting for worker acceptance)
        booking = self.db.get_booking_by_id(booking_id)
        self.assertEqual(booking['status'], 'REQUESTED')
        self.assertEqual(booking['worker_id'], target_worker_id)
        
        # Worker accepts
        self.db.update_booking_status(booking_id, 'ACCEPTED', worker_id=target_worker_id)
        
        booking = self.db.get_booking_by_id(booking_id)
        self.assertEqual(booking['status'], 'ACCEPTED')

if __name__ == '__main__':
    unittest.main()
