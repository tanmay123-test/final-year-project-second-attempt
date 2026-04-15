"""
Local Database Configuration for Development
Use this when Supabase is not accessible
"""
import os
from dotenv import load_dotenv

# Load from .env — do NOT override DATABASE_URL here
load_dotenv()

print("✅ Local database configuration loaded")
print("📊 DATABASE_URL:", os.environ.get('DATABASE_URL', 'NOT SET'))
print("🤖 GEMINI_API_KEY:", "✅ Set" if os.environ.get('GEMINI_API_KEY') else "❌ Missing")
