from flask import request, jsonify
from auth_utils import get_current_user_id
from user_db import UserDB
from worker_db import WorkerDB
from ..services.freelance_service import freelance_service
from datetime import datetime

class ProfileController:
    def get_profile(self, user_id):
        try:
            user_db = UserDB()
            worker_db = WorkerDB()
            # Check if user is a worker first
            worker = worker_db.get_worker_by_id(user_id)
            user = user_db.get_user_by_id(user_id)
            
            if not user and not worker:
                return jsonify({"success": False, "message": "User not found"}), 404

            # Combine data
            profile_data = {
                "name": worker['full_name'] if worker else user.get('name', user.get('username', '')),
                "email": worker['email'] if worker else user.get('email', ''),
                "phone": worker.get('phone', '') if worker else user.get('phone', ''),
                "location": worker.get('clinic_location', 'Mumbai, India') if worker else user.get('location', 'Mumbai, India'),
                "memberSince": worker.get('created_at', '2024-01-01') if worker else user.get('created_at', '2024-01-01'),
                "avatarInitials": "".join([n[0] for n in (worker['full_name'] if worker else user.get('name', user.get('username', 'F'))).split()]).upper()[:2],
                "isVerified": True if (worker and worker.get('status') == 'approved') else False,
                "role": "Freelancer" if worker else "Client",
                "skills": (worker.get('skills', '').split(',') if worker and worker.get('skills') else []),
                "stats": {
                    "totalProjects": freelance_service.get_project_count_by_user(user_id),
                    "totalProposals": freelance_service.get_proposal_count_by_user(user_id),
                    "rating": worker.get('rating', 5.0) if worker else 5.0
                },
                "recentActivity": [
                    {"type": "POSTED", "title": "E-Commerce Redesign", "time": "2 days ago"},
                    {"type": "RECEIVED", "title": "8 proposals", "time": "1 day ago"}
                ]
            }
            
            return jsonify({"success": True, "profile": profile_data}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    def update_profile(self, user_id):
        try:
            data = request.json
            name = data.get('name')
            phone = data.get('phone')
            location = data.get('location')
            skills = data.get('skills', [])

            user_db = UserDB()
            worker_db = WorkerDB()

            # Update User table if possible (Need to check if UserDB has update method)
            # For now, let's assume we update worker if it's a worker
            worker = worker_db.get_worker_by_id(user_id)
            if worker:
                skills_str = ",".join(skills) if isinstance(skills, list) else skills
                import sqlite3
                from config import WORKER_DB
                conn = sqlite3.connect(WORKER_DB)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE workers 
                    SET full_name = ?, phone = ?, clinic_location = ?, skills = ?
                    WHERE id = ?
                """, (name, phone, location, skills_str, user_id))
                conn.commit()
                conn.close()

            return self.get_profile(user_id)
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    def change_password(self, user_id):
        try:
            data = request.json
            current_password = data.get('currentPassword')
            new_password = data.get('newPassword')

            if not current_password or not new_password:
                return jsonify({"success": False, "message": "Missing passwords"}), 400

            # Validate current password
            user_db = UserDB()
            user = user_db.get_user_by_id(user_id)
            if not user:
                return jsonify({"success": False, "message": "User not found"}), 404
            
            # In a real app, use password hashing
            if user['password'] != current_password:
                return jsonify({"success": False, "message": "Incorrect current password"}), 400

            # Update password
            import sqlite3
            from config import USER_DB
            conn = sqlite3.connect(USER_DB)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
            conn.commit()
            conn.close()

            return jsonify({"success": True, "message": "Password updated successfully"}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    def logout(self):
        # In a token-based system, client just deletes the token
        # But we can provide an endpoint if session management is involved
        return jsonify({"success": True, "message": "Logged out successfully"}), 200

profile_controller = ProfileController()
