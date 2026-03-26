#!/usr/bin/env python3
"""
Simple Backend Startup using Organized Database Manager
Bypasses complex legacy code for clean startup
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from database.database_manager import db_manager
from routes.auth_routes import auth_bp
from services.healthcare.routes.healthcare_routes import healthcare_bp
from services.housekeeping.routes.housekeeping_routes import housekeeping_bp
from car_service.car_service_worker_routes import car_service_bp
from car_service.worker_routes import worker_bp
from car_service.tow_truck.routes import tow_bp

def create_app():
    """Create Flask app with organized database"""
    app = Flask(__name__)
    
    # CORS configuration
    CORS(app, resources={r"/*": {"origins": [
        "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
        "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175",
        "http://localhost:8081", "http://localhost:19006", "null"
    ]}})
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    print("  Authentication blueprint registered (using organized database)")
    
    app.register_blueprint(healthcare_bp)
    print("  Healthcare blueprint registered (using organized database)")
    
    app.register_blueprint(housekeeping_bp)
    print("  Housekeeping blueprint registered (using organized database)")
    
    app.register_blueprint(car_service_bp)
    print("  Car service blueprint registered (using organized database)")
    
    app.register_blueprint(worker_bp)
    print("  Worker blueprint registered (using organized database)")
    
    app.register_blueprint(tow_bp)
    print("  Tow truck blueprint registered (using organized database)")
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        try:
            db_health = db_manager.check_database_health()
            return jsonify({
                "success": True,
                "message": "Backend running with organized database",
                "databases": db_health
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Health check failed: {str(e)}"
            }), 500
    
    # Database status endpoint
    @app.route('/api/database/status', methods=['GET'])
    def database_status():
        try:
            # Get user count
            with db_manager.get_connection('users') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users')
                user_count = cursor.fetchone()[0]
            
            # Get worker count
            with db_manager.get_connection('workers') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM workers')
                worker_count = cursor.fetchone()[0]
            
            return jsonify({
                "success": True,
                "users": user_count,
                "workers": worker_count,
                "database_structure": "organized",
                "migration_status": "completed"
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Database status check failed: {str(e)}"
            }), 500
    
    return app

if __name__ == '__main__':
    print("  Starting Backend with Organized Database...")
    print("  Database Manager:   Initialized")
    print("   Blueprints:   Registered")
    print("  API Endpoints:   Ready")
    print("  Server: http://127.0.0.1:5000")
    print("  Health Check: http://127.0.0.1:5000/api/health")
    print("  Database Status: http://127.0.0.1:5000/api/database/status")
    print("\n" + "="*60)
    
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
