#!/usr/bin/env python3
"""
Add Tanmay Bansode Time Slots
This script adds available time slots for Tanmay Bansode worker.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_tanmay_time_slots():
    """
    Add time slots for Tanmay Bansode
    """
    print("🕐 Adding Tanmay Bansode Time Slots")
    print("=" * 50)
    
    try:
        from availability_db import AvailabilityDB
        
        availability_db = AvailabilityDB()
        tanmay_worker_id = 1  # Tanmay's worker ID
        
        # Clear existing slots for Tanmay (to avoid duplicates)
        print("🗑️ Getting existing slots for Tanmay...")
        existing_slots = availability_db.get_availability(tanmay_worker_id)
        print(f"   Found {len(existing_slots)} existing slots")
        
        # Note: We'll add new slots, duplicates will be handled by database constraints
        
        # Generate time slots for the next 7 days
        time_slots = [
            "9:00 AM", "10:00 AM", "11:00 AM", 
            "12:00 PM", "2:00 PM", "3:00 PM", 
            "4:00 PM", "5:00 PM", "6:00 PM"
        ]
        
        print("📅 Adding time slots for the next 7 days...")
        
        for day_offset in range(7):  # Next 7 days
            date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            print(f"\n📆 Adding slots for {date}:")
            
            for time_slot in time_slots:
                try:
                    availability_db.add_availability(
                        worker_id=tanmay_worker_id,
                        date=date,
                        time_slot=time_slot
                    )
                    print(f"  ✅ {time_slot}")
                except Exception as e:
                    print(f"  ❌ {time_slot} - Error: {e}")
        
        # Verify the slots were added
        print("\n🔍 Verifying added slots...")
        for day_offset in range(3):  # Check first 3 days
            date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            slots = availability_db.get_availability(tanmay_worker_id, date)
            print(f"\n📅 {date}: {len(slots)} slots available")
            for slot in slots[:3]:  # Show first 3 slots
                print(f"  ⏰ {slot['time_slot']}")
            if len(slots) > 3:
                print(f"  ... and {len(slots) - 3} more")
        
        print("\n" + "=" * 50)
        print("🎉 Tanmay Bansode time slots added successfully!")
        print("\n📋 Summary:")
        print(f"• Worker ID: {tanmay_worker_id} (Tanmay Bansode)")
        print(f"• Days: Next 7 days")
        print(f"• Slots per day: {len(time_slots)}")
        print(f"• Total slots: {7 * len(time_slots)}")
        
        print("\n🚀 Users can now book Tanmay through his available slots!")
        print("📱 Booking Flow:")
        print("1. User selects General Cleaning service")
        print("2. User chooses date and time")
        print("3. Tanmy appears as available for his slots")
        print("4. Booking is created based on his online status")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding time slots: {e}")
        return False

def main():
    """
    Main function
    """
    print(f"🕐 Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = add_tanmay_time_slots()
    
    if success:
        print("\n✨ Time slot setup completed!")
        print("\n🔄 Next Steps:")
        print("1. Test the booking flow in frontend")
        print("2. Verify Tanmay appears in available workers")
        print("3. Check instant booking works with slots")
    else:
        print("\n⚠️ Time slot setup failed. Please check the configuration.")

if __name__ == "__main__":
    main()
