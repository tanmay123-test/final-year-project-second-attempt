"""
Car Service Unified Worker CLI Interface
Handles all car service worker types with unified database
"""

import os
import requests
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

API = "http://127.0.0.1:5000"

def unified_mechanic_signup():
    """Unified mechanic signup process"""
    print("\n" + "="*60)
    print("  MECHANIC SIGNUP")
    print("="*60)
    
    try:
        # Basic info
        name = input("  Enter full name: ").strip()
        email = input("  Enter email: ").strip()
        phone = input("  Enter phone: ").strip()
        password = input("  Enter password: ").strip()
        age = input("  Enter age: ").strip()
        city = input("   Enter city: ").strip()
        address = input("  Enter address: ").strip()
        experience = input("  Enter experience (years): ").strip()
        skills = input("  Enter skills (comma separated): ").strip()
        
        # Document paths
        print("\n  Document Uploads")
        print("Enter file paths for required documents:")
        
        profile_photo = input("Profile photo filename: ").strip()
        aadhaar_card = input("Aadhaar card filename: ").strip()
        driving_license = input("Driving license filename: ").strip()
        certificate = input("Certificate filename (optional): ").strip() or None
        
        # Security declaration
        print("\n  SECURITY DECLARATION")
        print("I confirm all documents are valid and I agree to platform policies")
        print("(Type YES in any case: yes, YES, Yes)")
        confirm = input("Type YES to continue: ").strip()
        
        if confirm.upper() != "YES":
            print("  Security declaration not accepted. Signup cancelled.")
            return
        
        # Validation
        if not all([name, email, phone, password, age, city, address, experience, skills]):
            print("  All required fields must be filled")
            return
        
        # Prepare data
        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "role": "Mechanic",
            "age": age,
            "city": city,
            "address": address,
            "experience": experience,
            "skills": skills,
            "security_declaration": "1"
        }
        
        if certificate:
            data["certificate"] = certificate
        
        # For now, simulate file uploads with paths
        files = {}
        if profile_photo:
            files["profile_photo"] = ("profile_photo.jpg", "dummy", "image/jpeg")
        if aadhaar_card:
            files["aadhaar_card"] = ("aadhaar.jpg", "dummy", "image/jpeg")
        if driving_license:
            files["driving_license"] = ("license.jpg", "dummy", "image/jpeg")
        if certificate:
            files["certificate"] = ("certificate.pdf", "dummy", "application/pdf")
        
        # Call API
        response = requests.post(f"{API}/api/car/service/worker/signup", data=data, files=files)
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n  {result.get('message', 'Signup successful!')}")
            print(f"  Worker ID: {result.get('worker_id')}")
            print("\n" + "="*60)
            print("  APPROVAL STATUS")
            print("="*60)
            print("  Your account has been submitted for admin review")
            print("    Expected approval time: 2-24 hours")
            print("  You will receive a notification once approved")
            print("  After approval, you can login and access your dashboard")
            print("\n  For urgent inquiries, contact support")
            print("="*60)
        else:
            error = response.json().get("error", "Signup failed")
            print(f"  {error}")
        
    except Exception as e:
        print(f"  Signup error: {e}")

def unified_mechanic_login():
    """Unified mechanic login process"""
    print("\n" + "="*50)
    print("  MECHANIC LOGIN")
    print("="*50)
    
    try:
        email = input("  Enter email: ").strip()
        password = input("  Enter password: ").strip()
        
        if not email or not password:
            print("  Email and password are required")
            return
        
        # Call unified API
        response = requests.post(f"{API}/api/car/service/worker/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            result = response.json()
            worker = result.get("worker", {})
            token = result.get("token")
            
            print(f"\n  Login successful!")
            print(f"  Welcome, {worker.get('name', 'Mechanic')}!")
            print(f"  Role: {worker.get('role', 'Unknown')}")
            print(f"   City: {worker.get('city', 'Unknown')}")
            print(f"  Experience: {worker.get('experience', 0)} years")
            
            # Open mechanic dashboard
            unified_mechanic_dashboard(worker, token)
                
        elif response.status_code == 401:
            print("  Invalid email or password")
        elif response.status_code == 403:
            result = response.json()
            status = result.get("status", "PENDING")
            print("\n" + "="*60)
            print("  ACCOUNT PENDING APPROVAL")
            print("="*60)
            print("  Your account is still under admin review")
            print("    Expected approval time: 2-24 hours")
            print("  You will receive a notification once approved")
            print("  Current status: " + status)
            print("\n  Please try logging in again after approval")
            print("  For urgent inquiries, contact support")
            print("="*60)
        else:
            error = response.json().get("error", "Login failed")
            print(f"  {error}")
            
    except Exception as e:
        print(f"  Login error: {e}")

def unified_mechanic_dashboard(worker, token):
    """Unified mechanic dashboard menu"""
    while True:
        print("\n" + "="*60)
        print("  MECHANIC DASHBOARD")
        print("="*60)
        print(f"  {worker.get('name')}")
        print(f"  {worker.get('email')}")
        print(f"  {worker.get('phone')}")
        print(f"   {worker.get('city')}")
        print(f"  Experience: {worker.get('experience', 0)} years")
        print(f"  Skills: {worker.get('skills', 'N/A')}")
        print(f"  Status: {'ONLINE' if worker.get('is_online', 0) else 'OFFLINE'}")
        
        print("\nOptions:")
        print("1.   Go Online / Offline")
        print("2.   Job Requests (Transparent Queue)")
        print("3.   Active Jobs")
        print("4.   Earnings & Fairness Insights")
        print("5.   Performance, Safety & Support")
        print("6.   Manage Available Slots")
        print("7.   Logout")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            mechanic_status_control(worker, token)
        if choice == "2":
            job_requests_queue(worker, token)
        if choice == "3":
            active_jobs_screen(worker, token)
        if choice == "4":
            earnings_fairness_screen(worker, token)
        if choice == "5":
            performance_safety_screen(worker, token)
        if choice == "6":
            manage_available_slots(worker, token)
        elif choice == "7":
            print("  Logged out successfully")
            return
        else:
            print("  Invalid choice")

def toggle_online_status(worker, token):
    """Toggle mechanic online/offline status"""
    try:
        current_status = worker.get('is_online', 0)
        new_status = 1 if current_status == 0 else 0

        response = requests.put(
            f"{API}/api/car/mechanic/go-online" if new_status else f"{API}/api/car/mechanic/go-offline",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n {result.get('message', 'Status updated')}")
            # Update local worker data
            worker['is_online'] = new_status
        else:
            error = response.json().get("error", "Failed to update status")
            print(f" {error}")

        input("\nPress Enter to continue...")

    except Exception as e:
        print(f" Status update error: {e}")
        input("\nPress Enter to continue...")

def mechanic_status_control(worker, token):
    """Mechanic status control submenu"""
    while True:
        print("\n" + "="*50)
        print(" MECHANIC STATUS CONTROL")
        print("="*50)

        # Get current status
        try:
            response = requests.get(f"{API}/api/car/service/worker/status",
                                   headers={"Authorization": f"Bearer {token}"})
            
            if response.status_code == 200:
                result = response.json()
                status = "ONLINE" if result.get("is_online", 0) and not result.get("is_busy", 0) else "OFFLINE" if not result.get("is_online", 0) else "BUSY"
                is_online = result.get("is_online", 0)
                is_busy = result.get("is_busy", 0)
                service_radius = result.get("service_radius", 10)
                current_city = result.get("city", "Not set")
                
                print(f"\n  Current Status:")
                print(f"   Status: {status}")
                print(f"   Online: {' ' if is_online else ' '}")
                print(f"   Busy: {' ' if is_busy else ' '}")
                print(f"   Service Radius: {service_radius} km")
                print(f"   Current City: {current_city}")
                
            else:
                print("  Failed to get status")
                
        except Exception as e:
            print(f"  Status check error: {e}")

        print("\nOptions:")
        print("1. Go Online")
        print("2. Go Offline")
        print("3. Set Service Radius")
        print("4. Update Working City")
        print("5. View Current Status")
        print("6. Back")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            go_online(worker, token)
        elif choice == "2":
            go_offline(worker, token)
        elif choice == "3":
            update_service_radius(worker, token)
        elif choice == "4":
            update_current_location(worker, token)
        elif choice == "5":
            view_current_status(worker, token)
        elif choice == "6":
            return
        else:
            print("  Invalid choice")

def go_online(worker, token):
    """Set mechanic to ONLINE status"""
    try:
        response = requests.put(f"{API}/api/car/service/worker/availability",
                             json={"is_online": True},
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Status updated')}")
            # Update local worker data
            worker['is_online'] = 1
            worker['is_busy'] = 0
            worker['last_status_update'] = datetime.now().isoformat()
        else:
            error = response.json().get("error", "Failed to go online")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Go online error: {e}")
        input("\nPress Enter to continue...")

def go_offline(worker, token):
    """Set mechanic to OFFLINE status"""
    try:
        response = requests.put(f"{API}/api/car/service/worker/availability",
                             json={"is_online": False},
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Status updated')}")
            # Update local worker data
            worker['is_online'] = 0
            worker['is_busy'] = 0
            worker['last_status_update'] = datetime.now().isoformat()
        else:
            error = response.json().get("error", "Failed to go offline")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Go offline error: {e}")
        input("\nPress Enter to continue...")

def update_service_radius(worker, token):
    """Update mechanic service radius"""
    try:
        current_radius = worker.get('service_radius', 10)
        new_radius = input(f"\nCurrent service radius: {current_radius} km\nNew service radius (km): ").strip()
        
        if not new_radius:
            print("  Service radius cannot be empty")
            return
        
        try:
            new_radius = int(new_radius)
            if new_radius < 1 or new_radius > 50:
                print("  Service radius must be between 1 and 50 km")
                return
        except ValueError:
            print("  Invalid radius value")
            return
        
        response = requests.put(f"{API}/api/car/service/worker/availability",
                             json={"service_radius": new_radius},
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Service radius updated')}")
            # Update local worker data
            worker['service_radius'] = new_radius
        else:
            error = response.json().get("error", "Failed to update service radius")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Service radius update error: {e}")
        input("\nPress Enter to continue...")

def update_current_location(worker, token):
    """Update mechanic current working city"""
    try:
        current_city = worker.get('current_city', worker.get('city', 'Not set'))
        new_city = input(f"\nCurrent city: {current_city}\nNew working city: ").strip()
        
        if not new_city:
            print("  City cannot be empty")
            return
        
        response = requests.put(f"{API}/api/car/service/worker/availability",
                             json={"current_city": new_city},
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Location updated')}")
            # Update local worker data
            worker['current_city'] = new_city
        else:
            error = response.json().get("error", "Failed to update location")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Location update error: {e}")
        input("\nPress Enter to continue...")

def view_current_status(worker, token):
    """View mechanic's current status"""
    try:
        response = requests.get(f"{API}/api/car/service/worker/status",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "UNKNOWN")
            is_online = result.get("is_online", 0)
            is_busy = result.get("is_busy", 0)
            service_radius = result.get("service_radius", 10)
            current_city = result.get("current_city", result.get("city", "Not set"))
            last_update = result.get("last_status_update", "Never")
            cooldown_until = result.get("cooldown_until", "None")
            
            print(f"\n  CURRENT STATUS")
            print("=" * 40)
            print(f"   Status: {status}")
            print(f"   Online: {' ' if is_online else ' '}")
            print(f"   Busy: {' ' if is_busy else ' '}")
            print(f"   Service Radius: {service_radius} km")
            print(f"   Current City: {current_city}")
            print(f"   Last Update: {last_update}")
            if cooldown_until != "None":
                print(f"   Cooldown Until: {cooldown_until}")
            print("=" * 40)
            
        else:
            print("  Failed to get current status")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Status view error: {e}")
        input("\nPress Enter to continue...")

def job_completed(worker, token):
    """Handle job completion - automatically set mechanic to AVAILABLE"""
    try:
        print("\n JOB COMPLETED!")
        print("=" * 40)
        print(" Job marked as completed")
        print(" Status changing to ONLINE...")

        # Set to AVAILABLE (ONLINE but not BUSY)
        response = requests.put(f"{API}/api/car/mechanic/set-available",
                             headers={"Authorization": f"Bearer {token}"})

        if response.status_code == 200:
            result = response.json()
            print(f" {result.get('message', 'Status updated')}")
            # Update local worker data
            worker['is_online'] = 1
            worker['is_busy'] = 0
            worker['last_status_update'] = datetime.now().isoformat()
            print(" You can now receive new jobs")
        else:
            error = response.json().get("error", "Failed to update status")
            print(f" {error}")

        input("\nPress Enter to continue...")

    except Exception as e:
        print(f" Job completion error: {e}")
        input("\nPress Enter to continue...")

def job_accepted(worker, token):
    """Handle job acceptance - automatically set mechanic to BUSY"""
    try:
        print("\n JOB ACCEPTED!")
        print("=" * 40)
        print(" Job assigned to you")
        print(" Status changing to BUSY...")

        # Set to BUSY
        response = requests.put(f"{API}/api/car/mechanic/set-busy",
                             headers={"Authorization": f"Bearer {token}"})

        if response.status_code == 200:
            result = response.json()
            print(f" {result.get('message', 'Status updated')}")
            # Update local worker data
            worker['is_online'] = 1
            worker['is_busy'] = 1
            worker['last_status_update'] = datetime.now().isoformat()
            print(" You will not receive new jobs until current job completes")
        else:
            error = response.json().get("error", "Failed to set busy status")
            print(f" {error}")

        input("\nPress Enter to continue...")

    except Exception as e:
        print(f" Job acceptance error: {e}")
        input("\nPress Enter to continue...")

def job_requests_queue(worker, token):
    """Display and manage job requests queue"""
    try:
        # Get pending jobs
        response = requests.get(f"{API}/api/car/mechanic/jobs",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("jobs", [])
            
            print("\n" + "="*60)
            print("  JOB REQUESTS")
            print("="*60)
            
            if not jobs:
                print("  No pending job requests")
                print("  Go online to receive job requests")
                input("\nPress Enter to continue...")
                return
            
            # Display jobs
            for i, job in enumerate(jobs, 1):
                print(f"\n{' ' if job['priority'] == 'EMERGENCY' else ' '} Request ID: {job['id']}")
                print(f"  User: {job['user_name']}")
                print(f"  Email: {job['user_email']}")
                print(f"  Phone: {job['user_phone']}")
                print(f"  Car: {job['car_model']}")
                print(f"  Issue: {job['issue']}")
                print(f"   City: {job['user_city']}")
                print(f"  Distance: {job['distance_km']:.1f} km")
                print(f"   ETA: {job['eta_minutes']} minutes")
                print(f"  Estimated earning:  {job['estimated_earning']:.0f}")
                print(f"  Priority: {job['priority']}")
                
                if job['assignment_reason']:
                    print(f"  Assignment reason:")
                    print(f"   {job['assignment_reason']}")
                
                if i < len(jobs):
                    print("-" * 40)
            
            print(f"\nTotal pending requests: {len(jobs)}")
            
            # Handle job actions
            if len(jobs) == 1:
                handle_single_job(jobs[0], token)
            else:
                handle_multiple_jobs(jobs, token)
                
        else:
            print("  Failed to get job requests")
            input("\nPress Enter to continue...")
            
    except Exception as e:
        print(f"  Job requests error: {e}")
        input("\nPress Enter to continue...")

def handle_single_job(job, token):
    """Handle actions for a single job"""
    print(f"\n{' ' if job['priority'] == 'EMERGENCY' else ' '} Job Request: {job['id']}")
    print("="*50)
    print(f"  User: {job['user_name']}")
    print(f"  Email: {job['user_email']}")
    print(f"  Phone: {job['user_phone']}")
    print(f"  Car: {job['car_model']}")
    print(f"  Issue: {job['issue']}")
    print(f"  Distance: {job['distance_km']:.1f} km")
    print(f"   ETA: {job['eta_minutes']} minutes")
    print(f"  Estimated earning:  {job['estimated_earning']:.0f}")
    print(f"  Priority: {job['priority']}")
    
    if job['assignment_reason']:
        print(f"  Assignment reason:")
        print(f"   {job['assignment_reason']}")
    
    print("\nOptions:")
    print("1.   Accept")
    print("2.   Reject")
    print("3.    Back")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        accept_job(job['id'], token)
    elif choice == "2":
        reject_job(job['id'], token)
    elif choice == "3":
        return
    else:
        print("  Invalid choice")

def handle_multiple_jobs(jobs, token):
    """Handle actions for multiple jobs"""
    print("\nOptions:")
    print("1.   Accept Job")
    print("2.   Reject Job")
    print("3.   View Job Details")
    print("4.    Back")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        job_id = input("Enter Job ID to accept: ").strip()
        if job_id.isdigit():
            job_id = int(job_id)
            # Find job
            job = next((j for j in jobs if j['id'] == job_id), None)
            if job:
                accept_job(job['id'], token)
            else:
                print("  Job not found")
        else:
            print("  Invalid Job ID")
    
    elif choice == "2":
        job_id = input("Enter Job ID to reject: ").strip()
        if job_id.isdigit():
            job_id = int(job_id)
            # Find job
            job = next((j for j in jobs if j['id'] == job_id), None)
            if job:
                reject_job(job['id'], token)
            else:
                print("  Job not found")
        else:
            print("  Invalid Job ID")
    
    elif choice == "3":
        job_id = input("Enter Job ID to view: ").strip()
        if job_id.isdigit():
            job_id = int(job_id)
            # Find job
            job = next((j for j in jobs if j['id'] == job_id), None)
            if job:
                view_job_details(job)
            else:
                print("  Job not found")
        else:
            print("  Invalid Job ID")
    
    elif choice == "4":
        return
    else:
        print("  Invalid choice")

def view_job_details(job):
    """View detailed job information"""
    print(f"\n{' ' if job['priority'] == 'EMERGENCY' else ' '} Job Details: {job['id']}")
    print("="*60)
    print(f"  User: {job['user_name']}")
    print(f"  Car: {job['car_model']}")
    print(f"  Issue: {job['issue']}")
    print(f"  Issue Type: {job['issue_type']}")
    print(f"   User City: {job['user_city']}")
    print(f"  Distance: {job['distance_km']:.1f} km")
    print(f"   ETA: {job['eta_minutes']} minutes")
    print(f"  Estimated earning:  {job['estimated_earning']:.0f}")
    print(f"  Priority: {job['priority']}")
    print(f"  Created: {job['created_at']}")
    
    if job['assignment_reason']:
        print(f"\n  Assignment reason:")
        print(f"   {job['assignment_reason']}")
    
    print("\n" + "="*60)
    input("\nPress Enter to continue...")

def accept_job(job_id, token):
    """Accept a job request"""
    try:
        response = requests.post(f"{API}/api/car/mechanic/job/accept",
                              json={"job_id": job_id},
                              headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Job accepted')}")
            print(f"  {result.get('note', 'Status updated')}")
            print("  Job moved to Active Jobs")
        else:
            error = response.json().get("error", "Failed to accept job")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Accept job error: {e}")
        input("\nPress Enter to continue...")

def reject_job(job_id, token):
    """Reject a job request"""
    try:
        reason = input("Reason for rejection (optional): ").strip() or "Mechanic unavailable"
        
        response = requests.post(f"{API}/api/car/mechanic/job/reject",
                              json={"job_id": job_id, "reason": reason},
                              headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Job rejected')}")
            print(f"  {result.get('note', 'Request sent to next mechanic')}")
        else:
            error = response.json().get("error", "Failed to reject job")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Reject job error: {e}")
        input("\nPress Enter to continue...")

def active_jobs_screen(worker, token):
    """Display and manage active jobs"""
    try:
        # Get active job
        response = requests.get(f"{API}/api/car/mechanic/active-job",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            data = response.json()
            active_job = data.get("active_job")
            
            print("\n" + "="*60)
            print("  ACTIVE JOBS")
            print("="*60)
            
            if not active_job:
                print("  No active jobs")
                print("  Accept job requests to start working")
                input("\nPress Enter to continue...")
                return
            
            # Display active job
            print(f"\n  ACTIVE JOB: {active_job['id']}")
            print("="*50)
            print(f"  User: {active_job['user_name']}")
            print(f"  Car: {active_job['car_model']}")
            print(f"  Issue: {active_job['issue']}")
            print(f"   User Location: {active_job.get('user_city', 'Unknown')}")
            
            if active_job.get('user_lat') and active_job.get('user_long'):
                print(f"  User Coordinates: {active_job['user_lat']:.6f}, {active_job['user_long']:.6f}")
            
            if active_job.get('mechanic_lat') and active_job.get('mechanic_long'):
                print(f"  Your Coordinates: {active_job['mechanic_lat']:.6f}, {active_job['mechanic_long']:.6f}")
            
            print(f"  Distance: {active_job.get('distance_km', 0):.1f} km")
            print(f"   ETA: {active_job.get('eta_minutes', 0)} minutes")
            print(f"  Estimated earning:  {active_job.get('estimated_earning', 0):.0f}")
            print(f"  Status: {active_job['status']}")
            
            if active_job['status'] == 'WORKING':
                print(f"  Repair time: {active_job.get('repair_time', '0 minutes')}")
            
            if active_job.get('before_photo'):
                print(f"  Before photo:   Uploaded")
            else:
                print(f"  Before photo:   Not uploaded")
            
            if active_job.get('after_photo'):
                print(f"  After photo:   Uploaded")
            else:
                print(f"  After photo:   Not uploaded")
            
            print("\n" + "-"*50)
            
            # Show options based on status
            show_active_job_options(active_job, token)
                
        else:
            print("  Failed to get active job")
            input("\nPress Enter to continue...")
            
    except Exception as e:
        print(f"  Active jobs error: {e}")
        input("\nPress Enter to continue...")

def show_active_job_options(active_job, token):
    """Show options based on active job status"""
    status = active_job['status']
    
    if status == 'ARRIVING':
        print("\nOptions:")
        print("1.    Navigate")
        print("2.   Mark Arrived")
        print("3.    Back")
        
    elif status == 'ARRIVED':
        print("\nOptions:")
        print("1.   Start Job (Enter OTP)")
        print("2.   Upload Before Photo")
        print("3.    Back")
        
    elif status == 'WORKING':
        print("\nOptions:")
        print("1.   Upload Before Photo")
        print("2.   Upload After Photo")
        print("3.   Complete Job")
        print("4.    Back")
        
    else:
        print("\nOptions:")
        print("1.    Back")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        if status == 'ARRIVING':
            navigate_to_job(active_job)
        elif status == 'ARRIVED':
            start_job_with_otp(active_job, token)
        elif status == 'WORKING':
            upload_before_photo(active_job, token)
        else:
            return
    elif choice == "2":
        if status == 'ARRIVING':
            mark_arrived(active_job, token)
        elif status == 'ARRIVED':
            upload_before_photo(active_job, token)
        elif status == 'WORKING':
            upload_after_photo(active_job, token)
        else:
            return
    elif choice == "3":
        if status == 'ARRIVED':
            upload_after_photo(active_job, token)
        elif status == 'WORKING':
            complete_active_job(active_job, token)
        else:
            return
    elif choice == "4":
        if status == 'WORKING':
            complete_active_job(active_job, token)
        else:
            return
    elif choice in ["5", "6", "7", "8", "9"]:
        return
    else:
        print("  Invalid choice")

def navigate_to_job(active_job):
    """Simulate navigation to job location"""
    print("\n   Opening navigation...")
    print("="*40)
    
    if active_job.get('user_lat') and active_job.get('user_long'):
        print(f"  User coordinates:")
        print(f"   Latitude: {active_job['user_lat']:.6f}")
        print(f"   Longitude: {active_job['user_long']:.6f}")
        
        if active_job.get('mechanic_lat') and active_job.get('mechanic_long'):
            print(f"\n  Your coordinates:")
            print(f"   Latitude: {active_job['mechanic_lat']:.6f}")
            print(f"   Longitude: {active_job['mechanic_long']:.6f}")
            
            # Calculate distance
            from math import radians, sin, cos, sqrt, atan2
            lat1, lon1 = radians(active_job['mechanic_lat']), radians(active_job['mechanic_long'])
            lat2, lon2 = radians(active_job['user_lat']), radians(active_job['user_long'])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = 63710 * c  # Earth's radius in km
            
            print(f"\n  Distance remaining: {distance:.2f} km")
            print(f"   ETA: {int(distance * 3)} minutes")
    else:
        print("  Location coordinates not available")
    
    print("\n  Future: Will open Google Maps with navigation")
    input("\nPress Enter to continue...")

def mark_arrived(active_job, token):
    """Mark mechanic as arrived at job location"""
    try:
        response = requests.post(f"{API}/api/car/mechanic/mark-arrived",
                              headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Marked as arrived')}")
            print(f"  Status: {result.get('status', 'ARRIVED')}")
            print(f"  {result.get('note', 'Ask user for OTP')}")
        else:
            error = response.json().get("error", "Failed to mark arrived")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Mark arrived error: {e}")
        input("\nPress Enter to continue...")

def start_job_with_otp(active_job, token):
    """Start job with OTP verification"""
    otp = input("\n  Enter OTP: ").strip()
    
    if not otp:
        print("  OTP is required")
        input("\nPress Enter to continue...")
        return
    
    try:
        response = requests.post(f"{API}/api/car/mechanic/start-job",
                              json={"otp": otp},
                              headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Job started')}")
            print(f"  Status: {result.get('status', 'WORKING')}")
            print(f"  {result.get('note', 'Repair timer started')}")
        else:
            error = response.json().get("error", "Failed to start job")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Start job error: {e}")
        input("\nPress Enter to continue...")

def upload_before_photo(active_job, token):
    """Upload before repair photo"""
    print("\n  Upload Before Photo")
    print("="*30)
    print("Enter file path (e.g., C:/Photos/before.jpg):")
    
    file_path = input("File path: ").strip()
    
    if not file_path:
        print("  File path is required")
        input("\nPress Enter to continue...")
        return
    
    if not os.path.exists(file_path):
        print("  File not found")
        input("\nPress Enter to continue...")
        return
    
    try:
        with open(file_path, 'rb') as f:
            files = {'photo': (os.path.basename(file_path), f, 'image/jpeg')}
            response = requests.post(f"{API}/api/car/mechanic/upload-before",
                                  files=files,
                                  headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Photo uploaded')}")
            print(f"  File: {result.get('photo_path', 'Unknown')}")
        else:
            error = response.json().get("error", "Failed to upload photo")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Upload error: {e}")
        input("\nPress Enter to continue...")

def upload_after_photo(active_job, token):
    """Upload after repair photo"""
    print("\n  Upload After Photo")
    print("="*30)
    print("Enter file path (e.g., C:/Photos/after.jpg):")
    
    file_path = input("File path: ").strip()
    
    if not file_path:
        print("  File path is required")
        input("\nPress Enter to continue...")
        return
    
    if not os.path.exists(file_path):
        print("  File not found")
        input("\nPress Enter to continue...")
        return
    
    try:
        with open(file_path, 'rb') as f:
            files = {'photo': (os.path.basename(file_path), f, 'image/jpeg')}
            response = requests.post(f"{API}/api/car/mechanic/upload-after",
                                  files=files,
                                  headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Photo uploaded')}")
            print(f"  File: {result.get('photo_path', 'Unknown')}")
        else:
            error = response.json().get("error", "Failed to upload photo")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Upload error: {e}")
        input("\nPress Enter to continue...")

def complete_active_job(active_job, token):
    """Complete the active job"""
    print("\n  Complete Job")
    print("="*30)
    
    # Check if photos are uploaded
    if not active_job.get('before_photo'):
        print("  Before photo is required")
        input("\nPress Enter to continue...")
        return
    
    if not active_job.get('after_photo'):
        print("  After photo is required")
        input("\nPress Enter to continue...")
        return
    
    confirm = input("Are you sure you want to complete this job? (y/n): ").strip().lower()
    if confirm != 'y':
        print("  Job completion cancelled")
        input("\nPress Enter to continue...")
        return
    
    try:
        response = requests.post(f"{API}/api/car/mechanic/complete-job",
                              headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Job completed')}")
            print(f"  Status: {result.get('status', 'COMPLETED')}")
            print(f"  Earning:  {result.get('earning', 0):.0f}")
            print(f"  {result.get('note', 'Status updated')}")
        else:
            error = response.json().get("error", "Failed to complete job")
            print(f"  {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Complete job error: {e}")
        input("\nPress Enter to continue...")

def earnings_fairness_screen(worker, token):
    """Display earnings and fairness insights"""
    try:
        # Get earnings summary
        response = requests.get(f"{API}/api/car/mechanic/earnings",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            data = response.json()
            earnings = data.get("earnings", {})
            
            # Get stats
            stats_response = requests.get(f"{API}/api/car/mechanic/stats",
                                        headers={"Authorization": f"Bearer {token}"})
            
            stats = {}
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                stats = stats_data.get("stats", {})
            
            print("\n" + "="*60)
            print("  EARNINGS & FAIRNESS INSIGHTS")
            print("="*60)
            
            # Earnings Dashboard
            print(f"\n  EARNINGS DASHBOARD")
            print("="*40)
            print(f"  Today Earnings:  {earnings.get('today_earnings', 0):.0f}")
            print(f"  Total Earnings:  {earnings.get('total_earnings', 0):.0f}")
            print(f"  Today Jobs: {earnings.get('today_jobs', 0)}")
            print(f"  Total Jobs: {earnings.get('total_jobs', 0)}")
            print(f"  Today Bonus:  {earnings.get('today_bonus', 0):.0f}")
            print(f"  Today Commission:  {earnings.get('today_commission', 0):.0f}")
            
            # Performance Stats
            print(f"\n  PERFORMANCE STATS")
            print("="*40)
            print(f"  Rating: {stats.get('rating', 5):.1f}/5.0")
            print(f"  Completion Rate: {stats.get('completion_rate', 0)*100:.1f}%")
            print(f"  Fairness Score: {stats.get('fairness_score', 100):.0f}%")
            print(f"  Total Jobs: {stats.get('total_jobs', 0)}")
            print(f"  Completed: {stats.get('completed_jobs', 0)}")
            print(f"  Cancelled: {stats.get('cancelled_jobs', 0)}")
            
            # Recent Jobs (show last 3)
            history_response = requests.get(f"{API}/api/car/mechanic/earnings/history?limit=3",
                                          headers={"Authorization": f"Bearer {token}"})
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                history = history_data.get("history", [])
                
                if history:
                    print(f"\n  RECENT JOBS")
                    print("="*40)
                    for job in history:
                        print(f"  Job {job['job_id']}")
                        print(f"  User: {job['user_name']}")
                        print(f"  Car: {job['car_model']}")
                        print(f"  Earned:  {job['final_amount']:.0f}")
                        print(f"  Bonus:  {job['bonus']:.0f}")
                        print(f"  Commission:  {job['platform_commission']:.0f}")
                        print(f"  Date: {job['created_at'][:10]}")
                        print("-" * 30)
            
            print("\n" + "-"*50)
            print("Options:")
            print("1.   View Full History")
            print("2.   View Fairness Details")
            print("3.   View Commission Info")
            print("4.    Back")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                view_full_earnings_history(token)
            elif choice == "2":
                view_fairness_details(token)
            elif choice == "3":
                view_commission_info(token)
            else:
                return
                
        else:
            print("  Failed to get earnings data")
            input("\nPress Enter to continue...")
            
    except Exception as e:
        print(f"  Earnings screen error: {e}")
        input("\nPress Enter to continue...")

def view_full_earnings_history(token):
    """View full earnings history"""
    try:
        response = requests.get(f"{API}/api/car/mechanic/earnings/history?limit=20",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            data = response.json()
            history = data.get("history", [])
            
            print("\n" + "="*60)
            print("  FULL EARNINGS HISTORY")
            print("="*60)
            
            if not history:
                print("  No earnings history found")
                input("\nPress Enter to continue...")
                return
            
            for job in history:
                print(f"\n  Job {job['job_id']}")
                print("="*40)
                print(f"  User: {job['user_name']}")
                print(f"  Car: {job['car_model']}")
                print(f"  Issue: {job['issue']}")
                print(f"  Base Amount:  {job['base_amount']:.0f}")
                print(f"  Commission:  {job['platform_commission']:.0f}")
                print(f"  Bonus:  {job['bonus']:.0f}")
                print(f"  Final Amount:  {job['final_amount']:.0f}")
                print(f"  Distance: {job.get('distance', 0):.1f} km")
                print(f"   Time: {job.get('job_time_minutes', 0)} minutes")
                print(f"  Date: {job['created_at']}")
                print("-" * 50)
            
            print(f"\n  Total Records: {len(history)}")
            
        else:
            print("  Failed to get earnings history")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  History view error: {e}")
        input("\nPress Enter to continue...")

def view_fairness_details(token):
    """View fairness insights"""
    try:
        response = requests.get(f"{API}/api/car/mechanic/fairness-insights",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get("insights", {})
            
            print("\n" + "="*60)
            print("  DISPATCH FAIRNESS INSIGHTS")
            print("="*60)
            
            print(f"\n  FAIRNESS SCORE: {insights.get('fairness_score', 100):.0f}%")
            print(f"  COMPLETION RATE: {insights.get('completion_rate', 0):.1f}%")
            print(f"  TOTAL JOBS: {insights.get('total_jobs', 0)}")
            print(f"  RATING: {insights.get('rating', 5):.1f}/5.0")
            
            # Dispatch factors
            dispatch_factors = insights.get('dispatch_factors', [])
            if dispatch_factors:
                print(f"\n  WHY YOU RECEIVE JOBS:")
                print("="*40)
                for factor in dispatch_factors:
                    print(f"  {factor}")
            
            # Improvement suggestions
            suggestions = insights.get('improvement_suggestions', [])
            if suggestions:
                print(f"\n  IMPROVEMENT SUGGESTIONS:")
                print("="*40)
                for suggestion in suggestions:
                    print(f"  {suggestion}")
            
            print(f"\n  LAST JOB ACTIVITY: {insights.get('recent_job_activity', 'No recent jobs')}")
            
        else:
            print("  Failed to get fairness insights")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Fairness view error: {e}")
        input("\nPress Enter to continue...")

def view_commission_info(token):
    """View commission information"""
    try:
        response = requests.get(f"{API}/api/car/mechanic/commission-info",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            data = response.json()
            commission = data.get("commission_info", {})
            
            print("\n" + "="*60)
            print("  COMMISSION TRANSPARENCY")
            print("="*60)
            
            print(f"\n  COMMISSION STRUCTURE:")
            print("="*40)
            print(f"  Platform Commission: {commission.get('platform_commission_rate', 0.20)*100:.0f}%")
            print(f"  Your Share: {commission.get('mechanic_share_rate', 0.80)*100:.0f}%")
            print(f"  {commission.get('description', 'Transparent commission model')}")
            
            # Example
            example = commission.get('example', {})
            if example:
                print(f"\n  EXAMPLE:")
                print("="*40)
                print(f"  Customer pays:  {example.get('customer_pays', 500)}")
                print(f"  Platform commission:  {example.get('platform_commission', 100)}")
                print(f"  Your earning:  {example.get('mechanic_earning', 400)}")
            
            # Bonus types
            bonus_types = commission.get('bonus_types', [])
            if bonus_types:
                print(f"\n  BONUS TYPES:")
                print("="*40)
                for bonus in bonus_types:
                    print(f"  {bonus['type']}: + {bonus['amount']} ({bonus['condition']})")
            
            print(f"\n  NO HIDDEN DEDUCTIONS!")
            print(f"  100% TRANSPARENT EARNINGS!")
            
        else:
            print("  Failed to get commission info")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Commission view error: {e}")
        input("\nPress Enter to continue...")

def performance_safety_screen(worker, token):
    """Display performance metrics and safety tools"""
    try:
        response = requests.get(f"{API}/api/car/mechanic/performance",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            data = response.json()
            performance = data.get("performance", {})
            tips = data.get("tips", {})
            
            print("\n" + "="*60)
            print("  PERFORMANCE DASHBOARD")
            print("="*60)
            
            # Performance Metrics
            print(f"\n  PERFORMANCE METRICS")
            print("="*40)
            print(f"  Rating: {performance.get('rating', 5):.1f}/5.0")
            print(f"  Completion Rate: {performance.get('completion_rate', 0)*100:.1f}%")
            print(f"  Acceptance Rate: {performance.get('acceptance_rate', 0)*100:.1f}%")
            print(f"  Total Jobs: {performance.get('total_jobs', 0)}")
            print(f"  Completed: {performance.get('completed_jobs', 0)}")
            print(f"  Cancelled: {performance.get('cancelled_jobs', 0)}")
            print(f"   Avg Response Time: {performance.get('avg_response_time', 0):.1f} seconds")
            print(f"  Performance Level: {tips.get('performance_level', 'Average')}")
            
            # Performance Tips
            tips_list = tips.get('tips', [])
            if tips_list:
                print(f"\n  PERFORMANCE TIPS")
                print("="*40)
                for tip in tips_list:
                    print(f"  {tip}")
            
            print("\n" + "-"*50)
            print("   SAFETY TOOLS")
            print("="*40)
            print("1.   Panic Alert")
            print("2.   Report Incident")
            print("3.   View Safety Reports")
            print("4.   View Panic Alerts")
            print("5.    Back")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                send_panic_alert(worker, token)
            elif choice == "2":
                report_incident(worker, token)
            elif choice == "3":
                view_safety_reports(worker, token)
            elif choice == "4":
                view_panic_alerts(worker, token)
            else:
                return
                
        else:
            print("  Failed to get performance data")
            input("\nPress Enter to continue...")
            
    except Exception as e:
        print(f"  Performance screen error: {e}")
        input("\nPress Enter to continue...")

def send_panic_alert(worker, token):
    """Send panic alert for immediate help"""
    try:
        print("\n  PANIC ALERT")
        print("="*40)
        print("This will immediately notify admin for help.")
        print("Use only in emergency situations.")
        
        confirm = input("\nAre you sure you want to send panic alert? (y/n): ").strip().lower()
        if confirm != 'y':
            print("  Panic alert cancelled")
            input("\nPress Enter to continue...")
            return
        
        # Get current job info if available
        job_id = None
        active_job_response = requests.get(f"{API}/api/car/mechanic/active-job",
                                       headers={"Authorization": f"Bearer {token}"})
        
        if active_job_response.status_code == 200:
            active_data = active_job_response.json()
            if active_data.get("active_job"):
                job_id = active_data["active_job"]["job_request_id"]
        
        location = input("Enter your current location (optional): ").strip()
        
        # Send panic alert
        response = requests.post(f"{API}/api/car/mechanic/panic-alert",
                              json={"job_id": job_id, "location": location},
                              headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Panic alert sent')}")
            print(f"  Alert ID: {result.get('alert_id', 'Unknown')}")
            print(f"  {result.get('note', 'Admin has been notified')}")
        else:
            print("  Failed to send panic alert")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Panic alert error: {e}")
        input("\nPress Enter to continue...")

def report_incident(worker, token):
    """Report safety incident"""
    try:
        print("\n  REPORT INCIDENT")
        print("="*40)
        print("Select incident type:")
        print("1. Unsafe location")
        print("2. Fraud customer")
        print("3. Payment dispute")
        print("4. Threat")
        print("5. Fake booking")
        
        incident_choice = input("\nSelect incident type (1-5): ").strip()
        
        incident_types = {
            "1": "Unsafe location",
            "2": "Fraud customer", 
            "3": "Payment dispute",
            "4": "Threat",
            "5": "Fake booking"
        }
        
        if incident_choice not in incident_types:
            print("  Invalid incident type")
            input("\nPress Enter to continue...")
            return
        
        incident_type = incident_types[incident_choice]
        description = input(f"\nDescribe the {incident_type.lower()}: ").strip()
        
        if not description:
            print("  Description is required")
            input("\nPress Enter to continue...")
            return
        
        # Get current job info if available
        job_id = None
        active_job_response = requests.get(f"{API}/api/car/mechanic/active-job",
                                       headers={"Authorization": f"Bearer {token}"})
        
        if active_job_response.status_code == 200:
            active_data = active_job_response.json()
            if active_data.get("active_job"):
                job_id = active_data["active_job"]["job_request_id"]
        
        # Send incident report
        response = requests.post(f"{API}/api/car/mechanic/report-incident",
                              json={
                                  "incident_type": incident_type,
                                  "description": description,
                                  "job_id": job_id
                              },
                              headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n  {result.get('message', 'Incident reported')}")
            print(f"  Report ID: {result.get('report_id', 'Unknown')}")
        else:
            print("  Failed to report incident")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  Report incident error: {e}")
        input("\nPress Enter to continue...")

def view_safety_reports(worker, token):
    """View safety reports"""
    try:
        response = requests.get(f"{API}/api/car/mechanic/safety-reports",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            data = response.json()
            reports = data.get("reports", [])
            
            print("\n" + "="*60)
            print("  SAFETY REPORTS")
            print("="*60)
            
            if not reports:
                print("  No safety reports found")
            else:
                for report in reports:
                    print(f"\n  Report {report['id']}")
                    print("="*40)
                    print(f"  Type: {report['incident_type']}")
                    print(f"  Description: {report['description'][:50]}...")
                    print(f"  Date: {report['created_at'][:10]}")
                    print(f"  Status: {report['status']}")
                    print("-" * 50)
            
            print(f"\n  Total Reports: {len(reports)}")
            
        else:
            print("  Failed to get safety reports")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  View safety reports error: {e}")
        input("\nPress Enter to continue...")

def view_panic_alerts(worker, token):
    """View panic alerts"""
    try:
        response = requests.get(f"{API}/api/car/mechanic/panic-alerts",
                             headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code == 200:
            data = response.json()
            alerts = data.get("alerts", [])
            
            print("\n" + "="*60)
            print("  PANIC ALERTS")
            print("="*60)
            
            if not alerts:
                print("  No panic alerts found")
            else:
                for alert in alerts:
                    print(f"\n  Alert {alert['id']}")
                    print("="*40)
                    print(f"  Location: {alert['location']}")
                    print(f"  Date: {alert['created_at'][:10]}")
                    print(f"  Status: {alert['status']}")
                    if alert.get('resolved_at'):
                        print(f"  Resolved: {alert['resolved_at'][:10]}")
                    print("-" * 50)
            
            print(f"\n  Total Alerts: {len(alerts)}")
            
        else:
            print("  Failed to get panic alerts")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"  View panic alerts error: {e}")
        input("\nPress Enter to continue...")

def unified_mechanic_menu():
    """Unified mechanic menu"""
    while True:
        print("\n" + "="*50)
        print("  MECHANIC MENU")
        print("="*50)
        print("1.   Signup")
        print("2.   Login")
        print("3.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            unified_mechanic_signup()
        elif choice == "2":
            unified_mechanic_login()
        elif choice == "3":
            return
        else:
            print("  Invalid choice")

def manage_available_slots(worker, token):
    """Manage mechanic availability slots for pre-bookings"""
    from .worker_slots_db import worker_slots_db
    
    while True:
        print("\n" + "="*60)
        print("  MANAGE AVAILABLE SLOTS")
        print("="*60)
        print(f"  {worker.get('name')}")
        
        print("\nOptions:")
        print("1.   Add New Slot")
        print("2.   View My Slots")
        print("3.    Delete Slot")
        print("4.   View Slots by Date")
        print("5.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            add_new_slot(worker)
        elif choice == "2":
            view_my_slots(worker)
        elif choice == "3":
            delete_slot(worker)
        elif choice == "4":
            view_slots_by_date(worker)
        elif choice == "5":
            return
        else:
            print("  Invalid choice")

def add_new_slot(worker):
    """Add a new availability slot"""
    print("\n" + "="*60)
    print("  ADD NEW SLOT")
    print("="*60)
    
    try:
        # Get date
        date = input("  Enter date (YYYY-MM-DD): ").strip()
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print("  Invalid date format. Use YYYY-MM-DD")
            return
        
        # Get time range
        start_time = input("  Start time (HH:MM, 24-hour format): ").strip()
        end_time = input("  End time (HH:MM, 24-hour format): ").strip()
        
        # Validate time format
        try:
            datetime.strptime(start_time, '%H:%M')
            datetime.strptime(end_time, '%H:%M')
        except ValueError:
            print("  Invalid time format. Use HH:MM (24-hour format)")
            return
        
        # Add slot to database
        success = worker_slots_db.add_slot(worker['id'], date, start_time, end_time)
        
        if success:
            print(f"  Slot added successfully!")
            print(f"  Date: {date}")
            print(f"  Time: {start_time} - {end_time}")
        else:
            print("  Failed to add slot. Slot may already exist.")
            
    except Exception as e:
        print(f"  Error adding slot: {e}")

def view_my_slots(worker):
    """View all slots for the worker"""
    print("\n" + "="*60)
    print("  MY AVAILABLE SLOTS")
    print("="*60)
    
    try:
        slots = worker_slots_db.get_available_slots(worker['id'])
        
        if not slots:
            print("  No available slots found.")
            return
        
        print(f"  Total slots: {len(slots)}")
        print("-" * 60)
        
        for slot in slots:
            status_emoji = " " if slot['status'] == 'AVAILABLE' else " "
            print(f"{status_emoji} {slot['slot_date']} | {slot['start_time']} - {slot['end_time']} | {slot['status']}")
        
    except Exception as e:
        print(f"  Error viewing slots: {e}")

def delete_slot(worker):
    """Delete a slot"""
    print("\n" + "="*60)
    print("   DELETE SLOT")
    print("="*60)
    
    try:
        # Show available slots
        slots = worker_slots_db.get_available_slots(worker['id'])
        
        if not slots:
            print("  No slots available to delete.")
            return
        
        print("Available slots:")
        for i, slot in enumerate(slots, 1):
            print(f"{i}. {slot['slot_date']} | {slot['start_time']} - {slot['end_time']}")
        
        slot_num = input("\nEnter slot number to delete (or 0 to cancel): ").strip()
        
        if slot_num == "0":
            return
        
        try:
            slot_index = int(slot_num) - 1
            if 0 <= slot_index < len(slots):
                slot_id = slots[slot_index]['id']
                success = worker_slots_db.delete_slot(slot_id, worker['id'])
                
                if success:
                    print("  Slot deleted successfully!")
                else:
                    print("  Failed to delete slot.")
            else:
                print("  Invalid slot number.")
        except ValueError:
            print("  Invalid input. Enter a number.")
            
    except Exception as e:
        print(f"  Error deleting slot: {e}")

def view_slots_by_date(worker):
    """View slots for a specific date range"""
    print("\n" + "="*60)
    print("  VIEW SLOTS BY DATE RANGE")
    print("="*60)
    
    try:
        start_date = input("  Start date (YYYY-MM-DD): ").strip()
        end_date = input("  End date (YYYY-MM-DD): ").strip()
        
        # Validate date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            print("  Invalid date format. Use YYYY-MM-DD")
            return
        
        slots = worker_slots_db.get_worker_slots_by_date_range(worker['id'], start_date, end_date)
        
        if not slots:
            print(f"  No slots found between {start_date} and {end_date}")
            return
        
        print(f"\n  Slots from {start_date} to {end_date}:")
        print("-" * 60)
        
        for slot in slots:
            status_emoji = " " if slot['status'] == 'AVAILABLE' else " "
            print(f"{status_emoji} {slot['slot_date']} | {slot['start_time']} - {slot['end_time']} | {slot['status']}")
        
    except Exception as e:
        print(f"  Error viewing slots: {e}")
