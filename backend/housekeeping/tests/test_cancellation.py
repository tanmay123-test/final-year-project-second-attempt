import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from housekeeping.controllers.booking_controller import housekeeping_bp
from housekeeping.services.booking_service import booking_service

class TestCancellationController(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(housekeeping_bp, url_prefix='/api/housekeeping')
        self.client = self.app.test_client()
        
        # Patch the cancel_booking method on the imported service instance in the controller
        self.patcher_cancel = patch('housekeeping.controllers.booking_controller.booking_service.cancel_booking')
        self.mock_cancel = self.patcher_cancel.start()
        
        self.patcher_user = patch('housekeeping.controllers.booking_controller.get_current_user')
        self.mock_get_user = self.patcher_user.start()
        
    def tearDown(self):
        self.patcher_cancel.stop()
        self.patcher_user.stop()

    def test_cancel_endpoint_success(self):
        self.mock_get_user.return_value = ({'type': 'user', 'data': {'id': 1}}, None)
        self.mock_cancel.return_value = (True, "Cancelled")
        
        res = self.client.post('/api/housekeeping/cancel-booking', json={'booking_id': 101})
        self.assertEqual(res.status_code, 200)
        self.mock_cancel.assert_called_with(101, 1)

class TestCancellationService(unittest.TestCase):
    def setUp(self):
        self.service = booking_service
        self.original_db = self.service.db
        self.service.db = MagicMock()
        
    def tearDown(self):
        self.service.db = self.original_db
        
    def test_service_cancel_success(self):
        self.service.db.get_booking_by_id.return_value = {
            'id': 101, 'user_id': 1, 'status': 'PENDING', 'worker_id': None
        }
        self.service.db.update_booking_status.return_value = True
        
        success, msg = self.service.cancel_booking(101, 1)
        self.assertTrue(success)
        self.service.db.update_booking_status.assert_called_with(101, 'CANCELLED')

    def test_service_cancel_fail_status(self):
        self.service.db.get_booking_by_id.return_value = {
            'id': 101, 'user_id': 1, 'status': 'COMPLETED'
        }
        success, msg = self.service.cancel_booking(101, 1)
        self.assertFalse(success)
        self.assertIn("cannot be cancelled", msg)

if __name__ == '__main__':
    unittest.main()
