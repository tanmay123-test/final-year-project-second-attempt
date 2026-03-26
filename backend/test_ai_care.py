#!/usr/bin/env python3
"""
Test script for AI Care Engine
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.healthcare.ai_engine import analyze_symptoms_conversational

def test_ai_care():
    """Test the AI engine with different symptom scenarios"""
    
    test_cases = [
        'I have tooth pain and swollen gums',
        'मला दात दुखत आहेत',
        'Burning stomach after eating', 
        'Chest pain and breathing difficulty'
    ]
    
    print('🔍 Testing AI Care Engine...')
    print('=' * 50)
    
    for i, symptoms in enumerate(test_cases, 1):
        print(f'\n📝 Test Case {i}: "{symptoms}"')
        print('-' * 30)
        
        try:
            result = analyze_symptoms_conversational(symptoms, f'test_user_{i}', [])
            
            print(f'✅ Stage: {result.get("stage", "unknown")}')
            print(f'🩺 Severity: {result.get("severity", "unknown")}')
            print(f'👨‍⚕️ Specializations: {result.get("specializations", [])}')
            print(f'💬 Advice: {result.get("advice", "No advice")[:100]}...')
            print(f'🌐 Language: {result.get("detected_language", "english")}')
            print(f'🏥 First Aid: {result.get("first_aid", "No first aid")[:50]}...')
            
        except Exception as e:
            print(f'❌ Error: {str(e)}')
            import traceback
            traceback.print_exc()
    
    print('\n' + '=' * 50)
    print('🎯 AI Care Engine Test Complete!')

if __name__ == "__main__":
    test_ai_care()
