"""
Fuel Delivery Agent CLI Integration
Complete CLI interface for fuel delivery agent management system
"""

import requests
import os
from datetime import datetime
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API = "http://127.0.0.1:5001"
TOKEN = None
FUEL_AGENT_ID = None

def get_headers():
    """Get authenticated headers for API requests"""
    return {"Authorization": f"Bearer {TOKEN}"}

def make_fuel_api_request(method, endpoint, data=None, params=None):
    """Make authenticated API request for fuel agent"""
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
        print(f"❌ Fuel API request failed: {e}")
        return None

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_fuel_header(title):
    """Print formatted header for fuel agent"""
    clear_screen()
    print(f"\n⛽ {title}")
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

def print_fuel_info(message):
    """Print fuel-specific info message"""
    print(f"⛽ {message}")

# ==================== ONLINE STATUS & DEMAND ====================

def toggle_fuel_agent_online_status():
    """Toggle fuel agent online/offline status"""
    print_fuel_header("GO ONLINE / OFFLINE")
    
    response = make_fuel_api_request("POST", "/api/car/fuel-agent/toggle-online")
    
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Status updated to {data['new_status']}")
        print_info(f"Priority Score: {data['priority_score']}")
    else:
        print_error("Failed to update status")
    
    input("\nPress Enter to continue...")

def show_fuel_demand_status():
    """Show comprehensive fuel demand status"""
    print_fuel_header("DEMAND STATUS")
    
    response = make_fuel_api_request("GET", "/api/car/fuel-agent/status")
    
    if response and response.status_code == 200:
        data = response.json()
        
        print(f"🟢 Current Status: {data['current_status']}")
        print(f"📊 Demand Level: {data['demand_level']}")
        print(f"👥 Online Agents: {data['online_agents']}")
        print(f"⏰ Peak Hour: {'Yes' if data['peak_hour'] else 'No'}")
        print(f"🎯 Priority Score: {data['priority_score']}")
        print(f"💰 Potential Earnings Today: ₹{data['potential_earnings_today']:.2f}")
        print(f"⚖️ Fairness Score: {data['fairness_score']}/100")
        print(f"📍 High Delivery Zone: {data['high_delivery_zone']}")
        
        if data.get('fuel_shortage_alert'):
            print_warning("⚠️ FUEL SHORTAGE ALERT: High petrol demand detected!")
        
        print(f"\n📈 Fuel Demand Analysis:")
        for fuel in data['fuel_demand']:
            print(f"  • {fuel['fuel_type']}: {fuel['pending_count']} pending orders")
            print(f"    Avg Quantity: {fuel['avg_quantity']:.1f}L")
            print(f"    Avg Earning: ₹{fuel['avg_min_earning']:.2f} - ₹{fuel['avg_max_earning']:.2f}")
    else:
        print_error("Failed to get demand status")
    
    input("\nPress Enter to continue...")

def update_fuel_agent_location():
    """Update fuel agent location"""
    print_fuel_header("UPDATE LOCATION")
    
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
            
            response = make_fuel_api_request("POST", "/api/car/fuel-agent/update-location", {
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
        
        response = make_fuel_api_request("POST", "/api/car/fuel-agent/update-location", {
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

# ==================== FUEL ORDERS ====================

def show_fuel_orders():
    """Show transparent fuel orders"""
    print_fuel_header("TRANSPARENT FUEL ORDERS")
    
    response = make_fuel_api_request("GET", "/api/car/fuel-agent/fuel-orders")
    
    if response and response.status_code == 200:
        data = response.json()
        orders = data['orders']
        
        if not orders:
            print_info("No fuel orders available")
        else:
            print(f"📋 Total Orders: {data['total_orders']}")
            print(f"🟢 Your Status: {data['agent_status']}")
            print("\n" + "=" * 80)
            
            for i, order in enumerate(orders[:10], 1):  # Show top 10
                print(f"\n🔹 FUEL ORDER #{i}")
                print(f"⛽ Fuel Type: {order['fuel_type']}")
                print(f"📊 Quantity: {order['quantity_liters']} Litres")
                print(f"📍 Distance: {order['distance_km']} km")
                print(f"💰 Earnings: ₹{order['estimated_earning_min']:.2f} - ₹{order['estimated_earning_max']:.2f}")
                print(f"⏱️ Duration: {order['estimated_duration']} minutes")
                print(f"⭐ Profitability: {order['profitability_score']}/100")
                print(f"🚚 Delivery Efficiency: {order['delivery_efficiency']}/100")
                print(f"⚠️ Risk: {order['risk_level']}")
                print(f"📋 Assignment: {order['assignment_reason']}")
                
                if order.get('fuel_shortage_risk'):
                    print_warning("⚠️ FUEL SHORTAGE RISK: High demand in this area")
                
                print("-" * 40)
                
                # Action options
                print("1. ✅ Accept Order")
                print("2. ❌ Reject Order")
                print("3. ⬅️ Back")
                
                choice = input("\nSelect action: ").strip()
                
                if choice == "1":
                    accept_fuel_order_request(order['id'])
                elif choice == "2":
                    reject_fuel_order_request(order['id'])
                elif choice == "3":
                    break
                else:
                    print_warning("Invalid choice")
    else:
        print_error("Failed to get fuel orders")
    
    input("\nPress Enter to continue...")

def accept_fuel_order_request(order_id):
    """Accept a fuel order request"""
    response = make_fuel_api_request("POST", f"/api/car/fuel-agent/accept-order/{order_id}")
    
    if response and response.status_code == 200:
        data = response.json()
        print_success("Fuel order accepted successfully!")
        print_info(f"Order ID: {data['order_id']}")
        print_info(f"Next Status: {data['next_status']}")
        print_info(f"ETA: {data['estimated_arrival']}")
        
        if data.get('fuel_shortage_alert'):
            print_warning("⚠️ Check fuel availability before departure")
    else:
        print_error("Failed to accept fuel order")
    
    input("\nPress Enter to continue...")

def reject_fuel_order_request(order_id):
    """Reject a fuel order request"""
    reason = input("📝 Rejection reason (optional): ").strip()
    
    response = make_fuel_api_request("POST", f"/api/car/fuel-agent/reject-order/{order_id}", {
        "reason": reason or "Not interested"
    })
    
    if response and response.status_code == 200:
        print_success("Fuel order rejected")
    else:
        print_error("Failed to reject fuel order")
    
    input("\nPress Enter to continue...")

# ==================== ACTIVE DELIVERIES ====================

def show_active_fuel_deliveries():
    """Show active fuel deliveries with lifecycle management"""
    print_fuel_header("ACTIVE DELIVERIES")
    
    response = make_fuel_api_request("GET", "/api/car/fuel-agent/active-deliveries")
    
    if response and response.status_code == 200:
        data = response.json()
        deliveries = data['deliveries']
        
        if not deliveries:
            print_info("No active deliveries")
        else:
            print(f"🔥 Active Deliveries: {data['total_active']}")
            print("\n" + "=" * 80)
            
            for i, delivery in enumerate(deliveries, 1):
                print(f"\n🔹 ACTIVE DELIVERY #{i}")
                print(f"👤 Customer: {delivery['customer_name']}")
                print(f"⛽ Fuel Type: {delivery['fuel_type']}")
                print(f"📊 Quantity: {delivery['quantity_liters']} Litres")
                print(f"📊 Status: {delivery['status']}")
                print(f"⏱️ Time in Status: {delivery['time_in_status']}")
                print(f"📈 Progress: {delivery['progress_percentage']}%")
                print(f"⏰ ETA: {delivery['estimated_completion']}")
                print(f"🚚 Route Efficiency: {delivery['route_efficiency']}/100")
                print(f"💨 Delivery Speed: {delivery['delivery_speed_score']}/100")
                print("-" * 40)
                
                # Show next actions based on status
                print("🎯 Next Actions:")
                for action in delivery['next_actions']:
                    print(f"  • {action}")
                
                # Show upsell opportunities
                if delivery.get('upsell_opportunities'):
                    print("\n💡 Upsell Opportunities:")
                    for opportunity in delivery['upsell_opportunities']:
                        print(f"  • {opportunity}")
                
                print("\n📋 Status Update Options:")
                status_options = get_fuel_delivery_status_options(delivery['status'])
                for option in status_options:
                    print(f"  {option}")
                
                print("9. ⬅️ Back")
                
                choice = input("\nSelect action: ").strip()
                
                if choice == "9":
                    break
                elif choice in status_options:
                    update_fuel_delivery_status(delivery['id'], choice)
                else:
                    print_warning("Invalid choice")
    else:
        print_error("Failed to get active deliveries")
    
    input("\nPress Enter to continue...")

def get_fuel_delivery_status_options(current_status):
    """Get available status update options for fuel delivery"""
    options = {
        "ACCEPTED": ["1", "ON_THE_WAY"],
        "ON_THE_WAY": ["2", "ARRIVED"], 
        "ARRIVED": ["3", "DELIVERED"]
    }
    
    result = {}
    for status, opts in options.items():
        if status == current_status:
            for opt in opts:
                result[opt] = status
    return result

def update_fuel_delivery_status(order_id, new_status):
    """Update fuel delivery status"""
    status_map = {
        "1": "ON_THE_WAY",
        "2": "ARRIVED",
        "3": "DELIVERED"
    }
    
    if new_status not in status_map:
        print_warning("Invalid status option")
        return
    
    response = make_fuel_api_request("PUT", f"/api/car/fuel-agent/update-delivery-status/{order_id}", {
        "status": status_map[new_status]
    })
    
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Delivery status updated to {status_map[new_status]}")
        
        # If delivered, show proof upload prompt
        if status_map[new_status] == "DELIVERED":
            print_info("Delivery completed! Upload proof to receive payment.")
            upload_fuel_delivery_proof(order_id)
        else:
            print_info("Next actions updated")
    else:
        print_error("Failed to update delivery status")
    
    input("\nPress Enter to continue...")

# ==================== EARNINGS ====================

def show_fuel_earnings():
    """Show fuel earnings and delivery insights"""
    print_fuel_header("EARNINGS & DELIVERY INSIGHTS")
    
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
    
    response = make_fuel_api_request("GET", f"/api/car/fuel-agent/earnings?period={period}")
    
    if response and response.status_code == 200:
        data = response.json()
        insights = data['insights']
        
        print(f"\n💰 Earnings Summary ({period.upper()}):")
        print(f"  • Total Earnings: ₹{insights['total_earnings']:.2f}")
        print(f"  • Platform Commission: ₹{insights['total_commission']:.2f}")
        print(f"  • Net Earnings: ₹{insights['net_earnings']:.2f}")
        print(f"  • Deliveries Completed: {insights['delivery_count']}")
        print(f"  • Average per Delivery: ₹{insights['avg_earning']:.2f}")
        
        print(f"\n📈 Advanced Insights:")
        print(f"  • Income Stability: {insights['income_stability_score']}/100")
        print(f"  • Earnings Trend: {insights['earnings_trend']}")
        print(f"  • Most Profitable Fuel: {insights['most_profitable_fuel_type']}")
        print(f"  • Peak Earning Time: {insights['peak_earning_time']}")
        print(f"  • Delivery Efficiency: {insights['delivery_efficiency_index']}/100")
        
        print(f"\n💡 Financial Planning:")
        tax_info = insights['tax_estimation']
        print(f"  • Estimated Yearly Income: ₹{tax_info['yearly_earnings']:.2f}")
        print(f"  • Tax ({tax_info['tax_rate']}): ₹{tax_info['estimated_tax']:.2f}")
        print(f"  • After Tax Income: ₹{tax_info['after_tax_income']:.2f}")
        
        print(f"\n💎 Savings Suggestions:")
        for level, suggestion in insights['savings_suggestion'].items():
            print(f"  • {level.title()}: ₹{suggestion['amount']:.2f} ({suggestion['rate']}%)")
        
        print(f"\n⚖️ Commission Breakdown:")
        commission = insights['commission_breakdown']
        print(f"  • Platform Fee: {commission['commission_rate']}")
        print(f"  • Your Share: {commission['net_percentage']}")
    else:
        print_error("Failed to get earnings data")
    
    input("\nPress Enter to continue...")

# ==================== PERFORMANCE & SAFETY ====================

def show_fuel_performance():
    """Show fuel performance metrics and safety insights"""
    print_fuel_header("PERFORMANCE, SAFETY & SUPPORT")
    
    response = make_fuel_api_request("GET", "/api/car/fuel-agent/performance")
    
    if response and response.status_code == 200:
        data = response.json()
        metrics = data['metrics']
        
        print(f"\n📊 Fuel Delivery Metrics:")
        print(f"  • Trust Score: {metrics['trust_score']}/100")
        print(f"  • Completion Rate: {metrics['completion_rate']:.1f}%")
        print(f"  • On-Time Rate: {metrics['on_time_rate']:.1f}%")
        print(f"  • Acceptance Rate: {metrics['acceptance_rate']:.1f}%")
        print(f"  • Cancellation Rate: {metrics['cancellation_rate']:.1f}%")
        print(f"  • Total Deliveries: {metrics['total_deliveries']}")
        
        print(f"\n🛡️ Safety Score: {data['safety_score']}/100")
        
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
        
        if data.get('fuel_shortage_alerts'):
            print(f"\n⚠️ Fuel Shortage Alerts:")
            for alert in data['fuel_shortage_alerts']:
                print(f"  • {alert['message']} ({alert['severity']})")
    else:
        print_error("Failed to get performance data")
    
    input("\nPress Enter to continue...")

# ==================== EMERGENCY SOS ====================

def trigger_fuel_emergency_sos():
    """Trigger emergency SOS alert for fuel agent"""
    print_fuel_header("EMERGENCY SOS")
    
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
        
        response = make_fuel_api_request("POST", "/api/car/fuel-agent/emergency-alert", {
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

# ==================== DELIVERY PROOF SYSTEM ====================

def upload_fuel_delivery_proof(order_id):
    """Upload fuel delivery completion proof"""
    print_fuel_header(f"UPLOAD DELIVERY PROOF - Order #{order_id}")
    
    print("📸 This step is required to receive payment")
    print("   Upload fuel meter and delivery confirmation photos")
    
    # In CLI, we can't actually upload files, so we'll simulate
    print("\n📝 Delivery Notes:")
    notes = input("Enter delivery details: ").strip()
    
    print("\n📸 File Upload Simulation:")
    print("   • Fuel Meter Photo: [SIMULATED] fuel_meter.jpg")
    print("   • Delivery Confirmation: [SIMULATED] delivery_confirmation.jpg")
    
    confirm = input("\n✅ Confirm proof upload? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print_info("Proof upload cancelled")
        return
    
    # Simulate upload
    response = make_fuel_api_request("POST", f"/api/car/fuel-agent/upload-delivery-proof/{order_id}", {
        "delivery_notes": notes,
        "fuel_meter_photo": "simulated_fuel_meter.jpg",
        "delivery_confirmation_photo": "simulated_delivery_confirmation.jpg"
    })
    
    if response and response.status_code == 200:
        data = response.json()
        print_success("Fuel delivery proof uploaded successfully!")
        print_info(f"Proof ID: {data['proof_id']}")
        print_info("Payment will be processed after verification")
    else:
        print_error("Failed to upload proof")
    
    input("\nPress Enter to continue...")

# ==================== MAIN DASHBOARD ====================

def fuel_agent_dashboard(agent_id, token=None):
    """Main fuel agent dashboard interface"""
    global TOKEN, FUEL_AGENT_ID
    TOKEN = token  # Set the global token for API calls
    
    while True:
        print_fuel_header("⛽ FUEL DELIVERY DASHBOARD")
        print("1. 🟢 Go Online / Demand Status")
        print("2. 📥 Transparent Fuel Orders") 
        print("3. 🛵 Active Deliveries (Live Tracking)")
        print("4. 💰 Earnings & Delivery Insights")
        print("5. 🛡️ Performance, Safety & Support")
        print("6. 🚪 Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            show_fuel_online_status_menu()
        elif choice == "2":
            show_fuel_orders()
        elif choice == "3":
            show_active_fuel_deliveries()
        elif choice == "4":
            show_fuel_earnings()
        elif choice == "5":
            show_fuel_performance()
        elif choice == "6":
            print_success("Logged out successfully")
            break
        else:
            print_warning("Invalid choice")
            input("\nPress Enter to continue...")

def show_fuel_online_status_menu():
    """Show fuel online status submenu"""
    while True:
        print_fuel_header("ONLINE STATUS MANAGEMENT")
        print("1. 🟢 Toggle Online/Offline")
        print("2. 📍 Update Location")
        print("3. 📊 View Demand Status")
        print("4. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            toggle_fuel_agent_online_status()
        elif choice == "2":
            update_fuel_agent_location()
        elif choice == "3":
            show_fuel_demand_status()
        elif choice == "4":
            break
        else:
            print_warning("Invalid choice")
            input("\nPress Enter to continue...")
