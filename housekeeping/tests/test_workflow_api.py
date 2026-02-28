import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app

class HousekeepingWorkflowApiTestCase(unittest.TestCase):
    def setUp(self):
        # Create a new app instance for testing to ensure clean state
        from flask import Flask
        from housekeeping.controllers.booking_controller import housekeeping_bp
        
        self.app_instance = Flask(__name__)
        # Register blueprint with the same prefix as in app.py
        self.app_instance.register_blueprint(housekeeping_bp, url_prefix='/api/housekeeping')
        
        self.client = self.app_instance.test_client()
        self.app_instance.testing = True

    def test_start_job_unauthorized(self):
        # Test without auth
        response = self.client.post('/api/housekeeping/worker/start-job', json={"booking_id": 1})
        self.assertEqual(response.status_code, 401)

    def test_start_job_success(self):
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "worker", "data": {"id": 123}}, None)
            
            with patch('housekeeping.controllers.booking_controller.booking_service') as mock_service:
                # Mock start_job success
                mock_service.start_job.return_value = (True, "Job started", "123456")
                # Mock db.get_booking_by_id for socket emission
                mock_service.db.get_booking_by_id.return_value = {"user_id": 1}
                
                with patch('housekeeping.controllers.booking_controller.get_socketio') as mock_socket:
                    mock_socket.return_value = MagicMock()
                    
                    response = self.client.post('/api/housekeeping/worker/start-job', json={"booking_id": 1})
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.data)
                    self.assertTrue(data['success'])
                    self.assertEqual(data['otp'], "123456")

    def test_complete_job_success(self):
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "worker", "data": {"id": 123}}, None)
            
            with patch('housekeeping.controllers.booking_controller.booking_service') as mock_service:
                # Mock complete_job success
                mock_service.complete_job.return_value = (True, "Job completed")
                # Mock db.get_booking_by_id for socket emission
                mock_service.db.get_booking_by_id.return_value = {"user_id": 1}
                
                with patch('housekeeping.controllers.booking_controller.get_socketio') as mock_socket:
                    mock_socket.return_value = MagicMock()
                    
                    response = self.client.post('/api/housekeeping/worker/complete-job', json={"booking_id": 1, "otp": "123456"})
                    self.assertEqual(response.status_code, 200)
                    data = json.loads(response.data)
                    self.assertTrue(data['success'])

    def test_complete_job_failure(self):
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "worker", "data": {"id": 123}}, None)
            
            with patch('housekeeping.controllers.booking_controller.booking_service') as mock_service:
                # Mock complete_job failure
                mock_service.complete_job.return_value = (False, "Invalid OTP")
                
                response = self.client.post('/api/housekeeping/worker/complete-job', json={"booking_id": 1, "otp": "000000"})
                self.assertEqual(response.status_code, 400)
                data = json.loads(response.data)
                self.assertEqual(data['error'], "Invalid OTP")

if __name__ == '__main__':
    unittest.main()
