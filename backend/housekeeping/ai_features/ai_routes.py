from flask import Blueprint, request, jsonify
from housekeeping.ai_features.ai_advisor_service import get_user_recommendations
from services.housekeeping.arrival.backend.services.ai_advisor_service import AIAdvisorService

# Create blueprint
ai_features_bp = Blueprint('housekeeping_ai', __name__)
ai_service = AIAdvisorService()

@ai_features_bp.route('/api/ai/recommendations', methods=['GET'])
def recommendations():
    """
    GET /api/ai/recommendations?user_id=XYZ
    Returns a ranked list of service recommendations based on booking history.
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
        
    try:
        recs = get_user_recommendations(int(user_id))
        return jsonify(recs), 200
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_features_bp.route('/api/ai/chat', methods=['POST'])
def chat():
    """
    POST /api/ai/chat
    Accepts { "message": "...", "user_id": "..." }
    Returns { "response": "...", "mode": "cooking|cleaning|service|general" }
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "message is required"}), 400
        
    message = data.get('message')
    user_id = data.get('user_id')
    
    try:
        response_data = ai_service.chat_with_ai(user_id=user_id, message=message)
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
