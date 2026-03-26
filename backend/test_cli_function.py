import requests
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function
import cli

print("Testing CLI healthcare_pending_workers function...")
try:
    cli.healthcare_pending_workers()
    print("✅ CLI function executed successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
