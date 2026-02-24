"""
Mechanic Dashboard CLI Integration
Complete CLI interface for mechanic worker management system
"""

import requests
import os
from datetime import datetime
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API = "http://127.0.0.1:5001"
TOKEN = None
MECHANIC_ID = None

def get_headers():
    """Get authenticated headers for API requests"""
    return {"Authorization": f"Bearer {TOKEN}"}

def make_api_request(method, endpoint, data=None, params=None):
    """Make authenticated API request"""
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
        print(f"❌ API request failed: {e}")
        return None

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print formatted header"""
    clear_screen()
    print(f"\n🔧 {title}")
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

# ==================== ONLINE STATUS & DEMAND ====================

def toggle_online_status():
    """Toggle mechanic online/offline status"""
    print_header("GO ONLINE / OFFLINE")
    
    response = make_api_request("POST", "/api/car/mechanic/toggle-online")
    
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Status updated to {data['new_status']}")
        print_info(f"Priority Score: {data['priority_score']}")
    else:
        print_error("Failed to update status")
    
    input("\nPress Enter to continue...")

def show_demand_status():
    """Show comprehensive demand status"""
    print_header("DEMAND STATUS")
    
    response = make_api_request("GET", "/api/car/mechanic/status")
    
    if response and response.status_code == 200:
        data = response.json()
        
        print(f"🟢 Current Status: {data['current_status']}")
        print(f"📊 Demand Level: {data['demand_level']}")
        print(f"👥 Online Mechanics: {data['online_mechanics']}")
        print(f"⏰ Peak Hour: {'Yes' if data['peak_hour'] else 'No'}")
        print(f"🎯 Priority Score: {data['priority_score']}")
        print(f"💰 Potential Earnings Today: ₹{data['potential_earnings_today']:.2f}")
        print(f"⚖️ Fairness Score: {data['fairness_score']}/100")
        
        print(f"\n📈 Skill Demand Analysis:")
        for skill in data['skill_demand']:
            print(f"  • {skill['required_skill']}: {skill['pending_count']} pending jobs")
    else:
        print_error("Failed to get demand status")
    
    input("\nPress Enter to continue...")

def update_location():
    """Update mechanic location"""
    print_header("UPDATE LOCATION")
    
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
            
            response = make_api_request("POST", "/api/car/mechanic/update-location", {
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
            "thane": (19.2183, 72.9781)
        }
        
        lat, lng = area_coordinates.get(area.lower(), (19.0760, 72.8777))  # Default to Mumbai coordinates
        
        response = make_api_request("POST", "/api/car/mechanic/update-location", {
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

# ==================== JOB REQUESTS ====================

def show_job_requests():
    """Show transparent job requests"""
    print_header("TRANSPARENT JOB REQUESTS")
    
    response = make_api_request("GET", "/api/car/mechanic/job-requests")
    
    if response and response.status_code == 200:
        data = response.json()
        jobs = data['jobs']
        
        if not jobs:
            print_info("No job requests available")
        else:
            print(f"📋 Total Requests: {data['total_jobs']}")
            print(f"🟢 Your Status: {data['mechanic_status']}")
            print("\n" + "=" * 80)
            
            for i, job in enumerate(jobs[:10], 1):  # Show top 10
                print(f"\n🔹 JOB #{i}")
                print(f"📝 Issue: {job['issue_type']}")
                print(f"🔧 Required Skill: {job['required_skill']}")
                print(f"📍 Distance: {job['distance_km']} km")
                print(f"💰 Earnings: ₹{job['estimated_earning_min']:.2f} - ₹{job['estimated_earning_max']:.2f}")
                print(f"⏱️ Duration: {job['estimated_duration']} minutes")
                print(f"⭐ Profitability: {job['profitability_score']}/100")
                print(f"⚠️ Risk: {job['risk_level']}")
                print(f"📋 Assignment: {job['assignment_reason']}")
                print("-" * 40)
                
                # Action options
                print("1. ✅ Accept Job")
                print("2. ❌ Reject Job")
                print("3. ⬅️ Back")
                
                choice = input("\nSelect action: ").strip()
                
                if choice == "1":
                    accept_job_request(job['id'])
                elif choice == "2":
                    reject_job_request(job['id'])
                elif choice == "3":
                    break
                else:
                    print_warning("Invalid choice")
    else:
        print_error("Failed to get job requests")
    
    input("\nPress Enter to continue...")

def accept_job_request(job_id):
    """Accept a job request"""
    response = make_api_request("POST", f"/api/car/mechanic/accept-job/{job_id}")
    
    if response and response.status_code == 200:
        data = response.json()
        print_success("Job accepted successfully!")
        print_info(f"Job ID: {data['job_id']}")
        print_info(f"Next Status: {data['next_status']}")
        print_info(f"ETA: {data['estimated_arrival']}")
    else:
        print_error("Failed to accept job")
    
    input("\nPress Enter to continue...")

def reject_job_request(job_id):
    """Reject a job request"""
    reason = input("📝 Rejection reason (optional): ").strip()
    
    response = make_api_request("POST", f"/api/car/mechanic/reject-job/{job_id}", {
        "reason": reason or "Not interested"
    })
    
    if response and response.status_code == 200:
        print_success("Job rejected")
    else:
        print_error("Failed to reject job")
    
    input("\nPress Enter to continue...")

# ==================== ACTIVE JOBS ====================

def show_active_jobs():
    """Show active jobs with lifecycle management"""
    print_header("ACTIVE JOBS")
    
    response = make_api_request("GET", "/api/car/mechanic/active-jobs")
    
    if response and response.status_code == 200:
        data = response.json()
        jobs = data['jobs']
        
        if not jobs:
            print_info("No active jobs")
        else:
            print(f"🔥 Active Jobs: {data['total_active']}")
            print("\n" + "=" * 80)
            
            for i, job in enumerate(jobs, 1):
                print(f"\n🔹 ACTIVE JOB #{i}")
                print(f"👤 Customer: {job['customer_name']}")
                print(f"📝 Issue: {job['issue_type']}")
                print(f"📊 Status: {job['status']}")
                print(f"⏱️ Time in Status: {job['time_in_status']}")
                print(f"📈 Progress: {job['progress_percentage']}%")
                print(f"⏰ ETA: {job['estimated_completion']}")
                print("-" * 40)
                
                # Show next actions based on status
                print("🎯 Next Actions:")
                for action in job['next_actions']:
                    print(f"  • {action}")
                
                print("\n📋 Status Update Options:")
                status_options = get_status_update_options(job['status'])
                for option in status_options:
                    print(f"  {option}")
                
                print("9. ⬅️ Back")
                
                choice = input("\nSelect action: ").strip()
                
                if choice == "9":
                    break
                elif choice in status_options:
                    update_job_status(job['id'], choice)
                else:
                    print_warning("Invalid choice")
    else:
        print_error("Failed to get active jobs")
    
    input("\nPress Enter to continue...")

def get_status_update_options(current_status):
    """Get available status update options"""
    options = {
        "ACCEPTED": ["1", "ON_THE_WAY"],
        "ON_THE_WAY": ["2", "ARRIVED"], 
        "ARRIVED": ["3", "WORKING"],
        "WORKING": ["4", "COMPLETED"]
    }
    
    result = {}
    for status, opts in options.items():
        if status == current_status:
            for opt in opts:
                result[opt] = status
    return result

def update_job_status(job_id, new_status):
    """Update job status"""
    status_map = {
        "1": "ON_THE_WAY",
        "2": "ARRIVED",
        "3": "WORKING", 
        "4": "COMPLETED"
    }
    
    if new_status not in status_map:
        print_warning("Invalid status option")
        return
    
    response = make_api_request("PUT", f"/api/car/mechanic/update-job-status/{job_id}", {
        "status": status_map[new_status]
    })
    
    if response and response.status_code == 200:
        data = response.json()
        print_success(f"Job status updated to {status_map[new_status]}")
        
        # If completed, show proof upload prompt
        if status_map[new_status] == "COMPLETED":
            print_info("Job completed! Upload proof to receive payment.")
            upload_job_proof(job_id)
    else:
        print_error("Failed to update job status")
    
    input("\nPress Enter to continue...")

# ==================== EARNINGS ====================

def show_earnings():
    """Show earnings and fairness insights"""
    print_header("EARNINGS & FAIRNESS INSIGHTS")
    
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
    
    response = make_api_request("GET", f"/api/car/mechanic/earnings?period={period}")
    
    if response and response.status_code == 200:
        data = response.json()
        insights = data['insights']
        
        print(f"\n💰 Earnings Summary ({period.upper()}):")
        print(f"  • Total Earnings: ₹{insights['total_earnings']:.2f}")
        print(f"  • Platform Commission: ₹{insights['total_commission']:.2f}")
        print(f"  • Net Earnings: ₹{insights['net_earnings']:.2f}")
        print(f"  • Jobs Completed: {insights['job_count']}")
        print(f"  • Average per Job: ₹{insights['avg_earning']:.2f}")
        
        print(f"\n📈 Advanced Insights:")
        print(f"  • Income Stability: {insights['income_stability_score']}/100")
        print(f"  • Earnings Trend: {insights['earnings_trend']}")
        print(f"  • Most Profitable: {insights['most_profitable_service']}")
        print(f"  • Peak Day: {insights['peak_earning_day']}")
        
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

def show_performance():
    """Show performance metrics and safety insights"""
    print_header("PERFORMANCE, SAFETY & SUPPORT")
    
    response = make_api_request("GET", "/api/car/mechanic/performance")
    
    if response and response.status_code == 200:
        data = response.json()
        metrics = data['metrics']
        
        print(f"\n📊 Performance Metrics:")
        print(f"  • Trust Score: {metrics['trust_score']}/100")
        print(f"  • Completion Rate: {metrics['completion_rate']:.1f}%")
        print(f"  • On-Time Rate: {metrics['on_time_rate']:.1f}%")
        print(f"  • Acceptance Rate: {metrics['acceptance_rate']:.1f}%")
        print(f"  • Complaint Rate: {metrics['complaint_rate']:.1f}%")
        print(f"  • Total Jobs: {metrics['total_jobs']}")
        
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
    else:
        print_error("Failed to get performance data")
    
    input("\nPress Enter to continue...")

# ==================== EMERGENCY SOS ====================

def trigger_emergency_sos():
    """Trigger emergency SOS alert"""
    print_header("EMERGENCY SOS")
    
    print("🚨 This will trigger an emergency alert")
    print("   Your current location will be shared")
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
        
        response = make_api_request("POST", "/api/car/mechanic/emergency-alert", {
            "latitude": lat,
            "longitude": lng
        })
        
        if response and response.status_code == 200:
            data = response.json()
            print_success("Emergency alert triggered!")
            print_info(f"Alert ID: {data['alert_id']}")
            print_info(f"Location: {data['location']['lat']}, {data['location']['lng']}")
            print_info(f"Time: {data['timestamp']}")
        else:
            print_error("Failed to trigger emergency alert")
    
    except Exception as e:
        print_error(f"Emergency trigger failed: {e}")
    
    input("\nPress Enter to continue...")

# ==================== JOB PROOF SYSTEM ====================

def upload_job_proof(job_id):
    """Upload job completion proof"""
    print_header(f"UPLOAD JOB PROOF - Job #{job_id}")
    
    print("📸 This step is required to receive payment")
    print("   Upload before/after photos and work notes")
    
    # In CLI, we can't actually upload files, so we'll simulate
    print("\n📝 Work Notes:")
    notes = input("Enter work details: ").strip()
    
    print("\n📸 File Upload Simulation:")
    print("   • Before photo: [SIMULATED] before_photo.jpg")
    print("   • After photo: [SIMULATED] after_photo.jpg")
    
    confirm = input("\n✅ Confirm proof upload? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print_info("Proof upload cancelled")
        return
    
    # Simulate upload
    response = make_api_request("POST", f"/api/car/mechanic/upload-proof/{job_id}", {
        "work_notes": notes,
        "before_photo": "simulated_before.jpg",
        "after_photo": "simulated_after.jpg"
    })
    
    if response and response.status_code == 200:
        data = response.json()
        print_success("Job proof uploaded successfully!")
        print_info(f"Proof ID: {data['proof_id']}")
        print_info("Payment will be processed after verification")
    else:
        print_error("Failed to upload proof")
    
    input("\nPress Enter to continue...")

# ==================== MAIN DASHBOARD ====================

def mechanic_dashboard(mechanic_id, token=None):
    """Main mechanic dashboard interface"""
    global TOKEN
    TOKEN = token  # Set the global token for API calls
    
    while True:
        print_header("🔧 MECHANIC DASHBOARD")
        print("1. 🟢 Go Online / Demand Status")
        print("2. 📥 Transparent Job Requests") 
        print("3. 🔧 Active Jobs (With Proof System)")
        print("4. 💰 Earnings & Fairness Insights")
        print("5. 🛡️ Performance, Safety & Support")
        print("6. 🚪 Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            show_online_status_menu()
        elif choice == "2":
            show_job_requests()
        elif choice == "3":
            show_active_jobs()
        elif choice == "4":
            show_earnings()
        elif choice == "5":
            show_performance()
        elif choice == "6":
            print_success("Logged out successfully")
            break
        else:
            print_warning("Invalid choice")
            input("\nPress Enter to continue...")

def show_online_status_menu():
    """Show online status submenu"""
    while True:
        print_header("ONLINE STATUS MANAGEMENT")
        print("1. 🟢 Toggle Online/Offline")
        print("2. 📍 Update Location")
        print("3. 📊 View Demand Status")
        print("4. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            toggle_online_status()
        elif choice == "2":
            update_location()
        elif choice == "3":
            show_demand_status()
        elif choice == "4":
            break
        else:
            print_warning("Invalid choice")
            input("\nPress Enter to continue...")
