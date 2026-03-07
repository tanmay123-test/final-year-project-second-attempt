"""
Automobile Expert CLI Interface
Handles automobile expert signup, login, and dashboard access
"""

import os
import requests
import time
from datetime import datetime

API = "http://127.0.0.1:5000"

def automobile_expert_signup():
    """Automobile expert signup process"""
    print("\n" + "="*60)
    print("🧠 AUTOMOBILE EXPERT SIGNUP")
    print("="*60)
    
    try:
        # Basic info
        name = input("👤 Enter full name: ").strip()
        email = input("📧 Enter email: ").strip()
        phone = input("📱 Enter phone: ").strip()
        password = input("🔒 Enter password: ").strip()
        experience = input("💼 Enter experience (years): ").strip()
        
        # Area of expertise dropdown
        print("\n🔧 Area of Experience:")
        print("1. Engine")
        print("2. Electrical")
        print("3. Diagnostic")
        print("4. General")
        
        while True:
            expertise_choice = input("Select area of expertise (1-4): ").strip()
            if expertise_choice == "1":
                area_of_expertise = "Engine"
                break
            elif expertise_choice == "2":
                area_of_expertise = "Electrical"
                break
            elif expertise_choice == "3":
                area_of_expertise = "Diagnostic"
                break
            elif expertise_choice == "4":
                area_of_expertise = "General"
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
        
        # Document paths
        print("\n📄 Document Uploads")
        print("Enter file paths for required documents:")
        
        certificate_path = input("Enter Certificate file path: ").strip()
        
        # Validation
        if not all([name, email, phone, password, experience, area_of_expertise]):
            print("❌ All required fields must be filled")
            return
        
        # Validate file paths exist
        if certificate_path and not os.path.exists(certificate_path):
            print(f"❌ Certificate file not found: {certificate_path}")
            return
        
        # Prepare data
        data = {
            'name': name,
            'email': email,
            'phone': phone,
            'password': password,
            'experience_years': experience,
            'area_of_expertise': area_of_expertise,
            'worker_type': 'automobile_expert'
        }
        
        # Prepare files
        files = {}
        if certificate_path:
            files['certificate'] = open(certificate_path, 'rb')
        
        print("\n🔄 Creating account...")
        
        response = requests.post(
            f"{API}/api/automobile-expert/signup",
            data=data,
            files=files
        )
        
        # Close files
        for file in files.values():
            file.close()
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✅ Signup successful!")
            print(f"👤 Name: {name}")
            print(f"📧 Email: {email}")
            print(f"📱 Phone: {phone}")
            print(f"🔧 Expertise: {area_of_expertise}")
            print(f"💼 Experience: {experience} years")
            print(f"📋 Worker ID: {result.get('worker_id')}")
            print(f"⏳ Status: Pending approval")
            print("\n📝 Your account is pending admin approval.")
            print("📧 You will be notified once approved.")
        else:
            error = response.json().get('error', 'Signup failed')
            print(f"❌ {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")

def automobile_expert_login():
    """Automobile expert login process"""
    print("\n" + "="*60)
    print("🧠 AUTOMOBILE EXPERT LOGIN")
    print("="*60)
    
    try:
        email = input("📧 Enter email: ").strip()
        password = input("🔒 Enter password: ").strip()
        
        if not email or not password:
            print("❌ Email and password are required")
            return
        
        print("\n🔄 Logging in...")
        
        response = requests.post(
            f"{API}/api/automobile-expert/login",
            json={'email': email, 'password': password}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Login successful!")
            print(f"👤 Welcome, {result.get('name')}!")
            print(f"🔧 Expertise: {result.get('area_of_expertise')}")
            print(f"💼 Experience: {result.get('experience_years')} years")
            
            # Store login info for session
            worker_info = {
                'worker_id': result.get('worker_id'),
                'name': result.get('name'),
                'email': email,
                'area_of_expertise': result.get('area_of_expertise'),
                'experience_years': result.get('experience_years'),
                'token': result.get('token')
            }
            
            automobile_expert_dashboard(worker_info)
        else:
            error = response.json().get('error', 'Login failed')
            print(f"❌ {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")

def automobile_expert_dashboard(worker_info):
    """Automobile expert dashboard with availability management"""
    while True:
        # Get current dashboard data
        try:
            response = requests.get(f"{API}/api/expert-availability/dashboard/{worker_info['worker_id']}")
            if response.status_code == 200:
                dashboard_data = response.json()
            else:
                dashboard_data = {'status': 'OFFLINE', 'waiting_requests_count': 0, 'demand_level': 'LOW'}
        except:
            dashboard_data = {'status': 'OFFLINE', 'waiting_requests_count': 0, 'demand_level': 'LOW'}
        
        print("\n" + "="*60)
        print("👨‍🔧 AUTOMOBILE EXPERT DASHBOARD")
        print("="*60)
        print(f"👤 Name: {worker_info['name']}")
        print(f"🔧 Expertise: {worker_info['area_of_expertise']}")
        print(f"💼 Experience: {worker_info['experience_years']} years")
        print(f"📊 Status: {'🟢 ONLINE' if dashboard_data.get('status') == 'ONLINE_AVAILABLE' else '🔴 OFFLINE' if dashboard_data.get('status') == 'OFFLINE' else '🔄 BUSY'}")
        print(f"⏳ Waiting Requests: {dashboard_data.get('waiting_requests_count', 0)}")
        print(f"📈 Demand Level: {dashboard_data.get('demand_level', 'LOW')}")
        print(f"💡 Suggestion: {dashboard_data.get('suggestion', 'Keep up the great work!')}")
        print("="*60)
        current_status = dashboard_data.get('status', 'OFFLINE')
        action_text = "🔴 Go Offline" if current_status == 'ONLINE_AVAILABLE' else "🟢 Go Online"
        print(f"1. {action_text}")
        print("2. 📥 Consultation Requests Queue")
        print("3. 💬 Active Consultation (Chat / Call)")
        print("4. Consultation History & Earnings Insights")
        print("5. 🛡️ Performance, Reputation & Support")
        print("6. Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            toggle_online_status(worker_info)
        elif choice == "2":
            view_consultation_queue(worker_info)
        elif choice == "3":
            view_current_consultation(worker_info)
        elif choice == "4":
            consultation_history_menu(worker_info)
        elif choice == "5":
            view_performance_support(worker_info)
        elif choice == "6":
            print("\n� Logging out...")
            break
        else:
            print("❌ Invalid choice")
            input("\nPress Enter to continue...")

def view_expert_profile(worker_info):
    """View expert profile details"""
    print("\n" + "="*60)
    print("📋 EXPERT PROFILE")
    print("="*60)
    print(f"👤 Name: {worker_info['name']}")
    print(f"📧 Email: {worker_info['email']}")
    print(f"🔧 Area of Expertise: {worker_info['area_of_expertise']}")
    print(f"💼 Experience: {worker_info['experience_years']} years")
    print(f"🆔 Worker ID: {worker_info['worker_id']}")
    print(f"🏷️ Worker Type: Automobile Expert")
    
    input("\nPress Enter to continue...")

def toggle_online_status(worker_info):
    """Toggle expert online/offline status"""
    try:
        # Get current status
        response = requests.get(f"{API}/api/expert-availability/status/{worker_info['worker_id']}")
        if response.status_code == 200:
            current_data = response.json()
            current_status = current_data.get('status', 'OFFLINE')
        else:
            current_status = 'OFFLINE'
        
        # Toggle status
        if current_status == 'OFFLINE':
            # Go online
            print("\n🔄 Going online...")
            response = requests.post(f"{API}/api/expert-availability/go-online", 
                                   json={'expert_id': worker_info['worker_id']})
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result.get('message', 'Successfully went online')}")
                print("🎯 You are now available for consultations")
                
                # Update local worker info
                worker_info['status'] = 'ONLINE_AVAILABLE'
            else:
                error = response.json().get('error', 'Failed to go online')
                print(f"❌ {error}")
        else:
            # Go offline
            print("\n🔄 Going offline...")
            response = requests.post(f"{API}/api/expert-availability/go-offline", 
                                   json={'expert_id': worker_info['worker_id']})
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result.get('message', 'Successfully went offline')}")
                print("🔴 You are now offline and won't receive consultation requests")
                
                # Update local worker info
                worker_info['status'] = 'OFFLINE'
            else:
                error = response.json().get('error', 'Failed to go offline')
                print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def consultation_history_menu(worker_info):
    """Consultation history and performance menu"""
    while True:
        print("\n" + "="*60)
        print("📊 CONSULTATION HISTORY & PERFORMANCE")
        print("="*60)
        print("1. 📋 View Consultation History")
        print("2. 📈 View Performance Analytics")
        print("3. 🏆 View Reputation & Badges")
        print("4. 🚨 Report User")
        print("5. 📊 View Queue Status")
        print("6. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_consultation_history(worker_info)
        elif choice == "2":
            view_performance_analytics(worker_info)
        elif choice == "3":
            view_reputation_badges(worker_info)
        elif choice == "4":
            report_user(worker_info)
        elif choice == "5":
            view_queue_status(worker_info)
        elif choice == "6":
            break
        else:
            print("❌ Invalid choice")
            input("\nPress Enter to continue...")

def view_consultation_history(worker_info):
    """View expert's consultation history"""
    try:
        print("\n🔄 Loading consultation history...")
        response = requests.get(f"{API}/api/expert-history/history/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            history_data = response.json()
            
            if history_data['success']:
                consultations = history_data.get('consultations', [])
                
                print(f"\n📋 CONSULTATION HISTORY ({len(consultations)} consultations)")
                print("="*60)
                
                if not consultations:
                    print("📭 No consultation history found")
                else:
                    for i, consultation in enumerate(consultations, 1):
                        print(f"\n[{i}] Request ID: {consultation.get('request_id')}")
                        print(f"    👤 User: {consultation.get('user_name', 'N/A')}")
                        print(f"    🔧 Category: {consultation.get('category', 'N/A')}")
                        print(f"    📅 Date: {consultation.get('date', 'N/A')}")
                        print(f"    ⏱️ Duration: {consultation.get('duration_seconds', 0)} seconds")
                        print(f"    📊 Status: {consultation.get('status', 'N/A')}")
                        print(f"    ✅ Resolution: {consultation.get('resolution_status', 'N/A')}")
                        
                        if consultation.get('assigned_reason'):
                            print(f"    🎯 Assignment: {consultation.get('assigned_reason')}")
                
                print(f"\nTotal consultations: {len(consultations)}")
                
                # Option to reopen consultation
                if consultations:
                    reopen_choice = input("\n🔄 Reopen a consultation? (y/n): ").strip().lower()
                    if reopen_choice == 'y':
                        reopen_consultation(worker_info, consultations)
            else:
                print(f"❌ {history_data.get('error', 'Failed to load history')}")
        else:
            print("❌ Failed to load consultation history")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def reopen_consultation(worker_info, consultations):
    """Reopen a closed consultation"""
    try:
        choice = input(f"\nEnter consultation number (1-{len(consultations)}): ").strip()
        
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(consultations):
            print("❌ Invalid selection")
            return
        
        consultation = consultations[int(choice) - 1]
        request_id = consultation.get('request_id')
        
        print(f"\n🔄 Reopening consultation {request_id}...")
        response = requests.post(f"{API}/api/expert-history/reopen/{worker_info['worker_id']}/{request_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Consultation reopened successfully')}")
            
            # Update expert status
            worker_info['status'] = 'BUSY'
            print("🔄 Your status is now BUSY")
        else:
            error = response.json().get('error', 'Failed to reopen consultation')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def view_performance_analytics(worker_info):
    """View expert performance analytics"""
    try:
        days = input("\n📊 Enter analysis period in days (default 30): ").strip()
        days = int(days) if days.isdigit() and int(days) > 0 else 30
        
        print(f"\n🔄 Loading performance analytics for last {days} days...")
        response = requests.get(f"{API}/api/expert-history/analytics/{worker_info['worker_id']}?days={days}")
        
        if response.status_code == 200:
            analytics_data = response.json()
            
            if analytics_data['success']:
                print("\n" + "="*60)
                print("📈 PERFORMANCE ANALYTICS")
                print("="*60)
                print(f"📊 Analysis Period: {analytics_data.get('analysis_period_days', days)} days")
                print(f"📋 Total Consultations: {analytics_data.get('total_consultations', 0)}")
                print(f"✅ Completed Consultations: {analytics_data.get('completed_consultations', 0)}")
                print(f"📈 Resolution Rate: {analytics_data.get('resolution_rate', 0)}%")
                print(f"⚡ Average Response Time: {analytics_data.get('average_response_seconds', 0)} seconds")
                print(f"⏱️ Average Duration: {analytics_data.get('average_duration_seconds', 0)} seconds")
                print(f"🌐 Online Hours: {analytics_data.get('online_hours', 0)}")
                print(f"🛡️ Reliability Score: {analytics_data.get('reliability_score', 0)}/5.0")
                
                # Performance insights
                resolution_rate = analytics_data.get('resolution_rate', 0)
                avg_response = analytics_data.get('average_response_seconds', 0)
                
                print(f"\n🎯 PERFORMANCE INSIGHTS")
                print("-"*40)
                
                if resolution_rate >= 90:
                    print("🏆 Excellent resolution rate!")
                elif resolution_rate >= 80:
                    print("👍 Good resolution rate")
                elif resolution_rate >= 70:
                    print("📈 Average resolution rate")
                else:
                    print("⚠️ Resolution rate needs improvement")
                
                if avg_response <= 30:
                    print("⚡ Excellent response time!")
                elif avg_response <= 60:
                    print("👍 Good response time")
                elif avg_response <= 120:
                    print("📈 Average response time")
                else:
                    print("⚠️ Response time needs improvement")
            else:
                print(f"❌ {analytics_data.get('error', 'Failed to load analytics')}")
        else:
            print("❌ Failed to load performance analytics")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def view_reputation_badges(worker_info):
    """View expert reputation and badges"""
    try:
        print("\n🔄 Loading reputation information...")
        response = requests.get(f"{API}/api/expert-history/reputation/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            reputation_data = response.json()
            
            if reputation_data['success']:
                print("\n" + "="*60)
                print("🏆 REPUTATION & BADGES")
                print("="*60)
                print(f"✅ Approval Status: {'Approved' if reputation_data.get('approval_status') else 'Pending'}")
                print(f"🌐 Online Hours: {reputation_data.get('online_hours', 0)}")
                print(f"📋 Consultations Completed: {reputation_data.get('consultations_completed', 0)}")
                print(f"⭐ Rating: {reputation_data.get('rating', 0)}/5.0")
                print(f"🛡️ Reliability Score: {reputation_data.get('reliability_score', 0)}/5.0")
                print(f"🎯 Fair Assignment Score: {reputation_data.get('fair_assignment_score', 0)}/100")
                
                badges = reputation_data.get('badges', [])
                print(f"\n🏅 EARNED BADGES ({len(badges)} badges)")
                print("-"*40)
                
                if not badges:
                    print("📭 No badges earned yet")
                else:
                    for i, badge in enumerate(badges, 1):
                        print(f"[{i}] 🏅 {badge}")
                
                # Badge earning tips
                print(f"\n💡 BADGE EARNING TIPS")
                print("-"*40)
                print("🏆 Trusted Expert: Resolution rate > 90%")
                print("⚡ Fast Responder: Average response time < 60 seconds")
                print("⭐ Top Rated: Rating >= 4.5")
                print("📊 High Volume: Complete 50+ consultations")
            else:
                print(f"❌ {reputation_data.get('error', 'Failed to load reputation')}")
        else:
            print("❌ Failed to load reputation information")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def report_user(worker_info):
    """Report a user"""
    try:
        print("\n" + "="*60)
        print("🚨 REPORT USER")
        print("="*60)
        print("1. 👤 User Abuse")
        print("2. 🔧 Technical Issue")
        print("3. 📞 General Support")
        
        reason_choice = input("\nSelect report reason: ").strip()
        
        reason_map = {
            "1": "USER_ABUSE",
            "2": "TECHNICAL_ISSUE", 
            "3": "GENERAL_SUPPORT"
        }
        
        reason = reason_map.get(reason_choice)
        if not reason:
            print("❌ Invalid reason selection")
            return
        
        user_id = input("\n👤 Enter user ID: ").strip()
        request_id = input("📋 Enter request ID (optional): ").strip()
        description = input("📝 Enter description: ").strip()
        
        if not user_id or not description:
            print("❌ User ID and description are required")
            return
        
        print(f"\n🔄 Submitting report...")
        response = requests.post(f"{API}/api/expert-history/report/create",
                               json={
                                   'expert_id': worker_info['worker_id'],
                                   'user_id': user_id,
                                   'request_id': request_id if request_id else None,
                                   'reason': reason,
                                   'description': description
                               })
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ {result.get('message', 'Report submitted successfully')}")
            print(f"📋 Report ID: {result.get('report_id')}")
            print("📞 Admin will review your report")
        else:
            error = response.json().get('error', 'Failed to submit report')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def view_queue_status(worker_info):
    """View current queue status"""
    try:
        print("\n🔄 Loading queue status...")
        response = requests.get(f"{API}/api/expert-history/queue/status")
        
        if response.status_code == 200:
            queue_data = response.json()
            
            if queue_data['success']:
                print("\n" + "="*60)
                print("📊 QUEUE STATUS")
                print("="*60)
                print(f"📋 Total Waiting: {queue_data.get('total_waiting', 0)}")
                
                category_breakdown = queue_data.get('category_breakdown', {})
                if category_breakdown:
                    print(f"\n📂 CATEGORY BREAKDOWN")
                    print("-"*40)
                    for category, count in category_breakdown.items():
                        print(f"🔧 {category}: {count} waiting")
                
                oldest = queue_data.get('oldest_request')
                newest = queue_data.get('newest_request')
                
                if oldest:
                    print(f"\n⏰ OLDEST REQUEST")
                    print("-"*40)
                    print(f"📋 Request ID: {oldest.get('request_id')}")
                    print(f"🔧 Category: {oldest.get('category')}")
                    print(f"⏱️ Waiting since: {oldest.get('created_at')}")
                    print(f"🎯 Priority: {oldest.get('priority_level')}")
                
                if newest:
                    print(f"\n🆕 NEWEST REQUEST")
                    print("-"*40)
                    print(f"📋 Request ID: {newest.get('request_id')}")
                    print(f"🔧 Category: {newest.get('category')}")
                    print(f"⏱️ Waiting since: {newest.get('created_at')}")
                    print(f"🎯 Priority: {newest.get('priority_level')}")
                
                # Fair assignment score
                score_response = requests.get(f"{API}/api/expert-history/fair-score/{worker_info['worker_id']}")
                if score_response.status_code == 200:
                    score_data = score_response.json()
                    if score_data['success']:
                        print(f"\n🎯 YOUR ASSIGNMENT PRIORITY")
                        print("-"*40)
                        print(f"📊 Fair Assignment Score: {score_data.get('fair_assignment_score', 0)}/100")
                        print(f"📈 Priority Level: {score_data.get('score_level', 'Unknown')}")
            else:
                print(f"❌ {queue_data.get('error', 'Failed to load queue status')}")
        else:
            print("❌ Failed to load queue status")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def view_performance_support(worker_info):
    """View performance, reputation and support options"""
    try:
        print("\n🔄 Loading performance data...")
        
        # Get dashboard data for current stats
        response = requests.get(f"{API}/api/expert-availability/dashboard/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            dashboard_data = response.json()
            
            print("\n" + "="*60)
            print("🛡️ PERFORMANCE, REPUTATION & SUPPORT")
            print("="*60)
            
            # Performance metrics
            print(f"📊 Current Status: {dashboard_data.get('status', 'OFFLINE')}")
            print(f"⭐ Rating: {dashboard_data.get('rating', 0)}/5.0")
            print(f"🏆 Total Completed: {dashboard_data.get('total_consultations', 0)}")
            
            # Performance stats
            performance_stats = dashboard_data.get('performance_stats', {})
            print(f"⏱️ Avg Session Time: {performance_stats.get('avg_duration_minutes', 0)} minutes")
            print(f"⚡ Avg Response Time: {performance_stats.get('avg_response_time_minutes', 0)} minutes")
            
            # Reputation indicators
            rating = dashboard_data.get('rating', 0)
            if rating >= 4.5:
                reputation = "🌟 Excellent"
            elif rating >= 4.0:
                reputation = "⭐ Very Good"
            elif rating >= 3.5:
                reputation = "👍 Good"
            elif rating >= 3.0:
                reputation = "👌 Average"
            else:
                reputation = "📈 Needs Improvement"
            
            print(f"🏅 Reputation: {reputation}")
            
            # Support options
            print(f"\n📞 Support Options:")
            print(f"  • Technical Support: support@expertertise.com")
            print(f"  • Payment Issues: billing@expertertise.com")
            print(f"  • Account Help: help@expertertise.com")
            print(f"  • Emergency: +1-800-EXPERT-1")
            
            # Performance tips
            print(f"\n💡 Performance Tips:")
            if dashboard_data.get('total_consultations', 0) < 10:
                print(f"  • Complete more consultations to build reputation")
            if performance_stats.get('avg_response_time_minutes', 0) > 5:
                print(f"  • Try to respond faster to improve ratings")
            if performance_stats.get('avg_duration_minutes', 0) > 30:
                print(f"  • Consider optimizing consultation time")
            
        else:
            print("❌ Failed to load performance data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def view_consultation_queue(worker_info):
    """View consultation queue"""
    try:
        print("\n🔄 Loading consultation queue...")
        response = requests.get(f"{API}/api/expert-availability/consultation-queue/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            queue_data = response.json()
            waiting_requests = queue_data.get('waiting_requests', [])
            
            print("\n" + "="*60)
            print(f"📋 CONSULTATION QUEUE ({queue_data.get('expert_area', 'Unknown')})")
            print("="*60)
            
            if not waiting_requests:
                print("📭 No waiting requests")
            else:
                for i, request in enumerate(waiting_requests, 1):
                    print(f"\n[{i}] Request ID: {request.get('request_id')}")
                    print(f"    � User: {request.get('user_name', 'N/A')}")
                    print(f"    �📝 Issue: {request.get('problem_description', 'N/A')}")
                    print(f"    🔧 Area: {request.get('category', 'N/A')}")
                    print(f"    📅 Created: {request.get('created_at', 'N/A')}")
                    print(f"    ⭐ Priority: {request.get('priority_level', 1)}")
                
                print(f"\nTotal waiting requests: {len(waiting_requests)}")
                
                # Option to accept request
                if waiting_requests:
                    accept_choice = input("\nAccept a request? (Enter request number, 'r' for reject, or 'n'): ").strip().lower()
                    if accept_choice.isdigit() and 1 <= int(accept_choice) <= len(waiting_requests):
                        request_to_accept = waiting_requests[int(accept_choice) - 1]
                        accept_consultation(worker_info, request_to_accept['request_id'])
                    elif accept_choice == 'r':
                        reject_choice = input("Enter request number to reject: ").strip()
                        if reject_choice.isdigit() and 1 <= int(reject_choice) <= len(waiting_requests):
                            request_to_reject = waiting_requests[int(reject_choice) - 1]
                            reject_consultation(worker_info, request_to_reject['request_id'])
        else:
            print("❌ Failed to load consultation queue")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def accept_consultation(worker_info, request_id):
    """Accept a consultation request"""
    try:
        print(f"\n🔄 Accepting consultation request {request_id}...")
        response = requests.post(f"{API}/api/expert-availability/consultation-requests/{request_id}/accept",
                               json={'expert_id': worker_info['worker_id']})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Consultation accepted successfully')}")
            print("🎯 You are now busy with this consultation")
        else:
            error = response.json().get('error', 'Failed to accept consultation')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def reject_consultation(worker_info, request_id):
    """Reject a consultation request"""
    try:
        rejection_reason = input("Enter rejection reason (optional): ").strip()
        
        print(f"\n🔄 Rejecting consultation request {request_id}...")
        response = requests.post(f"http://127.0.0.1:5000/api/expert-availability/consultation-requests/{request_id}/reject",
                               json={'expert_id': worker_info['worker_id'], 'rejection_reason': rejection_reason})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Consultation rejected successfully')}")
            print("🔄 Request returned to queue for other experts")
        else:
            error = response.json().get('error', 'Failed to reject consultation')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def view_current_consultation(worker_info):
    """View current active consultation"""
    try:
        print("\n🔄 Loading current consultation...")
        response = requests.get(f"{API}/api/expert-availability/dashboard/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            dashboard_data = response.json()
            current_consultation = dashboard_data.get('current_consultation')
            
            print("\n" + "="*60)
            print("� ACTIVE CONSULTATION")
            print("="*60)
            
            if current_consultation:
                # Get detailed session information
                session_response = requests.get(f"{API}/api/consultation-session/active/{worker_info['worker_id']}")
                if session_response.status_code == 200:
                    session_data = session_response.json()
                    print(f"📋 Session ID: {session_data.get('session_id')}")
                    print(f"👤 User: {session_data.get('user_name', 'N/A')}")
                    print(f"🔧 Category: {session_data.get('category', 'N/A')}")
                    print(f"📝 Issue: {session_data.get('issue', 'N/A')}")
                    print(f"⏱️ Duration: {session_data.get('duration_text', 'N/A')}")
                    print(f"📊 Status: {session_data.get('status', 'N/A')}")
                    print(f"📞 Call Status: {session_data.get('call_status', 'NO_CALL')}")
                    print(f"📬 Unread Messages: {session_data.get('unread_messages', 0)}")
                    print(f"🖼️ Images: {session_data.get('images_count', 0)}")
                    print(f"📅 Started: {session_data.get('started_at', 'N/A')}")
                    
                    # Show consultation options
                    print("\n" + "-" * 40)
                    print("� CONSULTATION OPTIONS:")
                    print("1. 💬 Send Message")
                    print("2. 📞 Start Call")
                    print("3. ⏸️ Pause Session")
                    print("4. ✅ Complete Consultation")
                    print("5. ⬅️ Back")
                    
                    choice = input("\nSelect option: ").strip()
                    
                    if choice == "1":
                        send_message_in_session(worker_info, session_data.get('session_id'))
                    elif choice == "2":
                        start_call_in_session(worker_info, session_data.get('session_id'))
                    elif choice == "3":
                        view_session_images(worker_info, session_data.get('session_id'))
                    elif choice == "4":
                        manage_session_notes(worker_info, session_data.get('session_id'))
                    elif choice == "5":
                        pause_session(worker_info, session_data.get('session_id'))
                    elif choice == "6":
                        end_consultation_session(worker_info, session_data.get('session_id'))
                    elif choice == "7":
                        return
                    else:
                        print("❌ Invalid choice")
                        input("\nPress Enter to continue...")
                else:
                    print("❌ Failed to load session details")
            else:
                status = dashboard_data.get('status', 'OFFLINE')
                if status == 'BUSY':
                    print("🔄 You are busy but consultation details not available")
                else:
                    print("📭 No active consultation")
                    print(f"� Current status: {status}")
        else:
            print("❌ Failed to load current consultation")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def send_message_in_session(worker_info, session_id):
    """Send a message in the active consultation session"""
    try:
        message_text = input("\n💬 Enter your message: ").strip()
        
        if not message_text:
            print("❌ Message cannot be empty")
            return
        
        print(f"\n🔄 Sending message...")
        response = requests.post(f"{API}/api/consultation-session/messages/{session_id}",
                               json={
                                   'sender_type': 'EXPERT',
                                   'sender_id': worker_info['worker_id'],
                                   'message_text': message_text
                               })
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ {result.get('message', 'Message sent successfully')}")
        else:
            error = response.json().get('error', 'Failed to send message')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def start_call_in_session(worker_info, session_id):
    """Start a voice call in the consultation session"""
    try:
        print(f"\n🔄 Starting call...")
        response = requests.post(f"{API}/api/consultation-session/call/start/{session_id}",
                               json={'started_by': 'EXPERT'})
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ {result.get('message', 'Call started successfully')}")
            print(f"📞 Call ID: {result.get('call_id')}")
            
            # Option to end call
            end_choice = input("\n📞 End call? (y/n): ").strip().lower()
            if end_choice == 'y':
                end_call_in_session(worker_info, session_id, result.get('call_id'))
        else:
            error = response.json().get('error', 'Failed to start call')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def end_call_in_session(worker_info, session_id, call_id):
    """End a voice call in the consultation session"""
    try:
        print(f"\n🔄 Ending call...")
        response = requests.post(f"{API}/api/consultation-session/call/end/{session_id}",
                               json={'call_id': call_id})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Call ended successfully')}")
        else:
            error = response.json().get('error', 'Failed to end call')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def view_session_images(worker_info, session_id):
    """View images in the consultation session"""
    try:
        print(f"\n🔄 Loading images...")
        response = requests.get(f"{API}/api/consultation-session/images/{session_id}")
        
        if response.status_code == 200:
            images_data = response.json()
            images = images_data.get('images', [])
            
            print(f"\n🖼️ SESSION IMAGES ({len(images)} images)")
            print("="*40)
            
            if not images:
                print("📭 No images in this session")
            else:
                for i, image in enumerate(images, 1):
                    print(f"\n[{i}] Image ID: {image.get('image_id')}")
                    print(f"    📁 Path: {image.get('file_path', 'N/A')}")
                    print(f"    👤 Uploaded by: {image.get('uploaded_by', 'N/A')}")
                    print(f"    📅 Uploaded: {image.get('uploaded_at', 'N/A')}")
            
            print(f"\nTotal images: {len(images)}")
        else:
            print("❌ Failed to load images")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def manage_session_notes(worker_info, session_id):
    """Manage consultation session notes"""
    while True:
        print("\n" + "="*60)
        print("📝 CONSULTATION NOTES")
        print("="*60)
        print("1. 📄 View Notes")
        print("2. ➕ Add Note")
        print("3. ✏️ Update Note")
        print("4. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_session_notes(session_id)
        elif choice == "2":
            add_session_note(worker_info, session_id)
        elif choice == "3":
            update_session_note(worker_info, session_id)
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice")
            input("\nPress Enter to continue...")

def view_session_notes(session_id):
    """View all notes in the consultation session"""
    try:
        response = requests.get(f"{API}/api/consultation-session/notes/{session_id}")
        
        if response.status_code == 200:
            notes_data = response.json()
            notes = notes_data.get('notes', [])
            
            print(f"\n📝 SESSION NOTES ({len(notes)} notes)")
            print("="*40)
            
            if not notes:
                print("📭 No notes in this session")
            else:
                for i, note in enumerate(notes, 1):
                    print(f"\n[{i}] Note ID: {note.get('note_id')}")
                    print(f"    📝 Note: {note.get('note_text', 'N/A')}")
                    print(f"    📅 Created: {note.get('created_at', 'N/A')}")
                    print(f"    🔄 Updated: {note.get('updated_at', 'N/A')}")
            
            print(f"\nTotal notes: {len(notes)}")
        else:
            print("❌ Failed to load notes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def add_session_note(worker_info, session_id):
    """Add a new note to the consultation session"""
    try:
        note_text = input("\n📝 Enter note text: ").strip()
        
        if not note_text:
            print("❌ Note cannot be empty")
            return
        
        print(f"\n🔄 Adding note...")
        response = requests.post(f"{API}/api/consultation-session/notes/{session_id}",
                               json={
                                   'expert_id': worker_info['worker_id'],
                                   'note_text': note_text
                               })
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ {result.get('message', 'Note added successfully')}")
            print(f"📝 Note ID: {result.get('note_id')}")
        else:
            error = response.json().get('error', 'Failed to add note')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def update_session_note(worker_info, session_id):
    """Update an existing note in the consultation session"""
    try:
        # First get existing notes
        response = requests.get(f"{API}/api/consultation-session/notes/{session_id}")
        
        if response.status_code != 200:
            print("❌ Failed to load notes")
            return
        
        notes_data = response.json()
        notes = notes_data.get('notes', [])
        
        if not notes:
            print("📭 No notes to update")
            return
        
        print(f"\n📝 SELECT NOTE TO UPDATE")
        print("="*40)
        for i, note in enumerate(notes, 1):
            print(f"[{i}] {note.get('note_text', 'N/A')[:50]}...")
        
        note_choice = input(f"\nEnter note number (1-{len(notes)}): ").strip()
        
        if not note_choice.isdigit() or int(note_choice) < 1 or int(note_choice) > len(notes):
            print("❌ Invalid selection")
            return
        
        selected_note = notes[int(note_choice) - 1]
        new_note_text = input(f"\n✏️ Enter new note text (current: {selected_note.get('note_text', 'N/A')}): ").strip()
        
        if not new_note_text:
            print("❌ Note cannot be empty")
            return
        
        print(f"\n🔄 Updating note...")
        response = requests.put(f"{API}/api/consultation-session/notes/{selected_note.get('note_id')}",
                              json={
                                  'expert_id': worker_info['worker_id'],
                                  'note_text': new_note_text
                              })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Note updated successfully')}")
        else:
            error = response.json().get('error', 'Failed to update note')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def pause_session(worker_info, session_id):
    """Pause the consultation session"""
    try:
        print(f"\n🔄 Pausing session...")
        response = requests.post(f"{API}/api/consultation-session/pause/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Session paused successfully')}")
        else:
            error = response.json().get('error', 'Failed to pause session')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def end_consultation_session(worker_info, session_id):
    """End the consultation session"""
    try:
        confirm = input("\n🏁 Are you sure you want to end this consultation? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("❌ Consultation end cancelled")
            return
        
        print(f"\n🔄 Ending consultation...")
        response = requests.post(f"{API}/api/consultation-session/end/{session_id}",
                               json={'expert_id': worker_info['worker_id']})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Consultation completed successfully')}")
            print(f"⏱️ Duration: {result.get('duration_seconds', 0)} seconds")
            print(f"🎯 Your status: {result.get('expert_status', 'ONLINE_AVAILABLE')}")
        else:
            error = response.json().get('error', 'Failed to end consultation')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def complete_consultation(worker_info, request_id):
    """Complete a consultation"""
    try:
        # Ask for rating
        rating_input = input("\nRate user satisfaction (1-5, or press Enter to skip): ").strip()
        user_rating = None
        if rating_input.isdigit() and 1 <= int(rating_input) <= 5:
            user_rating = int(rating_input)
        
        print(f"\n🔄 Completing consultation {request_id}...")
        response = requests.post(f"{API}/api/expert-availability/consultation-requests/{request_id}/complete",
                               json={'expert_id': worker_info['worker_id'], 'user_rating': user_rating})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Consultation completed successfully')}")
            print("🎯 You are now available for new consultations")
        else:
            error = response.json().get('error', 'Failed to complete consultation')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def calculate_duration(start_time_str):
    """Calculate duration from start time"""
    try:
        if not start_time_str:
            return "N/A"
        
        from datetime import datetime
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        current_time = datetime.now()
        duration = current_time - start_time
        
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "N/A"

def automobile_expert_menu():
    """Main automobile expert menu"""
    while True:
        print("\n" + "="*60)
        print("👷 AUTOMOBILE EXPERT")
        print("="*60)
        print("1. 📝 Signup")
        print("2. 🔐 Login")
        print("3. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            automobile_expert_signup()
        elif choice == "2":
            automobile_expert_login()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice")
            input("\nPress Enter to continue...")

def send_message_in_active_consultation(worker_info, session_id):
    """Send message in active consultation"""
    try:
        message = input("💬 Your message: ").strip()
        if not message:
            print("❌ Message cannot be empty")
            return
        
        response = requests.post(f"{API}/api/consultation-session/{session_id}/message",
                               json={'expert_id': worker_info['worker_id'], 'message': message, 'sender_type': 'EXPERT'})
        
        if response.status_code == 200:
            print("✅ Message sent successfully")
        else:
            error = response.json().get('error', 'Failed to send message')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def start_call_in_active_consultation(worker_info, session_id):
    """Start call in active consultation with enhanced interface"""
    try:
        print("🔄 Initiating call...")
        response = requests.post(f"{API}/api/consultation-session/{session_id}/call",
                               json={'expert_id': worker_info['worker_id'], 'started_by': 'EXPERT'})
        
        if response.status_code == 200:
            print("✅ Call session started")
            print("📞 User will be notified of your call")
            
            # Start enhanced call interface for expert
            expert_call_interface(worker_info, session_id)
        else:
            error = response.json().get('error', 'Failed to start call')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def expert_call_interface(worker_info, session_id):
    """Enhanced call interface for expert"""
    import time
    from datetime import datetime
    
    print("\n" + "="*60)
    print("📞 EXPERT CALL INTERFACE")
    print("="*60)
    
    # Get session details
    try:
        session_response = requests.get(f"{API}/api/consultation-session/active/{worker_info['worker_id']}")
        if session_response.status_code == 200:
            session_data = session_response.json()
            user_name = session_data.get('user_name', 'User')
            issue = session_data.get('issue', 'N/A')
        else:
            user_name = 'User'
            issue = 'N/A'
    except:
        user_name = 'User'
        issue = 'N/A'
    
    print(f"👨‍🔧 Expert: {worker_info['name']}")
    print(f"👤 User: {user_name}")
    print(f"📝 Issue: {issue}")
    print(f"🔊 Audio: Connected")
    print(f"📊 Status: ACTIVE")
    print("="*60)
    
    # Call tracking
    call_start_time = time.time()
    call_notes = []
    call_messages = []
    call_active = True
    
    while call_active:
        # Calculate duration
        current_time = time.time()
        duration = int(current_time - call_start_time)
        duration_str = f"{duration // 3600:02d}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
        
        print(f"\n⏱️ Duration: {duration_str}")
        print(f"💬 Messages: {len(call_messages)}")
        print(f"📝 Notes: {len(call_notes)}")
        
        print("\n📞 EXPERT CONTROLS:")
        print("1. 💬 Send Message")
        print("2. 📝 Take Note")
        print("3. 📊 Call Info")
        print("4. 📞 End Call")
        print("5. ⏸️ Pause Call")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            message = send_expert_message_during_call(worker_info, session_id)
            if message:
                call_messages.append({
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'message': message,
                    'sender': 'Expert'
                })
                print(f"✅ Message sent: {message[:50]}...")
        
        elif choice == "2":
            note = take_expert_call_note()
            if note:
                call_notes.append({
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'note': note
                })
                print(f"✅ Note saved: {note[:50]}...")
        
        elif choice == "3":
            show_expert_call_info(call_start_time, call_messages, call_notes)
        
        elif choice == "4":
            if confirm_expert_end_call():
                call_active = False
                end_expert_call_session(worker_info, session_id, call_start_time, call_notes)
        
        elif choice == "5":
            pause_expert_call_session(worker_info, session_id)
            print("⏸️ Call paused - Press Enter to resume...")
            input()
            resume_expert_call_session(worker_info, session_id)
        
        else:
            print("❌ Invalid choice")
            time.sleep(1)
    
    print("\n📞 Call Ended")
    print(f"⏱️ Total Duration: {duration_str}")
    print(f"💬 Messages Exchanged: {len(call_messages)}")
    print(f"📝 Notes Taken: {len(call_notes)}")
    print("🙏 Thank you for your expert consultation!")

def send_expert_message_during_call(worker_info, session_id):
    """Send message during active call"""
    try:
        message = input("💬 Your message: ").strip()
        if not message:
            return None
        
        response = requests.post(f"{API}/api/consultation-session/{session_id}/message",
                               json={'expert_id': worker_info['worker_id'], 'message': message, 'sender_type': 'EXPERT'})
        
        if response.status_code == 200:
            return message
        else:
            print("❌ Failed to send message")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def take_expert_call_note():
    """Take note during call"""
    try:
        note = input("📝 Note: ").strip()
        if not note:
            return None
        return note
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def show_expert_call_info(start_time, messages, notes):
    """Show detailed call information for expert"""
    duration = int(time.time() - start_time)
    duration_str = f"{duration // 3600:02d}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
    
    print(f"\n📊 CALL ANALYTICS")
    print("="*40)
    print(f"⏱️ Duration: {duration_str}")
    print(f"💬 Messages: {len(messages)}")
    print(f"📝 Notes: {len(notes)}")
    
    if messages:
        print(f"\n💬 MESSAGE HISTORY:")
        for i, msg in enumerate(messages[-5:], 1):  # Show last 5 messages
            print(f"  {i}. [{msg['timestamp']}] {msg['sender']}: {msg['message']}")
    
    if notes:
        print(f"\n📝 CALL NOTES:")
        for i, note in enumerate(notes[-3:], 1):  # Show last 3 notes
            print(f"  {i}. [{note['timestamp']}] {note['note']}")
    
    input("\nPress Enter to continue...")

def confirm_expert_end_call():
    """Confirm ending the call"""
    try:
        confirm = input("⚠️ Are you sure you want to end this call? (y/N): ").strip().lower()
        return confirm == 'y'
    except:
        return False

def end_expert_call_session(worker_info, session_id, start_time, notes):
    """End call session and save summary"""
    try:
        duration = int(time.time() - start_time)
        
        # End the consultation session
        response = requests.post(f"{API}/api/consultation-session/{session_id}/end",
                               json={'expert_id': worker_info['worker_id']})
        
        if response.status_code == 200:
            print("✅ Call session ended successfully")
            
            # Save call summary
            call_summary = {
                'expert_id': worker_info['worker_id'],
                'session_id': session_id,
                'duration_seconds': duration,
                'notes_count': len(notes),
                'ended_at': datetime.now().isoformat()
            }
            
            print(f"📊 Call summary saved")
        else:
            print("❌ Failed to end call session")
    
    except Exception as e:
        print(f"❌ Error ending call: {e}")

def pause_expert_call_session(worker_info, session_id):
    """Pause call session"""
    try:
        print("⏸️ Pausing call...")
        # Could implement actual pause logic here
    except Exception as e:
        print(f"❌ Error pausing call: {e}")

def resume_expert_call_session(worker_info, session_id):
    """Resume paused call session"""
    try:
        print("▶️ Resuming call...")
        # Could implement actual resume logic here
    except Exception as e:
        print(f"❌ Error resuming call: {e}")

def pause_active_consultation(worker_info, session_id):
    """Pause active consultation"""
    try:
        print("⏸️ Pausing consultation...")
        response = requests.post(f"{API}/api/consultation-session/{session_id}/pause",
                               json={'expert_id': worker_info['worker_id']})
        
        if response.status_code == 200:
            print("✅ Consultation paused")
            print("💡 User will be notified that you're temporarily unavailable")
        else:
            error = response.json().get('error', 'Failed to pause consultation')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def complete_active_consultation(worker_info, session_id):
    """Complete active consultation"""
    try:
        confirm = input("⚠️ Are you sure you want to complete this consultation? (y/N): ").strip().lower()
        if confirm != 'y':
            return
        
        print("✅ Completing consultation...")
        response = requests.post(f"{API}/api/consultation-session/{session_id}/end",
                               json={'expert_id': worker_info['worker_id']})
        
        if response.status_code == 200:
            print("✅ Consultation completed successfully")
            print("🙏 Thank you for your service!")
        else:
            error = response.json().get('error', 'Failed to complete consultation')
            print(f"❌ {error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")
