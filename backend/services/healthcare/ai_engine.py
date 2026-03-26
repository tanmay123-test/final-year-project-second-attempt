"""
AI Engine for ExpertEase Healthcare Platform
True AI-driven medical analysis using Gemini API
"""

import json
import google.generativeai as genai
from datetime import datetime
import re
from services.healthcare.prompt_builder import prompt_builder

class AIEngine:
    def __init__(self):
        self.gemini_api_key = None
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            # Try to get API key from environment or config
            import os
            self.gemini_api_key = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')
            
            if self.gemini_api_key and self.gemini_api_key != 'YOUR_GEMINI_API_KEY':
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini AI initialized successfully")
            else:
                print("⚠️ Gemini API key not configured, using fallback mode")
                self.model = None
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            self.model = None
    
    def _detect_and_translate_language(self, text):
        """Detect language and translate to English if needed"""
        if not text or not text.strip():
            return {"detected_language": "english", "translated_text": text, "confidence": 1.0}
        
        # Quick language detection
        hindi_pattern = re.compile(r'[\u0900-\u097F]')
        marathi_pattern = re.compile(r'[\u0900-\u097F\u0985-\u098C\u098F-\u0990\u0993-\u09A8\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09CE-\u09DC\u09DD-\u09DF\u09E0-\u09E3]')
        
        if hindi_pattern.search(text):
            detected_lang = "hindi"
        elif marathi_pattern.search(text):
            detected_lang = "marathi" 
        else:
            detected_lang = "english"
        
        # If already English, return as-is
        if detected_lang == "english":
            return {
                "detected_language": "english", 
                "translated_text": text, 
                "confidence": 0.95
            }
        
        # Use Gemini for translation if available
        if self.model:
            try:
                translation_prompt = prompt_builder.build_translation_prompt(text)
                response = self.model.generate_content(translation_prompt)
                response_text = response.text
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    translation_result = json.loads(json_match.group())
                    return translation_result
            except Exception as e:
                print(f"Translation failed: {e}")
        
        # Fallback translation (basic)
        fallback_translations = {
            "hindi": {
                "सिर दर्द": "tooth pain",
                "खांसी": "cough", 
                "बुख़र": "fever",
                "सिर दुख": "headache",
                "पेट दुख": "stomach pain",
                "सांस लेना मुश्किल": "difficulty breathing",
                "छाती का दर्द": "chest pain"
            },
            "marathi": {
                "दात दुखत": "tooth pain",
                "खोजला": "cough",
                "जर": "fever", 
                "डोके दुखत": "headache",
                "पोटाचा दुखत": "stomach pain",
                "श्वास घेण्याला अडच": "difficulty breathing",
                "छातीचा दुखत": "chest pain"
            }
        }
        
        translated = text
        if detected_lang in fallback_translations:
            for original, english in fallback_translations[detected_lang].items():
                if original in text:
                    translated = translated.replace(original, english)
                    break
        
        return {
            "detected_language": detected_lang,
            "translated_text": translated,
            "confidence": 0.7
        }
    
    def analyze_symptoms(self, symptoms, user_id, conversation_history=None):
        """Analyze symptoms using AI (Gemini) with multilingual support"""
        try:
            # Step 1: Detect and translate language if needed
            translation_result = self._detect_and_translate_language(symptoms)
            translated_symptoms = translation_result["translated_text"]
            detected_language = translation_result["detected_language"]
            
            # Step 2: Check for emergency keywords
            emergency_keywords = [
                "chest pain", "difficulty breathing", "severe chest", 
                "cannot breathe", "emergency", "severe bleeding",
                "loss of consciousness", "heart attack"
            ]
            
            symptoms_lower = translated_symptoms.lower()
            is_emergency = any(keyword in symptoms_lower for keyword in emergency_keywords)
            
            # Step 3: Build appropriate prompt
            if is_emergency:
                analysis_prompt = prompt_builder.build_emergency_prompt(translated_symptoms)
            else:
                analysis_prompt = prompt_builder.build_analysis_prompt(
                    translated_symptoms, 
                    conversation_history
                )
            
            # Step 4: Get AI response
            if self.model:
                try:
                    response = self.model.generate_content(analysis_prompt)
                    response_text = response.text
                    
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        ai_result = json.loads(json_match.group())
                        
                        # Add metadata
                        ai_result.update({
                            "detected_language": detected_language,
                            "original_symptoms": symptoms,
                            "translated_symptoms": translated_symptoms,
                            "timestamp": datetime.now().isoformat(),
                            "stage": "final"
                        })
                        
                        return ai_result
                    
                except Exception as e:
                    print(f"Gemini analysis failed: {e}")
            
            # Fallback to basic analysis if Gemini fails
            return self._fallback_analysis(translated_symptoms, detected_language)
            
        except Exception as e:
            print(f"AI Engine error: {e}")
            return self._fallback_analysis(symptoms, "english")
    
    def _fallback_analysis(self, symptoms, detected_language="english"):
        """Fallback analysis when AI is unavailable"""
        symptoms_lower = symptoms.lower()
        
        # Basic specialist detection
        specialist_mapping = {
            "tooth": "Dentist",
            "dental": "Dentist", 
            "gum": "Dentist",
            "chest": "Cardiologist",
            "heart": "Cardiologist",
            "stomach": "Gastroenterologist",
            "abdomen": "Gastroenterologist",
            "skin": "Dermatologist",
            "rash": "Dermatologist",
            "head": "Neurologist",
            "migraine": "Neurologist",
            "bone": "Orthopedic",
            "joint": "Orthopedic",
            "fever": "General Physician",
            "cough": "General Physician"
        }
        
        detected_specialist = "General Physician"
        for keyword, specialist in specialist_mapping.items():
            if keyword in symptoms_lower:
                detected_specialist = specialist
                break
        
        # Basic severity assessment
        severe_keywords = ["chest pain", "difficulty breathing", "severe", "emergency"]
        severity = "emergency" if any(kw in symptoms_lower for kw in severe_keywords) else "medium"
        
        return {
            "advice": "Based on your symptoms, consult a healthcare professional for proper diagnosis.",
            "severity": severity,
            "first_aid": "Rest and stay hydrated. Monitor symptoms closely.",
            "otc_medicines": "Paracetamol for fever/pain relief. Consult pharmacist.",
            "specializations": [detected_specialist],
            "reasoning": f"Symptoms indicate {detected_specialist} may be appropriate",
            "follow_up": "Consult doctor if symptoms persist or worsen",
            "detected_language": detected_language,
            "original_symptoms": symptoms,
            "translated_symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "stage": "final"
        }

# Global AI engine instance
ai_engine = AIEngine()

# Session management for conversational context
_sessions = {}

def analyze_symptoms_conversational(symptoms, user_id, conversation_history=None):
    """Main AI analysis function with conversation support"""
    try:
        return ai_engine.analyze_symptoms(symptoms, user_id, conversation_history)
    except Exception as e:
        print(f"Analysis failed: {e}")
        return {
            "advice": "Sorry, I'm experiencing technical difficulties. Please try again.",
            "severity": "medium",
            "first_aid": "Monitor symptoms and seek medical help if needed.",
            "otc_medicines": "Consult pharmacist for appropriate medication.",
            "specializations": ["General Physician"],
            "reasoning": "AI system unavailable - defaulting to general care",
            "follow_up": "Please try again or consult healthcare provider directly.",
            "stage": "final"
        }

def get_session_info(user_id):
    """Return current session state for user"""
    sid = str(user_id)
    return _sessions.get(sid, {"message_count": 0, "stage": "idle"})

def reset_session(user_id):
    """Clear session for new conversation"""
    sid = str(user_id)
    _sessions[sid] = {"message_count": 0, "stage": "idle"}

def speak(text):
    """Text-to-speech function (enhanced)"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Configure voice for better medical communication
        voices = engine.getProperty('voices')
        if voices:
            # Prefer female voice for healthcare
            for voice in voices:
                if 'female' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        
        engine.setProperty('rate', 150)  # Slower for medical info
        engine.setProperty('volume', 0.9)
        
        engine.say(text)
        engine.runAndWait()
    except ImportError:
        print(f"🔊 {text}")
    except Exception as e:
        print(f"🔊 {text}")

def get_voice_input():
    """Voice input function (enhanced)"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        
        with sr.Microphone() as source:
            print("🎤 Listening...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        
        # Try multiple recognition engines
        try:
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            try:
                text = r.recognize_sphinx(audio)
                return text
            except:
                return ""
    except ImportError:
        return ""
    except Exception as e:
        print("❌ Voice input failed")
        return ""
