"""
Fuel Delivery Agent Service Layer
Handles business logic for fuel delivery operations
"""

import os
import time
from datetime import datetime, timedelta
from .fuel_delivery_db import fuel_delivery_db
from werkzeug.security import generate_password_hash

class FuelDeliveryService:
    def __init__(self):
        self.db = fuel_delivery_db
    
    def register_agent(self, agent_data):
        """Register new fuel delivery agent with validation"""
        # Validate required fields
        required_fields = [
            'name', 'email', 'phone_number', 'password', 
            'city', 'vehicle_type', 'vehicle_number'
        ]
        
        for field in required_fields:
            if not agent_data.get(field):
                return {'success': False, 'error': f'{field} is required'}
        
        # Validate vehicle type
        valid_vehicles = ['Bike', 'Van', 'Truck']
        if agent_data['vehicle_type'] not in valid_vehicles:
            return {'success': False, 'error': 'Invalid vehicle type'}
        
        # Validate safety declaration
        if not agent_data.get('safety_declaration_accepted'):
            return {'success': False, 'error': 'Safety declaration must be accepted'}
        
        # Hash password
        agent_data['password_hash'] = generate_password_hash(agent_data['password'])
        del agent_data['password']  # Remove plain password
        
        # Register agent
        result = self.db.register_agent(agent_data)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Registration successful! Please wait for admin approval.',
                'agent_id': result['agent_id']
            }
        
        return result
    
    def authenticate_agent(self, email, password):
        """Authenticate fuel delivery agent"""
        return self.db.authenticate_agent(email, password)
    
    def update_agent_status(self, agent_id, status):
        """Update agent online status with validation"""
        # Get current agent details
        agent = self.db.get_agent_details(agent_id)
        if not agent:
            return {'success': False, 'error': 'Agent not found'}
        
        # Check if agent is approved
        if agent['approval_status'] != 'APPROVED':
            return {'success': False, 'error': 'Agent not approved'}
        
        # Update status
        success = self.db.update_agent_status(agent_id, status)
        
        status_messages = {
            'OFFLINE': 'You are now offline',
            'ONLINE_AVAILABLE': 'You are now online and available for deliveries',
            'BUSY': 'You are now busy with a delivery'
        }
        
        return {
            'success': success,
            'message': status_messages.get(status, 'Status updated')
        }
    
    def get_nearby_agents(self, user_lat, user_lon, radius_km=10):
        """Get nearby available fuel agents"""
        if not user_lat or not user_lon:
            return []
        
        return self.db.get_nearby_agents(user_lat, user_lon, radius_km)
    
    def create_fuel_request(self, request_data):
        """Create new fuel delivery request"""
        # Validate required fields
        required_fields = ['user_id', 'fuel_type', 'quantity_liters']
        
        for field in required_fields:
            if not request_data.get(field):
                return {'success': False, 'error': f'{field} is required'}
        
        # Validate fuel type
        valid_fuels = ['Petrol', 'Diesel']
        if request_data['fuel_type'] not in valid_fuels:
            return {'success': False, 'error': 'Invalid fuel type'}
        
        # Validate quantity
        if request_data['quantity_liters'] <= 0:
            return {'success': False, 'error': 'Quantity must be greater than 0'}
        
        return self.db.create_fuel_request(request_data)
    
    def get_fuel_requests_queue(self, agent_lat=None, agent_lon=None):
        """Get fuel delivery requests queue"""
        return self.db.get_fuel_requests_queue(agent_lat, agent_lon)
    
    def assign_fuel_request(self, request_id, agent_id):
        """Assign fuel request to agent"""
        # Check if agent is available
        agent = self.db.get_agent_details(agent_id)
        if not agent:
            return {'success': False, 'error': 'Agent not found'}
        
        if agent['online_status'] != 'ONLINE_AVAILABLE':
            return {'success': False, 'error': 'Agent is not available'}
        
        success = self.db.assign_fuel_request(request_id, agent_id)
        
        if success:
            return {
                'success': True,
                'message': 'Fuel request assigned successfully',
                'request_id': request_id
            }
        
        return {'success': False, 'error': 'Failed to assign request'}
    
    def complete_fuel_delivery(self, request_id, agent_id):
        """Complete fuel delivery"""
        result = self.db.complete_fuel_delivery(request_id, agent_id)
        
        if result:
            return {
                'success': True,
                'message': 'Delivery completed successfully',
                'earnings': result
            }
        
        return {'success': False, 'error': 'Failed to complete delivery'}
    
    def add_agent_review(self, agent_id, user_id, rating, review_text=None):
        """Add review for fuel agent"""
        # Validate rating
        if not 1 <= rating <= 5:
            return {'success': False, 'error': 'Rating must be between 1 and 5'}
        
        success = self.db.add_agent_review(agent_id, user_id, rating, review_text)
        
        return {
            'success': success,
            'message': 'Review added successfully' if success else 'Failed to add review'
        }
    
    def get_agent_performance(self, agent_id):
        """Get comprehensive agent performance metrics"""
        performance = self.db.get_agent_performance(agent_id)
        
        # Calculate additional metrics
        performance['badges'] = self.db.get_agent_badges(agent_id)
        
        # Determine performance level
        if performance['rating'] >= 4.5:
            performance['performance_level'] = 'Excellent'
        elif performance['rating'] >= 4.0:
            performance['performance_level'] = 'Very Good'
        elif performance['rating'] >= 3.5:
            performance['performance_level'] = 'Good'
        elif performance['rating'] >= 3.0:
            performance['performance_level'] = 'Average'
        else:
            performance['performance_level'] = 'Needs Improvement'
        
        return performance
    
    def get_agent_dashboard_data(self, agent_id):
        """Get dashboard data for fuel agent"""
        agent = self.db.get_agent_details(agent_id)
        if not agent:
            return None
        
        performance = self.get_agent_performance(agent_id)
        requests_queue = self.get_fuel_requests_queue()
        
        # Filter agent's current delivery
        current_delivery = None
        for request in requests_queue:
            if request.get('agent_id') == agent_id and request.get('status') == 'IN_PROGRESS':
                current_delivery = request
                break
        
        return {
            'agent': agent,
            'performance': performance,
            'requests_queue': requests_queue,
            'current_delivery': current_delivery,
            'online_hours_today': self._calculate_online_hours(agent_id)
        }
    
    def _calculate_online_hours(self, agent_id):
        """Calculate online hours for today"""
        # This is a simplified calculation
        # In production, you'd track actual login/logout times
        return 8.5  # Example: 8.5 hours today

# Create service instance
fuel_delivery_service = FuelDeliveryService()
