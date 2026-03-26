#!/usr/bin/env python3
"""
Simple AI Care Test Server - No Database Required
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.healthcare.ai_engine import analyze_symptoms_conversational

app = Flask(__name__)
CORS(app)

@app.route("/healthcare/ai-care", methods=["POST"])
def ai_care():
    """AI-driven healthcare analysis using our working AI engine"""
    try:
        data = request.json
        message = data.get("message", "")
        conversation_history = data.get("conversation_history", [])
        user_id = data.get("user_id", "default")
        
        if not message.strip():
            return jsonify({
                "success": False,
                "message": "Message is required"
            }), 400
        
        print(f"🤕 AI Care Request: {message}")
        
        # Analyze with our working AI engine
        ai_result = analyze_symptoms_conversational(message, user_id, conversation_history)
        
        # Get specializations from AI result
        specializations = ai_result.get("specializations", ["General Physician"])
        
        # Create mock doctors based on specializations
        suggested_doctors = []
        if 'Neurologist' in specializations:
            suggested_doctors.append({
                'id': 1,
                'name': 'Dr. Test Neurologist',
                'specialization': 'Neurologist',
                'experience': 10,
                'rating': 4.8,
                'clinic_location': 'Test Hospital'
            })
        if 'General Physician' in specializations:
            suggested_doctors.append({
                'id': 2,
                'name': 'Dr. Test Physician',
                'specialization': 'General Physician',
                'experience': 8,
                'rating': 4.5,
                'clinic_location': 'Test Clinic'
            })
        
        # Return successful response
        response_data = {
            "success": True,
            "response": ai_result.get("advice", ""),
            "stage": ai_result.get("stage", "final"),
            "severity": ai_result.get("severity", "medium"),
            "first_aid": ai_result.get("first_aid", ""),
            "otc_medicines": ai_result.get("otc_medicines", ""),
            "suggested_doctors": suggested_doctors,
            "specializations": specializations,
            "reasoning": ai_result.get("reasoning", ""),
            "follow_up": ai_result.get("follow_up", ""),
            "detected_language": ai_result.get("detected_language", "english")
        }
        
        print(f"✅ AI Care Response: {response_data['severity']} - {specializations}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ AI Care Error: {e}")
        return jsonify({
            "success": False,
            "message": f"AI analysis failed: {str(e)}"
        }), 500

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "AI Care Test Server Running!"})

if __name__ == "__main__":
    print("🚀 Starting AI Care Test Server...")
    print("📡 Server will be available at: http://localhost:5001")
    print("🤕 AI Care endpoint: http://localhost:5001/healthcare/ai-care")
    print("🧪 Test endpoint: http://localhost:5001/test")
    print("\n✨ Features:")
    print("   • Perfect headache analysis")
    print("   • Neurologist recommendations")
    print("   • Emergency detection")
    print("   • Voice-ready responses")
    print("   • No database required")
    
    app.run(host="0.0.0.0", port=5001, debug=True)
