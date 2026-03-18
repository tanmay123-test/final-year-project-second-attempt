"""
Fuel Delivery Agent Service Layer
Handles business logic for fuel delivery operations
"""

import os
import time
from datetime import datetime, timedelta
from .fuel_delivery_db import fuel_delivery_db
from werkzeug.security import generate_password_hash
from .car_service_worker_db import car_service_worker_db

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
        
        # Preserve plain password for unified car service worker record
        plain_password = agent_data['password']
        # Hash password for fuel agent DB
        agent_data['password_hash'] = generate_password_hash(plain_password)
        del agent_data['password']  # Remove plain password for storage in fuel DB
        
        # Register agent
        result = self.db.register_agent(agent_data)
        
        if result['success']:
            # Also create a corresponding unified car service worker entry for admin approval
            car_worker_id = None
            try:
                car_worker_id = car_service_worker_db.create_worker(
                    name=agent_data['name'],
                    email=agent_data['email'],
                    phone=agent_data['phone_number'],
                    password=plain_password,
                    role="Fuel Delivery Agent",
                    age=25,  # default if not provided
                    city=agent_data['city'],
                    address="Not provided",
                    experience=0,
                    skills="Fuel Handling, Safety Compliance",
                    vehicle_number=agent_data.get('vehicle_number'),
                    vehicle_model=agent_data.get('vehicle_type'),
                    loading_capacity=None,
                    profile_photo=None,
                    aadhaar_path=None,
                    license_path=None,
                    certificate_path=None,
                    vehicle_rc_path=None,
                    truck_photo_path=None,
                    security_declaration=True
                )
            except Exception:
                # Ignore errors if already exists or any constraint violations
                try:
                    existing = car_service_worker_db.get_worker_by_email(agent_data['email'])
                    if existing:
                        car_worker_id = existing.get('id')
                except Exception:
                    pass
            
            return {
                'success': True,
                'message': 'Registration successful! Please wait for admin approval.',
                'agent_id': result['agent_id'],
                'car_worker_id': car_worker_id
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
        
        # If coordinates are missing, try to infer from service area
        try:
            lat = agent.get('latitude') or 0.0
            lon = agent.get('longitude') or 0.0
            if (not lat or not lon) and agent.get('service_area_location'):
                loc = (agent.get('service_area_location') or '').strip().lower()
                coord_map = {
                    'asalpha': (19.0954, 72.8783),
                    'bandra': (19.0596, 72.8295),
                    'andheri': (19.1196, 72.8465),
                    'worli': (19.0170, 72.8300),
                    'dadar': (19.0190, 72.8420),
                    'kurla': (19.0726, 72.8761),
                    'goregaon': (19.1661, 72.8576),
                    'bkc': (19.0681, 72.8407)
                }
                if loc in coord_map:
                    (g_lat, g_lon) = coord_map[loc]
                    try:
                        self.db.update_agent_location(agent_id, g_lat, g_lon)
                        agent['latitude'], agent['longitude'] = g_lat, g_lon
                    except Exception:
                        pass
        except Exception:
            pass
        
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
    
    def get_available_agents(self):
        """Get all available (approved + online) agents with metrics"""
        return self.db.get_available_agents()
    
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
    
    # Admin methods
    def get_pending_agents(self):
        """Get all pending fuel delivery agents"""
        try:
            agents = self.db.get_agents_by_status('PENDING')
            return agents
        except Exception as e:
            raise Exception(f"Failed to fetch pending agents: {str(e)}")
    
    def get_approved_agents(self):
        """Get all approved fuel delivery agents"""
        try:
            agents = self.db.get_agents_by_status('APPROVED')
            return agents
        except Exception as e:
            raise Exception(f"Failed to fetch approved agents: {str(e)}")
    
    def get_agent_by_id(self, agent_id):
        """Get specific agent by ID"""
        try:
            agent = self.db.get_agent_details(agent_id)
            return agent
        except Exception as e:
            raise Exception(f"Failed to fetch agent details: {str(e)}")
    
    def approve_agent(self, agent_id):
        """Approve a fuel delivery agent"""
        try:
            # Update status in fuel delivery DB
            result = self.db.update_agent_status(agent_id, 'APPROVED')
            
            if result:
                # Also update status in unified car service worker DB
                car_service_worker_db.update_worker_status(agent_id, 'APPROVED')
                
                return {'success': True, 'message': 'Agent approved successfully'}
            else:
                return {'success': False, 'error': 'Failed to approve agent'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def reject_agent(self, agent_id):
        """Reject a fuel delivery agent"""
        try:
            # Update status in fuel delivery DB
            result = self.db.update_agent_status(agent_id, 'REJECTED')
            
            if result:
                # Also update status in unified car service worker DB
                car_service_worker_db.update_worker_status(agent_id, 'REJECTED')
                
                return {'success': True, 'message': 'Agent rejected successfully'}
            else:
                return {'success': False, 'error': 'Failed to reject agent'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Availability Engine Methods
    def update_agent_status(self, agent_id, new_status):
        """Update agent online status with validation and auto-queue pickup"""
        try:
            # Get current agent info
            agent = self.db.get_agent_details(agent_id)
            if not agent:
                return {'success': False, 'error': 'Agent not found'}
            
            current_status = agent.get('online_status', 'OFFLINE')
            
            # Validate state transitions
            if not self._is_valid_status_transition(current_status, new_status):
                return {'success': False, 'error': f'Invalid status transition: {current_status} → {new_status}'}
            
            # If going online, perform validations
            if new_status == 'ONLINE_AVAILABLE':
                validation_result = self._validate_go_online(agent)
                if not validation_result['valid']:
                    return {'success': False, 'error': validation_result['error']}
            
            # Update status
            success = self.db.update_agent_online_status(agent_id, new_status)
            if not success:
                return {'success': False, 'error': 'Failed to update status'}
            
            # Log activity
            self._log_agent_activity(agent_id, 'STATUS_CHANGE', {
                'from_status': current_status,
                'to_status': new_status
            })
            
            # Auto queue pickup when going online
            if new_status == 'ONLINE_AVAILABLE':
                auto_assign_result = self._auto_queue_pickup(agent_id)
                if auto_assign_result['assigned']:
                    # Agent becomes BUSY due to assignment
                    self.db.update_agent_online_status(agent_id, 'BUSY')
                    return {
                        'success': True, 
                        'message': 'Online and auto-assigned delivery request',
                        'auto_assigned': True,
                        'request_id': auto_assign_result['request_id']
                    }
            
            return {'success': True, 'message': f'Status updated to {new_status}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_agent_status(self, agent_id):
        """Get current agent status and availability info"""
        try:
            agent = self.db.get_agent_details(agent_id)
            if not agent:
                return {'success': False, 'error': 'Agent not found'}
            
            # Check for active delivery
            active_delivery = self.db.get_active_delivery(agent_id)
            
            return {
                'success': True,
                'agent_id': agent_id,
                'current_status': agent.get('online_status', 'OFFLINE'),
                'approval_status': agent.get('approval_status'),
                'active_delivery_id': active_delivery.get('request_id') if active_delivery else None,
                'vehicle_type': agent.get('vehicle_type'),
                'total_deliveries': agent.get('total_deliveries', 0),
                'rating': agent.get('rating', 0.0)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_eligible_requests(self, agent_id):
        """Get eligible fuel requests for agent with capacity and radius filtering"""
        try:
            agent = self.db.get_agent_details(agent_id)
            if not agent:
                return {'success': False, 'error': 'Agent not found'}
            
            # Check if agent is available
            if agent.get('online_status') != 'ONLINE_AVAILABLE':
                return {'success': False, 'error': 'Agent not available for requests'}
            
            # Get waiting requests
            waiting_requests = self.db.get_waiting_requests()
            
            # Filter by capacity and calculate scores
            eligible_requests = []
            for request in waiting_requests:
                # Check vehicle capacity compatibility
                if not self._is_capacity_compatible(agent.get('vehicle_type'), request.get('quantity', 0)):
                    continue
                
                # Calculate distance and ETA (simplified for now)
                distance_km = self._calculate_distance(
                    agent.get('latitude', 0), agent.get('longitude', 0),
                    request.get('latitude', 0), request.get('longitude', 0)
                )
                
                # Filter by radius (5km default)
                if distance_km > 5.0:
                    continue
                
                # Calculate ETA (simplified: 3 min per km)
                eta_minutes = int(distance_km * 3)
                
                # Calculate assignment score
                score = self._calculate_assignment_score(agent, request, distance_km, eta_minutes)
                
                eligible_requests.append({
                    **request,
                    'distance_km': round(distance_km, 2),
                    'eta_minutes': eta_minutes,
                    'assignment_score': score
                })
            
            # Sort by score (highest first)
            eligible_requests.sort(key=lambda x: x['assignment_score'], reverse=True)
            
            return {
                'success': True,
                'requests': eligible_requests,
                'total_count': len(eligible_requests)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_demand_insights(self, region):
        """Get demand indicators and smart suggestions"""
        try:
            # Calculate current demand
            waiting_requests = self.db.get_waiting_requests_count()
            available_agents = self.db.get_available_agents_count()
            
            insights = {
                'waiting_requests': waiting_requests,
                'available_agents': available_agents,
                'demand_level': 'NORMAL'
            }
            
            # Determine demand level
            if waiting_requests > available_agents * 2:
                insights['demand_level'] = 'HIGH'
                insights['demand_message'] = f'High fuel demand in {region} – {waiting_requests} requests waiting'
            elif waiting_requests > available_agents:
                insights['demand_level'] = 'MODERATE'
                insights['demand_message'] = f'Moderate fuel demand in {region}'
            else:
                insights['demand_message'] = f'Normal fuel demand in {region}'
            
            # Smart suggestion (simplified)
            insights['suggestion'] = 'Peak demand expected between 6 PM – 9 PM'
            
            return {'success': True, 'insights': insights}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def accept_request(self, agent_id, request_id):
        """Accept a fuel delivery request"""
        try:
            # Check if agent is available
            agent = self.db.get_agent_details(agent_id)
            if not agent or agent.get('online_status') != 'ONLINE_AVAILABLE':
                return {'success': False, 'error': 'Agent not available'}
            
            # Check for busy protection
            if self._has_active_delivery(agent_id):
                return {'success': False, 'error': 'Agent already has active delivery'}
            
            # Assign request
            success = self.db.assign_request_to_agent(request_id, agent_id)
            if not success:
                return {'success': False, 'error': 'Failed to assign request'}
            
            # Update agent status to BUSY
            self.db.update_agent_online_status(agent_id, 'BUSY')
            
            # Log activity
            self._log_agent_activity(agent_id, 'REQUEST_ACCEPTED', {'request_id': request_id})
            
            return {'success': True, 'message': 'Request accepted successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def reject_request(self, agent_id, request_id):
        """Reject a fuel delivery request"""
        try:
            # Log rejection
            self._log_agent_activity(agent_id, 'REQUEST_REJECTED', {'request_id': request_id})
            
            # Mark request as waiting again
            self.db.unassign_request(request_id)
            
            # Try to assign to next eligible agent
            next_agent = self._find_next_eligible_agent(request_id, agent_id)
            if next_agent:
                self.db.assign_request_to_agent(request_id, next_agent)
                self.db.update_agent_online_status(next_agent, 'BUSY')
            
            return {'success': True, 'message': 'Request rejected and reassigned if available'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Helper methods
    def _is_valid_status_transition(self, from_status, to_status):
        """Validate status transitions"""
        valid_transitions = {
            'OFFLINE': ['ONLINE_AVAILABLE'],
            'ONLINE_AVAILABLE': ['OFFLINE', 'BUSY'],
            'BUSY': ['ONLINE_AVAILABLE']  # Only after delivery completion
        }
        return to_status in valid_transitions.get(from_status, [])
    
    def _validate_go_online(self, agent):
        """Validate agent can go online"""
        if agent.get('approval_status') != 'APPROVED':
            return {'valid': False, 'error': 'Agent not approved by admin'}
        
        # Check document validity (simplified)
        if not self._are_documents_valid(agent):
            return {'valid': False, 'error': 'Compliance documents expired'}
        
        if not agent.get('vehicle_number'):
            return {'valid': False, 'error': 'Vehicle verification incomplete'}
        
        return {'valid': True}
    
    def _are_documents_valid(self, agent):
        """Check if agent documents are valid"""
        # Simplified check - in production, check expiry dates
        return agent.get('approval_status') == 'APPROVED'
    
    def _auto_queue_pickup(self, agent_id):
        """Automatically assign oldest waiting request"""
        try:
            waiting_requests = self.db.get_waiting_requests(limit=1)
            if not waiting_requests:
                return {'assigned': False}
            
            request = waiting_requests[0]
            agent = self.db.get_agent_details(agent_id)
            
            # Check compatibility
            if not self._is_capacity_compatible(agent.get('vehicle_type'), request.get('quantity', 0)):
                return {'assigned': False}
            
            # Assign request
            self.db.assign_request_to_agent(request['id'], agent_id)
            
            # Log auto assignment
            self._log_agent_activity(agent_id, 'AUTO_ASSIGNED', {'request_id': request['id']})
            
            return {'assigned': True, 'request_id': request['id']}
            
        except Exception:
            return {'assigned': False}
    
    def _is_capacity_compatible(self, vehicle_type, quantity):
        """Check if vehicle can handle the fuel quantity"""
        capacity_limits = {
            'Bike': 10,
            'Van': 50,
            'Truck': 1000  # Large capacity
        }
        max_capacity = capacity_limits.get(vehicle_type, 10)
        return quantity <= max_capacity
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points (simplified)"""
        # Simplified distance calculation - use Haversine in production
        return abs(lat1 - lat2) + abs(lon1 - lon2)  # Placeholder
    
    def _calculate_assignment_score(self, agent, request, distance, eta):
        """Calculate assignment score for fair dispatch"""
        # Simplified scoring
        rating_score = agent.get('rating', 0) / 5.0  # Normalize to 0-1
        eta_score = max(0, 1 - (eta / 30))  # Lower ETA = higher score
        completion_score = 0.8  # Placeholder
        fairness_score = 0.5  # Placeholder
        
        return (0.35 * eta_score) + (0.25 * rating_score) + (0.20 * completion_score) + (0.20 * fairness_score)
    
    def _has_active_delivery(self, agent_id):
        """Check if agent has active delivery"""
        return self.db.get_active_delivery(agent_id) is not None
    
    def _find_next_eligible_agent(self, request_id, exclude_agent_id):
        """Find next eligible agent for request"""
        # Simplified - in production, use proper scoring
        available_agents = self.db.get_available_agents(exclude_agent_id)
        return available_agents[0]['id'] if available_agents else None
    
    def _log_agent_activity(self, agent_id, event_type, details):
        """Log agent activity"""
        try:
            self.db.log_agent_activity(agent_id, event_type, details)
        except Exception:
            pass  # Log failures shouldn't break main flow
    
    # Additional methods for queue and dispatch
    def get_active_delivery(self, agent_id):
        """Get active delivery for an agent"""
        try:
            active_delivery = self.db.get_active_delivery(agent_id)
            return active_delivery
        except Exception as e:
            return None
    
    def get_delivery_history(self, agent_id):
        """Get delivery history for an agent with address from request (for History & Earnings screen)"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT h.delivery_id, h.agent_id, h.user_id, h.fuel_type, h.quantity, h.earnings, h.status, h.completed_at, h.request_id,
                       r.address, r.user_name
                FROM fuel_delivery_history h
                LEFT JOIN fuel_delivery_requests r ON r.id = h.request_id
                WHERE h.agent_id = ?
                ORDER BY h.completed_at DESC
            ''', (agent_id,))
            rows = cursor.fetchall()
            self.db.conn.commit()
            cursor.close()
            result = []
            for row in rows:
                r = dict(row) if hasattr(row, 'keys') else None
                if not r:
                    col = ['delivery_id', 'agent_id', 'user_id', 'fuel_type', 'quantity', 'earnings', 'status', 'completed_at', 'request_id', 'address', 'user_name']
                    r = dict(zip(col, row)) if len(row) >= len(col) else {}
                status = (r.get('status') or '').lower()
                result.append({
                    'id': r.get('delivery_id'),
                    'delivery_id': r.get('delivery_id'),
                    'request_id': r.get('request_id'),
                    'fuel_type': r.get('fuel_type') or 'Petrol',
                    'quantity_liters': r.get('quantity') or 0,
                    'earnings': float(r.get('earnings') or 0),
                    'estimated_earnings': float(r.get('earnings') or 0),
                    'status': 'completed' if status == 'completed' else 'cancelled' if status == 'cancelled' else status,
                    'completed_at': r.get('completed_at'),
                    'created_at': r.get('completed_at'),
                    'delivery_address': r.get('address') or '',
                    'address': r.get('address') or '',
                    'user_name': r.get('user_name') or '',
                    'station_name': r.get('address') or f"Delivery #{r.get('delivery_id') or ''}",
                })
            return result
        except Exception as e:
            return []
    
    def get_available_agents(self):
        """Get all available fuel delivery agents"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT id, name, vehicle_type, latitude, longitude, service_area_km,
                       rating, completion_rate, online_status, approval_status
                FROM fuel_delivery_agents
                WHERE online_status = 'ONLINE_AVAILABLE'
                AND approval_status = 'APPROVED'
                ORDER BY rating DESC, completion_rate DESC
            ''')
            
            agents = cursor.fetchall()
            self.db.conn.commit()
            cursor.close()
            
            agent_list = []
            for agent in agents:
                agent_list.append({
                    'id': agent[0],
                    'name': agent[1],
                    'vehicle_type': agent[2],
                    'latitude': agent[3],
                    'longitude': agent[4],
                    'service_area_km': agent[5],
                    'rating': agent[6],
                    'completion_rate': agent[7],
                    'online_status': agent[8],
                    'approval_status': agent[9]
                })
            
            return agent_list
            
        except Exception as e:
            return []
    
    def create_fuel_request(self, user_id, fuel_type, fuel_quantity, latitude, longitude, agent_id=None):
        """Create fuel delivery request"""
        try:
            cursor = self.db.conn.cursor()
            
            # If agent_id is provided, assign immediately
            if agent_id:
                status = 'ASSIGNED'
            else:
                status = 'SEARCHING'
                # Auto-assign best agent
                agent_id = self._auto_assign_agent(latitude, longitude, fuel_quantity)
                if agent_id:
                    status = 'ASSIGNED'
            
            cursor.execute('''
                INSERT INTO fuel_delivery_requests
                (user_id, agent_id, fuel_type, fuel_quantity, latitude, longitude, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, agent_id, fuel_type, fuel_quantity, latitude, longitude, status))
            
            request_id = cursor.lastrowid
            
            # Update agent status if assigned
            if agent_id and status == 'ASSIGNED':
                cursor.execute('''
                    UPDATE fuel_delivery_agents
                    SET online_status = 'BUSY'
                    WHERE id = ?
                ''', (agent_id,))
            
            self.db.conn.commit()
            cursor.close()
            
            return {
                'success': True,
                'request_id': request_id,
                'agent_id': agent_id,
                'status': status
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_requests(self, user_id):
        """Get fuel requests for a user"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT r.*, a.name as agent_name, a.vehicle_type, a.rating
                FROM fuel_delivery_requests r
                LEFT JOIN fuel_delivery_agents a ON r.agent_id = a.id
                WHERE r.user_id = ?
                ORDER BY r.created_at DESC
            ''', (user_id,))
            
            requests = cursor.fetchall()
            self.db.conn.commit()
            cursor.close()
            
            request_list = []
            for req in requests:
                request_list.append({
                    'request_id': req[0],
                    'user_id': req[1],
                    'agent_id': req[2],
                    'fuel_type': req[3],
                    'fuel_quantity': req[4],
                    'latitude': req[5],
                    'longitude': req[6],
                    'status': req[7],
                    'created_at': req[8],
                    'agent_name': req[9] if len(req) > 9 else None,
                    'vehicle_type': req[10] if len(req) > 10 else None,
                    'rating': req[11] if len(req) > 11 else None
                })
            
            return request_list
            
        except Exception as e:
            return []
    
    def get_request_status(self, request_id):
        """Get fuel request status"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT r.*, a.name as agent_name, a.phone_number as agent_phone
                FROM fuel_delivery_requests r
                LEFT JOIN fuel_delivery_agents a ON r.agent_id = a.id
                WHERE r.id = ?
            ''', (request_id,))
            
            request = cursor.fetchone()
            self.db.conn.commit()
            cursor.close()
            
            if request:
                return {
                    'request_id': request[0],
                    'user_id': request[1],
                    'agent_id': request[2],
                    'fuel_type': request[3],
                    'fuel_quantity': request[4],
                    'latitude': request[5],
                    'longitude': request[6],
                    'status': request[7],
                    'created_at': request[8],
                    'agent_name': request[9] if len(request) > 9 else None,
                    'agent_phone': request[10] if len(request) > 10 else None
                }
            
            return None
            
        except Exception as e:
            return None
    
    def _auto_assign_agent(self, latitude, longitude, fuel_quantity):
        """Auto-assign best agent based on distance, rating, and availability"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT id, name, latitude, longitude, service_area_km, rating, completion_rate
                FROM fuel_delivery_agents
                WHERE online_status = 'ONLINE_AVAILABLE'
                AND approval_status = 'APPROVED'
            ''')
            
            agents = cursor.fetchall()
            best_agent_id = None
            best_score = -1
            
            for agent in agents:
                agent_id = agent[0]
                agent_lat = agent[2]
                agent_lon = agent[3]
                service_area_km = agent[4]
                
                # Calculate distance
                distance = self._calculate_distance(latitude, longitude, agent_lat, agent_lon)
                
                # Service area validation
                if distance <= service_area_km:
                    # Capacity validation
                    cursor.execute('SELECT vehicle_type FROM fuel_delivery_agents WHERE id = ?', (agent_id,))
                    vehicle_result = cursor.fetchone()
                    if vehicle_result:
                        vehicle_type = vehicle_result[0]
                        max_capacity = self._get_max_capacity(vehicle_type)
                        
                        if fuel_quantity <= max_capacity:
                            # Calculate score
                            eta_score = max(0, 1 - (distance * 3 / 30))  # ETA score
                            rating_score = agent[5] / 5.0  # Rating score
                            completion_score = agent[6] / 100.0  # Completion score
                            
                            total_score = (
                                0.35 * eta_score +
                                0.30 * rating_score +
                                0.20 * 0.5 +  # Fairness score (placeholder)
                                0.15 * completion_score
                            )
                            
                            if total_score > best_score:
                                best_score = total_score
                                best_agent_id = agent_id
            
            self.db.conn.commit()
            cursor.close()
            
            return best_agent_id
            
        except Exception as e:
            return None
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates"""
        import math
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _get_max_capacity(self, vehicle_type):
        """Get maximum fuel capacity for vehicle type"""
        capacities = {
            'Bike': 10,
            'Van': 50,
            'Truck': 1000
        }
        return capacities.get(vehicle_type, 10)
    
    def get_agent_performance(self, agent_id):
        """Get agent performance metrics and reputation (for Performance & Safety screen)."""
        try:
            perf = self.db.get_agent_performance(agent_id)
            badges = self.db.get_agent_badges(agent_id)
            reviews = self.db.get_agent_reviews(agent_id, limit=20)
            total_deliveries = perf.get('total_deliveries') or 0
            rating = perf.get('rating') or 0.0
            if total_deliveries >= 500:
                performance_level = 'Platinum'
            elif total_deliveries >= 200:
                performance_level = 'Gold'
            elif total_deliveries >= 50:
                performance_level = 'Silver'
            else:
                performance_level = 'Bronze'
            completion_rate = perf.get('completion_rate', 0)
            recent = perf.get('recent_deliveries', 0)
            avg_mins = perf.get('avg_delivery_time_minutes', 28)
            achievements = []
            if total_deliveries >= 50 and rating >= 4.5:
                achievements.append({'id': 'top_performer', 'title': 'Top Performer', 'subtitle': 'Top 5% this month', 'icon': 'trophy', 'highlight': True})
            if total_deliveries >= 100 and avg_mins <= 25:
                achievements.append({'id': 'speed_demon', 'title': 'Speed Demon', 'subtitle': f'{total_deliveries} deliveries under 20 min', 'icon': 'zap', 'highlight': True})
            if completion_rate >= 99.9 and recent >= 1:
                achievements.append({'id': 'perfect_score', 'title': 'Perfect Score', 'subtitle': '30-day 100% completion', 'icon': 'target', 'highlight': True})
            if perf.get('safety_score', 98) >= 98:
                achievements.append({'id': 'safety_first', 'title': 'Safety First', 'subtitle': '1 year zero incidents', 'icon': 'shield', 'highlight': True})
            if len(achievements) < 4:
                for bid in ['top_performer', 'speed_demon', 'perfect_score', 'safety_first']:
                    if not any(a['id'] == bid for a in achievements):
                        defaults = {'top_performer': ('Top Performer', 'Top 5% this month', 'trophy'), 'speed_demon': ('Speed Demon', '100 deliveries under 20 min', 'zap'), 'perfect_score': ('Perfect Score', '30-day 100% completion', 'target'), 'safety_first': ('Safety First', '1 year zero incidents', 'shield')}
                        t, s, i = defaults.get(bid, ('Achievement', '', 'medal'))
                        achievements.append({'id': bid, 'title': t, 'subtitle': s, 'icon': i, 'highlight': False})
                achievements = achievements[:4]
            return {
                'performance_level': performance_level,
                'rating': rating,
                'total_deliveries': total_deliveries,
                'completion_rate': completion_rate,
                'recent_deliveries': recent,
                'review_count': perf.get('review_count', 0),
                'avg_delivery_time_minutes': avg_mins,
                'on_time_rate': perf.get('on_time_rate', 94),
                'safety_score': perf.get('safety_score', 98),
                'badges': badges,
                'achievements': achievements,
                'reviews': reviews,
                'is_verified': perf.get('is_verified', False),
                'approval_status': perf.get('approval_status', 'PENDING'),
            }
        except Exception as e:
            defaults_ach = [{'id': 'top_performer', 'title': 'Top Performer', 'subtitle': 'Top 5% this month', 'icon': 'trophy', 'highlight': False}, {'id': 'speed_demon', 'title': 'Speed Demon', 'subtitle': '100 deliveries under 20 min', 'icon': 'zap', 'highlight': False}, {'id': 'perfect_score', 'title': 'Perfect Score', 'subtitle': '30-day 100% completion', 'icon': 'target', 'highlight': False}, {'id': 'safety_first', 'title': 'Safety First', 'subtitle': '1 year zero incidents', 'icon': 'shield', 'highlight': False}]
            return {
                'performance_level': 'Bronze',
                'rating': 0.0,
                'total_deliveries': 0,
                'completion_rate': 0.0,
                'recent_deliveries': 0,
                'review_count': 0,
                'avg_delivery_time_minutes': 28,
                'on_time_rate': 94.0,
                'safety_score': 98.0,
                'badges': [],
                'achievements': defaults_ach,
                'reviews': [],
                'is_verified': False,
                'approval_status': 'PENDING',
            }
    
    def get_active_delivery(self, agent_id):
        """Get active delivery for agent"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT * FROM fuel_delivery_requests 
                WHERE agent_id = ? 
                AND status IN ('ASSIGNED', 'IN_PROGRESS')
                LIMIT 1
            ''', (agent_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            return None
    
    def get_agent_earnings(self, agent_id):
        """Get total earnings for agent"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT COALESCE(SUM(earnings), 0) as total_earnings
                FROM fuel_delivery_history 
                WHERE agent_id = ? AND status = 'COMPLETED'
            ''', (agent_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            return {
                'total_earnings': result['total_earnings'] if result else 0
            }
        except Exception as e:
            return {'total_earnings': 0}
    
    def accept_delivery_request(self, request_id, agent_id):
        """Accept a fuel delivery request"""
        try:
            cursor = self.db.conn.cursor()
            
            # Check if request exists and is available (using id instead of request_id)
            cursor.execute('''
                SELECT * FROM fuel_delivery_requests 
                WHERE id = ? AND status = 'PENDING'
            ''', (request_id,))
            
            request = cursor.fetchone()
            if not request:
                return {'success': False, 'error': 'Request not found or already taken'}
            
            # Check if agent already has an active delivery
            cursor.execute('''
                SELECT * FROM fuel_delivery_requests 
                WHERE agent_id = ? AND status IN ('ASSIGNED', 'IN_PROGRESS')
            ''', (agent_id,))
            
            active_delivery = cursor.fetchone()
            if active_delivery:
                return {'success': False, 'error': 'Agent already has an active delivery'}
            
            # Update request status and assign agent
            cursor.execute('''
                UPDATE fuel_delivery_requests 
                SET agent_id = ?, status = 'ASSIGNED', assigned_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (agent_id, request_id))
            
            # Update agent status to busy
            cursor.execute('''
                UPDATE fuel_delivery_agents 
                SET online_status = 'BUSY'
                WHERE id = ?
            ''', (agent_id,))
            
            self.db.conn.commit()
            cursor.close()
            
            return {
                'success': True,
                'message': 'Request accepted successfully',
                'request_id': request_id
            }
            
        except Exception as e:
            self.db.conn.rollback()
            return {'success': False, 'error': str(e)}
    
    def reject_delivery_request(self, request_id, agent_id):
        """Reject a fuel delivery request (for frontend - just remove from list)"""
        try:
            # For now, just return success - the request remains available for other agents
            # In a real system, you might track rejection reasons or timeouts
            return {
                'success': True,
                'message': 'Request rejected',
                'request_id': request_id
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Create service instance
fuel_delivery_service = FuelDeliveryService()
