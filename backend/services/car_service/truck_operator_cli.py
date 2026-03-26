"""
Truck Operator CLI Interface
Handles truck operator signup, login, and dashboard access
"""

import os
import requests
import time
from datetime import datetime

API = "http://127.0.0.1:5000"

def truck_operator_signup():
    """Truck operator signup process"""
    print("\n" + "="*60)
    print("  TRUCK OPERATOR SIGNUP")
    print("="*60)
    
    try:
        # Basic info
        name = input("  Enter full name: ").strip()
        email = input("  Enter email: ").strip()
        phone = input("  Enter phone: ").strip()
        password = input("  Enter password: ").strip()
        city_name = input("   Enter city name: ").strip()
        
        # Vehicle type dropdown
        print("\n  Vehicle Type:")
        print("1. Mini Truck")
        print("2. Medium Truck")
        print("3. Heavy Truck")
        print("4. Trailer")
        print("5. Tanker")
        
        while True:
            vehicle_choice = input("Select vehicle type (1-5): ").strip()
            if vehicle_choice == "1":
                vehicle_type = "Mini Truck"
                break
            elif vehicle_choice == "2":
                vehicle_type = "Medium Truck"
                break
            elif vehicle_choice == "3":
                vehicle_type = "Heavy Truck"
                break
            elif vehicle_choice == "4":
                vehicle_type = "Trailer"
                break
            elif vehicle_choice == "5":
                vehicle_type = "Tanker"
                break
            else:
                print("  Invalid choice. Please select 1-5.")
        
        vehicle_number = input("  Enter vehicle number: ").strip()
        
        # Document paths
        print("\n  Document Uploads")
        print("Enter file paths for required documents:")
        
        vehicle_photo_path = input("Enter Vehicle Photo file path: ").strip()
        rc_book_path = input("Enter RC Book Photo file path: ").strip()
        petrol_pump_auth_path = input("Enter Petrol Pump Authorization Letter file path: ").strip()
        
        # Validation
        if not all([name, email, phone, password, city_name, vehicle_type, vehicle_number]):
            print("  All required fields must be filled")
            return
        
        # Validate file paths exist
        for file_path, file_name in [(vehicle_photo_path, "Vehicle Photo"), 
                                     (rc_book_path, "RC Book"), 
                                     (petrol_pump_auth_path, "Petrol Pump Authorization Letter")]:
            if file_path and not os.path.exists(file_path):
                print(f"  {file_name} file not found: {file_path}")
                return
        
        # Prepare data
        data = {
            'name': name,
            'email': email,
            'phone': phone,
            'password': password,
            'city_name': city_name,
            'vehicle_type': vehicle_type,
            'vehicle_number': vehicle_number,
            'worker_type': 'truck_operator'
        }
        
        # Prepare files
        files = {}
        if vehicle_photo_path:
            files['vehicle_photo'] = open(vehicle_photo_path, 'rb')
        if rc_book_path:
            files['rc_book'] = open(rc_book_path, 'rb')
        if petrol_pump_auth_path:
            files['petrol_pump_auth'] = open(petrol_pump_auth_path, 'rb')
        
        print("\n  Creating account...")
        
        response = requests.post(
            f"{API}/api/truck-operator/signup",
            data=data,
            files=files
        )
        
        # Close files
        for file in files.values():
            file.close()
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n  Signup successful!")
            print(f"  Name: {name}")
            print(f"  Email: {email}")
            print(f"  Phone: {phone}")
            print(f"   City: {city_name}")
            print(f"  Vehicle: {vehicle_type} - {vehicle_number}")
            print(f"  Worker ID: {result.get('worker_id')}")
            print(f"  Status: Pending approval")
            print("\n  Your account is pending admin approval.")
            print("  You will be notified once approved.")
        else:
            error = response.json().get('error', 'Signup failed')
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Error: {e}")
        input("\nPress Enter to continue...")

def truck_operator_login():
    """Truck operator login process"""
    print("\n" + "="*60)
    print("  TRUCK OPERATOR LOGIN")
    print("="*60)
    
    try:
        email = input("  Enter email: ").strip()
        password = input("  Enter password: ").strip()
        
        if not email or not password:
            print("  Email and password are required")
            return
        
        print("\n  Logging in...")
        
        response = requests.post(
            f"{API}/api/truck-operator/login",
            json={'email': email, 'password': password}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  Login successful!")
            print(f"  Welcome, {result.get('name')}!")
            print(f"  Vehicle: {result.get('vehicle_type')} - {result.get('vehicle_number')}")
            print(f"   City: {result.get('city_name')}")
            
            # Store login info for session
            worker_info = {
                'worker_id': result.get('worker_id'),
                'name': result.get('name'),
                'email': email,
                'vehicle_type': result.get('vehicle_type'),
                'vehicle_number': result.get('vehicle_number'),
                'city_name': result.get('city_name'),
                'token': result.get('token')
            }
            
            truck_operator_dashboard(worker_info)
        else:
            error = response.json().get('error', 'Login failed')
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Error: {e}")
        input("\nPress Enter to continue...")

def truck_operator_dashboard(worker_info):
    """Truck operator dashboard with application management"""
    while True:
        print("\n" + "="*60)
        print("  TRUCK OPERATOR DASHBOARD")
        print("="*60)
        print(f"  Name: {worker_info['name']}")
        print(f"  Vehicle: {worker_info['vehicle_type']} - {worker_info['vehicle_number']}")
        print(f"   City: {worker_info['city_name']}")
        print(f"  Email: {worker_info['email']}")
        print(f"  Worker ID: {worker_info['worker_id']}")
        print("="*60)
        print("1.   View Profile")
        print("2.   Available Applications/Jobs")
        print("3.   Active Jobs")
        print("4.   Job History & Earnings")
        print("5.    Performance & Support")
        print("6. Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_truck_operator_profile(worker_info)
        elif choice == "2":
            view_available_applications(worker_info)
        elif choice == "3":
            view_active_jobs(worker_info)
        elif choice == "4":
            job_history_menu(worker_info)
        elif choice == "5":
            view_performance_support(worker_info)
        elif choice == "6":
            print("\n  Logging out...")
            break
        else:
            print("  Invalid choice")
            input("\nPress Enter to continue...")

def view_truck_operator_profile(worker_info):
    """View truck operator profile details"""
    print("\n" + "="*60)
    print("  TRUCK OPERATOR PROFILE")
    print("="*60)
    print(f"  Name: {worker_info['name']}")
    print(f"  Email: {worker_info['email']}")
    print(f"  Vehicle Type: {worker_info['vehicle_type']}")
    print(f"  Vehicle Number: {worker_info['vehicle_number']}")
    print(f"   City: {worker_info['city_name']}")
    print(f"  Worker ID: {worker_info['worker_id']}")
    print(f"   Worker Type: Truck Operator")
    
    input("\nPress Enter to continue...")

def view_available_applications(worker_info):
    """View available applications/jobs for truck operators"""
    try:
        print("\n  Loading available applications...")
        response = requests.get(f"{API}/api/truck-operator/applications/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            applications_data = response.json()
            applications = applications_data.get('applications', [])
            
            print("\n" + "="*60)
            print("  AVAILABLE APPLICATIONS")
            print("="*60)
            
            if not applications:
                print("  No available applications at the moment")
            else:
                for i, app in enumerate(applications, 1):
                    print(f"\n[{i}] Application ID: {app.get('application_id')}")
                    print(f"      Pickup: {app.get('pickup_location', 'N/A')}")
                    print(f"      Drop-off: {app.get('dropoff_location', 'N/A')}")
                    print(f"      Cargo: {app.get('cargo_type', 'N/A')}")
                    print(f"      Payment: ${app.get('payment_amount', 0)}")
                    print(f"      Date: {app.get('pickup_date', 'N/A')}")
                    print(f"      Priority: {app.get('priority_level', 1)}")
                
                print(f"\nTotal available applications: {len(applications)}")
                
                # Option to accept application
                if applications:
                    accept_choice = input("\nAccept an application? (Enter application number or 'n'): ").strip().lower()
                    if accept_choice.isdigit() and 1 <= int(accept_choice) <= len(applications):
                        application_to_accept = applications[int(accept_choice) - 1]
                        accept_application(worker_info, application_to_accept['application_id'])
        else:
            print("  Failed to load applications")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def accept_application(worker_info, application_id):
    """Accept an application"""
    try:
        print(f"\n  Accepting application {application_id}...")
        response = requests.post(f"{API}/api/truck-operator/applications/{application_id}/accept",
                               json={'operator_id': worker_info['worker_id']})
        
        if response.status_code == 200:
            result = response.json()
            print(f"  {result.get('message', 'Application accepted successfully')}")
            print("  You are now assigned to this job")
        else:
            error = response.json().get('error', 'Failed to accept application')
            print(f"  {error}")
        
    except Exception as e:
        print(f"  Error: {e}")

def view_active_jobs(worker_info):
    """View current active jobs"""
    try:
        print("\n  Loading active jobs...")
        response = requests.get(f"{API}/api/truck-operator/active-jobs/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            jobs_data = response.json()
            active_jobs = jobs_data.get('active_jobs', [])
            
            print("\n" + "="*60)
            print("  ACTIVE JOBS")
            print("="*60)
            
            if not active_jobs:
                print("  No active jobs")
            else:
                for i, job in enumerate(active_jobs, 1):
                    print(f"\n[{i}] Job ID: {job.get('job_id')}")
                    print(f"      Pickup: {job.get('pickup_location', 'N/A')}")
                    print(f"      Drop-off: {job.get('dropoff_location', 'N/A')}")
                    print(f"      Cargo: {job.get('cargo_type', 'N/A')}")
                    print(f"      Started: {job.get('started_at', 'N/A')}")
                    print(f"      Status: {job.get('status', 'N/A')}")
        else:
            print("  Failed to load active jobs")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def job_history_menu(worker_info):
    """Job history and earnings menu"""
    while True:
        print("\n" + "="*60)
        print("  JOB HISTORY & EARNINGS")
        print("="*60)
        print("1.   View Job History")
        print("2.   View Earnings Summary")
        print("3.   Performance Analytics")
        print("4.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_job_history(worker_info)
        elif choice == "2":
            view_earnings_summary(worker_info)
        elif choice == "3":
            view_performance_analytics(worker_info)
        elif choice == "4":
            break
        else:
            print("  Invalid choice")
            input("\nPress Enter to continue...")

def view_job_history(worker_info):
    """View truck operator's job history"""
    try:
        print("\n  Loading job history...")
        response = requests.get(f"{API}/api/truck-operator/job-history/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            history_data = response.json()
            
            if history_data['success']:
                jobs = history_data.get('jobs', [])
                
                print(f"\n  JOB HISTORY ({len(jobs)} jobs)")
                print("="*60)
                
                if not jobs:
                    print("  No job history found")
                else:
                    for i, job in enumerate(jobs, 1):
                        print(f"\n[{i}] Job ID: {job.get('job_id')}")
                        print(f"      Route: {job.get('pickup_location', 'N/A')}   {job.get('dropoff_location', 'N/A')}")
                        print(f"      Cargo: {job.get('cargo_type', 'N/A')}")
                        print(f"      Date: {job.get('completed_date', 'N/A')}")
                        print(f"      Earnings: ${job.get('earnings', 0)}")
                        print(f"      Status: {job.get('status', 'N/A')}")
                
                print(f"\nTotal jobs completed: {len(jobs)}")
            else:
                print(f"  {history_data.get('error', 'Failed to load history')}")
        else:
            print("  Failed to load job history")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def view_earnings_summary(worker_info):
    """View earnings summary"""
    try:
        print("\n  Loading earnings summary...")
        response = requests.get(f"{API}/api/truck-operator/earnings/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            earnings_data = response.json()
            
            if earnings_data['success']:
                print("\n" + "="*60)
                print("  EARNINGS SUMMARY")
                print("="*60)
                print(f"  Total Earnings: ${earnings_data.get('total_earnings', 0)}")
                print(f"  Jobs Completed: {earnings_data.get('jobs_completed', 0)}")
                print(f"  Average per Job: ${earnings_data.get('average_per_job', 0)}")
                print(f"  This Month: ${earnings_data.get('this_month', 0)}")
                print(f"  Last Month: ${earnings_data.get('last_month', 0)}")
            else:
                print(f"  {earnings_data.get('error', 'Failed to load earnings')}")
        else:
            print("  Failed to load earnings summary")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def view_performance_analytics(worker_info):
    """View performance analytics"""
    try:
        print("\n  Loading performance analytics...")
        response = requests.get(f"{API}/api/truck-operator/analytics/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            analytics_data = response.json()
            
            if analytics_data['success']:
                print("\n" + "="*60)
                print("  PERFORMANCE ANALYTICS")
                print("="*60)
                print(f"  Total Jobs: {analytics_data.get('total_jobs', 0)}")
                print(f"  Completed Jobs: {analytics_data.get('completed_jobs', 0)}")
                print(f"  Completion Rate: {analytics_data.get('completion_rate', 0)}%")
                print(f"  Average Rating: {analytics_data.get('average_rating', 0)}/5.0")
                print(f"   Average Delivery Time: {analytics_data.get('avg_delivery_time', 0)} hours")
            else:
                print(f"  {analytics_data.get('error', 'Failed to load analytics')}")
        else:
            print("  Failed to load performance analytics")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def view_performance_support(worker_info):
    """View performance and support options"""
    try:
        print("\n  Loading performance data...")
        
        response = requests.get(f"{API}/api/truck-operator/performance/{worker_info['worker_id']}")
        
        if response.status_code == 200:
            performance_data = response.json()
            
            print("\n" + "="*60)
            print("   PERFORMANCE & SUPPORT")
            print("="*60)
            
            # Performance metrics
            print(f"  Total Jobs: {performance_data.get('total_jobs', 0)}")
            print(f"  Rating: {performance_data.get('rating', 0)}/5.0")
            print(f"  Total Earnings: ${performance_data.get('total_earnings', 0)}")
            
            # Support options
            print(f"\n  Support Options:")
            print(f"    Technical Support: support@truckoperator.com")
            print(f"    Payment Issues: billing@truckoperator.com")
            print(f"    Account Help: help@truckoperator.com")
            print(f"    Emergency: +1-800-TRUCK-1")
            
        else:
            print("  Failed to load performance data")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")
