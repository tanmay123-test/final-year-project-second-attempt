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
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("  Registration successful!")
                print("  Please check your email for approval status.")
                print("  You will be notified once approved by admin.")
            else:
                print(f"  Registration failed: {result.get('error', 'Unknown error')}")
        else:
            print("  Failed to connect to server")
        
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
        
        if response.status_code == 200:
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
            print("  Failed to connect to server")
        
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
            toggle_online_status(agent_info)
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
    """View active delivery for agent"""
    print("\n" + "="*60)
    print("  ACTIVE DELIVERY DASHBOARD")
    print("="*60)
    
    try:
        # Get agent's busy status or current requests
        # In a real app, this would fetch from an API like /api/fuel-delivery/agents/active-job
        # For this CLI simulation, we'll try to find any request assigned to this agent
        response = requests.get(f"{API}/api/fuel-delivery/requests")
        if response.status_code == 200:
            result = response.json()
            requests_queue = result.get('requests', [])
            
            # Since the /requests endpoint usually only shows WAITING_QUEUE, 
            # we need a way to find the current ASSIGNED/IN_PROGRESS job.
            # Let's assume there's an endpoint for this or we'll search locally if possible.
            # For now, we'll try to fetch status by looking at the last known request.
            print("  Searching for active jobs...")
            # Ideally: response = requests.get(f"{API}/api/fuel-delivery/agents/active-job/{agent_info['id']}")
            
            # Let's check if the agent is actually BUSY
            if agent_info.get('online_status') != 'BUSY':
                print("  You don't have any active delivery at the moment")
                input("\nPress Enter to continue...")
                return

            print("  You have an active delivery!")
            print("   NOTE: You must enter the OTP from the user to START the job.")
            print("   Once delivered, mark it as COMPLETED to receive earnings.")
            
            # Since we don't have a direct "get active job" endpoint yet, 
            # we'll ask the user to select the job from history or just track it.
            # In a real scenario, the 'request' object would be passed from 'accept_fuel_request'.
            print("\n  Use option 2 (Queue) to accept a job first.")
            print("  Once accepted, the job interface will start automatically.")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def toggle_online_status(agent_info):
    """Toggle agent online status"""
    try:
        current_status = agent_info.get('online_status', 'OFFLINE')
        
        if current_status == 'OFFLINE':
            print("  Going online...")
            new_status = 'ONLINE_AVAILABLE'
        elif current_status == 'ONLINE_AVAILABLE':
            print("  Going offline...")
            new_status = 'OFFLINE'
        elif current_status == 'BUSY':
            print("   You are currently busy with a delivery")
            input("\nPress Enter to continue...")
            return
        else:
            new_status = 'ONLINE_AVAILABLE'
        
        response = requests.post(f"{API}/api/fuel-delivery/status", json={
            'agent_id': agent_info['id'],
            'status': new_status
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                agent_info['online_status'] = new_status
                print(f"  {result['message']}")
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
        response = requests.get(f"{API}/api/fuel-delivery/requests")
        
        if response.status_code == 200:
            result = response.json()
            requests = result.get('requests', [])
            
            if not requests:
                print("  No fuel requests in queue")
                input("\nPress Enter to continue...")
                return
            
            print(f"  Total Requests: {len(requests)}\n")
            
            for i, request in enumerate(requests, 1):
                priority_emoji = " " if request.get('priority_level') >= 4 else " " if request.get('priority_level') >= 3 else " "
                fuel_emoji = " " if request.get('fuel_type') == 'Petrol' else "  "
                
                print(f"{i}. {fuel_emoji} {request.get('fuel_type', 'N/A')}")
                print(f"     Quantity: {request.get('quantity', 0)} liters")
                print(f"     Location: {request.get('address', 'N/A')}")
                print(f"     Priority: {priority_emoji} Level {request.get('priority_level', 1)}")
                print(f"     User: {request.get('user_name', 'N/A')}")
                print(f"     Contact: {request.get('user_phone', 'N/A')}")
                print(f"     Created: {request.get('created_at', 'N/A')}")
                print()
            
            # Accept request option
            try:
                choice = input("Enter request number to accept (0 to cancel): ").strip()
                if choice == "0":
                    return
                
                selected_idx = int(choice) - 1
                if 0 <= selected_idx < len(requests):
                    selected_request = requests[selected_idx]
                    accept_fuel_request(agent_info, selected_request)
                else:
                    print("  Invalid request number")
                    
            except ValueError:
                print("  Invalid input")
        
        else:
            print("  Failed to load requests")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def accept_fuel_request(agent_info, request):
    """Accept a fuel delivery request"""
    try:
        print(f"\n  Accepting fuel request...")
        print(f"  Fuel Type: {request.get('fuel_type', 'N/A')}")
        print(f"  Quantity: {request.get('quantity', 0)} liters")
        print(f"  Delivery: {request.get('address', 'N/A')}")
        
        confirm = input("Accept this request? (y/N): ").strip().lower()
        if confirm != 'y':
            return
        
        response = requests.post(f"{API}/api/fuel-delivery/requests/accept", json={
            'request_id': request['id'],
            'agent_id': agent_info['id']
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("  Request accepted successfully!")
                print("  Navigate to delivery location")
                print("  Contact user if needed")
                agent_info['online_status'] = 'BUSY'
                
                # Start delivery interface
                start_fuel_delivery(agent_info, request)
            else:
                print(f"  {result.get('error', 'Failed to accept request')}")
        else:
            print("  Failed to accept request")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def start_fuel_delivery(agent_info, request):
    """Start active fuel delivery interface with OTP verification"""
    print("\n" + "="*60)
    print("  ACTIVE FUEL DELIVERY")
    print("="*60)
    print(f"  Fuel: {request.get('fuel_type', 'N/A')} - {request.get('quantity', 0)} liters")
    print(f"  Location: {request.get('address', 'N/A')}")
    print(f"  User: {request.get('user_name', 'N/A')}")
    print(f"  Phone: {request.get('user_phone', 'N/A')}")
    
    # Require OTP before starting the job
    while True:
        otp = input("\n  Enter 4-digit OTP from user to START delivery: ").strip()
        if not otp:
            print("  OTP is required to start the job")
            continue
            
        response = requests.post(f"{API}/api/fuel-delivery/requests/start", json={
            'request_id': request['id'],
            'agent_id': agent_info['id'],
            'otp': otp
        })
        
        if response.status_code == 200:
            print("  OTP Verified! Delivery started.")
            break
        else:
            try:
                error = response.json().get('error', 'Invalid OTP')
            except:
                error = "Invalid OTP"
            print(f"  {error}. Please try again.")
            retry = input("Try again? (y/N): ").strip().lower()
            if retry != 'y':
                return
    
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

def call_user_for_delivery(request):
    """Call user for delivery details"""
    print(f"  Calling {request.get('user_name', 'N/A')}...")
    print(f"  Phone: {request.get('user_phone', 'N/A')}")
    input("  In call - Press Enter to hang up...")

def show_delivery_location(request):
    """Show delivery location"""
    print(f"\n  DELIVERY LOCATION:")
    print(f"  Address: {request.get('address', 'N/A')}")
    if request.get('latitude') and request.get('longitude'):
        print(f"   GPS: {request.get('latitude')}, {request.get('longitude')}")
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
        print(f"  Delivered: {request.get('fuel_type', 'N/A')} - {request.get('quantity', 0)} liters")
        
        confirm = input("Confirm delivery completion? (y/N): ").strip().lower()
        if confirm != 'y':
            return False
        
        response = requests.post(f"{API}/api/fuel-delivery/requests/complete", json={
            'request_id': request['id']
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
