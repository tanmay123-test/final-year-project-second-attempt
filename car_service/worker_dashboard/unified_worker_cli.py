"""
Unified Worker Dashboard CLI
All worker types (Mechanic, Fuel Agent, Tow Truck, Expert) in one module
"""

import os
import sys
import json
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_utils import verify_token, generate_token

class UnifiedWorkerDashboard:
    """Unified CLI dashboard for all worker types"""
    
    def __init__(self, worker_id: int, worker_type: str, token: str):
        self.worker_id = worker_id
        self.worker_type = worker_type
        self.token = token
        self.running = True
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print dashboard header"""
        self.clear_screen()
        worker_icons = {
            'MECHANIC': '🔧',
            'FUEL_AGENT': '⛽',
            'TOW_TRUCK': '🚛',
            'EXPERT': '👨‍🔧'
        }
        
        icon = worker_icons.get(self.worker_type, '👤')
        worker_names = {
            'MECHANIC': 'MECHANIC',
            'FUEL_AGENT': 'FUEL AGENT',
            'TOW_TRUCK': 'TOW TRUCK DRIVER',
            'EXPERT': 'AUTOMOBILE EXPERT'
        }
        
        name = worker_names.get(self.worker_type, 'WORKER')
        
        print(f"{icon} {name} DASHBOARD")
        print("=" * 50)
        print(f"🆔 Worker ID: {self.worker_id}")
        print(f"🔐 Token: {self.token[:20]}...")
        print("=" * 50)
    
    def show_main_menu(self):
        """Show main menu based on worker type"""
        if self.worker_type == 'MECHANIC':
            return self.mechanic_menu()
        elif self.worker_type == 'FUEL_AGENT':
            return self.fuel_agent_menu()
        elif self.worker_type == 'TOW_TRUCK':
            return self.tow_truck_menu()
        elif self.worker_type == 'EXPERT':
            return self.expert_menu()
        else:
            return self.default_menu()
    
    def mechanic_menu(self):
        """Mechanic-specific menu"""
        print("\n🔧 MECHANIC MENU")
        print("=" * 30)
        print("1. 📋 Available Jobs")
        print("2. 📅 My Appointments")
        print("3. 🚗 Service History")
        print("4. 💰 Earnings")
        print("5. 👤 Profile Management")
        print("6. 📊 Performance Stats")
        print("7. 🚪 Logout")
        
        choice = input("\nSelect option: ").strip()
        return choice
    
    def fuel_agent_menu(self):
        """Fuel Agent-specific menu"""
        print("\n⛽ FUEL AGENT MENU")
        print("=" * 30)
        print("1. 🚗 Available Deliveries")
        print("2. 📋 Delivery History")
        print("3. 📤 Upload Proof")
        print("4. 💰 Earnings & Commission")
        print("5. 📍 Route Management")
        print("6. 👤 Profile Management")
        print("7. 📊 Performance Stats")
        print("8. 🚪 Logout")
        
        choice = input("\nSelect option: ").strip()
        return choice
    
    def tow_truck_menu(self):
        """Tow Truck-specific menu"""
        print("\n🚛 TOW TRUCK MENU")
        print("=" * 30)
        print("1. 📋 Available Requests")
        print("2. 🚗 Active Jobs")
        print("3. 📄 Document Management")
        print("4. ⚠️ Expiry Alerts")
        print("5. 🚚 Truck Status")
        print("6. 💰 Earnings")
        print("7. 👤 Profile Management")
        print("8. 📊 Performance Stats")
        print("9. 🚪 Logout")
        
        choice = input("\nSelect option: ").strip()
        return choice
    
    def expert_menu(self):
        """Expert-specific menu"""
        print("\n👨‍🔧 EXPERT MENU")
        print("=" * 30)
        print("1. 🟢 Go Online / Offline")
        print("2. 📥 Incoming Expert Requests")
        print("3. 💬 Active Consultations")
        print("4. 📊 Performance & Case Insights")
        print("5. 🛡️ Professional Profile & Status")
        print("6. 🚪 Logout")
        
        choice = input("\nSelect option: ").strip()
        return choice
    
    def default_menu(self):
        """Default worker menu"""
        print("\n👤 WORKER MENU")
        print("=" * 30)
        print("1. 📋 Available Tasks")
        print("2. 🚗 Active Jobs")
        print("3. 📄 Job History")
        print("4. 👤 Profile Management")
        print("5. 📊 Performance Stats")
        print("6. 🚪 Logout")
        
        choice = input("\nSelect option: ").strip()
        return choice
    
    def handle_menu_choice(self, choice):
        """Handle menu choice based on worker type"""
        if self.worker_type == 'MECHANIC':
            self.handle_mechanic_choice(choice)
        elif self.worker_type == 'FUEL_AGENT':
            self.handle_fuel_agent_choice(choice)
        elif self.worker_type == 'TOW_TRUCK':
            self.handle_tow_truck_choice(choice)
        elif self.worker_type == 'EXPERT':
            self.handle_expert_choice(choice)
        else:
            self.handle_default_choice(choice)
    
    def handle_mechanic_choice(self, choice):
        """Handle mechanic menu choices"""
        if choice == '1':
            self.show_available_jobs()
        elif choice == '2':
            self.show_appointments()
        elif choice == '3':
            self.show_service_history()
        elif choice == '4':
            self.show_earnings()
        elif choice == '5':
            self.profile_management()
        elif choice == '6':
            self.show_performance_stats()
        elif choice == '7':
            self.logout()
            return False
        else:
            print("❌ Invalid option")
            input("\nPress Enter to continue...")
        return True
    
    def handle_fuel_agent_choice(self, choice):
        """Handle fuel agent menu choices"""
        if choice == '1':
            self.show_available_deliveries()
        elif choice == '2':
            self.show_delivery_history()
        elif choice == '3':
            self.upload_proof()
        elif choice == '4':
            self.show_earnings()
        elif choice == '5':
            self.route_management()
        elif choice == '6':
            self.profile_management()
        elif choice == '7':
            self.show_performance_stats()
        elif choice == '8':
            self.logout()
            return False
        else:
            print("❌ Invalid option")
            input("\nPress Enter to continue...")
        return True
    
    def handle_tow_truck_choice(self, choice):
        """Handle tow truck menu choices"""
        if choice == '1':
            self.show_available_requests()
        elif choice == '2':
            self.show_active_jobs()
        elif choice == '3':
            self.document_management()
        elif choice == '4':
            self.show_expiry_alerts()
        elif choice == '5':
            self.truck_status()
        elif choice == '6':
            self.show_earnings()
        elif choice == '7':
            self.profile_management()
        elif choice == '8':
            self.show_performance_stats()
        elif choice == '9':
            self.logout()
            return False
        else:
            print("❌ Invalid option")
            input("\nPress Enter to continue...")
        return True
    
    def handle_expert_choice(self, choice):
        """Handle expert menu choices"""
        if choice == '1':
            self.toggle_online_status()
        elif choice == '2':
            self.view_incoming_requests()
        elif choice == '3':
            self.active_consultations()
        elif choice == '4':
            self.performance_insights()
        elif choice == '5':
            self.professional_profile()
        elif choice == '6':
            self.logout()
            return False
        else:
            print("❌ Invalid option")
            input("\nPress Enter to continue...")
        return True
    
    def handle_default_choice(self, choice):
        """Handle default menu choices"""
        if choice == '1':
            self.show_available_jobs()
        elif choice == '2':
            self.show_active_jobs()
        elif choice == '3':
            self.show_job_history()
        elif choice == '4':
            self.profile_management()
        elif choice == '5':
            self.show_performance_stats()
        elif choice == '6':
            self.logout()
            return False
        else:
            print("❌ Invalid option")
            input("\nPress Enter to continue...")
        return True
    
    # Placeholder methods for all worker types
    def show_available_jobs(self):
        """Show available jobs/tasks"""
        self.clear_screen()
        print("📋 AVAILABLE JOBS")
        print("=" * 30)
        print("🔄 Loading available jobs...")
        # TODO: Implement based on worker type
        input("\nPress Enter to continue...")
    
    def show_appointments(self):
        """Show appointments"""
        self.clear_screen()
        print("📅 APPOINTMENTS")
        print("=" * 30)
        print("🔄 Loading appointments...")
        # TODO: Implement appointment fetching
        input("\nPress Enter to continue...")
    
    def show_service_history(self):
        """Show service/job history"""
        self.clear_screen()
        print("🚗 SERVICE HISTORY")
        print("=" * 30)
        print("🔄 Loading service history...")
        # TODO: Implement history fetching
        input("\nPress Enter to continue...")
    
    def show_earnings(self):
        """Show earnings information"""
        self.clear_screen()
        print("💰 EARNINGS")
        print("=" * 30)
        print("🔄 Loading earnings data...")
        # TODO: Implement earnings calculation
        input("\nPress Enter to continue...")
    
    def profile_management(self):
        """Profile management interface"""
        self.clear_screen()
        print("👤 PROFILE MANAGEMENT")
        print("=" * 30)
        print("1. 📝 Edit Profile")
        print("2. 📄 Upload Documents")
        print("3. 📊 Document Status")
        print("4. ⬅️ Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        if choice == '4':
            return
        
        # TODO: Implement profile management
        print("🔄 Loading profile management...")
        input("\nPress Enter to continue...")
    
    def show_performance_stats(self):
        """Show performance statistics"""
        self.clear_screen()
        print("📊 PERFORMANCE STATS")
        print("=" * 30)
        print("🔄 Loading performance data...")
        # TODO: Implement performance stats
        input("\nPress Enter to continue...")
    
    # Expert-specific methods
    def toggle_online_status(self):
        """Toggle expert online/offline status"""
        self.clear_screen()
        print("🟢 TOGGLE ONLINE STATUS")
        print("=" * 30)
        print("Current Status: 🟢 ONLINE")
        print("Toggle status? (online/offline/back): ")
        # TODO: Implement status toggle
        input("\nPress Enter to continue...")
    
    def view_incoming_requests(self):
        """View incoming expert requests"""
        self.clear_screen()
        print("📥 INCOMING REQUESTS")
        print("=" * 30)
        print("🔄 Loading incoming requests...")
        # TODO: Implement request fetching
        input("\nPress Enter to continue...")
    
    def active_consultations(self):
        """Manage active consultations"""
        self.clear_screen()
        print("💬 ACTIVE CONSULTATIONS")
        print("=" * 30)
        print("🔄 Loading active consultations...")
        # TODO: Implement consultation management
        input("\nPress Enter to continue...")
    
    def performance_insights(self):
        """Show performance insights"""
        self.clear_screen()
        print("📊 PERFORMANCE INSIGHTS")
        print("=" * 30)
        print("🔄 Loading performance insights...")
        # TODO: Implement insights
        input("\nPress Enter to continue...")
    
    def professional_profile(self):
        """Professional profile management"""
        self.clear_screen()
        print("🛡️ PROFESSIONAL PROFILE")
        print("=" * 30)
        print("🔄 Loading professional profile...")
        # TODO: Implement professional profile
        input("\nPress Enter to continue...")
    
    # Fuel Agent specific methods
    def show_available_deliveries(self):
        """Show available deliveries"""
        self.clear_screen()
        print("🚗 AVAILABLE DELIVERIES")
        print("=" * 30)
        print("🔄 Loading available deliveries...")
        # TODO: Implement delivery fetching
        input("\nPress Enter to continue...")
    
    def show_delivery_history(self):
        """Show delivery history"""
        self.clear_screen()
        print("📋 DELIVERY HISTORY")
        print("=" * 30)
        print("🔄 Loading delivery history...")
        # TODO: Implement history
        input("\nPress Enter to continue...")
    
    def upload_proof(self):
        """Upload delivery proof"""
        self.clear_screen()
        print("📤 UPLOAD PROOF")
        print("=" * 30)
        print("🔄 Loading upload interface...")
        # TODO: Implement proof upload
        input("\nPress Enter to continue...")
    
    def route_management(self):
        """Manage delivery routes"""
        self.clear_screen()
        print("📍 ROUTE MANAGEMENT")
        print("=" * 30)
        print("🔄 Loading route management...")
        # TODO: Implement route management
        input("\nPress Enter to continue...")
    
    # Tow Truck specific methods
    def show_available_requests(self):
        """Show available tow requests"""
        self.clear_screen()
        print("📋 AVAILABLE REQUESTS")
        print("=" * 30)
        print("🔄 Loading available requests...")
        # TODO: Implement request fetching
        input("\nPress Enter to continue...")
    
    def show_active_jobs(self):
        """Show active tow jobs"""
        self.clear_screen()
        print("🚗 ACTIVE JOBS")
        print("=" * 30)
        print("🔄 Loading active jobs...")
        # TODO: Implement active jobs
        input("\nPress Enter to continue...")
    
    def document_management(self):
        """Manage tow truck documents"""
        self.clear_screen()
        print("📄 DOCUMENT MANAGEMENT")
        print("=" * 30)
        print("🔄 Loading document management...")
        # TODO: Implement document management
        input("\nPress Enter to continue...")
    
    def show_expiry_alerts(self):
        """Show document expiry alerts"""
        self.clear_screen()
        print("⚠️ EXPIRY ALERTS")
        print("=" * 30)
        print("🔄 Loading expiry alerts...")
        # TODO: Implement expiry alerts
        input("\nPress Enter to continue...")
    
    def truck_status(self):
        """Show truck status"""
        self.clear_screen()
        print("🚚 TRUCK STATUS")
        print("=" * 30)
        print("🔄 Loading truck status...")
        # TODO: Implement truck status
        input("\nPress Enter to continue...")
    
    def show_job_history(self):
        """Show job history"""
        self.clear_screen()
        print("🚗 JOB HISTORY")
        print("=" * 30)
        print("🔄 Loading job history...")
        # TODO: Implement job history
        input("\nPress Enter to continue...")
    
    def logout(self):
        """Logout from dashboard"""
        self.clear_screen()
        print("🚪 LOGOUT")
        print("=" * 30)
        print("👋 Logging out...")
        print("🔐 Session terminated")
        self.running = False
    
    def run(self):
        """Main dashboard loop"""
        while self.running:
            self.print_header()
            choice = self.show_main_menu()
            
            if choice:
                continue_running = self.handle_menu_choice(choice)
                if not continue_running:
                    break


def unified_worker_dashboard(worker_id: int, worker_type: str, token: str):
    """Main entry point for unified worker dashboard"""
    try:
        dashboard = UnifiedWorkerDashboard(worker_id, worker_type, token)
        dashboard.run()
        
    except KeyboardInterrupt:
        print("\n👋 Worker dashboard exited by user")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        input("\nPress Enter to continue...")
