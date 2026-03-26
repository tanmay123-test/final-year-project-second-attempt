from flask import request, jsonify
from ..services.ai_gemini_client import freelance_ai_client
from ..services.freelance_service import freelance_service

class AIController:
    def __init__(self):
        self.gemini_client = freelance_ai_client

    def generate_description(self):
        try:
            data = request.json
            idea = data.get('idea')
            if not idea:
                return jsonify({"error": "Idea is required"}), 400

            system_prompt = "You are a professional freelance project consultant."
            user_message = f"Generate a detailed, professional project description for the following idea: '{idea}'\n\nThe description should include:\n1. Overview of the project\n2. Key features or requirements\n3. Technical stack suggestions (if applicable)\n4. Deliverables expected\n\nKeep the tone professional and clear."
            
            # Using the synchronous generate_response method
            response = self.gemini_client.generate_response(user_message, system_prompt=system_prompt)
            return jsonify({"description": response}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def suggest_budget(self):
        try:
            data = request.json
            category = data.get('category')
            experience_level = data.get('experienceLevel')
            description = data.get('description')

            if not all([category, experience_level, description]):
                return jsonify({"error": "Category, experienceLevel, and description are required"}), 400

            system_prompt = "As a freelance market expert, suggest a budget range in INR ( ) for projects."
            user_message = f"Suggest a budget range in INR ( ) for the following project:\nCategory: {category}\nExperience Level: {experience_level}\nDescription: {description}\n\nProvide the response in JSON format with 'minBudget', 'maxBudget', and 'currency' (INR)."
            
            response = self.gemini_client.generate_response(user_message, system_prompt=system_prompt)
            
            # Extract JSON from response
            try:
                # Basic JSON extraction logic
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                budget_data = json.loads(response[json_start:json_end])
                return jsonify(budget_data), 200
            except:
                # Fallback if AI doesn't return perfect JSON
                return jsonify({
                    "minBudget": 5000,
                    "maxBudget": 15000,
                    "currency": "INR"
                }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def suggest_milestones(self):
        try:
            data = request.json
            title = data.get('title')
            description = data.get('description')
            budget = data.get('budget')

            if not all([title, description, budget]):
                return jsonify({"error": "Title, description, and budget are required"}), 400

            system_prompt = "As a project manager, suggest 3-5 milestones for projects."
            user_message = f"Suggest 3-5 milestones for the following project:\nTitle: {title}\nDescription: {description}\nTotal Budget:  {budget}\n\nProvide the response in JSON format as a list of objects with 'name' and 'amount' (sharing the total budget).\nExample: {{\"milestones\": [{{\"name\": \"Initial Design\", \"amount\": 5000}}, ...]}}"
            
            response = self.gemini_client.generate_response(user_message, system_prompt=system_prompt)
            
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                milestone_data = json.loads(response[json_start:json_end])
                return jsonify(milestone_data), 200
            except:
                return jsonify({
                    "milestones": [
                        {"name": "Project Setup & Planning", "amount": int(float(budget) * 0.2)},
                        {"name": "Core Development", "amount": int(float(budget) * 0.5)},
                        {"name": "Final Review & Launch", "amount": int(float(budget) * 0.3)}
                    ]
                }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def recommend_freelancers(self):
        try:
            data = request.json
            category = data.get('category')
            skills = data.get('skills')
            budget = data.get('budget')

            # Fetch matching freelancers from database
            # For now, let's use the freelance_service to get freelancers by category
            # In a real app, we would use AI to rank them based on skills and budget
            freelancers = freelance_service.get_featured_freelancers(limit=5)
            
            # Filtering logic could be added here
            return jsonify({"freelancers": freelancers}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

ai_controller = AIController()

