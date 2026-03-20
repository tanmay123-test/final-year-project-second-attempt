import json
import random
from datetime import datetime

# AI Engine for ExpertEase Healthcare Platform
class AIEngine:
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load medical knowledge base"""
        try:
            with open('medical-knowledge.json', 'r') as f:
                return json.load(f)
        except:
            return {"conditions": []}
    
    def analyze_symptoms(self, symptoms, user_id):
        """Analyze symptoms and provide AI response with conversational triage"""
        sid = str(user_id)
        session = _sessions.get(sid, {"message_count": 0, "stage": "idle"})
        
        # Check for emergency keywords first
        emergency_keywords = ["chest pain", "difficulty breathing", "severe chest", "cannot breathe", "emergency"]
        symptoms_lower = symptoms.lower()
        
        for keyword in emergency_keywords:
            if keyword in symptoms_lower:
                return {
                    "stage": "emergency",
                    "message": "🚨 MEDICAL EMERGENCY DETECTED\nVisit nearest hospital immediately",
                    "severity": "severe",
                    "emergency": True
                }
        
        # Conversational triage logic
        if session["stage"] == "idle" or session["message_count"] == 0:
            # First interaction - ask clarifying questions
            if symptoms and symptoms.strip():  # Make sure symptoms is not empty
                if "pain" in symptoms_lower or "ache" in symptoms_lower:
                    if "stomach" in symptoms_lower or "abdomen" in symptoms_lower:
                        question = "Since when are you experiencing this stomach pain? Is it burning, sharp, or cramping?"
                    elif "tooth" in symptoms_lower or "dental" in symptoms_lower:
                        question = "Which tooth is affected? Is the pain constant or only when chewing/drinking?"
                    elif "head" in symptoms_lower:
                        question = "Is this a throbbing headache or sharp pain? Any fever or vision changes?"
                    else:
                        question = "Can you describe the pain more specifically? When did it start?"
                        
                elif "fever" in symptoms_lower:
                    question = "What's your temperature? Any other symptoms like cough, body ache, or chills?"
                else:
                    question = "Can you tell me more about your symptoms? When did they start?"
                    
                # Update session and return question
                _sessions[sid] = {"message_count": 1, "stage": "triage", "initial_symptoms": symptoms}
                return {
                    "stage": "triage",
                    "question": question,
                    "symptoms": symptoms,
                    "detected_language": "en"
                }
            else:
                # Invalid or empty symptoms - return to idle
                return {
                    "stage": "idle",
                    "message": "Please provide valid symptoms to continue"
                }
            
        elif session["stage"] == "triage":
            # Second interaction - analyze and provide final assessment
            initial_symptoms = session.get("initial_symptoms", "")
            
            # Check if user provided meaningful response
            if not symptoms or not symptoms.strip():
                return {
                    "stage": "triage",
                    "question": "Please describe your symptoms to continue analysis",
                    "symptoms": initial_symptoms,
                    "detected_language": "en"
                }
            
            all_symptoms = f"{initial_symptoms}. {symptoms}"
            
            severity = self.assess_severity(all_symptoms)
            specialist = self.determine_specialist(all_symptoms)
            
            response = {
                "stage": "final",
                "symptoms": all_symptoms,
                "severity": severity,
                "specialist": specialist,
                "advice": self.get_advice(all_symptoms, severity),
                "first_aid": self.get_first_aid(all_symptoms),
                "otc_medicines": self.get_medicines(all_symptoms),
                "when_to_visit_doctor": self.get_visit_timing(severity),
                "detected_language": "en",
                "timestamp": datetime.now().isoformat()
            }
            
            # Reset session for new conversation
            _sessions[sid] = {"message_count": 0, "stage": "idle"}
            return response
    
    def determine_specialist(self, symptoms):
        """Determine medical specialist based on symptoms"""
        symptoms_lower = symptoms.lower()
        
        if any(word in symptoms_lower for word in ["tooth", "dental", "molar", "gum"]):
            return "Dentist"
        elif any(word in symptoms_lower for word in ["stomach", "abdomen", "digestion", "acid", "gastric"]):
            return "Gastroenterologist"
        elif any(word in symptoms_lower for word in ["heart", "chest", "cardiac"]):
            return "Cardiologist"
        elif any(word in symptoms_lower for word in ["skin", "rash", "dermat"]):
            return "Dermatologist"
        elif any(word in symptoms_lower for word in ["brain", "neuro", "migraine", "seizure"]):
            return "Neurologist"
        elif any(word in symptoms_lower for word in ["bone", "joint", "orthopedic", "fracture"]):
            return "Orthopedic"
        elif any(word in symptoms_lower for word in ["eye", "vision", "optic"]):
            return "Eye Specialist"
        elif any(word in symptoms_lower for word in ["ear", "nose", "throat", "ent"]):
            return "ENT Specialist"
        elif any(word in symptoms_lower for word in ["mental", "depression", "anxiety", "psych"]):
            return "Psychiatrist"
        elif any(word in symptoms_lower for word in ["child", "pediatric", "baby"]):
            return "Pediatrician"
        elif any(word in symptoms_lower for word in ["woman", "pregnancy", "gynec"]):
            return "Gynecologist"
        else:
            return "General Physician"
    
    def assess_severity(self, symptoms):
        """Assess severity based on symptoms"""
        severe_keywords = ["chest pain", "difficulty breathing", "severe", "emergency"]
        moderate_keywords = ["fever", "headache", "pain", "cough"]
        
        symptoms_lower = symptoms.lower()
        
        for keyword in severe_keywords:
            if keyword in symptoms_lower:
                return "severe"
        
        for keyword in moderate_keywords:
            if keyword in symptoms_lower:
                return "moderate"
        
        return "mild"
    
    def get_advice(self, symptoms, severity):
        """Get medical advice based on symptoms"""
        if severity == "severe":
            return "Seek immediate medical attention. This may be an emergency."
        elif severity == "moderate":
            return "Consult a doctor within 24-48 hours. Monitor symptoms closely."
        else:
            return "Rest and monitor symptoms. Consult doctor if they worsen."
    
    def get_first_aid(self, symptoms):
        """Get first aid recommendations"""
        return "Rest, stay hydrated, and avoid strenuous activity."
    
    def get_medicines(self, symptoms):
        """Get OTC medicine recommendations"""
        return {
            "recommended": "Paracetamol (Crocin)",
            "alternatives": ["Ibuprofen", "Aspirin"],
            "dosage": "As directed on package",
            "notes": "Consult doctor if symptoms persist"
        }
    
    def get_visit_timing(self, severity):
        """Get recommended doctor visit timing"""
        if severity == "severe":
            return "Immediately - Emergency room"
        elif severity == "moderate":
            return "Within 24-48 hours"
        else:
            return "If symptoms persist beyond 3 days"

# Global AI engine instance
ai_engine = AIEngine()

# In-memory session store (per user_id)
_sessions = {}


def analyze_symptoms_conversational(symptoms, user_id):
    """Main AI analysis function"""
    return ai_engine.analyze_symptoms(symptoms, user_id)


def get_session_info(user_id):
    """Return current session state for user"""
    sid = str(user_id)
    return _sessions.get(sid, {"message_count": 0, "stage": "idle"})


def reset_session(user_id):
    """Clear session for new conversation"""
    sid = str(user_id)
    _sessions[sid] = {"message_count": 0, "stage": "idle"}


def speak(text):
    """Text-to-speech function"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except ImportError:
        print(f"🔊 {text}")
    except Exception as e:
        print(f"🔊 {text}")


def get_voice_input():
    """Voice input function"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            audio = r.listen(source)
        text = r.recognize_google(audio)
        return text
    except ImportError:
        return ""
    except Exception as e:
        print("❌ Voice input failed")
        return ""
