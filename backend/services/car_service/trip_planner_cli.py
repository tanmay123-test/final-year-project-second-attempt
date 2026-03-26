"""
AI Trip Planner CLI Interface
Command-line interface for trip planning functionality
"""

import requests
import sys

API = "http://127.0.0.1:5000"

def trip_planner_menu(user_id, token):
    """AI Trip Planner main menu"""
    while True:
        print("\n" + "="*60)
        print("  AI MECHANIC - TRIP PLANNER")
        print("="*60)
        print("1.     Plan New Trip")
        print("2.   Trip History")
        print("3.     Settings")
        print("4.     Back to Car Service")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            plan_new_trip(user_id, token)
        elif choice == "2":
            show_trip_history(user_id, token)
        elif choice == "3":
            show_settings()
        elif choice == "4":
            return
        else:
            print("  Invalid choice")

def plan_new_trip(user_id, token):
    """Plan a new trip"""
    print("\n" + "="*60)
    print("    PLAN NEW TRIP")
    print("="*60)
    
    try:
        # Get user input
        start = input("  Enter starting location: ").strip()
        if not start:
            print("  Starting location is required")
            return
        
        destination = input("  Enter destination location: ").strip()
        if not destination:
            print("  Destination location is required")
            return
        
        # Validate different locations
        if start.lower() == destination.lower():
            print("  Starting and destination locations cannot be the same")
            return
        
        # Get vehicle details
        try:
            mileage = float(input("  Enter your car mileage (km per liter): ").strip())
            if mileage <= 0:
                print("  Mileage must be greater than 0")
                return
        except ValueError:
            print("  Invalid mileage value")
            return
        
        try:
            fuel_price = float(input("  Enter fuel price per liter ( ): ").strip())
            if fuel_price <= 0:
                print("  Fuel price must be greater than 0")
                return
        except ValueError:
            print("  Invalid fuel price value")
            return
        
        print("\n  Planning your trip...")
        print("  Getting coordinates...")
        print("    Calculating route...")
        print("  Estimating costs...")
        
        # Call API
        trip_data = {
            "start": start,
            "destination": destination,
            "mileage": mileage,
            "fuel_price": fuel_price
        }
        
        response = requests.post(
            f"{API}/api/car/ai/trip-plan",
            json=trip_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                trip_plan = result.get("trip_plan", {})
                display_trip_plan(trip_plan)
                
                # Ask if user wants to save
                save = input("\n  Save this trip plan? (y/n): ").strip().lower()
                if save == 'y':
                    save_trip_plan(user_id, token, trip_plan)
            else:
                print("  Failed to plan trip")
        else:
            error = response.json().get("error", "Unknown error")
            print(f"  Error: {error}")
        
    except KeyboardInterrupt:
        print("\n\n  Trip planning cancelled")
    except Exception as e:
        print(f"  Error: {e}")

def display_trip_plan(trip_plan):
    """Display the trip plan in a formatted way"""
    if not trip_plan:
        print("  No trip plan to display")
        return
    
    print("\n" + "="*70)
    print("  AI TRIP PLANNER - YOUR JOURNEY PLAN")
    print("="*70)
    print(f"  From: {trip_plan.get('start', 'Unknown')}")
    print(f"  To: {trip_plan.get('destination', 'Unknown')}")
    print("")
    print("  JOURNEY DETAILS:")
    print(f"       Distance: {trip_plan.get('distance_km', 0)} km")
    print(f"       ETA: {trip_plan.get('duration_hours', 0)} hours")
    print("")
    print("  COST BREAKDOWN:")
    print(f"     Fuel needed: {trip_plan.get('fuel_needed', 0)} liters")
    print(f"     Fuel cost:  {trip_plan.get('fuel_cost', 0)}")
    print(f"       Estimated toll:  {trip_plan.get('toll_cost', 0)}")
    print(f"     Total cost:  {trip_plan.get('total_cost', 0)}")
    print("")
    print("  TRIP CHECKLIST:")
    checklist = trip_plan.get('checklist', [])
    for i, item in enumerate(checklist, 1):
        print(f"   {i}. {item}")
    print("")
    print("  VEHICLE INFO:")
    print(f"     Mileage: {trip_plan.get('mileage', 0)} km/liter")
    print(f"     Fuel price:  {trip_plan.get('fuel_price', 0)}/liter")
    print("")
    print("  Have a safe and pleasant journey!")
    print("="*70)

def save_trip_plan(user_id, token, trip_plan):
    """Save trip plan to user history (placeholder for future implementation)"""
    print("  Trip plan saved successfully!")
    print("  You can view your saved trips in Trip History")

def show_trip_history(user_id, token):
    """Show user's trip history (placeholder for future implementation)"""
    print("\n" + "="*60)
    print("  TRIP HISTORY")
    print("="*60)
    print("  No saved trips found")
    print("  Plan a new trip to get started!")
    input("\nPress Enter to continue...")

def show_settings():
    """Show trip planner settings"""
    print("\n" + "="*60)
    print("    TRIP PLANNER SETTINGS")
    print("="*60)
    print("  Toll rate per km:  0.75")
    print("  Geocoding service: OpenStreetMap Nominatim")
    print("    Routing service: OSRM")
    print("  Country focus: India")
    print("")
    print("  PERFORMANCE:")
    print("     Real-time geocoding")
    print("     Dynamic route calculation")
    print("     Accurate distance/ETA")
    print("     Fuel cost estimation")
    print("     Toll cost estimation")
    print("")
    print("  PRIVACY:")
    print("     No location data stored")
    print("     No personal tracking")
    print("     Anonymous API calls")
    input("\nPress Enter to continue...")

def quick_trip_planner(user_id, token):
    """Quick trip planner for direct access"""
    print("\n" + "="*60)
    print("  QUICK TRIP PLANNER")
    print("="*60)
    
    start = input("  Starting location: ").strip()
    if not start:
        print("  Starting location required")
        return
    
    destination = input("  Destination: ").strip()
    if not destination:
        print("  Destination required")
        return
    
    if start.lower() == destination.lower():
        print("  Locations must be different")
        return
    
    try:
        mileage = float(input("  Mileage (km/l): ").strip())
        fuel_price = float(input("  Fuel price ( /l): ").strip())
        
        if mileage <= 0 or fuel_price <= 0:
            print("  Invalid values")
            return
        
        print("\n  Planning trip...")
        
        trip_data = {
            "start": start,
            "destination": destination,
            "mileage": mileage,
            "fuel_price": fuel_price
        }
        
        response = requests.post(
            f"{API}/api/car/ai/trip-plan",
            json=trip_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                trip_plan = result.get("trip_plan", {})
                display_trip_plan(trip_plan)
            else:
                print("  Failed to plan trip")
        else:
            error = response.json().get("error", "Unknown error")
            print(f"  Error: {error}")
            
    except ValueError:
        print("  Invalid numeric values")
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")
