#!/usr/bin/env python3
"""
Set some mechanics to online status for testing
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def set_mechanics_online():
    """Set first few mechanics to online status"""
    try:
        from car_service.car_mechanics_db import car_mechanics_db
        
        print("🔧 SETTING MECHANICS TO ONLINE STATUS")
        print("=" * 50)
        
        # Get all approved mechanics
        mechanics = car_mechanics_db.get_mechanics(status='approved')
        
        if not mechanics:
            print("❌ No approved mechanics found")
            return
        
        print(f"📊 Found {len(mechanics)} approved mechanics")
        
        # Set first 3 mechanics to online
        online_count = 0
        for i, mech in enumerate(mechanics[:3], 1):
            mechanic_id = mech[0]
            mechanic_name = mech[1]
            
            # Set to online
            success = car_mechanics_db.update_mechanic_online_status(mechanic_id, 'online')
            
            if success:
                print(f"✅ {i}. {mechanic_name} is now ONLINE")
                online_count += 1
            else:
                print(f"❌ {i}. Failed to set {mechanic_name} online")
        
        # Set remaining mechanics to offline
        for mech in mechanics[3:]:
            mechanic_id = mech[0]
            car_mechanics_db.update_mechanic_online_status(mechanic_id, 'offline')
        
        print(f"\n🎉 {online_count} mechanics set to ONLINE")
        
        # Verify online mechanics
        print(f"\n🔍 VERIFYING ONLINE MECHANICS:")
        online_mechanics = car_mechanics_db.get_online_mechanics()
        
        if online_mechanics:
            print(f"📊 {len(online_mechanics)} mechanics are online:")
            for mech in online_mechanics:
                print(f"   👨‍🔧 {mech[1]} - {mech[4]} ({mech[7]})")
        else:
            print("❌ No online mechanics found")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    set_mechanics_online()
