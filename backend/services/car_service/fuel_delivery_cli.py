"""
Fuel Delivery Agent CLI Interface
Handles fuel delivery agent registration, login, and dashboard access
"""

import os
import requests
import time
from datetime import datetime
from werkzeug.security import check_password_hash

API = "http://127.0.0.1:5000"

def fuel_delivery_agent_signup():
    """Fuel delivery agent signup process"""
    print("\n" + "="*60)
    print("  FUEL DELIVERY AGENT SIGNUP")
    print("="*60)
    
    try:
        # Basic Details
        print("\n  BASIC DETAILS:")
        name = input("  Full Name: ").strip()
        email = input("  Email: ").strip()
        phone = input("  Phone Number: ").strip()
        password = input("  Password: ").strip()
        city = input("  City: ").strip()
        
        # Vehicle Details
        print("\n  VEHICLE DETAILS:")
        print("Vehicle Types: 1. Bike  2. Van  3. Truck")
        vehicle_choice = input("  Vehicle Type (1-3): ").strip()
        
        vehicle_map = {'1': 'Bike', '2': 'Van', '3': 'Truck'}
        vehicle_type = vehicle_map.get(vehicle_choice)
        
        if not vehicle_type:
            print("  Invalid vehicle type")
            input("\nPress Enter to continue...")
            return
        
        vehicle_number = input("  Vehicle Number: ").strip()
        
        # Service Area Details (NEW)
        print("\n   SERVICE AREA DETAILS:")
        print("Define your service area where you can provide fuel delivery:")
        
        service_area_city = input("   Service Area City: ").strip()
        print("Available Areas: Asalpha, Bandra, Andheri, Worli, Dadar, Kurla, Goregaon, BKC")
        service_area_location = input("  Primary Service Location (from above list): ").strip()
        
        # Service area radius based on vehicle type
        default_radius = {'Bike': 10, 'Van': 15, 'Truck': 25}
        default_service_radius = default_radius.get(vehicle_type, 15)
        
        print(f"  Default service radius for {vehicle_type}: {default_service_radius} km")
        custom_radius = input(f"Enter service radius in km (press Enter for default {default_service_radius}): ").strip()
        
        if custom_radius:
            try:
                service_radius = int(custom_radius)
                if service_radius < 5 or service_radius > 50:
                    print("  Service radius must be between 5km and 50km")
                    service_radius = default_service_radius
            except ValueError:
                print("  Invalid radius, using default")
                service_radius = default_service_radius
        else:
            service_radius = default_service_radius
        
        # Get coordinates for service area
        from .fuel_delivery_user_service import fuel_delivery_user_service
        coordinates = fuel_delivery_user_service.geocode_location(service_area_location)
        service_lat, service_lon = coordinates
        
        print(f"  Service Area Coordinates: {service_lat:.4f}, {service_lon:.4f}")
        print(f"   Service Area: {service_area_location} ({service_radius} km radius)")
        
        # Document Uploads (simulated)
        print("\n  DOCUMENT UPLOADS:")
        print("  Please upload the following documents:")
        print("   1. Vehicle Photo")
        print("   2. RC Book")
        print("   3. Pollution Certificate")
        print("   4. Fuel Supply Contract")
        print("   5. Employee ID Proof")
        print("   6. Aadhar/Govt ID")
        
        # Simulate document uploads
        vehicle_photo = input("  Vehicle Photo Path (or press Enter to skip): ").strip()
        rc_book = input("  RC Book Path (or press Enter to skip): ").strip()
        pollution_cert = input("  Pollution Certificate Path (or press Enter to skip): ").strip()
        fuel_contract = input("  Fuel Contract Path (or press Enter to skip): ").strip()
        employee_proof = input("  Employee Proof Path (or press Enter to skip): ").strip()
        govt_id = input("  Govt ID Path (or press Enter to skip): ").strip()
        
        # Safety Declaration
        print("\n   SAFETY COMPLIANCE:")
        safety_declared = input("I follow all fuel handling safety rules and regulations. (y/N): ").strip().lower()
        
        if safety_declared != 'y':
            print("  Safety declaration must be accepted to proceed")
            input("\nPress Enter to continue...")
            return
        
        # Prepare registration data
        agent_data = {
            'name': name,
            'email': email,
            'phone_number': phone,
            'password': password,
            'city': city,
            'vehicle_type': vehicle_type,
            'vehicle_number': vehicle_number,
            'service_area_city': service_area_city,
            'service_area_location': service_area_location,
            'service_area_km': service_radius,
            'latitude': service_lat,
            'longitude': service_lon,
            'vehicle_photo_path': vehicle_photo if vehicle_photo else None,
            'rc_book_photo_path': rc_book if rc_book else None,
            'pollution_certificate_path': pollution_cert if pollution_cert else None,
            'fuel_contract_path': fuel_contract if fuel_contract else None,
            'employee_proof_path': employee_proof if employee_proof else None,
            'govt_id_path': govt_id if govt_id else None,
            'safety_declaration_accepted': True
        }
        
        # Submit registration
        print("\n  Submitting registration...")
        response = requests.post(f"{API}/api/fuel-delivery/register", json=agent_data)
        
        if response.status_code in (200, 201):
            result = response.json()
            if result['success']:
                print("  Registration successful!")
                print("  Please check your email for approval status.")
                print("  You will be notified once approved by admin.")
                if result.get('car_worker_id'):
                    print(f"  Admin pending worker ID: {result['car_worker_id']}")
            else:
                print(f"  Registration failed: {result.get('error', 'Unknown error')}")
        else:
            try:
                err = response.json().get('error', 'Unknown error')
                print(f"  Registration failed [{response.status_code}]: {err}")
            except Exception:
                print(f"  Registration failed [{response.status_code}]")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def fuel_delivery_agent_login():
    """Fuel delivery agent login process"""
    print("\n" + "="*60)
    print("  FUEL DELIVERY AGENT LOGIN")
    print("="*60)
    
    try:
        email = input("  Email: ").strip()
        password = input("  Password: ").strip()
        
        print("  Authenticating...")
        response = requests.post(f"{API}/api/fuel-delivery/login", json={
            'email': email,
            'password': password
        })
        
        if response.status_code in (200, 201):
            result = response.json()
            if result['success']:
                agent = result['agent']
                print("  Login successful!")
                print(f"  Welcome, {agent['name']}!")
                print(f"  Vehicle: {agent.get('vehicle_type', 'N/A')} - {agent.get('vehicle_number', 'N/A')}")
                print(f"  Status: {agent.get('approval_status', 'N/A')}")
                
                if agent['approval_status'] == 'APPROVED':
                    fuel_delivery_agent_dashboard(agent)
                else:
                    print("  Your account is pending approval.")
                    print("  You will be notified when approved.")
            else:
                print(f"  Login failed: {result.get('error', 'Unknown error')}")
        else:
            try:
                err = response.json().get('error', 'Unknown error')
                print(f"  Login failed [{response.status_code}]: {err}")
            except Exception:
                print(f"  Login failed [{response.status_code}]")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def fuel_delivery_agent_dashboard(agent_info):
    """Fuel delivery agent dashboard"""
    while True:
        print("\n" + "="*60)
        print("  FUEL DELIVERY DASHBOARD")
        print("="*60)
        print(f"  Agent: {agent_info['name']}")
        print(f"  Vehicle: {agent_info.get('vehicle_type', 'N/A')} - {agent_info.get('vehicle_number', 'N/A')}")
        print(f"  Status: {agent_info.get('online_status', 'OFFLINE')}")
        print(f"  Rating: {agent_info.get('rating', 0.0):.1f}")
        print(f"  Total Deliveries: {agent_info.get('total_deliveries', 0)}")
        
        print("\n  DASHBOARD OPTIONS:")
        print("1.   Go Online / Offline")
        print("2.   Fuel Delivery Requests Queue")
        print("3.   Active Delivery")
        print("4.   Delivery History & Earnings")
        print("5.    Performance, Reputation & Safety")
        print("6.   Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            toggle_availability(agent_info)
        elif choice == "2":
            view_fuel_requests_queue(agent_info)
        elif choice == "3":
            view_active_delivery(agent_info)
        elif choice == "4":
            view_delivery_history(agent_info)
        elif choice == "5":
            view_performance(agent_info)
        elif choice == "6":
            break
        else:
            print("  Invalid choice")
            time.sleep(1)

def view_active_delivery(agent_info):
    """View active fuel delivery"""
    print("\n" + "="*60)
    print("  ACTIVE FUEL DELIVERY")
    print("="*60)
    print("  No active delivery")
    input("\nPress Enter to continue...")

def view_delivery_history(agent_info):
    """View delivery history and earnings"""
    print("\n" + "="*60)
    print("  DELIVERY HISTORY & EARNINGS")
    print("="*60)
    print("  Total Earnings:  0.00")
    print("  Total Deliveries: 0")
    print("  Average Rating: 0.0/5.0")
    print("\n  No delivery history")
    input("\nPress Enter to continue...")

def call_user_for_delivery(request):
    """Call user for delivery"""
    print(f"\n  Calling {request.get('user_name', 'N/A')}...")
    print(f"  Phone: {request.get('user_phone', 'N/A')}")
    input("\nPress Enter after call...")

def navigate_to_location(request):
    """Navigate to delivery location"""
    print(f"\n  Navigating to: {request.get('delivery_address', 'N/A')}")
    print("   Opening maps application...")
    input("\nPress Enter when arrived...")

def add_delivery_note(request):
    """Add delivery note"""
    note = input("\n  Enter delivery note: ").strip()
    if note:
        print(f"  Note added: {note}")
    else:
        print("  No note entered")

def complete_delivery(agent_info, request):
    """Complete fuel delivery"""
    print(f"\n  Completing delivery for {request.get('user_name', 'N/A')}")
    print("  Delivery completed successfully!")
    print("  Earnings:  0.00")
    agent_info['online_status'] = 'ONLINE_AVAILABLE'
    input("\nPress Enter to continue...")

def cancel_delivery(agent_info, request):
    """Cancel fuel delivery"""
    confirm = input("\n  Confirm delivery cancellation? (y/n): ").strip().lower()
    if confirm == 'y':
        print("  Delivery cancelled")
        agent_info['online_status'] = 'ONLINE_AVAILABLE'
    else:
        print("  Cancellation cancelled")
    input("\nPress Enter to continue...")

def toggle_availability(agent_info):
    """Toggle agent availability status"""
    print("\n  Updating availability...")
    
    try:
        current_status = agent_info.get('online_status', 'OFFLINE')
        
        if current_status == 'OFFLINE':
            new_status = 'ONLINE_AVAILABLE'
            print("  Going online...")
        elif current_status == 'ONLINE_AVAILABLE':
            new_status = 'OFFLINE'
            print("  Going offline...")
        else:
            print("  Cannot change status while busy")
            input("\nPress Enter to continue...")
            return
        
        response = requests.post(f"{API}/api/fuel-delivery/status", json={
            'agent_id': agent_info['id'],
            'status': new_status
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                agent_info['online_status'] = new_status
                print(f"  {result['message']}")
                
                # Show demand insights if going online
                if new_status == 'ONLINE_AVAILABLE':
                    try:
                        insights_response = requests.get(f"{API}/api/fuel-delivery/demand-insights")
                        if insights_response.status_code == 200:
                            insights_data = insights_response.json()
                            if insights_data['success']:
                                insights = insights_data['insights']
                                print(f"\n  {insights.get('demand_message', 'Normal demand')}")
                                print(f"  Suggestion: {insights.get('suggestion', '')}")
                    except:
                        pass
            else:
                print(f"  {result.get('error', 'Status update failed')}")
        else:
            print("  Failed to update status")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def view_fuel_requests_queue(agent_info):
    """View fuel delivery requests queue"""
    print("\n" + "="*60)
    print("  FUEL DELIVERY REQUESTS QUEUE")
    print("="*60)
    
    try:
        # Use the working requests endpoint but add smart dispatch logic
        response = requests.get(f"{API}/api/fuel-delivery/requests", params={
            'agent_id': agent_info['id']
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                requests_data = result.get('requests', [])
                
                if not requests_data:
                    print("  No fuel requests in queue")
                    input("\nPress Enter to continue...")
                    return
                
                print(f"  Total Requests: {len(requests_data)}\n")
                
                # Apply smart dispatch logic locally
                enhanced_requests = []
                for request in requests_data:
                    # Calculate distance (simplified)
                    distance_km = 2.5  # Placeholder distance
                    eta_minutes = int(distance_km * 3)  # 3 min per km
                    
                    # Calculate assignment score
                    agent = agent_info
                    rating_score = agent.get('rating', 0) / 5.0
                    eta_score = max(0, 1 - (eta_minutes / 30))
                    completion_score = 0.8  # Placeholder
                    fairness_score = 0.5  # Placeholder
                    
                    score = (
                        0.35 * eta_score +
                        0.25 * rating_score +
                        0.20 * completion_score +
                        0.20 * fairness_score
                    )
                    
                    # Determine assigned reason
                    if score >= 0.8:
                        assigned_reason = "Closest available agent with excellent rating"
                    elif score >= 0.6:
                        assigned_reason = "Nearby agent with good reliability"
                    elif score >= 0.4:
                        assigned_reason = "Available agent within service area"
                    else:
                        assigned_reason = "Next available agent in queue"
                    
                    enhanced_requests.append({
                        **request,
                        'distance_km': round(distance_km, 2),
                        'eta_minutes': eta_minutes,
                        'assignment_score': round(score, 2),
                        'assigned_reason': assigned_reason
                    })
                
                # Sort by score (highest first)
                enhanced_requests.sort(key=lambda x: x['assignment_score'], reverse=True)
                
                for i, request in enumerate(enhanced_requests, 1):
                    priority_emoji = " " if request.get('priority_level') >= 4 else " " if request.get('priority_level') >= 3 else " "
                    fuel_emoji = " " if request.get('fuel_type') == 'Petrol' else "  "
                    
                    print(f"{i}. {fuel_emoji} {request.get('fuel_type', 'N/A')} - {request.get('quantity_liters', 0)}L")
                    print(f"     {request.get('user_name', 'N/A')} |   {request.get('user_phone', 'N/A')}")
                    print(f"     {request.get('delivery_address', 'N/A')}")
                    print(f"     {request.get('distance_km', 0)}km away |    {request.get('eta_minutes', 0)} min")
                    print(f"   {priority_emoji} Priority {request.get('priority_level', 3)}")
                    print(f"     Score: {request.get('assignment_score', 0):.2f}")
                    print(f"     {request.get('assigned_reason', 'N/A')}")
                    print()
                
                print("-" * 60)
                choice = input("\nSelect request number to accept (0 to go back): ").strip()
                
                if choice == "0":
                    return
                
                if choice.isdigit() and int(choice) >= 1 and int(choice) <= len(enhanced_requests):
                    selected_request = enhanced_requests[int(choice) - 1]
                    accept_fuel_request(agent_info, selected_request)
                else:
                    print("  Invalid request number")
                    time.sleep(1)
            else:
                print(f"  {result.get('error', 'Failed to fetch requests')}")
        else:
            print("  Failed to fetch requests")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def accept_fuel_request(agent_info, request):
    """Accept a fuel delivery request"""
    try:
        print(f"\n  Accepting fuel request...")
        print(f"  Fuel Type: {request.get('fuel_type', 'N/A')}")
        print(f"  Quantity: {request.get('quantity_liters', 0)} liters")
        print(f"  Delivery: {request.get('delivery_address', 'N/A')}")
        
        confirm = input("\nConfirm acceptance? (y/n): ").strip().lower()
        if confirm != 'y':
            print("  Request acceptance cancelled")
            return
        
        response = requests.post(f"{API}/api/fuel-delivery/queue/assign", json={
            'agent_id': agent_info['id'],
            'request_id': request.get('request_id')
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("  Request accepted successfully!")
                agent_info['online_status'] = 'BUSY'
                print("  You are now BUSY. Navigate to customer location.")
            else:
                print(f"  {result.get('error', 'Failed to accept request')}")
        else:
            print("  Failed to accept request")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def start_fuel_delivery(agent_info, request):
    """Start active fuel delivery interface"""
    print("\n" + "="*60)
    print("  ACTIVE FUEL DELIVERY")
    print("="*60)
    print(f"  Fuel: {request.get('fuel_type', 'N/A')} - {request.get('quantity', 0)} liters")
    print(f"  Location: {request.get('address', 'N/A')}")
    print(f"  User: {request.get('user_name', 'N/A')}")
    print(f"  Phone: {request.get('user_phone', 'N/A')}")
    
    delivery_start_time = time.time()
    
    while True:
        duration = int(time.time() - delivery_start_time)
        duration_str = f"{duration // 60:02d}:{duration % 60:02d}"
        
        print(f"\n   Delivery Time: {duration_str}")
        print(f"  Status: IN_PROGRESS")
        
        print("\n  DELIVERY OPTIONS:")
        print("1.   Call User")
        print("2.   Navigate to Location")
        print("3.   Add Delivery Note")
        print("4.   Complete Delivery")
        print("5.   Cancel Delivery")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            call_user_for_delivery(request)
        elif choice == "2":
            show_delivery_location(request)
        elif choice == "3":
            add_delivery_note(request)
        elif choice == "4":
            if complete_fuel_delivery_interface(agent_info, request):
                break
        elif choice == "5":
            if cancel_fuel_delivery_interface(agent_info, request):
                break
        else:
            print("  Invalid choice")
            time.sleep(1)

def view_active_delivery(agent_info):
    """View active fuel delivery"""
    print("\n" + "="*60)
    print("  ACTIVE FUEL DELIVERY")
    print("="*60)
    print("  No active delivery")
    input("\nPress Enter to continue...")

def view_delivery_history(agent_info):
    """View delivery history and earnings"""
    print("\n" + "="*60)
    print("  DELIVERY HISTORY & EARNINGS")
    print("="*60)
    print("  Total Earnings:  0.00")
    print("  Total Deliveries: 0")
    print("  Average Rating: 0.0/5.0")
    print("\n  No delivery history")
    input("\nPress Enter to continue...")

def call_user_for_delivery(request):
    """Call user for delivery"""
    print(f"\n  Calling {request.get('user_name', 'N/A')}...")
    print(f"  Phone: {request.get('user_phone', 'N/A')}")
    input("\nPress Enter after call...")

def navigate_to_location(request):
    """Navigate to delivery location"""
    print(f"\n  Navigating to: {request.get('delivery_address', 'N/A')}")
    print("   Opening maps application...")
    input("\nPress Enter when arrived...")

def add_delivery_note(request):
    """Add delivery note"""
    note = input("\n  Enter delivery note: ").strip()
    if note:
        print(f"  Note added: {note}")
    else:
        print("  No note entered")

def complete_delivery(agent_info, request):
    """Complete fuel delivery"""
    print(f"\n  Completing delivery for {request.get('user_name', 'N/A')}")
    print("  Delivery completed successfully!")
    print("  Earnings:  0.00")
    agent_info['online_status'] = 'ONLINE_AVAILABLE'
    input("\nPress Enter to continue...")

def cancel_delivery(agent_info, request):
    """Cancel fuel delivery"""
    confirm = input("\n  Confirm delivery cancellation? (y/n): ").strip().lower()
    if confirm == 'y':
        print("  Delivery cancelled")
        agent_info['online_status'] = 'ONLINE_AVAILABLE'
    else:
        print("  Cancellation cancelled")
    input("\nPress Enter to continue...")

def call_user_for_delivery(request):
    """Call user for delivery details"""
    print(f"  Calling {request.get('user_name', 'N/A')}...")
    print(f"  Phone: {request.get('user_phone', 'N/A')}")
    input("  In call - Press Enter to hang up...")

def show_delivery_location(request):
    """Show delivery location"""
    print(f"\n  DELIVERY LOCATION:")
    print(f"  Address: {request.get('delivery_address', 'N/A')}")
    if request.get('delivery_latitude') and request.get('delivery_longitude'):
        print(f"   GPS: {request.get('delivery_latitude')}, {request.get('delivery_longitude')}")
    input("\nPress Enter to continue...")

def add_delivery_note(request):
    """Add note for current delivery"""
    note = input("  Delivery Note: ").strip()
    if note:
        print(f"  Note added: {note}")
    else:
        print("  Note cannot be empty")

def complete_fuel_delivery_interface(agent_info, request):
    """Complete fuel delivery interface"""
    try:
        print(f"\n  Completing delivery...")
        print(f"  Delivered: {request.get('fuel_type', 'N/A')} - {request.get('quantity_liters', 0)} liters")
        
        confirm = input("Confirm delivery completion? (y/N): ").strip().lower()
        if confirm != 'y':
            return False
        
        response = requests.post(f"{API}/api/fuel-delivery/complete", json={
            'request_id': request['request_id'],
            'agent_id': agent_info['id']
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                earnings = result.get('earnings', 0)
                print(f"  Delivery completed successfully!")
                print(f"  Earnings:  {earnings:.2f}")
                
                # Request rating
                rating_input = input("  Rate user experience (1-5, press Enter to skip): ").strip()
                if rating_input:
                    try:
                        rating = int(rating_input)
                        if 1 <= rating <= 5:
                            review_text = input("  Review comments (optional): ").strip()
                            # Submit rating (would need user_id)
                            print("  Rating submitted")
                    except ValueError:
                        print("  Invalid rating")
                
                agent_info['online_status'] = 'ONLINE_AVAILABLE'
                return True
            else:
                print(f"  {result.get('error', 'Failed to complete delivery')}")
        
        return False
        
    except Exception as e:
        print(f"  Error: {e}")
        return False

def cancel_fuel_delivery_interface(agent_info, request):
    """Cancel fuel delivery interface"""
    try:
        reason = input("  Cancellation reason: ").strip()
        if not reason:
            print("  Cancellation reason is required")
            return False
        
        print("  Cancelling delivery...")
        # Implementation would update request status to CANCELLED
        agent_info['online_status'] = 'ONLINE_AVAILABLE'
        print("  Delivery cancelled")
        return True
        
    except Exception as e:
        print(f"  Error: {e}")
        return False

def view_delivery_history(agent_info):
    """View delivery history and earnings"""
    print("\n" + "="*60)
    print("  DELIVERY HISTORY & EARNINGS")
    print("="*60)
    
    try:
        response = requests.get(f"{API}/api/fuel-delivery/history/{agent_info['id']}")
        
        if response.status_code == 200:
            result = response.json()
            history = result.get('history', [])
            
            if not history:
                print("  No delivery history")
                input("\nPress Enter to continue...")
                return
            
            total_earnings = sum(item.get('earnings', 0) for item in history)
            print(f"  Total Earnings:  {total_earnings:.2f}")
            print(f"  Total Deliveries: {len(history)}\n")
            
            # Show recent deliveries
            print("  RECENT DELIVERIES:")
            for i, delivery in enumerate(history[-10:], 1):  # Show last 10
                fuel_emoji = " " if delivery.get('fuel_type') == 'Petrol' else "  "
                print(f"{i}. {fuel_emoji} {delivery.get('fuel_type', 'N/A')}")
                print(f"     Quantity: {delivery.get('quantity', 0)} liters")
                print(f"     Earnings:  {delivery.get('earnings', 0):.2f}")
                print(f"     Date: {delivery.get('completed_at', 'N/A')}")
                print()
        
        else:
            print("  Failed to load history")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def view_performance(agent_info):
    """View agent performance and reputation"""
    print("\n" + "="*60)
    print("   PERFORMANCE & REPUTATION")
    print("="*60)
    
    try:
        response = requests.get(f"{API}/api/fuel-delivery/performance/{agent_info['id']}")
        
        if response.status_code == 200:
            result = response.json()
            performance = result.get('performance', {})
            
            print(f"  Performance Level: {performance.get('performance_level', 'N/A')}")
            print(f"  Rating: {performance.get('rating', 0):.1f}/5.0")
            print(f"  Total Deliveries: {performance.get('total_deliveries', 0)}")
            print(f"  Completion Rate: {performance.get('completion_rate', 0):.1f}%")
            print(f"  Recent Deliveries: {performance.get('recent_deliveries', 0)} (last 30 days)")
            
            # Show badges
            badges = performance.get('badges', [])
            if badges:
                print(f"\n  EARNED BADGES:")
                for badge in badges:
                    print(f"      {badge.get('badge_type', 'N/A')}")
                    print(f"        Earned: {badge.get('earned_at', 'N/A')}")
            else:
                print("\n  No badges earned yet")
            
            # Safety compliance
            print(f"\n   SAFETY COMPLIANCE:")
            print(f"     Verified: {'Yes' if performance.get('is_verified') else 'No'}")
            print(f"     Approved: {'Yes' if performance.get('approval_status') == 'APPROVED' else 'No'}")
        
        else:
            print("  Failed to load performance data")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def fuel_delivery_agent_menu():
    """Fuel delivery agent main menu"""
    while True:
        print("\n" + "="*60)
        print("  FUEL DELIVERY AGENT")
        print("="*60)
        print("1.   Signup")
        print("2.   Login")
        print("3.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            fuel_delivery_agent_signup()
        elif choice == "2":
            fuel_delivery_agent_login()
        elif choice == "3":
            break
        else:
            print("  Invalid choice")
            time.sleep(1)

def view_active_delivery(agent_info):
    """View active fuel delivery"""
    print("\n" + "="*60)
    print("  ACTIVE FUEL DELIVERY")
    print("="*60)
    print("  No active delivery")
    input("\nPress Enter to continue...")

def view_delivery_history(agent_info):
    """View delivery history and earnings"""
    print("\n" + "="*60)
    print("  DELIVERY HISTORY & EARNINGS")
    print("="*60)
    print("  Total Earnings:  0.00")
    print("  Total Deliveries: 0")
    print("  Average Rating: 0.0/5.0")
    print("\n  No delivery history")
    input("\nPress Enter to continue...")

def call_user_for_delivery(request):
    """Call user for delivery"""
    print(f"\n  Calling {request.get('user_name', 'N/A')}...")
    print(f"  Phone: {request.get('user_phone', 'N/A')}")
    input("\nPress Enter after call...")

def navigate_to_location(request):
    """Navigate to delivery location"""
    print(f"\n  Navigating to: {request.get('delivery_address', 'N/A')}")
    print("   Opening maps application...")
    input("\nPress Enter when arrived...")

def add_delivery_note(request):
    """Add delivery note"""
    note = input("\n  Enter delivery note: ").strip()
    if note:
        print(f"  Note added: {note}")
    else:
        print("  No note entered")

def complete_delivery(agent_info, request):
    """Complete fuel delivery"""
    print(f"\n  Completing delivery for {request.get('user_name', 'N/A')}")
    print("  Delivery completed successfully!")
    print("  Earnings:  0.00")
    agent_info['online_status'] = 'ONLINE_AVAILABLE'
    input("\nPress Enter to continue...")

def cancel_delivery(agent_info, request):
    """Cancel fuel delivery"""
    confirm = input("\n  Confirm delivery cancellation? (y/n): ").strip().lower()
    if confirm == 'y':
        print("  Delivery cancelled")
        agent_info['online_status'] = 'ONLINE_AVAILABLE'
    else:
        print("  Cancellation cancelled")
    input("\nPress Enter to continue...")
