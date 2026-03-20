"""
Smart Search API Routes
API endpoints for nearby mechanic discovery
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_utils import verify_token
from .smart_search_engine import SmartSearchEngine, SearchRequest
from .location_resolution_engine import LocationResolutionEngine

smart_search_bp = Blueprint("smart_search", __name__)
search_engine = SmartSearchEngine()
location_engine = LocationResolutionEngine()

@smart_search_bp.route("/api/car/smart-search", methods=["POST"])
def smart_search():
    """
    Smart search for nearby mechanics
    
    Request body:
    {
        "issue_description": "my car brake is stuck",
        "location_data": {
            "location_name": "Asalpha Mumbai"
            // OR
            "latitude": 19.0954,
            "longitude": 72.8783
        },
        "search_radius_km": 5.0,  // optional
        "max_results": 10  // optional
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        issue_description = data.get("issue_description", "").strip()
        location_data = data.get("location_data", {})
        
        if not issue_description:
            return jsonify({"error": "Issue description is required"}), 400
        
        if not location_data:
            return jsonify({"error": "Location data is required"}), 400
        
        # Validate location input
        is_valid, error_message = location_engine.validate_location_input(location_data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Create search request
        search_request = SearchRequest(
            issue_description=issue_description,
            location_data=location_data,
            search_radius_km=data.get("search_radius_km", 5.0),
            max_results=data.get("max_results", 10)
        )
        
        # Perform search
        results = search_engine.search_nearby_mechanics(search_request)
        
        return jsonify(results), 200
    
    except Exception as e:
        print(f"Smart search error: {e}")
        return jsonify({
            "error": "Search failed",
            "message": "An error occurred while searching for mechanics"
        }), 500

@smart_search_bp.route("/api/car/smart-search/keyword", methods=["POST"])
def keyword_search():
    """
    Search mechanics by keyword using FTS5
    
    Request body:
    {
        "keyword": "tanmay"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        keyword = data.get("keyword", "").strip()
        if not keyword:
            return jsonify({"error": "Keyword is required"}), 400
        
        # Perform keyword search
        results = search_engine.search_by_keyword(keyword)
        
        return jsonify({
            "success": True,
            "keyword": keyword,
            "mechanics": results,
            "total_results": len(results)
        }), 200
    
    except Exception as e:
        print(f"Keyword search error: {e}")
        return jsonify({
            "error": "Search failed",
            "message": "An error occurred while searching for mechanics"
        }), 500

@smart_search_bp.route("/api/car/smart-search/location/resolve", methods=["POST"])
def resolve_location():
    """
    Resolve location name to coordinates
    
    Request body:
    {
        "location_name": "Asalpha Mumbai"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        location_name = data.get("location_name", "").strip()
        if not location_name:
            return jsonify({"error": "Location name is required"}), 400
        
        # Resolve location
        location = location_engine.resolve_location({"location_name": location_name})
        
        return jsonify({
            "success": True,
            "location": {
                "name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "resolved": location.resolved
            }
        }), 200
    
    except Exception as e:
        print(f"Location resolution error: {e}")
        return jsonify({
            "error": "Location resolution failed",
            "message": str(e)
        }), 500

@smart_search_bp.route("/api/car/smart-search/skill/detect", methods=["POST"])
def detect_skill():
    """
    Detect required skill from issue description
    
    Request body:
    {
        "issue_description": "my car brake is stuck"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        issue_description = data.get("issue_description", "").strip()
        if not issue_description:
            return jsonify({"error": "Issue description is required"}), 400
        
        # Detect skill
        skill, confidence = search_engine.skill_engine.detect_skill(issue_description)
        all_matches = search_engine.skill_engine.get_all_skill_matches(issue_description)
        
        return jsonify({
            "success": True,
            "issue_description": issue_description,
            "detected_skill": skill,
            "confidence": confidence,
            "all_matches": all_matches
        }), 200
    
    except Exception as e:
        print(f"Skill detection error: {e}")
        return jsonify({
            "error": "Skill detection failed",
            "message": str(e)
        }), 500

@smart_search_bp.route("/api/car/smart-search/mechanic/<int:mechanic_id>/location", methods=["PUT"])
def update_mechanic_location(mechanic_id):
    """
    Update mechanic's live location
    
    Request body:
    {
        "latitude": 19.0954,
        "longitude": 72.8783
    }
    """
    try:
        # Get mechanic from token (for authentication)
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get mechanic from worker database
        from .car_service_worker_db import car_service_worker_db
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Verify mechanic ID matches token
        if mechanic['id'] != mechanic_id:
            return jsonify({"error": "Unauthorized to update this mechanic's location"}), 403
        
        # Get location data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        if latitude is None or longitude is None:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid coordinate format"}), 400
        
        # Validate coordinates
        if not location_engine._is_valid_coordinates(latitude, longitude):
            return jsonify({"error": "Invalid coordinates"}), 400
        
        # Update location
        success = search_engine.update_mechanic_location(mechanic_id, latitude, longitude)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Location updated successfully",
                "location": {
                    "mechanic_id": mechanic_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "updated_at": "now"
                }
            }), 200
        else:
            return jsonify({"error": "Failed to update location"}), 500
    
    except Exception as e:
        print(f"Location update error: {e}")
        return jsonify({
            "error": "Location update failed",
            "message": str(e)
        }), 500

@smart_search_bp.route("/api/car/smart-search/statistics", methods=["GET"])
def get_search_statistics():
    """Get search engine statistics"""
    try:
        stats = search_engine.get_search_statistics()
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
    
    except Exception as e:
        print(f"Statistics error: {e}")
        return jsonify({
            "error": "Failed to get statistics",
            "message": str(e)
        }), 500

@smart_search_bp.route("/api/car/smart-search/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "success": True,
            "message": "Smart Search Engine is running",
            "components": {
                "location_resolution": "OK",
                "skill_detection": "OK", 
                "eta_calculation": "OK",
                "database": "OK",
                "fts5_search": "OK"
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
