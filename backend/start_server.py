#!/usr/bin/env python3
"""
Backend Server Startup Script
Run this script to start the Flask backend server
"""

import sys
import os

def main():
    print("  Starting ExpertEase Backend Server...")
    print("  Location: http://127.0.0.1:5000")
    print("  AI Mechanic Endpoint: http://127.0.0.1:5000/api/ai/mechanic-diagnosis")
    print("  Server starting...")
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(host='127.0.0.1', port=5000, debug=True)
    except ImportError as e:
        print(f"  Import Error: {e}")
        print("  Make sure you're in the backend directory")
        sys.exit(1)
    except Exception as e:
        print(f"  Server Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
