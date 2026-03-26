"""
Uber-style Fuel Delivery User CLI
"""

from .fuel_delivery_user_service import fuel_delivery_user_service
import time

def fuel_delivery_user_interface(user_info):
    """Uber-style fuel delivery user interface"""
    print("\n" + "="*60)
    print("  FUEL DELIVERY SERVICE")
    print("="*60)
    
    # Step 1: Get fuel type
    print("\n  SELECT FUEL TYPE:")
    print("1.   Petrol")
    print("2.    Diesel")
    
    fuel_choice = input("\nSelect fuel type (1-2): ").strip()
    
    if fuel_choice == "1":
        fuel_type = "Petrol"
        fuel_emoji = " "
    elif fuel_choice == "2":
        fuel_type = "Diesel"
        fuel_emoji = "  "
    else:
        print("  Invalid choice")
        input("\nPress Enter to continue...")
        return
    
    # Step 2: Get fuel quantity
    print(f"\n  ENTER FUEL QUANTITY ({fuel_type}):")
    print("Common quantities: 5L, 10L, 20L, 30L, 50L")
    
    quantity_input = input("Enter quantity in liters: ").strip()
    
    # Remove 'L' suffix if present and convert to float
    if quantity_input.endswith('L') or quantity_input.endswith('l'):
        quantity_input = quantity_input[:-1]
    
    try:
        fuel_quantity = float(quantity_input)
        if fuel_quantity <= 0 or fuel_quantity > 100:
            print("  Invalid quantity (must be between 1L and 100L)")
            input("\nPress Enter to continue...")
            return
    except ValueError:
        print("  Invalid quantity format")
        input("\nPress Enter to continue...")
        return
    
    # Step 3: Get location
    print(f"\n  ENTER DELIVERY LOCATION:")
    print("Example: Asalpha, Bandra, Andheri, Worli, Dadar, Kurla, Goregaon, BKC")
    
    location_name = input("Enter location name: ").strip()
    if not location_name:
        print("  Location is required")
        input("\nPress Enter to continue...")
        return
    
    # Convert location to coordinates
    coordinates = fuel_delivery_user_service.geocode_location(location_name)
    user_lat, user_lon = coordinates
    
    print(f"\n   Location: {location_name}")
    print(f"  Coordinates: {user_lat:.4f}, {user_lon:.4f}")
    
    # Step 4: Find nearby agents
    print(f"\n  SEARCHING NEARBY FUEL AGENTS...")
    time.sleep(2)
    
    nearby_agents = fuel_delivery_user_service.find_nearby_agents(user_lat, user_lon, fuel_quantity)
    
    if not nearby_agents:
        print("  No nearby fuel agents available for this location and quantity")
        input("\nPress Enter to continue...")
        return
    
    # Display nearby agents (Uber-style)
    print(f"\n  NEARBY FUEL AGENTS (Top {len(nearby_agents)})")
    print("="*60)
    
    for i, agent in enumerate(nearby_agents, 1):
        vehicle_emoji = "  " if agent['vehicle_type'] == 'Bike' else " " if agent['vehicle_type'] == 'Van' else " "
        rating_stars = " " * int(agent['rating']) + " " * (5 - int(agent['rating']))
        
        print(f"{i}. {agent['name']}")
        print(f"   {vehicle_emoji} Vehicle: {agent['vehicle_type']} (Max: {fuel_delivery_user_service.get_max_capacity(agent['vehicle_type'])}L)")
        print(f"     Distance: {agent['distance_km']} km")
        print(f"      ETA: {agent['eta_minutes']} minutes")
        print(f"   {rating_stars} {agent['rating']:.1f}")
        print(f"     Completion Rate: {agent['completion_rate']:.1f}%")
        print(f"      Service Area: {agent['service_area_km']} km")
        print()
    
    # Step 5: Booking options
    print("  BOOKING OPTIONS:")
    print("1.   Select Agent (Manual)")
    print("2.   Auto-Dispatch (Best Agent)")
    print("3.   Cancel")
    
    booking_choice = input("\nSelect booking option (1-3): ").strip()
    
    if booking_choice == "1":
        # Manual agent selection
        try:
            agent_choice = int(input(f"Select agent (1-{len(nearby_agents)}): ").strip())
            if 1 <= agent_choice <= len(nearby_agents):
                selected_agent = nearby_agents[agent_choice - 1]
                create_fuel_request_manual(user_info, fuel_type, fuel_quantity, location_name, selected_agent)
            else:
                print("  Invalid agent selection")
        except ValueError:
            print("  Invalid selection format")
    
    elif booking_choice == "2":
        # Auto-dispatch
        create_fuel_request_auto(user_info, fuel_type, fuel_quantity, location_name, user_lat, user_lon)
    
    elif booking_choice == "3":
        print("  Booking cancelled")
    
    else:
        print("  Invalid choice")
    
    input("\nPress Enter to continue...")

def create_fuel_request_manual(user_info, fuel_type, fuel_quantity, location_name, selected_agent):
    """Create fuel request with manually selected agent"""
    print(f"\n  CREATING FUEL DELIVERY REQUEST...")
    print(f"  Fuel: {fuel_type} - {fuel_quantity}L")
    print(f"  Location: {location_name}")
    print(f"  Agent: {selected_agent['name']}")
    print(f"  Distance: {selected_agent['distance_km']} km")
    print(f"   ETA: {selected_agent['eta_minutes']} minutes")
    
    confirm = input("\nConfirm booking? (y/n): ").strip().lower()
    if confirm != 'y':
        print("  Booking cancelled")
        return
    
    # Create request
    coordinates = fuel_delivery_user_service.geocode_location(location_name)
    user_lat, user_lon = coordinates
    
    result = fuel_delivery_user_service.create_fuel_request(
        user_info['id'], fuel_type, fuel_quantity, 
        user_lat, user_lon, selected_agent['agent_id']
    )
    
    if result.get('success'):
        request_id = result.get('request_id')
        otp = result.get('otp', 'N/A')
        print(f"\n  Request sent successfully!")
        print(f"  Request ID: {request_id}")
        print(f"  YOUR OTP: {otp}")
        print("   PLEASE GIVE THIS OTP TO THE AGENT ONLY WHEN THEY ARRIVE")
        
        # Track status
        track_request_status(request_id)
    else:
        print(f"  Failed to create request: {result.get('error', 'Unknown error')}")

def track_request_status(request_id):
    """Track the status of a fuel request until completion"""
    print("\n  Tracking your request status...")
    last_status = None
    
    while True:
        try:
            # In a real app, this would call the service/API
            # For this CLI simulation, we'll check status via the service
            status_info = fuel_delivery_user_service.get_request_status(request_id)
            status = status_info.get('status')
            
            if status != last_status:
                print(f"\n  Status Update: {status}")
                last_status = status
                
            if status == 'COMPLETED':
                print("\n  Your fuel has been delivered!")
                print("  PAYMENT REQUIRED")
                print("1.   Pay Now")
                print("2.    Back to Menu")
                
                choice = input("\nSelect option: ").strip()
                if choice == "1":
                    print("\nRedirecting to payment gateway...")
                    time.sleep(2)
                    print("  Payment successful! Thank you for using ExpertEase.")
                return
            
            elif status == 'CANCELLED':
                print("\n  Your request was cancelled.")
                return
            
            time.sleep(5) # Check every 5 seconds
        except KeyboardInterrupt:
            print("\n  Stopped tracking status. You can check it later from history.")
            return
        except Exception as e:
            print(f"\n  Error tracking status: {e}")
            return

def create_fuel_request_auto(user_info, fuel_type, fuel_quantity, location_name, user_lat, user_lon):
    """Create fuel request with auto-dispatch"""
    print(f"\n  AUTO-DISPATCHING TO BEST AGENT...")
    print(f"  Fuel: {fuel_type} - {fuel_quantity}L")
    print(f"  Location: {location_name}")
    
    time.sleep(2)
    
    result = fuel_delivery_user_service.auto_dispatch_request(
        user_info['id'], fuel_type, fuel_quantity, user_lat, user_lon
    )
    
    if result.get('success'):
        print("  Auto-dispatch successful!")
        print(f"  Request ID: {result.get('request_id', 'N/A')}")
        print(f"  Best agent assigned based on distance, rating, and availability")
        print("  Agent will contact you soon")
    else:
        print(f"  Auto-dispatch failed: {result.get('error', 'Unknown error')}")

print("  UBER-STYLE FUEL DELIVERY USER SERVICE READY!")
print("  Location-based agent discovery")
print("  Service area validation")
print("  Capacity-based filtering")
print("  Uber-style worker listing")
print("  Fair dispatch algorithm")
print("  Manual and auto-dispatch options")
print("  Complete booking lifecycle")
