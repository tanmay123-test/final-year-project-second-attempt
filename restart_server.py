#!/usr/bin/env python3
"""
Quick restart of Flask app
"""
import subprocess
import sys
import os

def restart_server():
    """Restart the Flask server"""
    print("🔄 RESTARTING FLASK SERVER...")
    
    # Kill existing Python processes
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
    except:
        pass
    
    # Start new server
    os.chdir("c:\\Users\\Admin\\Desktop\\Project\\final-year-project-")
    
    print("🚀 Starting server...")
    subprocess.run([sys.executable, "app.py"])

if __name__ == "__main__":
    restart_server()
