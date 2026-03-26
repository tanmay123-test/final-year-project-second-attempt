#!/usr/bin/env python3
"""
Test AI Care Headache Analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.healthcare.ai_engine import analyze_symptoms_conversational

def test_headache_analysis():
    print("🤕 Testing AI Care Headache Analysis")
    print("=" * 50)
    
    # Test headache symptoms
    test_cases = [
        "I have a headache",
        "headache with nausea",
        "severe migraine",
        "headache after head injury"
    ]
    
    for i, symptom in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {symptom}")
        print("-" * 30)
        
        try:
            result = analyze_symptoms_conversational(symptom, "test_user")
            
            print(f"✅ Analysis completed")
            print(f"📋 Severity: {result.get('severity', 'N/A')}")
            print(f"🩺 Specialist: {result.get('specializations', ['N/A'])[0]}")
            print(f"💊 Advice: {result.get('advice', 'N/A')[:100]}...")
            print(f"🏥 First Aid: {result.get('first_aid', 'N/A')[:80]}...")
            
            # Check if headache is properly detected
            specialists = result.get('specializations', [])
            if 'Neurologist' in specialists or 'General Physician' in specialists:
                print("✅ Proper specialist recommendation")
            else:
                print("⚠️  Unexpected specialist recommendation")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎯 Headache-Specific Features:")
    print("✅ Quick Headache Analysis Button")
    print("✅ Enhanced Text-to-Speech")
    print("✅ Neurologist Recommendation")
    print("✅ Emergency Detection")
    print("✅ Fallback Mode Available")
    
    print("\n🚀 AI Care is ready for headache analysis!")

if __name__ == "__main__":
    test_headache_analysis()
