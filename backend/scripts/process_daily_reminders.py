#!/usr/bin/env python3
"""
Daily Reminder Scheduler
This script processes and sends due cleaning reminders via email.
Run this script daily (e.g., via cron job at 9 AM).
"""

import sys
import os
import requests
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def process_daily_reminders():
    """
    Process due reminders by calling the API endpoint
    """
    try:
        # Call the reminder processing API
        response = requests.post(
            "http://localhost:5000/api/ai/process-reminders",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            processed = result.get('processed', 0)
            total_due = result.get('total_due', 0)
            error = result.get('error')
            
            if error:
                print(f"❌ Error processing reminders: {error}")
            else:
                print(f"✅ Successfully processed {processed}/{total_due} due reminders")
                if processed > 0:
                    print(f"📧 Sent {processed} reminder emails")
                else:
                    print("📅 No due reminders found")
        else:
            print(f"❌ API call failed with status {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the backend server. Make sure it's running on localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Please try again.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """
    Main function to run the daily reminder processor
    """
    print(f"🕐 Running daily reminder processor: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    process_daily_reminders()
    
    print("=" * 60)
    print(f"✅ Daily reminder processing completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
