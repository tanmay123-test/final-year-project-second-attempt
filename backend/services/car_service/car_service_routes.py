"""
Car Service Routes using Organized Database Manager
Provides API endpoints for car service
"""

from flask import Blueprint, request, jsonify
from database.database_manager import db_manager
from auth_utils import generate_token, verify_token
from datetime import datetime
import json

# Create blueprint
car_service_bp = Blueprint('car_service', __name__)

# Car Service Routes
@car_service_bp.route('/api/car_service/mechanics', methods=['GET'])
def get_mechanics():
    """Get car service mechanics"""
    try:
        # Get filters from query params
        is_verified = request.args.get('is_verified', 'true').lower() == 'true'
        search = request.args.get('search')
        
        # Get mechanics from organized database
        mechanics = db_manager.get_mechanics()
        
        # Filter mechanics
        filtered_mechanics = []
        for mechanic in mechanics:
            if is_verified and not mechanic.get('is_verified'):
                continue
            if search and search.lower() not in mechanic.get('name', '').lower():
                continue
            filtered_mechanics.append(mechanic)
        
        return jsonify({
            "success": True,
            "mechanics": filtered_mechanics
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get mechanics: {str(e)}"
        }), 500

@car_service_bp.route('/api/car_service/fuel_delivery', methods=['GET'])
def get_fuel_delivery_agents():
    """Get fuel delivery agents"""
    try:
        # Get filters from query params
        is_verified = request.args.get('is_verified', 'true').lower() == 'true'
        search = request.args.get('search')
        
        # Get fuel delivery agents from organized database
        agents = db_manager.get_fuel_delivery_agents()
        
        # Filter agents
        filtered_agents = []
        for agent in agents:
            if is_verified and not agent.get('is_verified'):
                continue
            if search and search.lower() not in agent.get('name', '').lower():
                continue
            filtered_agents.append(agent)
        
        return jsonify({
            "success": True,
            "agents": filtered_agents
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get fuel delivery agents: {str(e)}"
        }), 500

@car_service_bp.route('/api/car_service/tow_truck', methods=['GET'])
def get_tow_truck_operators():
    """Get tow truck operators"""
    try:
        # Get filters from query params
        is_verified = request.args.get('is_verified', 'true').lower() == 'true'
        search = request.args.get('search')
        
        # Get tow truck operators from organized database
        operators = db_manager.get_tow_truck_operators()
        
        # Filter operators
        filtered_operators = []
        for operator in operators:
            if is_verified and not operator.get('is_verified'):
                continue
            if search and search.lower() not in operator.get('name', '').lower():
                continue
            filtered_operators.append(operator)
        
        return jsonify({
            "success": True,
            "operators": filtered_operators
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get tow truck operators: {str(e)}"
        }), 500

@car_service_bp.route('/api/car_service/bookings', methods=['POST'])
def create_booking():
    """Create car service booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'worker_id', 'booking_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Create booking using organized database
        booking_id = db_manager.create_booking(
            'car_service',
            data['user_id'],
            data['worker_id'],
            data['booking_data']
        )
        
        return jsonify({
            "success": True,
            "message": "Booking created successfully",
            "booking_id": booking_id
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to create booking: {str(e)}"
        }), 500

@car_service_bp.route('/api/car_service/bookings', methods=['GET'])
def get_bookings():
    """Get car service bookings"""
    try:
        # Get filters from query params
        user_id = request.args.get('user_id')
        worker_id = request.args.get('worker_id')
        status = request.args.get('status')
        
        # Get bookings from organized database
        bookings = db_manager.get_bookings(
            'car_service',
            user_id=int(user_id) if user_id else None,
            worker_id=int(worker_id) if worker_id else None,
            status=status
        )
        
        return jsonify({
            "success": True,
            "bookings": bookings
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get bookings: {str(e)}"
        }), 500

@car_service_bp.route('/api/car_service/tow_truck/signup', methods=['POST'])
def tow_truck_operator_signup():
    """Tow truck operator signup"""
    try:
        data = request.get_json() or request.form.to_dict()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'password', 'city', 'experience', 'truck_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Register worker using organized database
        worker_id = db_manager.create_worker(
            data['email'],
            data['password'],
            data['name'],
            data['phone'],
            'car_service',
            'tow_truck'
        )
        
        # Store additional tow truck specific data
        tow_truck_data = {
            'truck_type': data.get('truck_type'),
            'truck_registration': data.get('truck_registration'),
            'truck_model': data.get('truck_model'),
            'truck_capacity': data.get('truck_capacity'),
            'license_path': data.get('license_path'),
            'insurance_path': data.get('insurance_path'),
            'fitness_cert_path': data.get('fitness_cert_path'),
            'pollution_cert_path': data.get('pollution_cert_path')
        }
        
        # Store in tow_truck database
        with db_manager.get_connection('tow_truck') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tow_truck_requests 
                (worker_id, tow_truck_data, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (worker_id, json.dumps(tow_truck_data), 'pending', datetime.now(), datetime.now()))
            conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Tow truck operator signup successful! Please wait for approval.",
            "operator_id": worker_id
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Signup failed: {str(e)}"
        }), 500

@car_service_bp.route('/api/car_service/tow_truck/login', methods=['POST'])
def tow_truck_operator_login():
    """Tow truck operator login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({
                "success": False,
                "message": "Email and password required"
            }), 400
        
        # Authenticate worker using organized database
        worker = db_manager.authenticate_worker(data['email'], data['password'])
        
        if worker and worker.get('worker_type') == 'tow_truck':
            # Check if approved
            with db_manager.get_connection('tow_truck') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT status FROM tow_truck_requests 
                    WHERE worker_id = ? ORDER BY created_at DESC LIMIT 1
                ''', (worker['id'],))
                result = cursor.fetchone()
                
                if result and result[0] == 'pending':
                    return jsonify({
                        "success": False,
                        "message": "Account is pending approval",
                        "status": "PENDING"
                    }), 403
                elif result and result[0] == 'rejected':
                    return jsonify({
                        "success": False,
                        "message": "Account has been rejected",
                        "status": "REJECTED"
                    }), 403
            
            # Generate token
            token = generate_token(worker['id'], "worker")
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "operator": worker,
                "token": token
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Login failed: {str(e)}"
        }), 500

@car_service_bp.route('/api/car_service/statistics', methods=['GET'])
def get_car_service_statistics():
    """Get car service statistics"""
    try:
        stats = db_manager.get_service_statistics('car_service')
        
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get statistics: {str(e)}"
        }), 500


@car_service_bp.route('/api/car/profile', methods=['GET'])
def get_car_profile():
    """Get car service profile"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"success": False, "message": "Invalid token"}), 401
        
        # Get car profile from database
        with db_manager.get_connection('users') as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute('''
                SELECT u.city, u.address, cp.emergency_contact_name, cp.emergency_contact_phone,
                       cp.brand, cp.model, cp.year, cp.fuel_type, cp.registration_number
                FROM users u
                JOIN car_profiles cp ON u.id = cp.user_id
                WHERE u.id = ?
            ''', (int(user_id),))
            
            profile = cursor.fetchone()
            
            if profile:
                return jsonify({
                    "success": True,
                    "profile": profile
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "message": "Profile not found"
                }), 404
                
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get profile: {str(e)}"
        }), 500





@car_service_bp.route('/api/car/setup-profile', methods=['POST'])
def setup_car_profile():
    """Setup car service profile"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"success": False, "message": "Invalid token"}), 401
        
        data = request.get_json()
        
        # Create car service profile
        with db_manager.get_connection('users') as conn:
            cursor = conn.cursor()
            
            # Update user with car service profile data
            cursor.execute('''
                UPDATE users SET 
                city = ?, address = ?, updated_at = ?
                WHERE id = ?
            ''', (data.get('city'), data.get('address'), datetime.now(), int(user_id)))
            
            # Create car profile
            cursor.execute('''
                INSERT INTO car_profiles (
                    user_id, emergency_contact_name, emergency_contact_phone,
                    brand, model, year, fuel_type, registration_number, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                int(user_id),
                data.get('emergency_contact_name'),
                data.get('emergency_contact_phone'),
                data.get('brand'),
                data.get('model'),
                data.get('year'),
                data.get('fuel_type'),
                data.get('registration_number'),
                datetime.now()
            ))
            
            conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Car service profile created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to setup profile: {str(e)}"
        }), 500




@car_service_bp.route('/api/car/expert/online-experts', methods=['GET'])
def get_online_experts():
    """Get online experts by category"""
    try:
        category = request.args.get('category')
        if not category:
            return jsonify({"success": False, "message": "Category is required"}), 400
        
        # Get all approved experts
        with db_manager.get_connection('workers') as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT id, name, email, phone, city, experience, skills, rating, is_online
                FROM workers
                WHERE worker_type = 'Automobile Expert' AND status = 'approved' AND area_of_expertise = ?
            ''', (category,))
            experts = cursor.fetchall()
        
        return jsonify({
            "success": True,
            "experts": experts
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get experts: {str(e)}"
        }), 500

@car_service_bp.route('/api/car_service/health', methods=['GET'])
def health_check():
    """Car service health check"""
    try:
        return jsonify({
            "success": True,
            "service": "car_service",
            "status": "healthy",
            "database": "organized"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "service": "car_service",
            "status": "error",
            "error": str(e)
        }), 500






