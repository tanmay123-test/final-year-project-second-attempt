"""
Tow Truck Driver CLI Integration
Complete CLI interface for tow truck driver management system
"""

import requests
import os
from datetime import datetime
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API = "http://127.0.0.1:5001"
TOKEN = None
TOW_DRIVER_ID = None

def get_headers():
    """Get authenticated headers for API requests"""
    return {"Authorization": f"Bearer {TOKEN}"}

def make_tow_api_request(method, endpoint, data=None, params=None):
    """Make authenticated API request for tow truck driver"""
    url = f"{API}{endpoint}"
    
    # Only add headers if TOKEN is set
    headers = get_headers() if TOKEN else {}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        
        return response
    except Exception as e:
        print(f"❌ Tow API request failed: {e}")
        return None

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_tow_header(title):
    """Print formatted header for tow truck driver"""
    clear_screen()
    print(f"\n🚛 {title}")
    print("=" * 50)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_tow_info(message):
    """Print tow-specific info message"""
    print(f"🚛 {message}")

# ==================== ONLINE STATUS & EMERGENCY ZONE ====================

def toggle_tow_driver_online_status():
    """Toggle tow driver online/offline status"""
    print_tow_header("GO ONLINE / OFFLINE")
    
    response = make_tow_api_request("POST", "/api/car/tow-driver/toggle-online")
    
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Status updated to {data['new_status']}")
        print_info(f"Priority Score: {data['priority_score']}")
    else:
        print_error("Failed to update status")
    
    input("\nPress Enter to continue...")

def show_emergency_zone_status():
    """Show comprehensive emergency zone status"""
    print_tow_header("EMERGENCY ZONE STATUS")
    
    response = make_tow_api_request("GET", "/api/car/tow-driver/status")
    
    if response and response.status_code == 200:
        data = response.json()
        
        print(f"🟢 Current Status: {data['current_status']}")
        print(f"🚨 Emergency Demand: {data['emergency_demand_level']}")
        print(f"👥 Online Drivers: {data['online_drivers']}")
        print(f"🎯 Priority Score: {data['priority_score']}")
        print(f"💰 Potential Earnings Today: ₹{data['potential_earnings_today']:.2f}")
        print(f"⚖️ Fairness Score: {data['fairness_score']}/100")
        print(f"📍 High Incident Zone: {data['high_incident_zone']}")
        print(f"🚚 Truck Type: {data['truck_type']}")
        
        if data.get('heavy_vehicle_alert', 0) > 0:
            print_warning(f"⚠️ HEAVY VEHICLE ALERT: {data['heavy_vehicle_alert']} pending")
        
        if data.get('surge_pricing_active'):
            print_warning("⚠️ SURGE PRICING ACTIVE: Higher earnings available!")
        
        print(f"\n📈 Risk Demand Analysis:")
        for risk in data['risk_demand']:
            print(f"  • {risk['risk_level']}: {risk['pending_count']} pending requests")
            print(f"    Avg Price: ₹{risk['avg_min_price']:.2f} - ₹{risk['avg_max_price']:.2f}")
            print(f"    Avg Distance: {risk['avg_distance']:.1f} km")
        
        print(f"\n💰 Risk Bonus Multiplier: {data['risk_bonus_multiplier']}x")
    else:
        print_error("Failed to get emergency zone status")
    
    input("\nPress Enter to continue...")

def update_tow_driver_location():
    """Update tow driver location"""
    print_tow_header("UPDATE LOCATION")
    
    print("📍 Enter your current location:")
    print("Options:")
    print("1. 🏠 Use GPS Coordinates (lat/lng)")
    print("2. 🏢 Enter Area/Landmark")
    print("3. ⬅️ Back")
    
    choice = input("\nSelect location method: ").strip()
    
    if choice == "3":
        return
    elif choice == "1":
        # GPS coordinate input
        try:
            lat = input("📍 Enter latitude: ").strip()
            lng = input("📍 Enter longitude: ").strip()
            
            if not lat or not lng:
                print_error("Location coordinates required")
                input("\nPress Enter to continue...")
                return
            
            lat = float(lat)
            lng = float(lng)
            
            response = make_tow_api_request("POST", "/api/car/tow-driver/update-location", {
                "latitude": lat,
                "longitude": lng
            })
            
            if response and response.status_code == 200:
                print_success("Location updated successfully")
            else:
                print_error("Failed to update location")
        
        except Exception as e:
            print_error(f"Location update failed: {e}")
    
    elif choice == "2":
        # Area/landmark input
        area = input("🏢 Enter your area/landmark (e.g., Bandra, Dadar, Andheri): ").strip()
        
        if not area:
            print_error("Area/landmark is required")
            input("\nPress Enter to continue...")
            return
        
        # Convert area to approximate coordinates (simplified)
        area_coordinates = {
            "bandra": (19.0760, 72.8777),
            "dadar": (19.2183, 72.9784),
            "andheri": (19.1135, 72.8697),
            "powai": (18.6298, 73.0187),
            "kurla": (19.0728, 72.8826),
            "thane": (19.2183, 72.9781),
            "borival": (19.1833, 72.8357),
            "vashi": (19.0760, 73.0999)
        }
        
        lat, lng = area_coordinates.get(area.lower(), (19.0760, 72.8777))  # Default to Mumbai coordinates
        
        response = make_tow_api_request("POST", "/api/car/tow-driver/update-location", {
            "latitude": lat,
            "longitude": lng,
            "area": area
        })
        
        if response and response.status_code == 200:
            print_success(f"Location set to {area}")
            print_info(f"Coordinates: {lat}, {lng}")
        else:
            print_error("Failed to update location")
    
    else:
        print_warning("Invalid choice")
    
    input("\nPress Enter to continue...")

def update_tow_driver_truck_type():
    """Update tow driver truck type"""
    print_tow_header("UPDATE TRUCK TYPE")
    
    print("🚚 Select your truck type:")
    print("1. 🛗 FLATBED (All vehicles)")
    print("2. 🔧 WHEEL_LIFT (Cars/Motorcycles)")
    print("3. 🚛 HEAVY_DUTY (Trucks/Buses)")
    print("4. ⬅️ Back")
    
    choice = input("\nSelect truck type: ").strip()
    
    truck_types = {
        "1": "FLATBED",
        "2": "WHEEL_LIFT",
        "3": "HEAVY_DUTY"
    }
    
    if choice == "4":
        return
    elif choice not in truck_types:
        print_warning("Invalid choice")
        input("\nPress Enter to continue...")
        return
    
    truck_type = truck_types[choice]
    
    response = make_tow_api_request("POST", "/api/car/tow-driver/update-truck-type", {
        "truck_type": truck_type
    })
    
    if response and response.status_code == 200:
        print_success(f"Truck type updated to {truck_type}")
    else:
        print_error("Failed to update truck type")
    
    input("\nPress Enter to continue...")

# ==================== EMERGENCY TOW REQUESTS ====================

def show_emergency_tow_requests():
    """Show emergency tow requests"""
    print_tow_header("EMERGENCY TOW REQUESTS")
    
    response = make_tow_api_request("GET", "/api/car/tow-driver/emergency-requests")
    
    if response and response.status_code == 200:
        data = response.json()
        requests = data['requests']
        
        if not requests:
            print_info("No emergency tow requests available")
        else:
            print(f"📋 Total Requests: {data['total_requests']}")
            print(f"🟢 Your Status: {data['driver_status']}")
            print(f"🚚 Your Truck: {data['truck_type']}")
            print("\n" + "=" * 80)
            
            for i, request in enumerate(requests[:10], 1):  # Show top 10
                print(f"\n🔹 EMERGENCY REQUEST #{i}")
                print(f"🚗 Vehicle Type: {request['vehicle_type']}")
                print(f"⚠️ Issue: {request['issue_type']}")
                print(f"📍 Pickup Distance: {request['pickup_distance_km']} km")
                print(f"📍 Drop Distance: {request['distance_km']} km")
                print(f"💰 Earnings: ₹{request['estimated_price_min']:.2f} - ₹{request['estimated_price_max']:.2f}")
                print(f"⏱️ Duration: {request['estimated_duration']} minutes")
                print(f"⚠️ Risk Level: {request['risk_level']}")
                print(f"⭐ Urgency: {request['urgency_level']}/10")
                print(f"💎 Risk Bonus: ₹{request['risk_bonus']:.2f}")
                print(f"📊 Total Earning: ₹{request['estimated_total_earning']:.2f}")
                print(f"🚚 Truck Compatible: {'✅' if request['truck_compatibility'] else '❌'}")
                print(f"📋 Assignment: {request['assignment_reason']}")
                print(f"⭐ Customer Rating: {request['customer_rating']}/5")
                print(f"🛣️ Route Efficiency: {request['route_efficiency']}/100")
                
                print("-" * 40)
                
                # Action options
                print("1. ✅ Accept Request")
                print("2. ❌ Reject Request")
                print("3. ⬅️ Back")
                
                choice = input("\nSelect action: ").strip()
                
                if choice == "1":
                    accept_tow_request(request['id'])
                elif choice == "2":
                    reject_tow_request(request['id'])
                elif choice == "3":
                    break
                else:
                    print_warning("Invalid choice")
    else:
        print_error("Failed to get emergency tow requests")
    
    input("\nPress Enter to continue...")

def accept_tow_request(request_id):
    """Accept an emergency tow request"""
    response = make_tow_api_request("POST", f"/api/car/tow-driver/accept-request/{request_id}")
    
    if response and response.status_code == 200:
        data = response.json()
        print_success("Emergency tow request accepted successfully!")
        print_info(f"Request ID: {data['request_id']}")
        print_info(f"Next Status: {data['next_status']}")
        print_info(f"ETA: {data['estimated_arrival']}")
        
        if data.get('risk_bonus_applied', 0) > 0:
            print_warning(f"⚠️ Risk Bonus Applied: ₹{data['risk_bonus_applied']:.2f}")
    else:
        print_error("Failed to accept tow request")
    
    input("\nPress Enter to continue...")

def reject_tow_request(request_id):
    """Reject an emergency tow request"""
    reason = input("📝 Rejection reason (optional): ").strip()
    
    response = make_tow_api_request("POST", f"/api/car/tow-driver/reject-request/{request_id}", {
        "reason": reason or "Not available"
    })
    
    if response and response.status_code == 200:
        print_success("Tow request rejected")
    else:
        print_error("Failed to reject tow request")
    
    input("\nPress Enter to continue...")

# ==================== ACTIVE TOWING OPERATIONS ====================

def show_active_tow_operations():
    """Show active towing operations with lifecycle management"""
    print_tow_header("ACTIVE TOWING OPERATIONS")
    
    response = make_tow_api_request("GET", "/api/car/tow-driver/active-operations")
    
    if response and response.status_code == 200:
        data = response.json()
        operations = data['operations']
        
        if not operations:
            print_info("No active towing operations")
        else:
            print(f"🔥 Active Operations: {data['total_active']}")
            print("\n" + "=" * 80)
            
            for i, operation in enumerate(operations, 1):
                print(f"\n🔹 ACTIVE OPERATION #{i}")
                print(f"👤 Customer: {operation['customer_name']}")
                print(f"🚗 Vehicle: {operation['vehicle_type']}")
                print(f"⚠️ Issue: {operation['issue_type']}")
                print(f"📊 Status: {operation['status']}")
                print(f"⏱️ Time in Status: {operation['time_in_status']}")
                print(f"📈 Progress: {operation['progress_percentage']}%")
                print(f"⏰ ETA: {operation['estimated_completion']}")
                print(f"🛣️ Route Efficiency: {operation['route_efficiency']}/100")
                print(f"💎 Risk Bonus: ₹{operation['risk_bonus_earned']:.2f}")
                print("-" * 40)
                
                # Show next actions based on status
                print("🎯 Next Actions:")
                for action in operation['next_actions']:
                    print(f"  • {action}")
                
                # Show safety alerts
                if operation.get('safety_alerts'):
                    print("\n⚠️ Safety Alerts:")
                    for alert in operation['safety_alerts']:
                        print(f"  • {alert}")
                
                # Manual charge option
                if operation.get('manual_charge_allowed'):
                    print("\n💰 Manual Charge: Available (requires user approval)")
                
                print("\n📋 Status Update Options:")
                status_options = get_tow_operation_status_options(operation['status'])
                for option in status_options:
                    print(f"  {option}")
                
                print("9. ⬅️ Back")
                
                choice = input("\nSelect action: ").strip()
                
                if choice == "9":
                    break
                elif choice in status_options:
                    update_tow_operation_status(operation['id'], choice)
                elif choice == "8" and operation.get('manual_charge_allowed'):
                    request_manual_extra_charge(operation['id'])
                else:
                    print_warning("Invalid choice")
    else:
        print_error("Failed to get active operations")
    
    input("\nPress Enter to continue...")

def get_tow_operation_status_options(current_status):
    """Get available status update options for tow operation"""
    options = {
        "ACCEPTED": ["1", "ON_THE_WAY"],
        "ON_THE_WAY": ["2", "ARRIVED"], 
        "ARRIVED": ["3", "LOADING"],
        "LOADING": ["4", "IN_TRANSIT"],
        "IN_TRANSIT": ["5", "COMPLETED"]
    }
    
    result = {}
    for status, opts in options.items():
        if status == current_status:
            for opt in opts:
                result[opt] = status
    return result

def update_tow_operation_status(request_id, new_status):
    """Update tow operation status"""
    status_map = {
        "1": "ON_THE_WAY",
        "2": "ARRIVED",
        "3": "LOADING",
        "4": "IN_TRANSIT",
        "5": "COMPLETED"
    }
    
    if new_status not in status_map:
        print_warning("Invalid status option")
        return
    
    response = make_tow_api_request("PUT", f"/api/car/tow-driver/update-operation-status/{request_id}", {
        "status": status_map[new_status]
    })
    
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Tow operation status updated to {status_map[new_status]}")
        
        # If completed, show proof upload prompt
        if status_map[new_status] == "COMPLETED":
            print_info("Tow operation completed! Upload proof to receive payment.")
            upload_towing_proof(request_id)
        else:
            print_info("Next actions updated")
    else:
        print_error("Failed to update tow operation status")
    
    input("\nPress Enter to continue...")

def request_manual_extra_charge(request_id):
    """Request manual extra charge"""
    print_tow_header("REQUEST EXTRA CHARGE")
    
    try:
        amount = input("💰 Extra charge amount (₹): ").strip()
        reason = input("📝 Reason for extra charge: ").strip()
        
        if not amount or not reason:
            print_error("Amount and reason are required")
            input("\nPress Enter to continue...")
            return
        
        amount = float(amount)
        
        response = make_tow_api_request("POST", f"/api/car/tow-driver/request-extra-charge/{request_id}", {
            "amount": amount,
            "reason": reason
        })
        
        if response and response.status_code == 200:
            data = response.json()
            print_success("Extra charge request sent to user")
            print_info(f"Extra Amount: ₹{amount:.2f}")
            print_info(f"Reason: {reason}")
            print_info("Status: Pending user approval")
        else:
            print_error("Failed to request extra charge")
    
    except Exception as e:
        print_error(f"Extra charge request failed: {e}")
    
    input("\nPress Enter to continue...")

# ==================== EARNINGS & DISTANCE INSIGHTS ====================

def show_tow_earnings():
    """Show tow earnings and distance insights"""
    print_tow_header("EARNINGS & DISTANCE INSIGHTS")
    
    print("📊 Select Period:")
    print("1. 📅 Today")
    print("2. 📆 This Week")
    print("3. 📅 This Month")
    print("4. 📊 All Time")
    print("5. ⬅️ Back")
    
    choice = input("\nSelect period: ").strip()
    
    period_map = {
        "1": "today",
        "2": "week", 
        "3": "month",
        "4": "all"
    }
    
    if choice == "5":
        return
    elif choice not in period_map:
        print_warning("Invalid choice")
        input("\nPress Enter to continue...")
        return
    
    period = period_map[choice]
    
    response = make_tow_api_request("GET", f"/api/car/tow-driver/earnings?period={period}")
    
    if response and response.status_code == 200:
        data = response.json()
        insights = data['insights']
        
        print(f"\n💰 Earnings Summary ({period.upper()}):")
        print(f"  • Total Earnings: ₹{insights['total_earnings']:.2f}")
        print(f"  • Platform Commission: ₹{insights['total_commission']:.2f}")
        print(f"  • Risk Bonus Total: ₹{insights['total_risk_bonus']:.2f}")
        print(f"  • Net Earnings: ₹{insights['net_earnings']:.2f}")
        print(f"  • Total Tows: {insights['tow_count']}")
        print(f"  • Total Distance: {insights['total_distance']:.1f} km")
        print(f"  • Average per Tow: ₹{insights['avg_earning']:.2f}")
        print(f"  • Average per km: ₹{insights['avg_earning_per_km']:.2f}")
        
        print(f"\n📈 Advanced Insights:")
        print(f"  • Distance Profitability: {insights['distance_profitability_score']}/100")
        print(f"  • Heavy Vehicle Bonus: ₹{insights['heavy_vehicle_bonus']:.2f}")
        print(f"  • Earnings Trend: {insights['earnings_trend']}")
        print(f"  • Most Profitable Vehicle: {insights['most_profitable_vehicle_type']}")
        print(f"  • Surge Performance: {insights['surge_performance_score']}/100")
        
        print(f"\n💡 Financial Planning:")
        tax_info = insights['tax_projection']
        print(f"  • Estimated Yearly Income: ₹{tax_info['yearly_earnings']:.2f}")
        print(f"  • Tax ({tax_info['tax_rate']}): ₹{tax_info['estimated_tax']:.2f}")
        print(f"  • After Tax Income: ₹{tax_info['after_tax_income']:.2f}")
        
        print(f"\n⚖️ Commission Breakdown:")
        commission = insights['commission_breakdown']
        print(f"  • Platform Fee: {commission['commission_rate']}")
        print(f"  • Risk Bonus: ₹{commission['risk_bonus_total']:.2f}")
        print(f"  • Your Share: {commission['net_percentage']}")
    else:
        print_error("Failed to get earnings data")
    
    input("\nPress Enter to continue...")

# ==================== PERFORMANCE, SAFETY & RISK SUPPORT ====================

def show_tow_performance():
    """Show tow performance metrics and safety insights"""
    print_tow_header("PERFORMANCE, SAFETY & RISK SUPPORT")
    
    response = make_tow_api_request("GET", "/api/car/tow-driver/performance")
    
    if response and response.status_code == 200:
        data = response.json()
        metrics = data['metrics']
        
        print(f"\n📊 Tow Operation Metrics:")
        print(f"  • Trust Score: {metrics['trust_score']}/100")
        print(f"  • Completion Rate: {metrics['completion_rate']:.1f}%")
        print(f"  • On-Time Rate: {metrics['on_time_rate']:.1f}%")
        print(f"  • Acceptance Rate: {metrics['acceptance_rate']:.1f}%")
        print(f"  • Risk Handling Score: {metrics['risk_handling_score']:.1f}%")
        print(f"  • Total Tows: {metrics['total_tows']}")
        
        print(f"\n🛡️ Safety Score: {data['safety_score']}/100")
        
        # Risk assessment
        risk_assessment = data.get('risk_assessment', {})
        if risk_assessment:
            print(f"\n⚠️ Risk Assessment:")
            print(f"  • Risk Score: {risk_assessment.get('risk_score', 0)}/100")
            print(f"  • Risk Level: {risk_assessment.get('risk_level', 'UNKNOWN')}")
            print(f"  • Recommendation: {risk_assessment.get('recommendation', 'N/A')}")
        
        if data['emergency_alerts']:
            print(f"\n🚨 Emergency Alerts: {len(data['emergency_alerts'])}")
            for alert in data['emergency_alerts'][:3]:  # Show recent 3
                print(f"  • {alert['alert_time']} - {alert['status']}")
        
        if data['performance_tips']:
            print(f"\n💡 Performance Tips:")
            for tip in data['performance_tips']:
                print(f"  • {tip}")
        
        if data['improvement_areas']:
            print(f"\n🎯 Improvement Areas:")
            for area in data['improvement_areas']:
                print(f"  • {area}")
        
        # Safety alerts
        if data.get('night_risk_alert'):
            print_warning("\n⚠️ NIGHT RISK ALERT: Extra caution required during night operations")
        
        unsafe_alerts = data.get('unsafe_zone_alerts', [])
        if unsafe_alerts:
            print(f"\n⚠️ Unsafe Zone Alerts:")
            for alert in unsafe_alerts:
                print(f"  • {alert['message']} ({alert['severity']})")
    else:
        print_error("Failed to get performance data")
    
    input("\nPress Enter to continue...")

# ==================== EMERGENCY SOS ====================

def trigger_tow_emergency_sos():
    """Trigger emergency SOS alert for tow driver"""
    print_tow_header("EMERGENCY SOS")
    
    print("🚨 This will trigger an emergency alert")
    print("   Your current location will be shared with admin")
    confirm = input("\n⚠️ Trigger emergency alert? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print_info("Emergency cancelled")
        input("\nPress Enter to continue...")
        return
    
    # Get current location (simplified - would use GPS in real app)
    print("\n📍 Enter your current location:")
    try:
        lat = input("Latitude: ").strip()
        lng = input("Longitude: ").strip()
        
        if not lat or not lng:
            print_error("Location coordinates required")
            input("\nPress Enter to continue...")
            return
        
        lat = float(lat)
        lng = float(lng)
        
        response = make_tow_api_request("POST", "/api/car/tow-driver/emergency-alert", {
            "latitude": lat,
            "longitude": lng
        })
        
        if response and response.status_code == 200:
            data = response.json()
            print_success("Emergency alert triggered successfully!")
            print_info(f"Alert ID: {data['alert_id']}")
            print_info(f"Location: {data['location']['lat']}, {data['location']['lng']}")
            print_info(f"Timestamp: {data['timestamp']}")
            if data.get('admin_notified'):
                print_info("🚨 Admin notified. Stay safe.")
        else:
            print_error("Failed to trigger emergency alert")
    
    except Exception as e:
        print_error(f"Emergency trigger failed: {e}")
    
    input("\nPress Enter to continue...")

# ==================== TOWING PROOF SYSTEM ====================

def upload_towing_proof(request_id):
    """Upload tow operation completion proof"""
    print_tow_header(f"UPLOAD TOWING PROOF - Request #{request_id}")
    
    print("📸 This step is required to receive payment")
    print("   Upload pickup, vehicle loaded, and drop photos")
    
    # In CLI, we can't actually upload files, so we'll simulate
    print("\n📝 Damage Notes:")
    notes = input("Enter any damage notes: ").strip()
    
    print("\n📸 File Upload Simulation:")
    print("   • Pickup Photo: [SIMULATED] pickup.jpg")
    print("   • Vehicle Loaded Photo: [SIMULATED] loaded.jpg")
    print("   • Drop Photo: [SIMULATED] drop.jpg")
    
    confirm = input("\n✅ Confirm proof upload? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print_info("Proof upload cancelled")
        return
    
    # Simulate upload
    response = make_tow_api_request("POST", f"/api/car/tow-driver/upload-towing-proof/{request_id}", {
        "damage_notes": notes,
        "pickup_photo": "simulated_pickup.jpg",
        "vehicle_loaded_photo": "simulated_loaded.jpg",
        "drop_photo": "simulated_drop.jpg"
    })
    
    if response and response.status_code == 200:
        data = response.json()
        print_success("Tow operation proof uploaded successfully!")
        print_info(f"Proof ID: {data['proof_id']}")
        print_info("Payment will be processed after verification")
    else:
        print_error("Failed to upload proof")
    
    input("\nPress Enter to continue...")

# ==================== MAIN DASHBOARD ====================

def tow_truck_dashboard(driver_id, token=None):
    """Main tow truck dashboard interface"""
    global TOKEN, TOW_DRIVER_ID
    TOKEN = token  # Set the global token for API calls
    
    while True:
        print_tow_header("🚛 TOW TRUCK DASHBOARD")
        print("1. 🟢 Go Online / Emergency Zone Status")
        print("2. 🚨 Emergency Tow Requests") 
        print("3. 🪝 Active Towing Operations")
        print("4. 💰 Earnings & Distance Insights")
        print("5. 🛡️ Performance, Safety & Risk Support")
        print("6. 🚪 Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            show_tow_online_status_menu()
        elif choice == "2":
            show_emergency_tow_requests()
        elif choice == "3":
            show_active_tow_operations()
        elif choice == "4":
            show_tow_earnings()
        elif choice == "5":
            show_tow_performance()
        elif choice == "6":
            print_success("Logged out successfully")
            break
        else:
            print_warning("Invalid choice")
            input("\nPress Enter to continue...")

def show_tow_online_status_menu():
    """Show tow online status submenu"""
    while True:
        print_tow_header("ONLINE STATUS MANAGEMENT")
        print("1. 🟢 Toggle Online/Offline")
        print("2. 📍 Update Location")
        print("3. 🚚 Update Truck Type")
        print("4. 📊 View Emergency Zone Status")
        print("5. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            toggle_tow_driver_online_status()
        elif choice == "2":
            update_tow_driver_location()
        elif choice == "3":
            update_tow_driver_truck_type()
        elif choice == "4":
            show_emergency_zone_status()
        elif choice == "5":
            break
        else:
            print_warning("Invalid choice")
            input("\nPress Enter to continue...")
