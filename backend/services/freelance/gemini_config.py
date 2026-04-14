# Gemini API Key Configuration
# Always read from environment so the single .env key is used everywhere
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDhIxvJpy1UGc5BO1-YREiBXZbAjdNZpoQ")
