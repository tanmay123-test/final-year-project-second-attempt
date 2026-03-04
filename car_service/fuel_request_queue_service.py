"""
Fuel Delivery Request Queue and Smart Dispatch Engine
"""

import sqlite3
import math
from datetime import datetime
from .fuel_delivery_db import fuel_delivery_db

class FuelRequestQueueService:
    def __init__(self):
        self.db = fuel_delivery_db
        self.MAX_SERVICE_RADIUS = 5.0  # km
    
    def get_available_fuel_requests(self, agent_id):
        """Get available fuel requests for an agent with filtering"""
        try:
            # Get agent profile
            agent = self.db.get_agent_details(agent_id)
            if not agent:
                return {'success': False, 'error': 'Agent not found'}
            
            # Get agent location (simplified - use stored location)
            agent_lat = agent.get('latitude', 0.0)
            agent_lon = agent.get('longitude', 0.0)
            
            # Get waiting requests
            waiting_requests = self.db.get_waiting_requests()
            
            eligible_requests = []
            
            for request in waiting_requests:
                # Apply vehicle capacity filtering
                if not self._is_vehicle_compatible(
                    agent.get('vehicle_type'), 
                    request.get('quantity_liters', 0)
                ):
                    continue
                
                # Apply GPS radius filtering
                request_lat = request.get('delivery_latitude', 0.0)
                request_lon = request.get('delivery_longitude', 0.0)
                
                distance_km = self._haversine_distance(
                    agent_lat, agent_lon, request_lat, request_lon
                )
                
                if distance_km > self.MAX_SERVICE_RADIUS:
                    continue
                
                # Calculate ETA
                eta_minutes = int(distance_km * 3)  # Simplified: 3 min per km
                
                # Calculate assignment score
                score = self._calculate_assignment_score(
                    agent, request, distance_km, eta_minutes
                )
                
                # Determine assigned reason
                assigned_reason = self._get_assignment_reason(score, agent, request)
                
                eligible_requests.append({
                    'request_id': request.get('request_id'),
                    'user_name': request.get('user_name', 'N/A'),
                    'user_phone': request.get('user_phone', 'N/A'),
                    'fuel_type': request.get('fuel_type', 'N/A'),
                    'quantity_liters': request.get('quantity_liters', 0),
                    'delivery_address': request.get('delivery_address', 'N/A'),
                    'distance_km': round(distance_km, 2),
                    'eta_minutes': eta_minutes,
                    'priority_level': request.get('priority_level', 3),
                    'assignment_score': round(score, 2),
                    'assigned_reason': assigned_reason
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
    
    def assign_fuel_request(self, agent_id, request_id):
        """Assign a fuel request to an agent"""
        try:
            # Update request status
            success = self.db.assign_request_to_agent(request_id, agent_id)
            if not success:
                return {'success': False, 'error': 'Failed to assign request'}
            
            # Update agent status to BUSY
            self.db.update_agent_online_status(agent_id, 'BUSY')
            
            # Log assignment
            self._log_agent_activity(agent_id, 'REQUEST_ACCEPTED', {
                'request_id': request_id
            })
            
            return {'success': True, 'message': 'Request assigned successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def reject_fuel_request(self, agent_id, request_id):
        """Reject a fuel request and reassign"""
        try:
            # Log rejection
            self._log_agent_activity(agent_id, 'REQUEST_REJECTED', {
                'request_id': request_id
            })
            
            # Set request back to waiting
            self.db.unassign_request(request_id)
            
            # Try to assign to next eligible agent
            next_agent = self._find_next_eligible_agent(request_id, agent_id)
            if next_agent:
                self.db.assign_request_to_agent(request_id, next_agent)
                self.db.update_agent_online_status(next_agent, 'BUSY')
                
                self._log_agent_activity(next_agent, 'AUTO_ASSIGNED', {
                    'request_id': request_id
                })
            
            return {'success': True, 'message': 'Request rejected and reassigned if available'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def auto_dispatch_waiting_requests(self):
        """Automatically dispatch waiting requests to available agents"""
        try:
            # Get all waiting requests
            waiting_requests = self.db.get_waiting_requests()
            
            if not waiting_requests:
                return {'success': True, 'dispatched': 0, 'message': 'No waiting requests'}
            
            dispatched_count = 0
            
            for request in waiting_requests:
                # Find best available agent
                best_agent = self._find_best_agent_for_request(request)
                
                if best_agent:
                    # Assign request
                    self.db.assign_request_to_agent(request.get('request_id'), best_agent['agent_id'])
                    self.db.update_agent_online_status(best_agent['agent_id'], 'BUSY')
                    
                    # Log assignment
                    self._log_agent_activity(best_agent['agent_id'], 'AUTO_ASSIGNED', {
                        'request_id': request.get('request_id')
                    })
                    
                    dispatched_count += 1
            
            return {
                'success': True,
                'dispatched': dispatched_count,
                'message': f'Auto-dispatched {dispatched_count} requests'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _is_vehicle_compatible(self, vehicle_type, fuel_quantity):
        """Check if vehicle can handle the fuel quantity"""
        capacity_limits = {
            'Bike': 10,
            'Van': 50,
            'Truck': 1000  # Large capacity
        }
        
        max_capacity = capacity_limits.get(vehicle_type, 10)
        return fuel_quantity <= max_capacity
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two GPS coordinates using Haversine formula"""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.sin(dlon/2)**2 * math.cos(lat2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return c * r
    
    def _calculate_assignment_score(self, agent, request, distance_km, eta_minutes):
        """Calculate assignment score for fair dispatch"""
        # Normalize factors to 0-1 scale
        
        # ETA score (lower ETA = higher score)
        eta_score = max(0, 1 - (eta_minutes / 30))  # 30 min as reference
        
        # Rating score (higher rating = higher score)
        rating_score = agent.get('rating', 0) / 5.0  # Normalize to 0-1
        
        # Completion rate score (higher completion = higher score)
        completion_rate = 0.8  # Placeholder - should come from agent stats
        
        # Fairness rotation score (boosts agents with fewer recent jobs)
        fairness_score = 0.5  # Placeholder - should track recent assignments
        
        # Weighted score calculation
        score = (
            0.35 * eta_score +
            0.25 * rating_score +
            0.20 * completion_rate +
            0.20 * fairness_score
        )
        
        return score
    
    def _get_assignment_reason(self, score, agent, request):
        """Generate transparent assignment reason"""
        if score >= 0.8:
            return "Closest available agent with excellent rating"
        elif score >= 0.6:
            return "Nearby agent with good reliability"
        elif score >= 0.4:
            return "Available agent within service area"
        else:
            return "Next available agent in queue"
    
    def _find_best_agent_for_request(self, request):
        """Find the best available agent for a request"""
        try:
            # Get all available agents
            available_agents = self.db.get_available_agents()
            
            if not available_agents:
                return None
            
            best_agent = None
            best_score = -1
            
            for agent in available_agents:
                # Check vehicle compatibility
                if not self._is_vehicle_compatible(
                    agent.get('vehicle_type'), 
                    request.get('quantity_liters', 0)
                ):
                    continue
                
                # Calculate distance and score
                agent_lat = agent.get('latitude', 0.0)
                agent_lon = agent.get('longitude', 0.0)
                request_lat = request.get('delivery_latitude', 0.0)
                request_lon = request.get('delivery_longitude', 0.0)
                
                distance_km = self._haversine_distance(
                    agent_lat, agent_lon, request_lat, request_lon
                )
                
                if distance_km > self.MAX_SERVICE_RADIUS:
                    continue
                
                eta_minutes = int(distance_km * 3)
                score = self._calculate_assignment_score(
                    agent, request, distance_km, eta_minutes
                )
                
                if score > best_score:
                    best_score = score
                    best_agent = {
                        'agent_id': agent.get('id'),
                        'score': score,
                        'distance_km': distance_km,
                        'eta_minutes': eta_minutes
                    }
            
            return best_agent
            
        except Exception as e:
            return None
    
    def _find_next_eligible_agent(self, request_id, exclude_agent_id):
        """Find next eligible agent for a request"""
        try:
            # Get request details
            waiting_requests = self.db.get_waiting_requests()
            request = None
            
            for req in waiting_requests:
                if req.get('request_id') == request_id:
                    request = req
                    break
            
            if not request:
                return None
            
            # Find best available agent (excluding the rejecting agent)
            available_agents = self.db.get_available_agents(exclude_agent_id)
            
            if not available_agents:
                return None
            
            best_agent = None
            best_score = -1
            
            for agent in available_agents:
                # Check vehicle compatibility
                if not self._is_vehicle_compatible(
                    agent.get('vehicle_type'), 
                    request.get('quantity_liters', 0)
                ):
                    continue
                
                # Calculate score
                agent_lat = agent.get('latitude', 0.0)
                agent_lon = agent.get('longitude', 0.0)
                request_lat = request.get('delivery_latitude', 0.0)
                request_lon = request.get('delivery_longitude', 0.0)
                
                distance_km = self._haversine_distance(
                    agent_lat, agent_lon, request_lat, request_lon
                )
                
                if distance_km > self.MAX_SERVICE_RADIUS:
                    continue
                
                eta_minutes = int(distance_km * 3)
                score = self._calculate_assignment_score(
                    agent, request, distance_km, eta_minutes
                )
                
                if score > best_score:
                    best_score = score
                    best_agent = agent.get('id')
            
            return best_agent
            
        except Exception as e:
            return None
    
    def _log_agent_activity(self, agent_id, event_type, details):
        """Log agent activity"""
        try:
            self.db.log_agent_activity(agent_id, event_type, details)
        except Exception:
            pass  # Log failures shouldn't break main flow

# Create service instance
fuel_request_queue_service = FuelRequestQueueService()
