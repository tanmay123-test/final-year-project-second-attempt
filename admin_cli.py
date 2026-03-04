#!/usr/bin/env python3
"""
Super Admin CLI Interface
Command-line interface for the Super Admin Backend System
"""
import os
import sys
import requests
import json
import getpass
from datetime import datetime

API_BASE = "http://127.0.0.1:5001/api"

class AdminCLI:
    def __init__(self):
        self.token = None
        self.admin_info = None

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        """Print formatted header"""
        self.clear_screen()
        print("=" * 60)
        print(f"🚀 {title}")
        print("=" * 60)

    def login(self):
        """Admin login"""
        self.print_header("ADMIN LOGIN")
        
        username = input("👤 Username: ").strip()
        password = getpass.getpass("🔒 Password: ")
        
        if not username or not password:
            input("❌ Username and password required. Press Enter to continue...")
            return False
        
        try:
            response = requests.post(f"{API_BASE}/admin/login", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token')
                    self.admin_info = data.get('admin', {})
                    print(f"✅ Login successful!")
                    print(f"   Welcome, {self.admin_info.get('full_name', username)}!")
                    print(f"   Role: {self.admin_info.get('role', 'admin')}")
                    input("\nPress Enter to continue...")
                    return True
                else:
                    print(f"❌ Login failed: {data.get('error')}")
            else:
                print(f"❌ Login error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Details: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text[:200]}")
        
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server")
            print("   Make sure backend is running: python app.py")
        except Exception as e:
            print(f"❌ Login error: {e}")
        
        input("\nPress Enter to continue...")
        return False

    def verify_token(self):
        """Verify current token"""
        if not self.token:
            print("❌ No token found. Please login first.")
            input("\nPress Enter to continue...")
            return False
        
        try:
            response = requests.post(f"{API_BASE}/admin/verify-token", json={
                "token": self.token
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    admin = data.get('admin', {})
                    print(f"✅ Token valid")
                    print(f"   Admin: {admin.get('username')} ({admin.get('role')})")
                    return True
                else:
                    print(f"❌ Token invalid: {data.get('error')}")
            else:
                print(f"❌ Token verification failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Token verification error: {e}")
        
        input("\nPress Enter to continue...")
        return False

    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        if not self._check_auth():
            return
        
        self.print_header("DASHBOARD STATISTICS")
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{API_BASE}/admin/dashboard/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('stats', {})
                    
                    print("📊 PLATFORM OVERVIEW")
                    print("-" * 40)
                    
                    # Users
                    users = stats.get('users', {})
                    print(f"👥 Users:")
                    print(f"   Total: {users.get('total', 0)}")
                    print(f"   Growth: {users.get('growth', 'N/A')}")
                    
                    # Workers
                    workers = stats.get('workers', {})
                    print(f"\n👨‍⚕️ Workers:")
                    print(f"   Total: {workers.get('total', 0)}")
                    print(f"   Pending: {workers.get('pending', 0)}")
                    print(f"   Approved: {workers.get('approved', 0)}")
                    print(f"   Rejected: {workers.get('rejected', 0)}")
                    
                    # Appointments
                    appointments = stats.get('appointments', {})
                    print(f"\n📅 Appointments:")
                    print(f"   Total: {appointments.get('total', 0)}")
                    print(f"   Today: {appointments.get('today', 0)}")
                    print(f"   Completed: {appointments.get('completed', 0)}")
                    print(f"   Pending: {appointments.get('pending', 0)}")
                    
                    # Revenue
                    revenue = stats.get('revenue', {})
                    print(f"\n💰 Revenue:")
                    print(f"   Total: ₹{revenue.get('total', 0)}")
                    print(f"   Commission: ₹{revenue.get('commission', 0)}")
                    print(f"   Pending: ₹{revenue.get('pending', 0)}")
                    
                else:
                    print(f"❌ Stats error: {data.get('error')}")
            else:
                print(f"❌ Stats request failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Stats error: {e}")
        
        input("\nPress Enter to continue...")

    def get_recent_activity(self):
        """Get recent platform activity"""
        if not self._check_auth():
            return
        
        self.print_header("RECENT ACTIVITY")
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{API_BASE}/admin/dashboard/recent-activity", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    activities = data.get('activity', [])
                    
                    if activities:
                        print("⏰ LATEST PLATFORM ACTIVITY")
                        print("-" * 50)
                        
                        for i, activity in enumerate(activities[:10], 1):
                            activity_type = activity.get('type', 'unknown')
                            
                            if activity_type == 'appointment':
                                print(f"\n[{i}] 📅 Appointment")
                                print(f"    Patient: {activity.get('user_name', 'N/A')}")
                                print(f"    Date: {activity.get('booking_date', 'N/A')}")
                                print(f"    Status: {activity.get('status', 'N/A')}")
                                print(f"    Created: {activity.get('created_at', 'N/A')}")
                            
                            elif activity_type == 'worker_registration':
                                print(f"\n[{i}] 👨‍⚕️ Worker Registration")
                                print(f"    Name: {activity.get('full_name', 'N/A')}")
                                print(f"    Email: {activity.get('email', 'N/A')}")
                                print(f"    Specialization: {activity.get('specialization', 'N/A')}")
                                print(f"    Status: {activity.get('status', 'N/A')}")
                                print(f"    Created: {activity.get('created_at', 'N/A')}")
                            
                            else:
                                print(f"\n[{i}] 📋 {activity_type.title()}")
                                print(f"    Details: {activity}")
                    else:
                        print("📭 No recent activity found")
                        
                else:
                    print(f"❌ Activity error: {data.get('error')}")
            else:
                print(f"❌ Activity request failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Activity error: {e}")
        
        input("\nPress Enter to continue...")

    def get_platform_commission(self):
        """Get platform commission settings"""
        if not self._check_auth():
            return
        
        self.print_header("PLATFORM COMMISSION")
        
        try:
            response = requests.get(f"{API_BASE}/admin/platform/commission")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    commission = data.get('commission', {})
                    
                    print("💰 COMMISSION SETTINGS")
                    print("-" * 30)
                    print(f"Percentage: {commission.get('percentage', 0)}%")
                    print(f"Decimal: {commission.get('decimal', 0)}")
                    print(f"Description: {commission.get('description', 'N/A')}")
                    
                    print(f"\n💡 Example Calculation:")
                    doctor_fee = 500
                    platform_fee = doctor_fee * commission.get('decimal', 0)
                    total_patient = doctor_fee + platform_fee
                    print(f"   Doctor Fee: ₹{doctor_fee}")
                    print(f"   Platform Fee ({commission.get('percentage', 0)}%): ₹{platform_fee}")
                    print(f"   Total Patient Pays: ₹{total_patient}")
                    
                else:
                    print(f"❌ Commission error: {data.get('error')}")
            else:
                print(f"❌ Commission request failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Commission error: {e}")
        
        input("\nPress Enter to continue...")

    def manage_workers(self):
        """Worker management menu"""
        if not self._check_auth():
            return
        
        while True:
            self.print_header("WORKER MANAGEMENT")
            print("1. 📋 View All Workers")
            print("2. ⏳ View Pending Workers")
            print("3. ✅ Approve Worker")
            print("4. ❌ Reject Worker")
            print("5. ⬅️ Back to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._view_all_workers()
            elif choice == "2":
                self._view_pending_workers()
            elif choice == "3":
                self._approve_worker()
            elif choice == "4":
                self._reject_worker()
            elif choice == "5":
                break
            else:
                print("❌ Invalid choice")
                input("\nPress Enter to continue...")

    def _view_all_workers(self):
        """View all workers"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{API_BASE}/admin/workers", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    workers = data.get('workers', [])
                    pagination = data.get('pagination', {})
                    
                    print(f"\n👨‍⚕️ ALL WORKERS (Page {pagination.get('page', 1)} of {pagination.get('pages', 1)})")
                    print(f"Total: {pagination.get('total', 0)} workers")
                    print("-" * 80)
                    
                    for worker in workers:
                        status_icon = "✅" if worker.get('status') == 'approved' else "⏳" if worker.get('status') == 'pending' else "❌"
                        print(f"{status_icon} ID:{worker.get('id')} | {worker.get('full_name', 'N/A')}")
                        print(f"    📧 {worker.get('email', 'N/A')}")
                        print(f"    🩺 {worker.get('specialization', 'N/A')} | 🏢 {worker.get('service', 'N/A')}")
                        print(f"    📅 Created: {worker.get('created_at', 'N/A')}")
                        print()
                else:
                    print(f"❌ Workers error: {data.get('error')}")
            else:
                print(f"❌ Workers request failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Workers error: {e}")
        
        input("\nPress Enter to continue...")

    def _view_pending_workers(self):
        """View pending workers"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{API_BASE}/admin/workers/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    workers = data.get('workers', [])
                    
                    print(f"\n⏳ PENDING WORKERS ({len(workers)} workers)")
                    print("-" * 80)
                    
                    if workers:
                        for worker in workers:
                            print(f"⏳ ID:{worker.get('id')} | {worker.get('full_name', 'N/A')}")
                            print(f"    📧 {worker.get('email', 'N/A')}")
                            print(f"    🩺 {worker.get('specialization', 'N/A')} | 🏢 {worker.get('service', 'N/A')}")
                            print(f"    📅 Applied: {worker.get('created_at', 'N/A')}")
                            print()
                    else:
                        print("📭 No pending workers found")
                        
                else:
                    print(f"❌ Pending workers error: {data.get('error')}")
            else:
                print(f"❌ Pending workers request failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Pending workers error: {e}")
        
        input("\nPress Enter to continue...")

    def _approve_worker(self):
        """Approve a worker"""
        worker_id = input("Enter Worker ID to approve: ").strip()
        
        if not worker_id.isdigit():
            print("❌ Invalid Worker ID")
            input("\nPress Enter to continue...")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{API_BASE}/admin/worker/{worker_id}/approve", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Worker {worker_id} approved successfully!")
                else:
                    print(f"❌ Approval failed: {data.get('error')}")
            else:
                print(f"❌ Approval request failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Approval error: {e}")
        
        input("\nPress Enter to continue...")

    def _reject_worker(self):
        """Reject a worker"""
        worker_id = input("Enter Worker ID to reject: ").strip()
        reason = input("Rejection reason: ").strip()
        
        if not worker_id.isdigit():
            print("❌ Invalid Worker ID")
            input("\nPress Enter to continue...")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{API_BASE}/admin/worker/{worker_id}/reject", 
                                   headers=headers, json={"reason": reason})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Worker {worker_id} rejected successfully!")
                    print(f"   Reason: {reason}")
                else:
                    print(f"❌ Rejection failed: {data.get('error')}")
            else:
                print(f"❌ Rejection request failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Rejection error: {e}")
        
        input("\nPress Enter to continue...")

    def view_profile(self):
        """View admin profile"""
        if not self._check_auth():
            return
        
        self.print_header("ADMIN PROFILE")
        
        print("👤 ADMIN INFORMATION")
        print("-" * 30)
        print(f"ID: {self.admin_info.get('id', 'N/A')}")
        print(f"Username: {self.admin_info.get('username', 'N/A')}")
        print(f"Full Name: {self.admin_info.get('full_name', 'N/A')}")
        print(f"Email: {self.admin_info.get('email', 'N/A')}")
        print(f"Role: {self.admin_info.get('role', 'N/A')}")
        print(f"Last Login: {self.admin_info.get('last_login', 'N/A')}")
        print(f"Created: {self.admin_info.get('created_at', 'N/A')}")
        
        input("\nPress Enter to continue...")

    def test_connection(self):
        """Test API connection"""
        self.print_header("API CONNECTION TEST")
        
        try:
            response = requests.get(f"{API_BASE}/admin/platform/commission")
            
            if response.status_code == 200:
                print("✅ API server is running!")
                print(f"   Endpoint: {API_BASE}")
                print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
            else:
                print(f"⚠️ API server responded with: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server")
            print("   Make sure backend is running: python app.py")
            print("   API should be available at: http://127.0.0.1:5001")
        except Exception as e:
            print(f"❌ Connection test error: {e}")
        
        input("\nPress Enter to continue...")

    def _check_auth(self):
        """Check if user is authenticated"""
        if not self.token:
            print("❌ Please login first")
            input("\nPress Enter to continue...")
            return False
        
        # Verify token is still valid
        if not self.verify_token():
            self.token = None
            self.admin_info = None
            return False
        
        return True

    def main_menu(self):
        """Main admin menu"""
        while True:
            self.print_header("SUPER ADMIN CLI")
            
            if self.admin_info:
                print(f"👤 Logged in as: {self.admin_info.get('username', 'Unknown')} ({self.admin_info.get('role', 'admin')})")
                print()
            
            print("🔐 Authentication:")
            print("1. 🔑 Login")
            print("2. ✅ Verify Token")
            print("3. 👤 View Profile")
            print()
            print("📊 Dashboard:")
            print("4. 📈 Dashboard Statistics")
            print("5. ⏰ Recent Activity")
            print("6. 💰 Platform Commission")
            print()
            print("👥 Management:")
            print("7. 👨‍⚕️ Manage Workers")
            print()
            print("🔧 System:")
            print("8. 🌐 Test Connection")
            print("9. 🚪 Exit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.login()
            elif choice == "2":
                self.verify_token()
            elif choice == "3":
                self.view_profile()
            elif choice == "4":
                self.get_dashboard_stats()
            elif choice == "5":
                self.get_recent_activity()
            elif choice == "6":
                self.get_platform_commission()
            elif choice == "7":
                self.manage_workers()
            elif choice == "8":
                self.test_connection()
            elif choice == "9":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")
                input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    print("🚀 Super Admin CLI")
    print("=" * 30)
    print("Command-line interface for ExpertEase Super Admin Backend")
    print()
    
    # Check if backend is running
    try:
        response = requests.get("http://127.0.0.1:5001/api/admin/platform/commission", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running!")
        else:
            print("⚠️ Backend server responded unexpectedly")
    except:
        print("⚠️ Backend server may not be running")
        print("   Start it with: python app.py")
        print()
    
    cli = AdminCLI()
    cli.main_menu()

if __name__ == "__main__":
    main()
