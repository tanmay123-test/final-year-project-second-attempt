"""
Dispatch System API Endpoints
Production-grade API endpoints for the smart dispatch system
"""

from flask import request, jsonify
from datetime import datetime
import uuid
import sqlite3

# Import all engines
try:
    from dispatch_engine import dispatch_engine, Location, ServiceType, JobStatus, MechanicStatus
    from dispatch_database import dispatch_db
    from offer_engine import offer_engine, sequential_offer_manager
    from tracking_engine import tracking_engine
    from otp_engine import otp_engine, arrival_engine
    from commission_engine import commission_engine, completion_engine
except ImportError as e:
    print(f"⚠️ Dispatch engine import error: {e}")
    # Create dummy objects for now
    dispatch_engine = None
    dispatch_db = None
    offer_engine = None
    sequential_offer_manager = None
    tracking_engine = None
    otp_engine = None
    arrival_engine = None
    commission_engine = None
    completion_engine = None

def register_dispatch_endpoints(app):
    """Register all dispatch system endpoints"""
    
    @app.route("/api/dispatch/job/create", methods=["POST"])
    def create_job_request():
        """Create a new job request"""
        if not dispatch_engine:
            return jsonify({"error": "Dispatch system not available"}), 503
            
        try:
            data = request.json
            
            # Parse location
            if "latitude" in data and "longitude" in data:
                location = Location(
                    latitude=float(data["latitude"]),
                    longitude=float(data["longitude"]),
                    address=data.get("address")
                )
            elif "location_name" in data:
                # TODO: Implement geocoding
                location = Location(19.2183, 72.9781, data["location_name"])
            else:
                return jsonify({"error": "Location required"}), 400
            
            # Create job
            job = dispatch_engine.create_job_request(
                user_id=data["user_id"],
                issue=data["issue"],
                location=location,
                service_type=ServiceType(data["service_type"]),
                urgency=data.get("urgency", False)
            )
            
            # Store in database
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO mechanic_jobs 
                (id, user_id, issue, latitude, longitude, address, service_type, urgency, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id, job.user_id, job.issue, job.location.latitude,
                job.location.longitude, job.location.address,
                job.service_type.value, int(job.urgency), job.status.value
            ))
            
            conn.commit()
            conn.close()
            
            # Start dispatch process
            dispatch_job(job.id)
            
            return jsonify({
                "success": True,
                "job_id": job.id,
                "status": job.status.value,
                "message": "Job request created successfully"
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/dispatch/job/status/<job_id>", methods=["GET"])
    def get_job_status(job_id: str):
        """Get current job status"""
        try:
            job = dispatch_engine.active_jobs.get(job_id)
            if not job:
                return jsonify({"error": "Job not found"}), 404
            
            response = {
                "job_id": job.id,
                "status": job.status.value,
                "issue": job.issue,
                "service_type": job.service_type.value,
                "urgency": job.urgency,
                "created_at": job.created_at.isoformat()
            }
            
            # Add mechanic info if assigned
            if job.mechanic_id:
                mechanic = dispatch_engine.mechanics.get(job.mechanic_id)
                if mechanic:
                    response["mechanic"] = {
                        "id": mechanic.id,
                        "name": mechanic.name,
                        "phone": mechanic.phone,
                        "specialization": mechanic.specialization,
                        "rating": mechanic.rating
                    }
            
            # Add tracking info if active
            tracking_info = tracking_engine.get_current_tracking(job_id)
            if tracking_info:
                response["tracking"] = tracking_info
            
            # Add OTP info if arrived
            otp_info = arrival_engine.get_active_otp(job_id)
            if otp_info:
                response["otp"] = otp_info
            
            return jsonify(response), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/dispatch/mechanic/offer/<offer_id>/respond", methods=["POST"])
    def respond_to_offer(offer_id: str):
        """Mechanic responds to job offer"""
        try:
            data = request.json
            accepted = data.get("accepted", False)
            
            success = sequential_offer_manager.handle_mechanic_response(offer_id, accepted)
            
            if success:
                offer = offer_engine.active_offers.get(offer_id)
                if offer:
                    job = dispatch_engine.active_jobs.get(offer.job_id)
                    if job and accepted:
                        return jsonify({
                            "success": True,
                            "message": "Job accepted successfully",
                            "job_id": job.id,
                            "status": job.status.value
                        }), 200
                
                return jsonify({
                    "success": True,
                    "message": "Offer rejected successfully"
                }), 200
            else:
                return jsonify({"error": "Invalid offer or response"}), 400
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/dispatch/mechanic/location/update", methods=["PUT"])
    def update_mechanic_location():
        """Update mechanic location"""
        try:
            data = request.json
            
            location = Location(
                latitude=float(data["latitude"]),
                longitude=float(data["longitude"]),
                address=data.get("address")
            )
            
            dispatch_engine.update_mechanic_location(data["mechanic_id"], location)
            
            # Update database
            conn = sqlite3.connect(dispatch_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE mechanics 
                SET latitude = ?, longitude = ?, last_location_update = ?
                WHERE id = ?
            """, (location.latitude, location.longitude, datetime.utcnow().isoformat(), data["mechanic_id"]))
            
            cursor.execute("""
                INSERT OR REPLACE INTO mechanic_live_locations 
                (mechanic_id, latitude, longitude, address, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (data["mechanic_id"], location.latitude, location.longitude, 
                  location.address, datetime.utcnow().isoformat()))
            
            conn.commit()
            conn.close()
            
            # Check for arrival
            for job_id, job in dispatch_engine.active_jobs.items():
                if (job.mechanic_id == data["mechanic_id"] and 
                    job.status == JobStatus.ACCEPTED):
                    arrival_engine.check_arrival(job_id, data["mechanic_id"])
            
            return jsonify({"success": True, "message": "Location updated"}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/dispatch/otp/verify", methods=["POST"])
    def verify_otp():
        """Verify OTP for job completion"""
        try:
            data = request.json
            
            success = otp_engine.verify_otp(data["job_id"], data["otp_code"])
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "OTP verified successfully"
                }), 200
            else:
                return jsonify({"error": "Invalid OTP"}), 400
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/dispatch/job/complete", methods=["POST"])
    def complete_job():
        """Complete a job"""
        try:
            data = request.json
            
            success = completion_engine.complete_job(
                data["job_id"],
                data.get("proof_notes", "")
            )
            
            if success:
                job = dispatch_engine.active_jobs.get(data["job_id"])
                if job:
                    return jsonify({
                        "success": True,
                        "message": "Job completed successfully",
                        "total_fee": job.total_fee,
                        "mechanic_earnings": job.mechanic_earnings,
                        "platform_commission": job.platform_commission
                    }), 200
            
            return jsonify({"error": "Failed to complete job"}), 400
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/dispatch/mechanic/wallet/<mechanic_id>", methods=["GET"])
    def get_mechanic_wallet(mechanic_id: int):
        """Get mechanic wallet information"""
        try:
            wallet = commission_engine.get_mechanic_wallet(int(mechanic_id))
            return jsonify(wallet), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/dispatch/mechanic/metrics/<mechanic_id>", methods=["GET"])
    def get_mechanic_metrics(mechanic_id: int):
        """Get mechanic performance metrics"""
        try:
            metrics = commission_engine.get_mechanic_metrics(int(mechanic_id))
            return jsonify(metrics), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/dispatch/admin/jobs/active", methods=["GET"])
    def get_active_jobs():
        """Get all active jobs (admin)"""
        try:
            active_jobs = []
            
            for job_id, job in dispatch_engine.active_jobs.items():
                if job.status not in [JobStatus.COMPLETED, JobStatus.CANCELLED_BY_USER, 
                                     JobStatus.CANCELLED_BY_MECHANIC, JobStatus.NO_MECHANIC_FOUND]:
                    job_data = {
                        "job_id": job.id,
                        "user_id": job.user_id,
                        "issue": job.issue,
                        "status": job.status.value,
                        "service_type": job.service_type.value,
                        "urgency": job.urgency,
                        "created_at": job.created_at.isoformat()
                    }
                    
                    if job.mechanic_id:
                        mechanic = dispatch_engine.mechanics.get(job.mechanic_id)
                        if mechanic:
                            job_data["mechanic"] = {
                                "id": mechanic.id,
                                "name": mechanic.name,
                                "phone": mechanic.phone
                            }
                    
                    active_jobs.append(job_data)
            
            return jsonify({"jobs": active_jobs}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def dispatch_job(job_id: str):
    """Dispatch job to available mechanics"""
    try:
        job = dispatch_engine.active_jobs.get(job_id)
        if not job:
            return
        
        # Get available mechanics
        available_mechanics = dispatch_engine.get_available_mechanics(
            job.service_type, job.location
        )
        
        if not available_mechanics:
            job.status = JobStatus.NO_MECHANIC_FOUND
            dispatch_engine._log_job_event(
                job_id, "NO_MECHANICS_AVAILABLE",
                "No available mechanics found"
            )
            return
        
        # Rank mechanics
        ranked_mechanics = dispatch_engine.rank_mechanics(
            available_mechanics, job.location, job.urgency
        )
        
        if not ranked_mechanics:
            job.status = JobStatus.NO_MECHANIC_FOUND
            return
        
        # Start sequential offers
        sequential_offer_manager.start_sequential_offers(job, ranked_mechanics)
        
        dispatch_engine._log_job_event(
            job_id, "DISPATCH_STARTED",
            f"Dispatch started with {len(ranked_mechanics)} mechanics"
        )
        
    except Exception as e:
        print(f"⚠️ Dispatch error: {e}")
        if job_id in dispatch_engine.active_jobs:
            dispatch_engine.active_jobs[job_id].status = JobStatus.NO_MECHANIC_FOUND
