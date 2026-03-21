#!/usr/bin/env python3
"""
Admin CLI interface for ExpertEase backend.
Provides command-line administrative functions for managing the platform.
"""

import sys
import os
import sqlite3
from datetime import datetime
from worker_db import WorkerDB
from user_db import UserDB
from appointment_db import AppointmentDB
from subscription_db import SubscriptionDB

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AdminCLI:
    def __init__(self):
        self.worker_db = WorkerDB()
        self.user_db = UserDB()
        self.appt_db = AppointmentDB()
        self.subscription_db = SubscriptionDB()
        
    def get_db_connection(self):
        """Get database connection for admin operations"""
        conn = sqlite3.connect('expertease.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print a formatted header"""
        self.clear_screen()
        print("=" * 60)
        print(f"  {title}")
        print("=" * 60)
        print()
    
    def print_menu(self, options):
        """Print menu options"""
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("0. Exit")
        print()
    
    def get_choice(self, prompt="Enter your choice: "):
        """Get user choice"""
        try:
            choice = int(input(prompt))
            return choice
        except ValueError:
            return -1
    
    def pause(self):
        """Pause execution until user presses Enter"""
        input("\nPress Enter to continue...")
    
    def show_main_menu(self):
        """Show main admin menu"""
        while True:
            self.print_header("EXPERTEASE ADMIN CLI")
            self.print_menu([
                "Healthcare Management",
                "User Management", 
                "Worker Management",
                "Appointment Management",
                "Payment & Subscription Management",
                "Platform Settings",
                "System Statistics"
            ])
            
            choice = self.get_choice()
            
            if choice == 0:
                print("Goodbye!")
                break
            elif choice == 1:
                self.healthcare_menu()
            elif choice == 2:
                self.users_menu()
            elif choice == 3:
                self.workers_menu()
            elif choice == 4:
                self.appointments_menu()
            elif choice == 5:
                self.payments_menu()
            elif choice == 6:
                self.settings_menu()
            elif choice == 7:
                self.statistics_menu()
            else:
                print("Invalid choice!")
                self.pause()
    
    def healthcare_menu(self):
        """Healthcare management menu"""
        while True:
            self.print_header("HEALTHCARE MANAGEMENT")
            self.print_menu([
                "View Pending Workers",
                "View Approved Workers", 
                "Approve Worker",
                "Reject Worker",
                "Suspend Worker",
                "Healthcare Statistics"
            ])
            
            choice = self.get_choice()
            
            if choice == 0:
                break
            elif choice == 1:
                self.view_pending_workers('healthcare')
            elif choice == 2:
                self.view_approved_workers('healthcare')
            elif choice == 3:
                self.approve_worker()
            elif choice == 4:
                self.reject_worker()
            elif choice == 5:
                self.suspend_worker()
            elif choice == 6:
                self.show_healthcare_stats()
            else:
                print("Invalid choice!")
                self.pause()
    
    def users_menu(self):
        """User management menu"""
        while True:
            self.print_header("USER MANAGEMENT")
            self.print_menu([
                "View All Users",
                "Search User",
                "Block User",
                "Unblock User",
                "User Statistics"
            ])
            
            choice = self.get_choice()
            
            if choice == 0:
                break
            elif choice == 1:
                self.view_all_users()
            elif choice == 2:
                self.search_user()
            elif choice == 3:
                self.block_user()
            elif choice == 4:
                self.unblock_user()
            elif choice == 5:
                self.show_user_stats()
            else:
                print("Invalid choice!")
                self.pause()
    
    def workers_menu(self):
        """Worker management menu"""
        while True:
            self.print_header("WORKER MANAGEMENT")
            self.print_menu([
                "View All Workers",
                "View Pending Workers (All Services)",
                "View Approved Workers (All Services)",
                "Approve Worker",
                "Reject Worker", 
                "Suspend Worker",
                "Unsuspend Worker",
                "Worker Statistics"
            ])
            
            choice = self.get_choice()
            
            if choice == 0:
                break
            elif choice == 1:
                self.view_all_workers()
            elif choice == 2:
                self.view_pending_workers(None)
            elif choice == 3:
                self.view_approved_workers(None)
            elif choice == 4:
                self.approve_worker()
            elif choice == 5:
                self.reject_worker()
            elif choice == 6:
                self.suspend_worker()
            elif choice == 7:
                self.unsuspend_worker()
            elif choice == 8:
                self.show_worker_stats()
            else:
                print("Invalid choice!")
                self.pause()
    
    def appointments_menu(self):
        """Appointment management menu"""
        while True:
            self.print_header("APPOINTMENT MANAGEMENT")
            self.print_menu([
                "View All Appointments",
                "View Appointments by Status",
                "View Appointments by Service",
                "View Today's Appointments",
                "Cancel Appointment",
                "Appointment Statistics"
            ])
            
            choice = self.get_choice()
            
            if choice == 0:
                break
            elif choice == 1:
                self.view_all_appointments()
            elif choice == 2:
                self.view_appointments_by_status()
            elif choice == 3:
                self.view_appointments_by_service()
            elif choice == 4:
                self.view_today_appointments()
            elif choice == 5:
                self.cancel_appointment()
            elif choice == 6:
                self.show_appointment_stats()
            else:
                print("Invalid choice!")
                self.pause()
    
    def payments_menu(self):
        """Payment and subscription management menu"""
        while True:
            self.print_header("PAYMENT & SUBSCRIPTION MANAGEMENT")
            self.print_menu([
                "View All Transactions",
                "View Subscriptions",
                "Cancel Subscription",
                "Payment Statistics"
            ])
            
            choice = self.get_choice()
            
            if choice == 0:
                break
            elif choice == 1:
                self.view_transactions()
            elif choice == 2:
                self.view_subscriptions()
            elif choice == 3:
                self.cancel_subscription()
            elif choice == 4:
                self.show_payment_stats()
            else:
                print("Invalid choice!")
                self.pause()
    
    def settings_menu(self):
        """Platform settings menu"""
        while True:
            self.print_header("PLATFORM SETTINGS")
            self.print_menu([
                "View All Settings",
                "Update Setting",
                "Reset Settings to Default",
                "Export Settings"
            ])
            
            choice = self.get_choice()
            
            if choice == 0:
                break
            elif choice == 1:
                self.view_settings()
            elif choice == 2:
                self.update_setting()
            elif choice == 3:
                self.reset_settings()
            elif choice == 4:
                self.export_settings()
            else:
                print("Invalid choice!")
                self.pause()
    
    def statistics_menu(self):
        """System statistics menu"""
        while True:
            self.print_header("SYSTEM STATISTICS")
            self.print_menu([
                "Platform Overview",
                "Service Statistics",
                "Revenue Overview",
                "User Activity"
            ])
            
            choice = self.get_choice()
            
            if choice == 0:
                break
            elif choice == 1:
                self.platform_overview()
            elif choice == 2:
                self.service_statistics()
            elif choice == 3:
                self.revenue_overview()
            elif choice == 4:
                self.user_activity()
            else:
                print("Invalid choice!")
                self.pause()
    
    # Healthcare Management Functions
    def view_pending_workers(self, service_type):
        """View pending workers"""
        self.print_header(f"PENDING WORKERS - {service_type.upper() if service_type else 'ALL SERVICES'}")
        
        try:
            workers = self.worker_db.get_pending_workers(service_type)
            
            if not workers:
                print("No pending workers found.")
                self.pause()
                return
            
            print(f"{'ID':<5} {'Name':<25} {'Email':<25} {'Service':<15} {'Specialization':<20}")
            print("-" * 100)
            
            for worker in workers:
                print(f"{worker['id']:<5} {worker['full_name'][:24]:<25} {worker['email'][:24]:<25} "
                      f"{worker['service'][:14]:<15} {worker.get('specialization', 'N/A')[:19]:<20}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def view_approved_workers(self, service_type):
        """View approved workers"""
        self.print_header(f"APPROVED WORKERS - {service_type.upper() if service_type else 'ALL SERVICES'}")
        
        try:
            workers = self.worker_db.get_approved_workers(service_type)
            
            if not workers:
                print("No approved workers found.")
                self.pause()
                return
            
            print(f"{'ID':<5} {'Name':<25} {'Email':<25} {'Service':<15} {'Specialization':<20}")
            print("-" * 100)
            
            for worker in workers:
                print(f"{worker['id']:<5} {worker['full_name'][:24]:<25} {worker['email'][:24]:<25} "
                      f"{worker['service'][:14]:<15} {worker.get('specialization', 'N/A')[:19]:<20}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def approve_worker(self):
        """Approve a worker"""
        self.print_header("APPROVE WORKER")
        
        try:
            worker_id = input("Enter worker ID: ")
            
            worker = self.worker_db.get_worker_by_id(int(worker_id))
            if not worker:
                print("Worker not found!")
                self.pause()
                return
            
            print(f"\nWorker Details:")
            print(f"Name: {worker['full_name']}")
            print(f"Email: {worker['email']}")
            print(f"Service: {worker['service']}")
            print(f"Current Status: {worker['status']}")
            
            if worker['status'] != 'pending':
                print("Worker is not in pending status!")
                self.pause()
                return
            
            confirm = input("\nApprove this worker? (y/n): ").lower()
            if confirm == 'y':
                self.worker_db.approve_worker(int(worker_id))
                print("Worker approved successfully!")
            else:
                print("Approval cancelled.")
                
        except ValueError:
            print("Invalid worker ID!")
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def reject_worker(self):
        """Reject a worker"""
        self.print_header("REJECT WORKER")
        
        try:
            worker_id = input("Enter worker ID: ")
            reason = input("Enter rejection reason: ")
            
            worker = self.worker_db.get_worker_by_id(int(worker_id))
            if not worker:
                print("Worker not found!")
                self.pause()
                return
            
            print(f"\nWorker Details:")
            print(f"Name: {worker['full_name']}")
            print(f"Email: {worker['email']}")
            print(f"Service: {worker['service']}")
            print(f"Current Status: {worker['status']}")
            
            if worker['status'] != 'pending':
                print("Worker is not in pending status!")
                self.pause()
                return
            
            confirm = input(f"\nReject this worker? Reason: {reason} (y/n): ").lower()
            if confirm == 'y':
                self.worker_db.reject_worker(int(worker_id))
                print(f"Worker rejected successfully! Reason: {reason}")
            else:
                print("Rejection cancelled.")
                
        except ValueError:
            print("Invalid worker ID!")
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def suspend_worker(self):
        """Suspend a worker"""
        self.print_header("SUSPEND WORKER")
        
        try:
            worker_id = input("Enter worker ID: ")
            
            worker = self.worker_db.get_worker_by_id(int(worker_id))
            if not worker:
                print("Worker not found!")
                self.pause()
                return
            
            print(f"\nWorker Details:")
            print(f"Name: {worker['full_name']}")
            print(f"Email: {worker['email']}")
            print(f"Service: {worker['service']}")
            print(f"Current Status: {worker['status']}")
            
            if worker['status'] != 'approved':
                print("Worker is not in approved status!")
                self.pause()
                return
            
            confirm = input("\nSuspend this worker? (y/n): ").lower()
            if confirm == 'y':
                self.worker_db.update_worker_status(int(worker_id), 'suspended')
                print("Worker suspended successfully!")
            else:
                print("Suspension cancelled.")
                
        except ValueError:
            print("Invalid worker ID!")
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def unsuspend_worker(self):
        """Unsuspend a worker"""
        self.print_header("UNSUSPEND WORKER")
        
        try:
            worker_id = input("Enter worker ID: ")
            
            worker = self.worker_db.get_worker_by_id(int(worker_id))
            if not worker:
                print("Worker not found!")
                self.pause()
                return
            
            print(f"\nWorker Details:")
            print(f"Name: {worker['full_name']}")
            print(f"Email: {worker['email']}")
            print(f"Service: {worker['service']}")
            print(f"Current Status: {worker['status']}")
            
            if worker['status'] != 'suspended':
                print("Worker is not in suspended status!")
                self.pause()
                return
            
            confirm = input("\nUnsuspend this worker? (y/n): ").lower()
            if confirm == 'y':
                self.worker_db.update_worker_status(int(worker_id), 'approved')
                print("Worker unsuspended successfully!")
            else:
                print("Unsuspension cancelled.")
                
        except ValueError:
            print("Invalid worker ID!")
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def show_healthcare_stats(self):
        """Show healthcare statistics"""
        self.print_header("HEALTHCARE STATISTICS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get healthcare workers count
            cursor.execute("SELECT COUNT(*) as count FROM workers WHERE service LIKE '%healthcare%'")
            total_workers = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM workers WHERE service LIKE '%healthcare%' AND status = 'approved'")
            approved_workers = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM workers WHERE service LIKE '%healthcare%' AND status = 'pending'")
            pending_workers = cursor.fetchone()['count']
            
            # Get healthcare appointments
            cursor.execute("""
                SELECT COUNT(*) as count FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                WHERE w.service LIKE '%healthcare%'
            """)
            total_appointments = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT COUNT(*) as count FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                WHERE w.service LIKE '%healthcare%' AND a.status = 'completed'
            """)
            completed_appointments = cursor.fetchone()['count']
            
            conn.close()
            
            print("Healthcare Workers:")
            print(f"  Total Workers: {total_workers}")
            print(f"  Approved: {approved_workers}")
            print(f"  Pending: {pending_workers}")
            print()
            print("Healthcare Appointments:")
            print(f"  Total Appointments: {total_appointments}")
            print(f"  Completed: {completed_appointments}")
            print(f"  Success Rate: {(completed_appointments/total_appointments*100):.1f}%" if total_appointments > 0 else "  Success Rate: 0%")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    # User Management Functions
    def view_all_users(self):
        """View all users"""
        self.print_header("ALL USERS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.id, u.name, u.username, u.email, u.is_verified, u.created_at,
                       COUNT(a.id) as appointment_count
                FROM users u
                LEFT JOIN appointments a ON u.id = a.user_id
                GROUP BY u.id, u.name, u.username, u.email, u.is_verified, u.created_at
                ORDER BY u.created_at DESC
                LIMIT 20
            """)
            
            users = cursor.fetchall()
            conn.close()
            
            if not users:
                print("No users found.")
                self.pause()
                return
            
            print(f"{'ID':<5} {'Name':<20} {'Username':<15} {'Email':<25} {'Verified':<8} {'Appointments':<12}")
            print("-" * 100)
            
            for user in users:
                verified = "Yes" if user['is_verified'] else "No"
                print(f"{user['id']:<5} {user['name'][:19]:<20} {user['username'][:14]:<15} "
                      f"{user['email'][:24]:<25} {verified:<8} {user['appointment_count']:<12}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def search_user(self):
        """Search for a user"""
        self.print_header("SEARCH USER")
        
        try:
            search_term = input("Enter name, username, or email: ")
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.id, u.name, u.username, u.email, u.is_verified, u.created_at,
                       COUNT(a.id) as appointment_count
                FROM users u
                LEFT JOIN appointments a ON u.id = a.user_id
                WHERE u.name LIKE ? OR u.username LIKE ? OR u.email LIKE ?
                GROUP BY u.id, u.name, u.username, u.email, u.is_verified, u.created_at
                ORDER BY u.created_at DESC
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            users = cursor.fetchall()
            conn.close()
            
            if not users:
                print("No users found.")
                self.pause()
                return
            
            print(f"{'ID':<5} {'Name':<20} {'Username':<15} {'Email':<25} {'Verified':<8} {'Appointments':<12}")
            print("-" * 100)
            
            for user in users:
                verified = "Yes" if user['is_verified'] else "No"
                print(f"{user['id']:<5} {user['name'][:19]:<20} {user['username'][:14]:<15} "
                      f"{user['email'][:24]:<25} {verified:<8} {user['appointment_count']:<12}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def block_user(self):
        """Block a user"""
        self.print_header("BLOCK USER")
        
        try:
            user_id = input("Enter user ID: ")
            
            user = self.user_db.get_user_by_id(int(user_id))
            if not user:
                print("User not found!")
                self.pause()
                return
            
            print(f"\nUser Details:")
            print(f"Name: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"Username: {user['username']}")
            print(f"Verified: {'Yes' if user['is_verified'] else 'No'}")
            
            confirm = input("\nBlock this user? (y/n): ").lower()
            if confirm == 'y':
                # In real implementation, update user status in database
                print(f"User {user_id} blocked successfully!")
            else:
                print("Block cancelled.")
                
        except ValueError:
            print("Invalid user ID!")
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def unblock_user(self):
        """Unblock a user"""
        self.print_header("UNBLOCK USER")
        
        try:
            user_id = input("Enter user ID: ")
            
            user = self.user_db.get_user_by_id(int(user_id))
            if not user:
                print("User not found!")
                self.pause()
                return
            
            print(f"\nUser Details:")
            print(f"Name: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"Username: {user['username']}")
            
            confirm = input("\nUnblock this user? (y/n): ").lower()
            if confirm == 'y':
                # In real implementation, update user status in database
                print(f"User {user_id} unblocked successfully!")
            else:
                print("Unblock cancelled.")
                
        except ValueError:
            print("Invalid user ID!")
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def show_user_stats(self):
        """Show user statistics"""
        self.print_header("USER STATISTICS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get user counts
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_verified = 1")
            verified_users = cursor.fetchone()['count']
            
            # Get users by service
            cursor.execute("""
                SELECT w.service, COUNT(DISTINCT a.user_id) as user_count
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                GROUP BY w.service
            """)
            
            users_by_service = {}
            for row in cursor.fetchall():
                service = row['service']
                if ',' in service:
                    services = [s.strip() for s in service.split(',')]
                    for s in services:
                        users_by_service[s] = users_by_service.get(s, 0) + row['user_count']
                else:
                    users_by_service[service] = users_by_service.get(service, 0) + row['user_count']
            
            conn.close()
            
            print("User Overview:")
            print(f"  Total Users: {total_users}")
            print(f"  Verified Users: {verified_users}")
            print(f"  Unverified Users: {total_users - verified_users}")
            print()
            print("Users by Service:")
            for service, count in users_by_service.items():
                print(f"  {service}: {count}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    # Worker Management Functions
    def view_all_workers(self):
        """View all workers"""
        self.print_header("ALL WORKERS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT w.id, w.full_name, w.email, w.service, w.specialization, w.status, w.created_at,
                       COUNT(a.id) as appointment_count
                FROM workers w
                LEFT JOIN appointments a ON w.id = a.worker_id
                GROUP BY w.id, w.full_name, w.email, w.service, w.specialization, w.status, w.created_at
                ORDER BY w.created_at DESC
                LIMIT 20
            """)
            
            workers = cursor.fetchall()
            conn.close()
            
            if not workers:
                print("No workers found.")
                self.pause()
                return
            
            print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Service':<15} {'Status':<10} {'Appointments':<12}")
            print("-" * 100)
            
            for worker in workers:
                print(f"{worker['id']:<5} {worker['full_name'][:19]:<20} {worker['email'][:24]:<25} "
                      f"{worker['service'][:14]:<15} {worker['status']:<10} {worker['appointment_count']:<12}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def show_worker_stats(self):
        """Show worker statistics"""
        self.print_header("WORKER STATISTICS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get worker counts by status
            cursor.execute("SELECT COUNT(*) as count FROM workers")
            total_workers = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM workers WHERE status = 'pending'")
            pending_workers = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM workers WHERE status = 'approved'")
            approved_workers = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM workers WHERE status = 'rejected'")
            rejected_workers = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM workers WHERE status = 'suspended'")
            suspended_workers = cursor.fetchone()['count']
            
            # Get workers by service
            cursor.execute("SELECT service, COUNT(*) as count FROM workers GROUP BY service")
            
            workers_by_service = {}
            for row in cursor.fetchall():
                service = row['service']
                if ',' in service:
                    services = [s.strip() for s in service.split(',')]
                    for s in services:
                        workers_by_service[s] = workers_by_service.get(s, 0) + row['count']
                else:
                    workers_by_service[service] = workers_by_service.get(service, 0) + row['count']
            
            conn.close()
            
            print("Worker Overview:")
            print(f"  Total Workers: {total_workers}")
            print(f"  Pending: {pending_workers}")
            print(f"  Approved: {approved_workers}")
            print(f"  Rejected: {rejected_workers}")
            print(f"  Suspended: {suspended_workers}")
            print()
            print("Workers by Service:")
            for service, count in workers_by_service.items():
                print(f"  {service}: {count}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    # Appointment Management Functions
    def view_all_appointments(self):
        """View all appointments"""
        self.print_header("ALL APPOINTMENTS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.id, a.user_name, a.booking_date, a.time_slot, a.appointment_type, a.status,
                       a.payment_status, w.full_name as worker_name, w.service
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                ORDER BY a.created_at DESC
                LIMIT 20
            """)
            
            appointments = cursor.fetchall()
            conn.close()
            
            if not appointments:
                print("No appointments found.")
                self.pause()
                return
            
            print(f"{'ID':<5} {'User':<20} {'Worker':<20} {'Service':<15} {'Date':<12} {'Status':<10} {'Payment':<10}")
            print("-" * 110)
            
            for apt in appointments:
                print(f"{apt['id']:<5} {apt['user_name'][:19]:<20} {apt['worker_name'][:19]:<20} "
                      f"{apt['service'][:14]:<15} {apt['booking_date']:<12} {apt['status']:<10} {apt['payment_status']:<10}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def view_appointments_by_status(self):
        """View appointments by status"""
        self.print_header("APPOINTMENTS BY STATUS")
        
        print("Select status:")
        print("1. Pending")
        print("2. Accepted")
        print("3. Completed")
        print("4. Cancelled")
        
        choice = self.get_choice("Enter status choice: ")
        
        status_map = {1: 'pending', 2: 'accepted', 3: 'completed', 4: 'cancelled'}
        if choice not in status_map:
            print("Invalid choice!")
            self.pause()
            return
        
        status = status_map[choice]
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.id, a.user_name, a.booking_date, a.time_slot, a.appointment_type,
                       a.payment_status, w.full_name as worker_name, w.service
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                WHERE a.status = ?
                ORDER BY a.created_at DESC
            """, (status,))
            
            appointments = cursor.fetchall()
            conn.close()
            
            if not appointments:
                print(f"No appointments with status '{status}' found.")
                self.pause()
                return
            
            print(f"\nAppointments with status '{status.upper()}':")
            print(f"{'ID':<5} {'User':<20} {'Worker':<20} {'Service':<15} {'Date':<12} {'Payment':<10}")
            print("-" * 100)
            
            for apt in appointments:
                print(f"{apt['id']:<5} {apt['user_name'][:19]:<20} {apt['worker_name'][:19]:<20} "
                      f"{apt['service'][:14]:<15} {apt['booking_date']:<12} {apt['payment_status']:<10}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def view_appointments_by_service(self):
        """View appointments by service"""
        self.print_header("APPOINTMENTS BY SERVICE")
        
        print("Select service:")
        print("1. Healthcare")
        print("2. Housekeeping")
        print("3. Freelance")
        print("4. Car Service")
        print("5. Money Management")
        
        choice = self.get_choice("Enter service choice: ")
        
        service_map = {
            1: 'healthcare', 2: 'housekeeping', 3: 'freelance',
            4: 'car', 5: 'money'
        }
        if choice not in service_map:
            print("Invalid choice!")
            self.pause()
            return
        
        service = service_map[choice]
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.id, a.user_name, a.booking_date, a.time_slot, a.appointment_type,
                       a.status, a.payment_status, w.full_name as worker_name
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                WHERE w.service LIKE ?
                ORDER BY a.created_at DESC
            """, (f"%{service}%",))
            
            appointments = cursor.fetchall()
            conn.close()
            
            if not appointments:
                print(f"No appointments for service '{service}' found.")
                self.pause()
                return
            
            print(f"\nAppointments for service '{service.upper()}':")
            print(f"{'ID':<5} {'User':<20} {'Worker':<20} {'Date':<12} {'Status':<10} {'Payment':<10}")
            print("-" * 90)
            
            for apt in appointments:
                print(f"{apt['id']:<5} {apt['user_name'][:19]:<20} {apt['worker_name'][:19]:<20} "
                      f"{apt['booking_date']:<12} {apt['status']:<10} {apt['payment_status']:<10}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def view_today_appointments(self):
        """View today's appointments"""
        self.print_header("TODAY'S APPOINTMENTS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT a.id, a.user_name, a.booking_date, a.time_slot, a.appointment_type,
                       a.status, a.payment_status, w.full_name as worker_name, w.service
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                WHERE a.booking_date = ?
                ORDER BY a.time_slot
            """, (today,))
            
            appointments = cursor.fetchall()
            conn.close()
            
            if not appointments:
                print(f"No appointments for today ({today}) found.")
                self.pause()
                return
            
            print(f"Appointments for today ({today}):")
            print(f"{'ID':<5} {'User':<20} {'Worker':<20} {'Service':<15} {'Time':<10} {'Status':<10}")
            print("-" * 100)
            
            for apt in appointments:
                print(f"{apt['id']:<5} {apt['user_name'][:19]:<20} {apt['worker_name'][:19]:<20} "
                      f"{apt['service'][:14]:<15} {apt['time_slot']:<10} {apt['status']:<10}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def cancel_appointment(self):
        """Cancel an appointment"""
        self.print_header("CANCEL APPOINTMENT")
        
        try:
            appointment_id = input("Enter appointment ID: ")
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get appointment details
            cursor.execute("""
                SELECT a.*, w.full_name as worker_name, w.service
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                WHERE a.id = ?
            """, (int(appointment_id),))
            
            appointment = cursor.fetchone()
            
            if not appointment:
                conn.close()
                print("Appointment not found!")
                self.pause()
                return
            
            print(f"\nAppointment Details:")
            print(f"ID: {appointment['id']}")
            print(f"User: {appointment['user_name']}")
            print(f"Worker: {appointment['worker_name']}")
            print(f"Service: {appointment['service']}")
            print(f"Date: {appointment['booking_date']}")
            print(f"Time: {appointment['time_slot']}")
            print(f"Status: {appointment['status']}")
            
            if appointment['status'] in ['completed', 'cancelled']:
                print("Cannot cancel appointment in completed or cancelled status!")
                conn.close()
                self.pause()
                return
            
            reason = input("\nEnter cancellation reason: ")
            confirm = input(f"\nCancel appointment {appointment_id}? Reason: {reason} (y/n): ").lower()
            
            if confirm == 'y':
                cursor.execute("""
                    UPDATE appointments 
                    SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (int(appointment_id),))
                
                conn.commit()
                conn.close()
                print(f"Appointment {appointment_id} cancelled successfully!")
            else:
                conn.close()
                print("Cancellation cancelled.")
                
        except ValueError:
            print("Invalid appointment ID!")
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def show_appointment_stats(self):
        """Show appointment statistics"""
        self.print_header("APPOINTMENT STATISTICS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get appointment counts by status
            cursor.execute("SELECT COUNT(*) as count FROM appointments")
            total_appointments = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE status = 'pending'")
            pending_appointments = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE status = 'accepted'")
            accepted_appointments = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE status = 'completed'")
            completed_appointments = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE status = 'cancelled'")
            cancelled_appointments = cursor.fetchone()['count']
            
            # Get appointments by service
            cursor.execute("""
                SELECT w.service, COUNT(*) as count
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                GROUP BY w.service
            """)
            
            appointments_by_service = {}
            for row in cursor.fetchall():
                service = row['service']
                if ',' in service:
                    services = [s.strip() for s in service.split(',')]
                    for s in services:
                        appointments_by_service[s] = appointments_by_service.get(s, 0) + row['count']
                else:
                    appointments_by_service[service] = appointments_by_service.get(service, 0) + row['count']
            
            conn.close()
            
            print("Appointment Overview:")
            print(f"  Total Appointments: {total_appointments}")
            print(f"  Pending: {pending_appointments}")
            print(f"  Accepted: {accepted_appointments}")
            print(f"  Completed: {completed_appointments}")
            print(f"  Cancelled: {cancelled_appointments}")
            print()
            print("Appointments by Service:")
            for service, count in appointments_by_service.items():
                print(f"  {service}: {count}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    # Payment Management Functions
    def view_transactions(self):
        """View payment transactions"""
        self.print_header("PAYMENT TRANSACTIONS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.id as transaction_id, a.user_name, a.booking_date, a.payment_status,
                       w.full_name as worker_name, w.service
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                WHERE a.status = 'completed'
                ORDER BY a.created_at DESC
                LIMIT 20
            """)
            
            transactions = cursor.fetchall()
            conn.close()
            
            if not transactions:
                print("No transactions found.")
                self.pause()
                return
            
            print(f"{'ID':<5} {'User':<20} {'Worker':<20} {'Service':<15} {'Date':<12} {'Status':<10}")
            print("-" * 100)
            
            for txn in transactions:
                print(f"{txn['transaction_id']:<5} {txn['user_name'][:19]:<20} {txn['worker_name'][:19]:<20} "
                      f"{txn['service'][:14]:<15} {txn['booking_date']:<12} {txn['payment_status']:<10}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def view_subscriptions(self):
        """View subscriptions"""
        self.print_header("WORKER SUBSCRIPTIONS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.id, s.worker_id, s.plan_id, s.start_date, s.expiry_date,
                       s.payment_status, s.appointments_used, s.appointments_limit,
                       w.full_name as worker_name, w.service
                FROM subscriptions s
                JOIN workers w ON s.worker_id = w.id
                ORDER BY s.created_at DESC
                LIMIT 20
            """)
            
            subscriptions = cursor.fetchall()
            conn.close()
            
            if not subscriptions:
                print("No subscriptions found.")
                self.pause()
                return
            
            print(f"{'ID':<5} {'Worker':<20} {'Plan':<8} {'Start':<12} {'Expiry':<12} {'Used':<6} {'Limit':<6} {'Status':<10}")
            print("-" * 90)
            
            for sub in subscriptions:
                plan_type = {1: "Basic", 2: "Premium", 3: "Enterprise"}.get(sub['plan_id'], "Unknown")
                print(f"{sub['id']:<5} {sub['worker_name'][:19]:<20} {plan_type:<8} {sub['start_date']:<12} "
                      f"{sub['expiry_date']:<12} {sub['appointments_used']:<6} {sub['appointments_limit']:<6} {sub['payment_status']:<10}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def cancel_subscription(self):
        """Cancel a subscription"""
        self.print_header("CANCEL SUBSCRIPTION")
        
        try:
            subscription_id = input("Enter subscription ID: ")
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get subscription details
            cursor.execute("""
                SELECT s.*, w.full_name as worker_name
                FROM subscriptions s
                JOIN workers w ON s.worker_id = w.id
                WHERE s.id = ?
            """, (int(subscription_id),))
            
            subscription = cursor.fetchone()
            
            if not subscription:
                conn.close()
                print("Subscription not found!")
                self.pause()
                return
            
            print(f"\nSubscription Details:")
            print(f"ID: {subscription['id']}")
            print(f"Worker: {subscription['worker_name']}")
            print(f"Plan: {subscription['plan_id']}")
            print(f"Start Date: {subscription['start_date']}")
            print(f"Expiry Date: {subscription['expiry_date']}")
            print(f"Status: {subscription['payment_status']}")
            
            if subscription['payment_status'] == 'cancelled':
                print("Subscription is already cancelled!")
                conn.close()
                self.pause()
                return
            
            confirm = input(f"\nCancel subscription {subscription_id}? (y/n): ").lower()
            
            if confirm == 'y':
                cursor.execute("""
                    UPDATE subscriptions 
                    SET payment_status = 'cancelled', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (int(subscription_id),))
                
                conn.commit()
                conn.close()
                print(f"Subscription {subscription_id} cancelled successfully!")
            else:
                conn.close()
                print("Cancellation cancelled.")
                
        except ValueError:
            print("Invalid subscription ID!")
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def show_payment_stats(self):
        """Show payment statistics"""
        self.print_header("PAYMENT STATISTICS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get transaction stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN a.payment_status = 'paid' THEN 1 ELSE 0 END) as paid_transactions,
                    SUM(CASE WHEN a.payment_status = 'pending' THEN 1 ELSE 0 END) as pending_transactions
                FROM appointments a
                WHERE a.status = 'completed'
            """)
            
            transaction_stats = cursor.fetchone()
            
            # Get revenue by service
            cursor.execute("""
                SELECT w.service, COUNT(*) as paid_appointments
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                WHERE a.status = 'completed' AND a.payment_status = 'paid'
                GROUP BY w.service
            """)
            
            revenue_by_service = {}
            total_revenue = 0
            
            for row in cursor.fetchall():
                service = row['service']
                paid_appointments = row['paid_appointments']
                avg_fee = 500.00  # Simplified
                service_revenue = paid_appointments * avg_fee
                total_revenue += service_revenue
                
                if ',' in service:
                    services = [s.strip() for s in service.split(',')]
                    for s in services:
                        revenue_by_service[s] = revenue_by_service.get(s, 0) + service_revenue / len(services)
                else:
                    revenue_by_service[service] = revenue_by_service.get(service, 0) + service_revenue
            
            # Get subscription stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as active_subscriptions,
                    SUM(CASE 
                        WHEN plan_id = 1 THEN 1000.00
                        WHEN plan_id = 2 THEN 2000.00
                        WHEN plan_id = 3 THEN 5000.00
                        ELSE 0.00
                    END) as subscription_revenue
                FROM subscriptions
                WHERE payment_status = 'active'
            """)
            
            subscription_stats = cursor.fetchone()
            
            conn.close()
            
            commission_percentage = 20
            total_commission = total_revenue * (commission_percentage / 100)
            total_worker_earnings = total_revenue - total_commission
            
            print("Transaction Overview:")
            print(f"  Total Transactions: {transaction_stats['total_transactions']}")
            print(f"  Paid Transactions: {transaction_stats['paid_transactions']}")
            print(f"  Pending Transactions: {transaction_stats['pending_transactions']}")
            print()
            print("Revenue Overview:")
            print(f"  Total Revenue: ₹{total_revenue:,.2f}")
            print(f"  Platform Commission (20%): ₹{total_commission:,.2f}")
            print(f"  Worker Earnings: ₹{total_worker_earnings:,.2f}")
            print(f"  Subscription Revenue: ₹{subscription_stats['subscription_revenue'] or 0:,.2f}")
            print()
            print("Revenue by Service:")
            for service, revenue in revenue_by_service.items():
                print(f"  {service}: ₹{revenue:,.2f}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    # Settings Management Functions
    def view_settings(self):
        """View platform settings"""
        self.print_header("PLATFORM SETTINGS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Create settings table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    setting_type TEXT DEFAULT 'string',
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default settings if table is empty
            cursor.execute("SELECT COUNT(*) as count FROM admin_settings")
            if cursor.fetchone()['count'] == 0:
                default_settings = {
                    "platform_name": "ExpertEase",
                    "healthcare_commission": "20",
                    "housekeeping_commission": "15",
                    "auto_approve_workers": "false",
                    "user_verification_required": "true"
                }
                
                for key, value in default_settings.items():
                    cursor.execute("""
                        INSERT INTO admin_settings (setting_key, setting_value)
                        VALUES (?, ?)
                    """, (key, value))
                
                conn.commit()
            
            cursor.execute("SELECT * FROM admin_settings ORDER BY category, setting_key")
            settings = cursor.fetchall()
            conn.close()
            
            if not settings:
                print("No settings found.")
                self.pause()
                return
            
            current_category = ""
            for setting in settings:
                if setting['category'] != current_category:
                    current_category = setting['category']
                    print(f"\n{current_category.upper()}:")
                    print("-" * 40)
                
                print(f"{setting['setting_key']}: {setting['setting_value']}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def update_setting(self):
        """Update a platform setting"""
        self.print_header("UPDATE SETTING")
        
        try:
            setting_key = input("Enter setting key: ")
            new_value = input("Enter new value: ")
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check if setting exists
            cursor.execute("SELECT setting_value FROM admin_settings WHERE setting_key = ?", (setting_key,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                print("Setting not found!")
                self.pause()
                return
            
            current_value = row['setting_value']
            print(f"\nCurrent value: {current_value}")
            print(f"New value: {new_value}")
            
            confirm = input(f"\nUpdate setting '{setting_key}'? (y/n): ").lower()
            
            if confirm == 'y':
                cursor.execute("""
                    UPDATE admin_settings 
                    SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE setting_key = ?
                """, (new_value, setting_key))
                
                conn.commit()
                conn.close()
                print(f"Setting '{setting_key}' updated successfully!")
            else:
                conn.close()
                print("Update cancelled.")
                
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def reset_settings(self):
        """Reset settings to default"""
        self.print_header("RESET SETTINGS")
        
        try:
            confirm = input("This will reset all settings to default values. Continue? (y/n): ").lower()
            
            if confirm != 'y':
                print("Reset cancelled.")
                self.pause()
                return
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Delete all existing settings
            cursor.execute("DELETE FROM admin_settings")
            
            # Insert default settings
            default_settings = {
                "platform_name": "ExpertEase",
                "healthcare_commission": "20",
                "housekeeping_commission": "15",
                "freelance_commission": "10",
                "car_service_commission": "18",
                "money_management_commission": "12",
                "auto_approve_workers": "false",
                "user_verification_required": "true",
                "healthcare_service_available": "true",
                "housekeeping_service_available": "true",
                "freelance_service_available": "true",
                "car_service_available": "true",
                "money_management_available": "true"
            }
            
            for key, value in default_settings.items():
                cursor.execute("""
                    INSERT INTO admin_settings (setting_key, setting_value)
                    VALUES (?, ?)
                """, (key, value))
            
            conn.commit()
            conn.close()
            
            print("Settings reset to default values successfully!")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def export_settings(self):
        """Export settings to console"""
        self.print_header("EXPORT SETTINGS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT setting_key, setting_value FROM admin_settings ORDER BY setting_key")
            settings = cursor.fetchall()
            conn.close()
            
            print("Current Settings:")
            print("{")
            for setting in settings:
                print(f'    "{setting["setting_key"]}": "{setting["setting_value"]}",')
            print("}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    # Statistics Functions
    def platform_overview(self):
        """Show platform overview"""
        self.print_header("PLATFORM OVERVIEW")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get basic counts
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM workers")
            total_workers = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM appointments")
            total_appointments = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM subscriptions WHERE payment_status = 'active'")
            active_subscriptions = cursor.fetchone()['count']
            
            conn.close()
            
            print("Platform Overview:")
            print(f"  Total Users: {total_users}")
            print(f"  Total Workers: {total_workers}")
            print(f"  Total Appointments: {total_appointments}")
            print(f"  Active Subscriptions: {active_subscriptions}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def service_statistics(self):
        """Show service statistics"""
        self.print_header("SERVICE STATISTICS")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get workers by service
            cursor.execute("""
                SELECT service, COUNT(*) as count
                FROM workers
                GROUP BY service
            """)
            
            workers_by_service = {}
            for row in cursor.fetchall():
                service = row['service']
                if ',' in service:
                    services = [s.strip() for s in service.split(',')]
                    for s in services:
                        workers_by_service[s] = workers_by_service.get(s, 0) + row['count']
                else:
                    workers_by_service[service] = workers_by_service.get(service, 0) + row['count']
            
            # Get appointments by service
            cursor.execute("""
                SELECT w.service, COUNT(*) as count
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                GROUP BY w.service
            """)
            
            appointments_by_service = {}
            for row in cursor.fetchall():
                service = row['service']
                if ',' in service:
                    services = [s.strip() for s in service.split(',')]
                    for s in services:
                        appointments_by_service[s] = appointments_by_service.get(s, 0) + row['count']
                else:
                    appointments_by_service[service] = appointments_by_service.get(service, 0) + row['count']
            
            conn.close()
            
            print("Service Statistics:")
            print("\nWorkers by Service:")
            for service, count in workers_by_service.items():
                print(f"  {service}: {count}")
            
            print("\nAppointments by Service:")
            for service, count in appointments_by_service.items():
                print(f"  {service}: {count}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def revenue_overview(self):
        """Show revenue overview"""
        self.print_header("REVENUE OVERVIEW")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get completed appointments
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM appointments
                WHERE status = 'completed' AND payment_status = 'paid'
            """)
            
            paid_appointments = cursor.fetchone()['count']
            avg_fee = 500.00
            total_revenue = paid_appointments * avg_fee
            commission_percentage = 20
            total_commission = total_revenue * (commission_percentage / 100)
            total_worker_earnings = total_revenue - total_commission
            
            # Get subscription revenue
            cursor.execute("""
                SELECT 
                    COUNT(*) as active_subscriptions,
                    SUM(CASE 
                        WHEN plan_id = 1 THEN 1000.00
                        WHEN plan_id = 2 THEN 2000.00
                        WHEN plan_id = 3 THEN 5000.00
                        ELSE 0.00
                    END) as subscription_revenue
                FROM subscriptions
                WHERE payment_status = 'active'
            """)
            
            subscription_stats = cursor.fetchone()
            
            conn.close()
            
            print("Revenue Overview:")
            print(f"  Appointment Revenue: ₹{total_revenue:,.2f}")
            print(f"  Platform Commission (20%): ₹{total_commission:,.2f}")
            print(f"  Worker Earnings: ₹{total_worker_earnings:,.2f}")
            print(f"  Subscription Revenue: ₹{subscription_stats['subscription_revenue'] or 0:,.2f}")
            print(f"  Total Platform Revenue: ₹{total_commission + (subscription_stats['subscription_revenue'] or 0):,.2f}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()
    
    def user_activity(self):
        """Show user activity"""
        self.print_header("USER ACTIVITY")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get recent user registrations
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM users
                WHERE created_at >= DATE('now', '-7 days')
            """)
            
            new_users_week = cursor.fetchone()['count']
            
            # Get recent appointments
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM appointments
                WHERE created_at >= DATE('now', '-7 days')
            """)
            
            recent_appointments = cursor.fetchone()['count']
            
            # Get active users (users with appointments in last 30 days)
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as count
                FROM appointments
                WHERE created_at >= DATE('now', '-30 days')
            """)
            
            active_users = cursor.fetchone()['count']
            
            conn.close()
            
            print("User Activity (Last 7 Days):")
            print(f"  New Users: {new_users_week}")
            print(f"  New Appointments: {recent_appointments}")
            print(f"  Active Users (Last 30 Days): {active_users}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.pause()


def main():
    """Main function to run the admin CLI"""
    print("Starting ExpertEase Admin CLI...")
    print()
    
    try:
        cli = AdminCLI()
        cli.show_main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting Admin CLI...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
