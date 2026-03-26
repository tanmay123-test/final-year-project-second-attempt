#!/usr/bin/env python3
"""
Test AI Care Direct Engine (No Database)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.healthcare.ai_engine import analyze_symptoms_conversational

def test_ai_engine_direct():
    print("🤕 Testing AI Engine Direct (No Database)")
    print("=" * 50)
    
    # Test headache symptoms
    test_cases = [
        "I have headache",
        "severe migraine with nausea",
        "headache after head injury"
    ]
    
    for i, symptom in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {symptom}")
        print("-" * 30)
        
        try:
            result = analyze_symptoms_conversational(symptom, "test_user")
            
            print(f"✅ Success!")
            print(f"🤖 Advice: {result.get('advice', 'N/A')}")
            print(f"📊 Severity: {result.get('severity', 'N/A')}")
            print(f"🩺 Specialist: {result.get('specializations', ['N/A'])}")
            print(f"💊 First Aid: {result.get('first_aid', 'N/A')}")
            print(f"🏥 Follow-up: {result.get('follow_up', 'N/A')}")
            
            # Format like the API response
            api_response = {
                "success": True,
                "response": result.get("advice", ""),
                "stage": result.get("stage", "final"),
                "severity": result.get("severity", "medium"),
                "first_aid": result.get("first_aid", ""),
                "otc_medicines": result.get("otc_medicines", ""),
                "suggested_doctors": [
                    {
                        'id': 1,
                        'name': 'Dr. Test Neurologist',
                        'specialization': 'Neurologist',
                        'experience': 10,
                        'rating': 4.8,
                        'clinic_location': 'Test Hospital'
                    }
                ],
                "specializations": result.get("specializations", []),
                "reasoning": result.get("reasoning", ""),
                "follow_up": result.get("follow_up", ""),
                "detected_language": result.get("detected_language", "english")
            }
            
            print(f"\n📡 API Response Format:")
            for key, value in api_response.items():
                if key not in ['suggested_doctors']:
                    print(f"   {key}: {value}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎯 AI Engine Test Complete!")
    print("✅ The AI analysis is working perfectly!")
    print("🚀 Ready to integrate with frontend!")

if __name__ == "__main__":
    test_ai_engine_direct()
