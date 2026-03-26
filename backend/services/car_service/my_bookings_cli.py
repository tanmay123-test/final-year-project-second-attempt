"""
My Bookings CLI Interface
View and manage mechanic job bookings
"""

import requests
from .booking_db import booking_db
from .car_profile_db import car_profile_db

API = "http://127.0.0.1:5000"

def show_my_bookings(user_id, token):
    """Display user's mechanic bookings"""
    while True:
        print("\n" + "="*60)
        print("  MY BOOKINGS")
        print("="*60)
        
        # Get active job
        active_job = booking_db.get_active_job(user_id)
        
        if active_job:
            print("  ACTIVE JOB")
            print("-" * 40)
            print(f"Job ID: {active_job['id']}")
            print(f"Mechanic: {active_job['mechanic_name']}")
            print(f"Issue: {active_job['issue']}")
            print(f"Status: {active_job['status']}")
            print(f"Created: {active_job['created_at']}")
            
            if active_job.get('car_info'):
                car = active_job['car_info']
                print(f"Car: {car['brand']} {car['model']} ({car['registration_number']})")
            
            if active_job['status'] == 'ACCEPTED':
                print(f"  Accepted at: {active_job.get('accepted_at', 'Pending')}")
            elif active_job['status'] == 'ARRIVING':
                print(f"  Started at: {active_job.get('started_at', 'Pending')}")
                print("  Mechanic is on the way!")
            elif active_job['status'] == 'WORKING':
                print(f"  Working since: {active_job.get('started_at', 'Pending')}")
            
            print("\nOptions:")
            print("1.   Contact Mechanic")
            print("2.   Add Notes")
            print("3.   Cancel Job")
            print("4.   View All Bookings")
            print("5.    Back")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                contact_mechanic(active_job, token)
            elif choice == "2":
                add_job_notes(active_job['id'], token)
            elif choice == "3":
                cancel_job(active_job['id'], token)
            elif choice == "4":
                show_all_bookings(user_id, token)
            elif choice == "5":
                return
            else:
                print("  Invalid choice")
        else:
            print("  No active bookings")
            print("\nOptions:")
            print("1.   View Past Bookings")
            print("2.   Book New Mechanic")
            print("3.    Back")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                show_all_bookings(user_id, token)
            elif choice == "2":
                from .book_mechanic_cli import book_mechanic
                book_mechanic(user_id, token)
            elif choice == "3":
                return
            else:
                print("  Invalid choice")

def show_all_bookings(user_id, token):
    """Show all bookings (active and past)"""
    try:
        response = requests.get(
            f"{API}/api/car/jobs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            
            print("\n" + "="*60)
            print("  ALL BOOKINGS")
            print("="*60)
            
            if not jobs:
                print("  No bookings found")
                input("\nPress Enter to continue...")
                return
            
            # Separate active and past jobs
            active_jobs = [job for job in jobs if job['status'] in ['SEARCHING', 'ACCEPTED', 'ARRIVING', 'WORKING']]
            past_jobs = [job for job in jobs if job['status'] in ['COMPLETED', 'CANCELLED']]
            
            if active_jobs:
                print("\n  ACTIVE BOOKINGS")
                print("-" * 40)
                for i, job in enumerate(active_jobs, 1):
                    status_emoji = {
                        'SEARCHING': ' ',
                        'ACCEPTED': ' ',
                        'ARRIVING': ' ',
                        'WORKING': ' '
                    }.get(job['status'], ' ')
                    
                    print(f"{i}. Job ID: {job['id']}")
                    print(f"   {status_emoji} {job['status']}")
                    print(f"   Mechanic: {job['mechanic_name']}")
                    print(f"   Issue: {job['issue']}")
                    print(f"   Created: {job['created_at']}")
                    print("")
            
            if past_jobs:
                print("\n  PAST BOOKINGS")
                print("-" * 40)
                for i, job in enumerate(past_jobs, 1):
                    status_emoji = {
                        'COMPLETED': ' ',
                        'CANCELLED': ' '
                    }.get(job['status'], ' ')
                    
                    print(f"{i}. Job ID: {job['id']}")
                    print(f"   {status_emoji} {job['status']}")
                    print(f"   Mechanic: {job['mechanic_name']}")
                    print(f"   Issue: {job['issue']}")
                    print(f"   Created: {job['created_at']}")
                    if job.get('completed_at'):
                        print(f"   Completed: {job['completed_at']}")
                    print("")
            
            input("\nPress Enter to continue...")
            
    except Exception as e:
        print(f"  Error loading bookings: {e}")
        input("\nPress Enter to continue...")

def contact_mechanic(active_job, token):
    """Contact mechanic for active job"""
    print("\n" + "="*50)
    print("  CONTACT MECHANIC")
    print("="*50)
    print(f"Mechanic: {active_job['mechanic_name']}")
    print("What would you like to discuss?")
    print("1.   Share Location")
    print("2.   Update ETA")
    print("3.   Send Message")
    print("4.    Back")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        print("  Sharing your location with mechanic...")
        print("(Feature coming soon)")
    elif choice == "2":
        print("  Updating ETA...")
        print("(Feature coming soon)")
    elif choice == "3":
        print("  Sending message...")
        print("(Feature coming soon)")
    elif choice == "4":
        return
    else:
        print("  Invalid choice")

def add_job_notes(job_id, token):
    """Add notes to a job"""
    notes = input("  Enter notes: ").strip()
    if not notes:
        print("  Notes cannot be empty")
        return
    
    try:
        response = requests.put(
            f"{API}/api/car/jobs/{job_id}/notes",
            json={"notes": notes},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            print("  Notes added successfully")
        else:
            print("  Failed to add notes")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def cancel_job(job_id, token):
    """Cancel an active job"""
    print("\n" + "="*50)
    print("  CANCEL JOB")
    print("="*50)
    print(f"Job ID: {job_id}")
    
    confirm = input("Are you sure you want to cancel this job? (y/n): ").strip().lower()
    if confirm != 'y':
        print("  Cancellation cancelled")
        return
    
    reason = input("Reason for cancellation: ").strip()
    if not reason:
        reason = "User cancelled"
    
    try:
        response = requests.put(
            f"{API}/api/car/jobs/{job_id}/cancel",
            json={"reason": reason},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            print("  Job cancelled successfully")
            print("  You may still be charged for the mechanic's time")
        else:
            print("  Failed to cancel job")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")
