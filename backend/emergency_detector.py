import os
from dotenv import load_dotenv

load_dotenv()

# Prefer new google.genai client; fallback to deprecated google.generativeai
_USE_NEW_GENAI = False
_gen_text = None
api_key = os.getenv("GEMINI_API_KEY")

try:
    from google import genai as genai_new
    client = genai_new.Client(api_key=api_key)
    def _gen_text(prompt: str) -> str:
        resp = client.responses.generate(model="gemini-2.0-flash", input=prompt)
        return (getattr(resp, "output_text", None) or "").strip()
    _USE_NEW_GENAI = True
except Exception:
    try:
        import google.generativeai as genai_old
        genai_old.configure(api_key=api_key)
        model = genai_old.GenerativeModel("gemini-2.0-flash")
        def _gen_text(prompt: str) -> str:
            r = model.generate_content(prompt)
            return (getattr(r, "text", None) or "").strip()
    except Exception:
        def _gen_text(prompt: str) -> str:
            return ""

SAFETY_KEYWORDS = [
    "chest pain", "can't breathe", "shortness of breath",
    "stroke", "unconscious", "heavy bleeding",
    "heart attack", "seizure"
]


def is_emergency(text: str) -> bool:
    text_lower = text.lower()

    #    Step 1   Safety keyword backup
    for word in SAFETY_KEYWORDS:
        if word in text_lower:
            return True

    #   Step 2   Ask AI severity dynamically
    try:
        prompt = f"""
Is this a medical emergency?

Symptoms: {text}

Answer only YES or NO.
"""
        answer = _gen_text(prompt).lower()

        return "yes" in answer

    except:
        return False
