import os
import httpx
import json
from datetime import datetime, timedelta
from housekeeping.models.database import HousekeepingDatabase

# Initialize database
db = HousekeepingDatabase()

# Gemini Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-2.0-flash"

# IDEAL FREQUENCIES (using average of ranges provided)
IDEAL_FREQUENCIES = {
    "Bathroom Cleaning": 25,  # 20-30 days
    "Kitchen Cleaning": 17.5, # 15-20 days
    "General Cleaning": 37.5, # 30-45 days (Full Home)
    "Sofa Cleaning": 75       # 60-90 days
}

def get_user_recommendations(user_id):
    """
    FEATURE 1 — Smart Recommendation Engine
    Fetches user's booking history, calculates days since each service was last booked,
    compares against ideal frequency rules, computes hygiene score, and returns ranked recommendations.
    """
    conn = None
    cursor = None
    try:
        conn = db.get_conn()
        cursor = conn.cursor()
        
        # Fetch last completed booking for each service type for this user
        cursor.execute("""
            SELECT service_type, MAX(booking_date) as last_booked
            FROM bookings
            WHERE user_id = %s AND status = 'COMPLETED'
            GROUP BY service_type
        """, (user_id,))
        
        history = cursor.fetchall()
        
        recommendations = []
        today = datetime.now()
        
        # Track which services we have history for
        services_with_history = set()
        
        for row in history:
            service_type, last_booked_str = row
            services_with_history.add(service_type)
            
            if service_type not in IDEAL_FREQUENCIES:
                continue
                
            ideal_days = IDEAL_FREQUENCIES[service_type]
            
            try:
                # Assuming booking_date is stored as 'YYYY-MM-DD' or similar
                # We split by ' ' in case it has time attached
                date_part = str(last_booked_str).split(' ')[0]
                last_booked_date = datetime.strptime(date_part, '%Y-%m-%d')
            except Exception as e:
                print(f"Date parsing error for {last_booked_str}: {e}")
                last_booked_date = today - timedelta(days=365) # Fallback to long ago
                
            days_since_last = (today - last_booked_date).days
            
            # score = 10 - (days_since_last / ideal_days * 10)
            score = 10 - (days_since_last / ideal_days * 10)
            score = max(0, min(10, score)) # Clamp between 0 and 10
            
            urgency = "LOW"
            if score < 3:
                urgency = "HIGH"
            elif score < 7:
                urgency = "MEDIUM"
                
            recommendations.append({
                "service": service_type,
                "score": round(score, 1),
                "urgency": urgency,
                "days_since_last": days_since_last,
                "message": f"It has been {days_since_last} days since your last {service_type.lower()}."
            })
            
        # Add recommendations for services never booked
        for service, ideal_days in IDEAL_FREQUENCIES.items():
            if service not in services_with_history:
                recommendations.append({
                    "service": service,
                    "score": 0,
                    "urgency": "HIGH",
                    "days_since_last": None,
                    "message": f"You haven't booked a {service.lower()} yet. It's highly recommended to start your hygiene journey!"
                })
                
        # Rank by urgency (HIGH first) and then by score (lowest first)
        urgency_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        recommendations.sort(key=lambda x: (urgency_map[x['urgency']], x['score']))
        
        return recommendations
        
    except Exception as e:
        print(f"Error in get_user_recommendations: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def process_home_query(query):
    """
    FEATURE 2 — Home Assistant Chat
    Classifies the query and generates a response using Google Gemini API.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"response": "Gemini API key not configured.", "mode": "error"}
        
    # Classification logic
    query_lower = query.lower()
    if "recipe" in query_lower:
        mode = "cooking"
        system_prompt = "You are a helpful cooking assistant. Provide delicious recipes and kitchen tips."
    elif "clean" in query_lower:
        mode = "cleaning"
        system_prompt = "You are a professional cleaning expert. Provide efficient cleaning tips and home maintenance hacks."
    elif "dirty" in query_lower or "problem" in query_lower:
        mode = "service"
        system_prompt = "You are a home service advisor. Suggest appropriate housekeeping services based on the user's problem."
    else:
        mode = "general"
        system_prompt = "You are a friendly home assistant. Help with general home management and organizational tasks."
        
    try:
        # Prepare the prompt
        full_prompt = f"{system_prompt}\n\nUser Question:\n{query}"
        
        # Prepare API request
        url = f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        # Make API call synchronously for this simple implementation
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the generated text
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        ai_text = candidate["content"]["parts"][0]["text"].strip()
                        return {
                            "response": ai_text,
                            "mode": mode
                        }
                
                return {"response": "I apologize, but I couldn't generate a response. Please try rephrasing your question.", "mode": mode}
            
            return {"response": f"Technical difficulties (Status: {response.status_code}). Please try again later.", "mode": "error"}
            
    except Exception as e:
        print(f"Error in process_home_query: {e}")
        return {"response": f"Sorry, I encountered an error: {str(e)}", "mode": "error"}
