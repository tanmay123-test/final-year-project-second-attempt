#!/usr/bin/env python3
"""
Environment Variables Check Script
Verifies all required API keys are present and tests connectivity
"""

import os
import sys
from dotenv import load_dotenv
import httpx
import json

def check_gemini_connectivity(api_key):
    """Test Gemini API connectivity"""
    if not api_key or api_key == "your_gemini_api_key_here":
        return False, "❌ GEMINI_API_KEY not set or using placeholder"
    
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": "OK"}]}]
        }
        
        with httpx.Client(timeout=10) as client:
            response = client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return True, "✅ Gemini API connectivity verified"
            else:
                return False, f"❌ Gemini API returned status {response.status_code}"
    except Exception as e:
        return False, f"❌ Gemini API connection failed: {str(e)}"

def check_finnhub_connectivity(api_key):
    """Test Finnhub API connectivity"""
    if not api_key or api_key == "your_finnhub_api_key_here":
        return False, "❌ FINNHUB_API_KEY not set or using placeholder"
    
    try:
        url = "https://finnhub.io/api/v1/quote?symbol=AAPL"
        headers = {"X-Finnhub-Token": api_key}
        
        with httpx.Client(timeout=10) as client:
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                return True, "✅ Finnhub API connectivity verified"
            else:
                return False, f"❌ Finnhub API returned status {response.status_code}"
    except Exception as e:
        return False, f"❌ Finnhub API connection failed: {str(e)}"

def main():
    """Main check function"""
    print("🔍 Checking environment variables and API connectivity...\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check required keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    
    all_good = True
    issues = []
    
    # Check Gemini
    gemini_ok, gemini_msg = check_gemini_connectivity(gemini_key)
    print(f"Gemini API: {gemini_msg}")
    if not gemini_ok:
        all_good = False
        issues.append("Gemini API")
    
    # Check Finnhub
    finnhub_ok, finnhub_msg = check_finnhub_connectivity(finnhub_key)
    print(f"Finnhub API: {finnhub_msg}")
    if not finnhub_ok:
        all_good = False
        issues.append("Finnhub API")
    
    # Summary
    print("\n" + "="*50)
    if all_good:
        print("🎉 All API keys are configured and working correctly!")
        print("✅ Ready to start the application")
        return 0
    else:
        print("⚠️ Issues found with the following APIs:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n📝 Please check your .env file and ensure all API keys are set correctly.")
        print("📋 Reference .env.example for required keys format.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
