from flask import Blueprint, request, jsonify
from services.housekeeping.arrival.backend.services.ai_advisor_service import AIAdvisorService

ai_advisor_bp = Blueprint('ai_advisor', __name__)
ai_advisor_service = AIAdvisorService()

@ai_advisor_bp.route('/cleaning-status', methods=['GET'])
def get_cleaning_status():
    """
    Returns data for the Smart Home Hygiene Advisor Tab:
    - Status Badge, Last Clean Date, Service Type, Days Ago, Next Suggested Date
    - Hygiene Score, Recommendation
    - Seasonal Tip
    """
    user_id = request.args.get('user_id') # In real app, get from token
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
        
    data = ai_advisor_service.get_cleaning_status(user_id)
    return jsonify(data), 200

@ai_advisor_bp.route('/set-reminder', methods=['POST'])
def set_reminder():
    """
    Set a global cleaning reminder.
    Input: { user_id, reminder_type, frequency_type, custom_date, repeat }
    """
    data = request.json
    user_id = data.get('user_id')
    reminder_type = data.get('reminder_type')
    frequency_type = data.get('frequency_type')
    custom_date = data.get('custom_date')
    repeat = data.get('repeat', False)
    
    if not user_id or not reminder_type or not frequency_type:
        return jsonify({"error": "Missing required fields"}), 400
        
    next_date, msg = ai_advisor_service.set_reminder(user_id, reminder_type, frequency_type, custom_date, repeat)
    
    if next_date:
        return jsonify({"message": msg, "next_reminder": next_date}), 200
    else:
        return jsonify({"error": msg}), 500

@ai_advisor_bp.route('/get-reminders', methods=['GET'])
def get_reminders():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    reminders = ai_advisor_service.get_user_reminders(user_id)
    return jsonify(reminders), 200

@ai_advisor_bp.route('/delete-reminder', methods=['POST'])
def delete_reminder():
    data = request.json
    reminder_id = data.get('reminder_id')
    if not reminder_id:
        return jsonify({"error": "Reminder ID required"}), 400
    success = ai_advisor_service.delete_reminder(reminder_id)
    if success:
        return jsonify({"message": "Reminder deleted"}), 200
    return jsonify({"error": "Failed to delete"}), 500

@ai_advisor_bp.route('/upgrade-suggestion', methods=['GET'])
def get_upgrade_suggestion():
    """
    Returns whether to suggest an upgrade to Deep Cleaning.
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
        
    data = ai_advisor_service.get_upgrade_suggestion(user_id)
    return jsonify(data), 200

@ai_advisor_bp.route('/seasonal-tip', methods=['GET'])
def get_seasonal_tip():
    """
    Returns the seasonal tip based on current month.
    """
    tip = ai_advisor_service.get_seasonal_tip()
    return jsonify({"tip": tip}), 200
