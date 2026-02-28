import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app

class HousekeepingTestCase(unittest.TestCase):
    def setUp(self):
        # Create a new app instance for testing to ensure clean state
        from flask import Flask
        from housekeeping.controllers.booking_controller import housekeeping_bp
        
        self.app_instance = Flask(__name__)
        # Register blueprint with the same prefix as in app.py
        self.app_instance.register_blueprint(housekeeping_bp, url_prefix='/api/housekeeping')
        
        self.client = self.app_instance.test_client()
        self.app_instance.testing = True

    def test_list_services(self):
        with patch('housekeeping.controllers.booking_controller.booking_service') as mock_service:
            mock_service.get_service_types.return_value = [{"name": "Test Service", "price": 100, "description": "Test"}]
            mock_service.get_top_cleaners.return_value = []
            
            # Use the full prefixed URL
            response = self.client.get('/api/housekeeping/services')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data['services']), 1)
            self.assertEqual(data['services'][0]['name'], "Test Service")

    def test_worker_status_unauthorized(self):
        # Test without auth
        response = self.client.get('/api/housekeeping/worker/status')
        self.assertEqual(response.status_code, 401)

    def test_worker_status_authorized(self):
        # Mock get_current_user to return a worker
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "worker", "data": {"id": 123}}, None)
            
            with patch('housekeeping.controllers.booking_controller.booking_service.db') as mock_db:
                # Test GET status
                mock_db.get_worker_online_status.return_value = True
                response = self.client.get('/api/housekeeping/worker/status')
                self.assertEqual(response.status_code, 200)
                self.assertTrue(json.loads(response.data)['is_online'])
                
                # Test POST status
                mock_db.set_worker_online.return_value = None # Mock void return
                response = self.client.post('/api/housekeeping/worker/status', json={"is_online": False})
                self.assertEqual(response.status_code, 200)
                mock_db.set_worker_online.assert_called_with(123, False)
                self.assertFalse(json.loads(response.data)['is_online'])

    def test_book_service_no_availability(self):
        # Mock user
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "user", "data": {"id": 1}}, None)
            
            with patch('housekeeping.controllers.booking_controller.booking_service') as mock_service:
                # Mock check_availability to return empty list
                mock_service.check_availability.return_value = []
                
                payload = {
                    "service_type": "General Cleaning",
                    "address": "123 Test St",
                    "date": "2023-01-01",
                    "time": "10:00"
                }
                response = self.client.post('/api/housekeeping/book', json=payload)
                self.assertEqual(response.status_code, 404)
                # Check response JSON or text depending on implementation
                # The controller returns JSON {"error": "...", "retry": True}
                self.assertIn("No workers available", str(response.data))

    def test_book_service_available(self):
        # Mock user
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "user", "data": {"id": 1}}, None)
            
            with patch('housekeeping.controllers.booking_controller.booking_service') as mock_service:
                # Mock check_availability to return workers
                mock_service.check_availability.return_value = [{"id": 1, "name": "Worker 1"}]
                # Mock db.get_service_price
                mock_service.db.get_service_price.return_value = 50.0
                
                payload = {
                    "service_type": "General Cleaning",
                    "address": "123 Test St",
                    "date": "2023-01-01",
                    "time": "10:00"
                }
                response = self.client.post('/api/housekeeping/book', json=payload)
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['available'])
                self.assertEqual(data['price_estimate'], 50.0)

    def test_confirm_booking(self):
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "user", "data": {"id": 1}}, None)
            
            with patch('housekeeping.controllers.booking_controller.booking_service') as mock_service:
                # Mock create_booking_request
                mock_service.create_booking_request.return_value = {'booking_id': 123}
                # Mock confirm_booking
                mock_service.confirm_booking.return_value = (True, "Booking confirmed")
                
                payload = {
                    "service_type": "General Cleaning",
                    "address": "123 Test St",
                    "date": "2023-01-01",
                    "time": "10:00",
                    "payment_method": "card"
                }
                response = self.client.post('/api/housekeeping/confirm-booking', json=payload)
                self.assertEqual(response.status_code, 201)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                self.assertEqual(data['booking_id'], 123)

    def test_update_booking_status(self):
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "worker", "data": {"id": 1}}, None)
            
            with patch('housekeeping.controllers.booking_controller.booking_service.db') as mock_db:
                # Mock get_booking_by_id
                mock_db.get_booking_by_id.return_value = {"id": 123, "worker_id": 1, "status": "ASSIGNED"}
                # Mock update_booking_status
                mock_db.update_booking_status.return_value = True
                
                payload = {
                    "booking_id": 123,
                    "status": "ACCEPTED"
                }
                response = self.client.post('/api/housekeeping/worker/update-status', json=payload)
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])

    def test_complete_booking(self):
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "worker", "data": {"id": 1}}, None)
            
            with patch('housekeeping.controllers.booking_controller.booking_service') as mock_service:
                # Mock get_booking_by_id via db
                mock_service.db.get_booking_by_id.return_value = {"id": 123, "worker_id": 1, "status": "IN_PROGRESS", "price": 100}
                # Mock complete_booking
                mock_service.complete_booking.return_value = (True, "Completed")
                
                payload = {
                    "booking_id": 123,
                    "status": "COMPLETED"
                }
                response = self.client.post('/api/housekeeping/worker/update-status', json=payload)
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])

    def test_get_wallet_balance(self):
        with patch('housekeeping.controllers.booking_controller.get_current_user') as mock_user:
            mock_user.return_value = ({"type": "worker", "data": {"id": 1}}, None)
            
            with patch('housekeeping.controllers.booking_controller.worker_db') as mock_worker_db:
                mock_worker_db.get_worker_by_id.return_value = {"id": 1, "wallet_balance": 500.0}
                
                response = self.client.get('/api/housekeeping/worker/balance')
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data['balance'], 500.0)

if __name__ == '__main__':
    unittest.main()
