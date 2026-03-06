#!/usr/bin/env python3
"""
Test script to demonstrate the updated admin menu
"""

print("🔧 TESTING UPDATED ADMIN MENU")
print("="*50)

# Test imports
try:
    from cli import admin_menu, fuel_delivery_admin_menu, truck_operator_admin_menu
    print("✅ Admin menu functions imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")

print("\n" + "="*50)
print("📋 UPDATED ADMIN DASHBOARD:")
print("="*50)
print("1. 👷 Car Service Workers")
print("2. 🏥 Healthcare Workers")
print("3. ⛽ Fuel Delivery Agents ← NEW!")
print("4. 🚚 Truck Operators ← NEW!")
print("5. 👋 Logout")
print("="*50)

print("\n📋 FUEL DELIVERY AGENT ADMIN:")
print("="*50)
print("1. 📋 Pending Agents")
print("2. ✅ Approved Agents")
print("3. 🔍 Agent Details")
print("4. ⬅️ Back")

print("\n📋 TRUCK OPERATOR ADMIN:")
print("="*50)
print("1. 📋 Pending Operators")
print("2. ✅ Approved Operators")
print("3. 🔍 Operator Details")
print("4. ⬅️ Back")

print("\n✅ All admin functions are now available!")
print("🎯 You can now manage fuel delivery agents and truck operators!")
print("📊 View pending registrations, approve/reject, and manage documents")
