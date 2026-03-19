from flask import request, jsonify
from ..services.freelance_service import freelance_service
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# Configure upload folder
UPLOAD_FOLDER = 'uploads/freelance/attachments'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'zip', 'txt'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class FreelanceController:
    def create_project(self, user_id):
        try:
            # Handle multipart/form-data
            if 'multipart/form-data' in request.content_type:
                data = request.form
                files = request.files.getlist('attachments')
            else:
                data = request.json
                files = []

            # Validation
            title = data.get('title')
            description = data.get('description')
            category = data.get('category')
            budget_type = data.get('budget_type', 'Fixed Price')
            budget = data.get('budget')
            deadline = data.get('deadline')
            experience_level = data.get('experience_level', 'Beginner')
            required_skills = data.get('required_skills', '[]')
            enable_milestones = data.get('enable_milestones', 'false').lower() == 'true'

            # Parse required_skills if it's a string (from form-data)
            if isinstance(required_skills, str):
                import json
                try:
                    required_skills = json.loads(required_skills)
                except:
                    required_skills = [s.strip() for s in required_skills.split(',') if s.strip()]

            if not all([title, description, category, budget, deadline]):
                return jsonify({"success": False, "message": "Missing required fields"}), 400

            # Validate budget
            try:
                budget_val = float(budget)
                if budget_val <= 0:
                    raise ValueError
            except ValueError:
                return jsonify({"success": False, "message": "Budget must be a positive number"}), 400

            # Validate deadline
            try:
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
                if deadline_date < datetime.now():
                    return jsonify({"success": False, "message": "Deadline must be a future date"}), 400
            except ValueError:
                return jsonify({"success": False, "message": "Invalid date format for deadline"}), 400

            # Handle file uploads
            attachment_paths = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{user_id}_{datetime.now().timestamp()}_{file.filename}")
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    attachment_paths.append(file_path)

            # Save to database using service
            # Map budget_type to backend enum if needed (Backend uses FIXED/HOURLY)
            backend_budget_type = 'FIXED' if 'Fixed' in budget_type else 'HOURLY'
            
            project_id = freelance_service.create_project(
                client_id=user_id,
                title=title,
                description=description,
                category=category,
                budget_type=backend_budget_type,
                budget_amount=budget_val,
                deadline=deadline,
                skills=', '.join(required_skills) if isinstance(required_skills, list) else required_skills,
                exp_level=experience_level,
                milestones=None # Milestones can be added later or passed here if parsed
            )

            if project_id:
                # In a real app, we'd also save attachment_paths to a separate table
                project_data = {
                    "id": project_id,
                    "title": title,
                    "description": description,
                    "category": category,
                    "budget_type": budget_type,
                    "budget": budget_val,
                    "deadline": deadline,
                    "experience_level": experience_level,
                    "required_skills": required_skills,
                    "attachments": attachment_paths,
                    "enable_milestones": enable_milestones,
                    "posted_by": user_id
                }
                return jsonify({
                    "success": True, 
                    "message": "Project posted successfully", 
                    "project": project_data
                }), 201
            
            return jsonify({"success": False, "message": "Failed to save project to database"}), 500

        except Exception as e:
            print(f"Error in create_project controller: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 500

    def get_dashboard(self, user_id):
        try:
            dashboard_data = freelance_service.get_freelancer_dashboard_data(user_id)
            if not dashboard_data:
                return jsonify({"success": False, "message": "Freelancer not found"}), 404
            
            return jsonify({
                "success": True,
                "dashboard": dashboard_data
            }), 200
        except Exception as e:
            print(f"Error in get_dashboard: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 500

    def upload_deliverable(self, user_id, project_id):
        try:
            if 'file' not in request.files:
                return jsonify({"success": False, "message": "No file part"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"success": False, "message": "No selected file"}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(f"deliverable_{project_id}_{user_id}_{datetime.now().timestamp()}_{file.filename}")
                upload_path = os.path.join(UPLOAD_FOLDER, 'deliverables')
                os.makedirs(upload_path, exist_ok=True)
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)
                
                deliverable_id = freelance_service.save_deliverable(project_id, user_id, file_path, file.filename)
                
                return jsonify({
                    "success": True,
                    "message": "Deliverable uploaded successfully",
                    "deliverable_id": deliverable_id
                }), 201
            
            return jsonify({"success": False, "message": "File type not allowed"}), 400
        except Exception as e:
            print(f"Error in upload_deliverable: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 500

freelance_controller = FreelanceController()
