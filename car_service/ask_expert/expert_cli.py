"""
Automobile Expert CLI Dashboard
Interactive command-line interface for expert operations
"""

import os
import sys
import json
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_utils import verify_token, generate_token
from .expert_service import expert_service

class ExpertDashboard:
    """Interactive CLI dashboard for Automobile Experts"""
    
    def __init__(self, expert_id: int, token: str):
        self.expert_id = expert_id
        self.token = token
        self.service = expert_service
        self.running = True
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print dashboard header"""
        self.clear_screen()
        print("👨‍🔧 AUTOMOBILE EXPERT DASHBOARD")
        print("=" * 50)
        print(f"🆔 Expert ID: {self.expert_id}")
        print(f"🔐 Token: {self.token[:20]}...")
        print("=" * 50)
    
    def toggle_online_status(self):
        """Toggle expert online/offline status"""
        try:
            print("\n🟢 TOGGLE ONLINE STATUS")
            print("-" * 30)
            
            # Get current status (placeholder - would update in DB)
            current_status = "ONLINE"  # Placeholder
            
            print(f"Current Status: {current_status}")
            choice = input("Toggle status? (online/offline/back): ").strip().lower()
            
            if choice == 'offline':
                print("🔴 Status: OFFLINE - You won't receive new requests")
                # Update status in database
            elif choice == 'online':
                print("🟢 Status: ONLINE - You will receive new requests")
                # Update status in database
            elif choice == 'back':
                return
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error toggling status: {e}")
            input("\nPress Enter to continue...")
    
    def view_incoming_requests(self):
        """View and manage incoming expert requests"""
        try:
            while True:
                self.clear_screen()
                print("📥 INCOMING EXPERT REQUESTS")
                print("=" * 40)
                
                # Get pending requests (placeholder API call)
                requests_data = self.service.get_pending_requests(self.expert_id)
                
                if not requests_data["success"]:
                    print("❌ Failed to load requests")
                    input("\nPress Enter to continue...")
                    return
                
                requests = requests_data["requests"]
                
                if not requests:
                    print("📭 No pending requests")
                    print("\nOptions:")
                    print("1. 🔄 Refresh requests")
                    print("2. ⬅️ Back to main menu")
                else:
                    print(f"📋 You have {len(requests)} pending requests:")
                    for i, req in enumerate(requests[:5], 1):  # Show max 5
                        print(f"\n{i}. 🚗 Request #{req.get('id', 'N/A')}")
                        print(f"   📝 Problem: {req.get('problem_description', 'N/A')[:50]}...")
                        print(f"   🏷️ Category: {req.get('category', 'N/A')}")
                        print(f"   📍 Location: {req.get('user_city', 'N/A')}")
                    
                    if len(requests) > 5:
                        print(f"\n... and {len(requests) - 5} more requests")
                    
                    print("\nOptions:")
                    print("1. 📋 View request details")
                    print("2. ✅ Accept request")
                    print("3. ❌ Reject request")
                    print("4. 🔄 Refresh requests")
                    print("5. ⬅️ Back to main menu")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == '1':
                    self.view_request_details(requests)
                elif choice == '2':
                    self.accept_request(requests)
                elif choice == '3':
                    self.reject_request(requests)
                elif choice == '4':
                    continue  # Refresh
                elif choice == '5':
                    return
                else:
                    print("❌ Invalid option")
                    input("\nPress Enter to continue...")
                    
        except Exception as e:
            print(f"❌ Error loading requests: {e}")
            input("\nPress Enter to continue...")
    
    def view_request_details(self, requests):
        """View detailed information about a specific request"""
        try:
            self.clear_screen()
            print("📋 REQUEST DETAILS")
            print("=" * 30)
            
            req_id = input("Enter Request ID: ").strip()
            
            # Find request
            target_request = None
            for req in requests:
                if str(req.get('id')) == req_id:
                    target_request = req
                    break
            
            if not target_request:
                print("❌ Request not found")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n🚗 Request #{target_request.get('id')}")
            print(f"📝 Problem: {target_request.get('problem_description')}")
            print(f"🏷️ Category: {target_request.get('category')}")
            print(f"📍 Location: {target_request.get('user_city')}")
            print(f"📅 Created: {target_request.get('created_at')}")
            print(f"📊 Status: {target_request.get('status')}")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error viewing request: {e}")
            input("\nPress Enter to continue...")
    
    def accept_request(self, requests):
        """Accept an expert request"""
        try:
            req_id = input("Enter Request ID to accept: ").strip()
            
            # Find request
            target_request = None
            for req in requests:
                if str(req.get('id')) == req_id:
                    target_request = req
                    break
            
            if not target_request:
                print("❌ Request not found")
                input("\nPress Enter to continue...")
                return
            
            # Accept request (placeholder API call)
            result = self.service.assign_expert_to_request(int(req_id))
            
            if result["success"]:
                print("✅ Request accepted successfully!")
                print("🎯 You can now start consultation")
            else:
                print(f"❌ Failed to accept request: {result.get('error')}")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error accepting request: {e}")
            input("\nPress Enter to continue...")
    
    def reject_request(self, requests):
        """Reject an expert request"""
        try:
            req_id = input("Enter Request ID to reject: ").strip()
            
            # Find request
            target_request = None
            for req in requests:
                if str(req.get('id')) == req_id:
                    target_request = req
                    break
            
            if not target_request:
                print("❌ Request not found")
                input("\nPress Enter to continue...")
                return
            
            reason = input("Enter rejection reason: ").strip()
            
            # Reject request (placeholder API call)
            result = self.service.update_request_status(int(req_id), 'REJECTED')
            
            if result["success"]:
                print("✅ Request rejected successfully!")
            else:
                print(f"❌ Failed to reject request: {result.get('error')}")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error rejecting request: {e}")
            input("\nPress Enter to continue...")
    
    def active_consultations(self):
        """Manage active consultations"""
        try:
            while True:
                self.clear_screen()
                print("💬 ACTIVE CONSULTATIONS")
                print("=" * 40)
                
                # Get active consultations (placeholder)
                print("📋 Active Consultations:")
                print("1. 💬 Chat with User")
                print("2. 📷 Upload Images")
                print("3. 📞 Voice Call (placeholder)")
                print("4. ✅ Mark as Resolved")
                print("5. ⬅️ Back to main menu")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == '1':
                    self.chat_consultation()
                elif choice == '2':
                    self.upload_consultation_image()
                elif choice == '3':
                    print("📞 Voice call feature coming soon...")
                    input("\nPress Enter to continue...")
                elif choice == '4':
                    self.resolve_consultation()
                elif choice == '5':
                    return
                else:
                    print("❌ Invalid option")
                    input("\nPress Enter to continue...")
                    
        except Exception as e:
            print(f"❌ Error in consultations: {e}")
            input("\nPress Enter to continue...")
    
    def chat_consultation(self):
        """Chat interface for consultation"""
        try:
            self.clear_screen()
            print("💬 CHAT CONSULTATION")
            print("=" * 30)
            print("Type 'exit' to return to menu")
            print("-" * 30)
            
            while True:
                message = input("\n💬 You: ").strip()
                
                if message.lower() == 'exit':
                    break
                
                # Send message (placeholder API call)
                result = self.service.send_message(
                    1,  # Request ID placeholder
                    self.expert_id,
                    1,  # User ID placeholder
                    message,
                    'expert'
                )
                
                if not result["success"]:
                    print(f"❌ Failed to send: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error in chat: {e}")
            input("\nPress Enter to continue...")
    
    def upload_consultation_image(self):
        """Upload image for consultation"""
        try:
            self.clear_screen()
            print("📷 UPLOAD CONSULTATION IMAGE")
            print("=" * 30)
            
            file_path = input("Enter image path: ").strip().strip('"\'')
            
            if not file_path or not os.path.exists(file_path):
                print("❌ Invalid file path")
                input("\nPress Enter to continue...")
                return
            
            # Upload image (placeholder API call)
            print(f"📤 Uploading: {os.path.basename(file_path)}")
            print("✅ Image uploaded successfully!")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error uploading image: {e}")
            input("\nPress Enter to continue...")
    
    def resolve_consultation(self):
        """Resolve consultation and update stats"""
        try:
            self.clear_screen()
            print("✅ RESOLVE CONSULTATION")
            print("=" * 30)
            
            req_id = input("Enter Request ID: ").strip()
            summary = input("Enter resolution summary: ").strip()
            
            if not req_id or not summary:
                print("❌ Request ID and summary are required")
                input("\nPress Enter to continue...")
                return
            
            # Resolve consultation (placeholder API call)
            result = self.service.resolve_request(int(req_id), self.expert_id)
            
            if result["success"]:
                print("✅ Consultation resolved successfully!")
                print("🎯 Your trust score has increased!")
                print(f"📊 Summary: {summary}")
            else:
                print(f"❌ Failed to resolve: {result.get('error')}")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error resolving consultation: {e}")
            input("\nPress Enter to continue...")
    
    def performance_insights(self):
        """View performance analytics and insights"""
        try:
            self.clear_screen()
            print("📊 PERFORMANCE & INSIGHTS")
            print("=" * 40)
            
            # Get expert profile for stats (placeholder)
            profile_data = self.service.get_expert_document_status(self.expert_id)
            
            print("🎯 Your Performance:")
            print(f"📈 Total Cases Handled: {0}")  # Placeholder
            print(f"⭐ Trust Score: 0.0")  # Placeholder
            print(f"🏆 Rating: 0.0")  # Placeholder
            print(f"🔥 Resolution Rate: 0%")  # Placeholder
            
            print("\n📋 Skill Breakdown:")
            print("   🔧 Engine Systems: 0 cases")
            print("   ⚡ Electrical Systems: 0 cases")
            print("   🔄 Transmission: 0 cases")
            print("   🔍 Diagnostics: 0 cases")
            
            print("\n🏅 Reputation Badge:")
            print("   🥉 Bronze Expert (Trust Score: <70)")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error loading insights: {e}")
            input("\nPress Enter to continue...")
    
    def professional_profile(self):
        """View and update professional profile"""
        try:
            while True:
                self.clear_screen()
                print("🛡️ PROFESSIONAL PROFILE & STATUS")
                print("=" * 40)
                
                print("👤 Profile Information:")
                print("1. 📝 Edit Profile")
                print("2. 📄 Upload Documents")
                print("3. 📊 Document Status")
                print("4. ⬅️ Back to main menu")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == '1':
                    self.edit_profile()
                elif choice == '2':
                    self.upload_documents()
                elif choice == '3':
                    self.check_document_status()
                elif choice == '4':
                    return
                else:
                    print("❌ Invalid option")
                    input("\nPress Enter to continue...")
                    
        except Exception as e:
            print(f"❌ Error in profile: {e}")
            input("\nPress Enter to continue...")
    
    def edit_profile(self):
        """Edit professional profile information"""
        try:
            self.clear_screen()
            print("📝 EDIT PROFILE")
            print("=" * 30)
            
            print("✏️ Profile Editing:")
            print("1. 🏷️ Primary Expertise")
            print("2. 📅 Years of Experience")
            print("3. 💼 Work Type")
            print("4. ⏰ Consultation Hours")
            print("5. 🌍 Languages")
            print("6. ⬅️ Back")
            
            choice = input("\nSelect field to edit: ").strip()
            
            if choice == '6':
                return
            elif choice in ['1', '2', '3', '4', '5']:
                field_names = {
                    '1': 'Primary Expertise',
                    '2': 'Years of Experience',
                    '3': 'Work Type',
                    '4': 'Consultation Hours',
                    '5': 'Languages'
                }
                
                new_value = input(f"Enter new {field_names[choice]}: ").strip()
                
                if new_value:
                    print(f"✅ {field_names[choice]} updated to: {new_value}")
                    # Update in database (placeholder)
                    input("\nPress Enter to continue...")
                else:
                    print("❌ No changes made")
                    input("\nPress Enter to continue...")
            else:
                print("❌ Invalid option")
                input("\nPress Enter to continue...")
                
        except Exception as e:
            print(f"❌ Error editing profile: {e}")
            input("\nPress Enter to continue...")
    
    def upload_documents(self):
        """Upload required documents"""
        try:
            self.clear_screen()
            print("📄 UPLOAD DOCUMENTS")
            print("=" * 30)
            
            print("📋 Required Documents:")
            print("1. 🆔 Government ID (Aadhaar/PAN)")
            print("2. 🛠️ Technical Proof (Certificate/Diploma)")
            print("3. 📄 Optional: LinkedIn Profile")
            print("4. 📄 Optional: Workshop License")
            print("5. ⬅️ Back")
            
            choice = input("\nSelect document type: ").strip()
            
            if choice == '5':
                return
            elif choice in ['1', '2', '3', '4']:
                doc_types = {
                    '1': 'government_id',
                    '2': 'technical_proof',
                    '3': 'linkedin_profile',
                    '4': 'workshop_license'
                }
                
                file_path = input(f"Enter {doc_types[choice]} file path: ").strip().strip('"\'')
                
                if file_path and os.path.exists(file_path):
                    print(f"📤 Uploading {doc_types[choice]}...")
                    # Upload document (placeholder API call)
                    print("✅ Document uploaded successfully!")
                    input("\nPress Enter to continue...")
                else:
                    print("❌ File not found")
                    input("\nPress Enter to continue...")
            else:
                print("❌ Invalid option")
                input("\nPress Enter to continue...")
                
        except Exception as e:
            print(f"❌ Error uploading documents: {e}")
            input("\nPress Enter to continue...")
    
    def check_document_status(self):
        """Check document verification status"""
        try:
            self.clear_screen()
            print("📊 DOCUMENT STATUS")
            print("=" * 30)
            
            # Get document status (placeholder API call)
            result = self.service.get_expert_document_status(self.expert_id)
            
            if result["success"]:
                documents = result["documents"]
                
                print("📋 Your Documents:")
                for doc in documents:
                    status_icon = "✅" if doc["verification_status"] == "APPROVED" else "⏳"
                    print(f"   {status_icon} {doc['document_type'].replace('_', ' ').title()}: {doc['verification_status']}")
                
                if result["missing_documents"]:
                    print(f"\n⚠️ Missing Documents: {', '.join(result['missing_documents'])}")
                
                if result["pending_documents"]:
                    print(f"\n⏳ Pending Verification: {', '.join(result['pending_documents'])}")
                
                if result["upload_complete"] and result["verification_complete"]:
                    print("\n✅ All documents uploaded and verified!")
                elif result["upload_complete"]:
                    print("\n📤 All documents uploaded, awaiting verification")
                else:
                    print("\n❌ Document upload incomplete")
            else:
                print("❌ Failed to load document status")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            input("\nPress Enter to continue...")
    
    def logout(self):
        """Logout from expert dashboard"""
        try:
            self.clear_screen()
            print("🚪 LOGOUT")
            print("=" * 30)
            print("👋 Logging out from expert dashboard...")
            print("🔐 Session terminated")
            self.running = False
            
        except Exception as e:
            print(f"❌ Error during logout: {e}")
    
    def run(self):
        """Main dashboard loop"""
        while self.running:
            self.print_header()
            
            print("👨‍🔧 AUTOMOBILE EXPERT MENU")
            print("=" * 40)
            print("1. 🟢 Go Online / Offline")
            print("2. 📥 Incoming Expert Requests")
            print("3. 💬 Active Consultations")
            print("4. 📊 Performance & Case Insights")
            print("5. 🛡️ Professional Profile & Status")
            print("6. 🚪 Logout")
            
            choice = input("\nSelect option: ").strip()
            
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
                return
            else:
                print("❌ Invalid option")
                input("\nPress Enter to continue...")


def expert_dashboard(expert_id: int, token: str):
    """Main entry point for expert dashboard"""
    try:
        dashboard = ExpertDashboard(expert_id, token)
        dashboard.run()
        
    except KeyboardInterrupt:
        print("\n👋 Expert dashboard exited by user")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        input("\nPress Enter to continue...")
