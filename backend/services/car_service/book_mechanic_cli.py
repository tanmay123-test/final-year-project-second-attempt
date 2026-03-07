import requests
from .booking_db import booking_db
from .car_profile_db import car_profile_db
from .car_service_worker_db import car_service_worker_db
from .smart_search_engine import SmartSearchEngine, SearchRequest
from .location_resolution_engine import LocationResolutionEngine

API = "http://127.0.0.1:5000"

def _get_top_mechanics():
    # Get all mechanics from unified car service worker database
    all_workers = car_service_worker_db.get_all_workers()
    # Filter for mechanics using role field instead of service
    mechanics = [w for w in all_workers if (w.get('role') or '').lower() == 'mechanic' and w.get('status') == 'APPROVED']
    mechanics.sort(key=lambda w: float(w.get('rating') or 0), reverse=True)
    top = mechanics[:5]
    for m in top:
        m['completed_jobs'] = booking_db.get_completed_count_for_mechanic(m['id'])
    return top

def _search_mechanics_by_name(name):
    # Search mechanics in unified car service worker database
    results = car_service_worker_db.search_workers(name or "")
    return [w for w in results if (w.get('role') or '').lower() == 'mechanic' and w.get('status') == 'APPROVED']

def _print_queue_cards(mechanics):
    print("\n" + "="*50)
    print("🔧 AVAILABLE MECHANICS (Top Rated)")
    print("="*50)
    for idx, m in enumerate(mechanics, 1):
        print(f"\n[{idx}] 👨‍🔧 {m.get('name','Unknown')}")
        print(f"⭐ Rating: {float(m.get('rating') or 0):.1f}")
        print(f"Experience: {int(m.get('experience') or 0)} years")
        print(f"Completed Jobs: {int(m.get('completed_jobs') or 0)}")
    print("\n----------------------------------------")

def _select_mechanic(top_mechanics):
    sel = input("\nSelect mechanic number or press 0 to search all mechanics: ").strip()
    if sel == "0":
        print("\nSearch options:")
        print("1. Search by name")
        print("2. Search by issue/skill (Smart Search)")
        print("3. Back")
        
        search_choice = input("\nSelect search option: ").strip()
        
        if search_choice == "1":
            q = input("Enter mechanic name to search (or press Enter to skip): ").strip()
            results = _search_mechanics_by_name(q)
            if not results:
                print("❌ No mechanics found")
                return None
            _print_queue_cards(results[:5])
            sel = input("\nSelect mechanic number from above list: ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > min(len(results[:5]), 5):
                print("❌ Invalid selection")
                return None
            return results[int(sel) - 1]
            
        elif search_choice == "2":
            return _smart_search_mechanics()
            
        else:
            print("❌ Invalid selection")
            return None
            
    if not sel.isdigit() or int(sel) < 1 or int(sel) > len(top_mechanics):
        print("❌ Invalid selection")
        return None
    return top_mechanics[int(sel) - 1]

def _booking_type_menu():
    print("\nSelect booking type:")
    print("\n1. Instant Book")
    print("2. Pre-Book (Schedule)")
    print("3. Back")
    return input("\nChoice: ").strip()

def _prebook_flow(user_id, mechanic):
    # Simplified prebook flow without slots
    default_car = car_profile_db.get_default_car(user_id)
    if not default_car:
        print("❌ No cars found. Please add a car first in My Garage.")
        return
    
    issue = input("Describe your issue: ").strip()
    if not issue:
        print("❌ Issue is required")
        return
    
    # Create a prebook job without slot system
    booking_db.create_job(
        user_id=user_id,
        mechanic_id=mechanic['id'],
        car_id=default_car['id'],
        issue=issue,
        estimated_cost=500  # Default estimated cost
    )
    
    print("\n✅ Mechanic booked successfully (PREBOOK).")
    print("📅 Mechanic will contact you to schedule the appointment.")
    print("💡 You can contact the mechanic directly to arrange the timing.")

def _instant_flow(user_id, mechanic):
    default_car = car_profile_db.get_default_car(user_id)
    if not default_car:
        print("❌ No cars found. Please add a car first in My Garage.")
        return
    issue = input("Describe your issue: ").strip()
    if not issue:
        print("❌ Issue is required")
        return
    booking_db.create_job(
        user_id=user_id,
        mechanic_id=mechanic['id'],
        car_id=default_car['id'],
        issue=issue,
        estimated_cost=500  # Default estimated cost
    )
    print("\n✅ Mechanic booked successfully (INSTANT).")
    print("Mechanic will contact you shortly.")

def book_mechanic(user_id):
    top = _get_top_mechanics()
    if not top:
        print("❌ No approved mechanics found")
        return
    _print_queue_cards(top)
    mechanic = _select_mechanic(top)
    if not mechanic:
        return
    print("\nMechanic Selected:")
    print(f"Name: {mechanic.get('full_name','Unknown')}")
    print(f"Rating: {float(mechanic.get('rating') or 0):.1f}")
    print(f"Experience: {int(mechanic.get('experience') or 0)} years")
    print(f"Specialization: {mechanic.get('specialization','N/A')}")
    while True:
        choice = _booking_type_menu()
        if choice == "1":
            _instant_flow(user_id, mechanic)
            break
        elif choice == "2":
            _prebook_flow(user_id, mechanic)
            break
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice")

def _smart_search_mechanics():
    """Smart search for mechanics using issue description and location"""
    print("\n" + "="*60)
    print("🔍 SMART SEARCH - FIND MECHANICS BY ISSUE")
    print("="*60)
    
    # Get issue description
    issue = input("\n🔧 Describe your car issue: ").strip()
    if not issue:
        print("❌ Issue description is required")
        return None
    
    # Get location
    print("\n📍 Location options:")
    print("1. Enter location name (e.g., 'Asalpha Mumbai')")
    print("2. Enter GPS coordinates")
    print("3. Use current location (if available)")
    
    location_choice = input("\nSelect option: ").strip()
    
    location_data = {}
    
    if location_choice == "1":
        location_name = input("Enter location name: ").strip()
        if not location_name:
            print("❌ Location name cannot be empty")
            return None
        location_data["location_name"] = location_name
    
    elif location_choice == "2":
        try:
            latitude = float(input("Enter latitude: ").strip())
            longitude = float(input("Enter longitude: ").strip())
            location_data["latitude"] = latitude
            location_data["longitude"] = longitude
        except ValueError:
            print("❌ Invalid coordinates")
            return None
    
    elif location_choice == "3":
        # Use default location (could be enhanced with GPS)
        location_data["location_name"] = "Asalpha Mumbai"
        print("📍 Using default location: Asalpha Mumbai")
    
    else:
        print("❌ Invalid choice")
        return None
    
    # Get search radius
    try:
        radius = float(input("Enter search radius in km (default 5): ").strip() or "5")
    except ValueError:
        radius = 5.0
    
    print(f"\n🔍 Searching for mechanics...")
    print(f"Issue: {issue}")
    print(f"Location: {location_data}")
    print(f"Radius: {radius} km")
    
    try:
        # Use Smart Search Engine
        engine = SmartSearchEngine()
        request = SearchRequest(
            issue_description=issue,
            location_data=location_data,
            search_radius_km=radius,
            max_results=5
        )
        
        result = engine.search_nearby_mechanics(request)
        
        if not result.get("success"):
            print(f"❌ Search failed: {result.get('message', 'Unknown error')}")
            return None
        
        mechanics = result.get("mechanics", [])
        
        if not mechanics:
            print(f"\n📭 No mechanics found within {radius} km")
            print("💡 Try:")
            print("  • Increasing search radius")
            print("  • Checking different location")
            print("  • Using simpler issue description")
            return None
        
        # Display results
        print(f"\n🎯 Found {len(mechanics)} nearby mechanics:")
        print("="*50)
        
        for idx, mech in enumerate(mechanics, 1):
            print(f"\n[{idx}] 👨‍🔧 {mech.get('name', 'Unknown')}")
            print(f"⭐ Rating: {mech.get('rating', 0.0)}")
            print(f"💼 Experience: {mech.get('experience', 0)} years")
            print(f"🔧 Skills: {mech.get('skill', 'General')}")
            print(f"📏 Distance: {mech.get('distance_km', 0):.1f} km")
            print(f"⏱️ ETA: {mech.get('eta_minutes', 0)} minutes")
            print(f"📱 Phone: {mech.get('phone', 'Not available')}")
            print(f"🟢 Status: {mech.get('status', 'Unknown')}")
        
        print("\n----------------------------------------")
        
        # Select mechanic
        sel = input("\nSelect mechanic number: ").strip()
        
        if not sel.isdigit() or int(sel) < 1 or int(sel) > len(mechanics):
            print("❌ Invalid selection")
            return None
        
        selected_mechanic = mechanics[int(sel) - 1]
        
        # Convert to expected format
        mechanic_dict = {
            'id': selected_mechanic.get('mechanic_id'),
            'name': selected_mechanic.get('name'),
            'rating': selected_mechanic.get('rating', 0),
            'experience': selected_mechanic.get('experience', 0),
            'skills': selected_mechanic.get('skill'),
            'phone': selected_mechanic.get('phone'),
            'email': selected_mechanic.get('email'),
            'distance_km': selected_mechanic.get('distance_km'),
            'eta_minutes': selected_mechanic.get('eta_minutes')
        }
        
        print(f"\n✅ Selected: {selected_mechanic.get('name')}")
        print(f"📍 Distance: {selected_mechanic.get('distance_km', 0):.1f} km")
        print(f"⏱️ ETA: {selected_mechanic.get('eta_minutes', 0)} minutes")
        
        return mechanic_dict
        
    except Exception as e:
        print(f"❌ Smart search error: {e}")
        return None
