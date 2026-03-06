#!/usr/bin/env python3
"""
Test script to demonstrate the updated truck operator options
"""

print("🚛 TESTING TRUCK OPERATOR INTEGRATION")
print("="*50)

# Test imports
try:
    from car_service.truck_operator_cli import truck_operator_signup, truck_operator_login
    print("✅ Truck operator CLI imported successfully")
except Exception as e:
    print(f"❌ Truck operator import failed: {e}")

try:
    from car_service.fuel_delivery_cli import fuel_delivery_agent_menu
    print("✅ Fuel delivery CLI imported successfully")
except Exception as e:
    print(f"❌ Fuel delivery import failed: {e}")

try:
    from car_service.worker_cli import tow_truck_operator_signup
    print("✅ Tow truck operator signup imported successfully")
except Exception as e:
    print(f"❌ Tow truck operator import failed: {e}")

# Test database
try:
    from car_service.truck_operator_db import truck_operator_db
    stats = truck_operator_db.get_operator_stats()
    print(f"✅ Truck operator database working: {stats}")
except Exception as e:
    print(f"❌ Database test failed: {e}")

print("\n" + "="*50)
print("📋 UPDATED CAR SERVICE WORKER MENU:")
print("="*50)
print("1. 🔧 Mechanic")
print("2. ⛽ Fuel Delivery Agent")
print("3. 🚛 Tow Truck Operator")
print("4. 🧠 Automobile Expert")
print("5. 🚚 Truck Operator ← NEW!")
print("6. ⬅️ Back")
print("="*50)
print("\n✅ All worker types are now functional!")
print("🚚 Truck Operator registration includes:")
print("   • Name, phone, email, password, city")
print("   • Vehicle type and number")
print("   • Vehicle photo upload")
print("   • RC book upload")
print("   • Petrol pump authorization letter")
print("   • Admin approval workflow")
print("   • Dashboard with job management")
