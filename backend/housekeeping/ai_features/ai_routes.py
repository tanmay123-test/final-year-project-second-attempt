from flask import Blueprint, request, jsonify
from housekeeping.ai_features.ai_advisor_service import get_user_recommendations, process_home_query

# Create blueprint
ai_features_bp = Blueprint('housekeeping_ai', __name__)

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
    Accepts { "query": "...", "user_id": "..." }
    Returns { "response": "...", "mode": "cooking|cleaning|service|general" }
    """
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "query is required"}), 400
        
    query = data.get('query')
    # user_id is provided in request but not strictly needed for basic stateless chat logic yet
    # but we can pass it if we want to personalize in the future.
    
    try:
        response_data = process_home_query(query)
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
