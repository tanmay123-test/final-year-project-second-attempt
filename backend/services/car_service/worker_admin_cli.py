"""
Car Service Worker Admin CLI Interface
Handles worker approval and management for admins using unified database
"""

import requests

API = "http://127.0.0.1:5000"

def worker_admin_menu():
    """Worker admin menu for managing workers"""
    while True:
        print("\n" + "="*60)
        print("  WORKER ADMIN")
        print("="*60)
        print("1.   Pending Workers")
        print("2.   Approved Workers")
        print("3.   Worker Details")
        print("4.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            show_pending_workers()
        elif choice == "2":
            show_approved_workers()
        elif choice == "3":
            worker_details()
        elif choice == "4":
            return
        else:
            print("  Invalid choice")

def show_pending_workers():
    """Show pending workers for approval (includes both regular workers and automobile experts)"""
    try:
        # Fetch both regular workers and automobile experts
        workers_response = requests.get(f"{API}/api/car/service/workers/pending")
        experts_response = requests.get(f"{API}/api/automobile-expert/experts?status=PENDING")
        
        all_pending = []
        
        # Get regular workers
        if workers_response.status_code == 200:
            workers_data = workers_response.json()
            workers = workers_data.get("workers", [])
            for worker in workers:
                worker['worker_type'] = 'Regular Worker'
                all_pending.append(worker)
        
        # Get automobile experts
        if experts_response.status_code == 200:
            experts_data = experts_response.json()
            experts = experts_data.get("experts", [])
            for expert in experts:
                expert['worker_type'] = 'Automobile Expert'
                all_pending.append(expert)
        
        print("\n" + "="*60)
        print("  PENDING WORKERS")
        print("="*60)
        
        if not all_pending:
            print("  No pending workers found")
            input("\nPress Enter to continue...")
            return
        
        for i, worker in enumerate(all_pending, 1):
            print(f"\n[{i}] {worker.get('name', 'Unknown')} ({worker.get('worker_type', 'Unknown')})")
            print(f"      Email: {worker.get('email', 'N/A')}")
            print(f"      Phone: {worker.get('phone', 'N/A')}")
            
            if worker.get('worker_type') == 'Automobile Expert':
                print(f"      Expertise: {worker.get('area_of_expertise', 'N/A')}")
                print(f"      Experience: {worker.get('experience_years', 0)} years")
            else:
                print(f"      Role: {worker.get('role', 'N/A')}")
                print(f"       City: {worker.get('city', 'N/A')}")
                print(f"      Experience: {worker.get('experience', 0)} years")
            
            print(f"      Applied: {worker.get('created_at', 'N/A')}")
        
        print(f"\nTotal pending workers: {len(all_pending)}")
        
        # Approval options
        print("\nOptions:")
        print("1.   Approve Worker")
        print("2.   Reject Worker")
        print("3.    Back")
        
        action = input("\nSelect action: ").strip()
        
        if action == "1":
            approve_worker(all_pending)
        elif action == "2":
            reject_worker(all_pending)
        elif action == "3":
            return
        else:
            print("  Invalid choice")
                
    except Exception as e:
        print(f"  Error: {e}")

def show_approved_workers():
    """Show approved workers (includes both regular workers and automobile experts)"""
    try:
        # Fetch both regular workers and automobile experts
        workers_response = requests.get(f"{API}/api/car/service/workers/approved")
        experts_response = requests.get(f"{API}/api/automobile-expert/experts?status=APPROVED")
        
        all_approved = []
        
        # Get regular workers
        if workers_response.status_code == 200:
            workers_data = workers_response.json()
            workers = workers_data.get("workers", [])
            for worker in workers:
                worker['worker_type'] = 'Regular Worker'
                all_approved.append(worker)
        
        # Get automobile experts
        if experts_response.status_code == 200:
            experts_data = experts_response.json()
            experts = experts_data.get("experts", [])
            for expert in experts:
                expert['worker_type'] = 'Automobile Expert'
                all_approved.append(expert)
        
        print("\n" + "="*60)
        print("  APPROVED WORKERS")
        print("="*60)
        
        if not all_approved:
            print("  No approved workers found")
            input("\nPress Enter to continue...")
            return
        
        # Group by type and role
        mechanics = [w for w in all_approved if w.get('role') == 'Mechanic' and w.get('worker_type') == 'Regular Worker']
        fuel_agents = [w for w in all_approved if w.get('role') == 'Fuel Delivery Agent' and w.get('worker_type') == 'Regular Worker']
        tow_operators = [w for w in all_approved if w.get('role') == 'Tow Truck Operator' and w.get('worker_type') == 'Regular Worker']
        auto_experts = [w for w in all_approved if w.get('worker_type') == 'Automobile Expert']
        
        if mechanics:
            print(f"\n  MECHANICS ({len(mechanics)})")
            print("-" * 40)
            for i, worker in enumerate(mechanics, 1):
                print(f"  [{i}] {worker.get('name', 'Unknown')} - {worker.get('city', 'N/A')}")
        
        if fuel_agents:
            print(f"\n  FUEL DELIVERY AGENTS ({len(fuel_agents)})")
            print("-" * 40)
            for i, worker in enumerate(fuel_agents, 1):
                print(f"  [{i}] {worker.get('name', 'Unknown')} - {worker.get('city', 'N/A')}")
        
        if tow_operators:
            print(f"\n  TOW TRUCK OPERATORS ({len(tow_operators)})")
            print("-" * 40)
            for i, worker in enumerate(tow_operators, 1):
                print(f"  [{i}] {worker.get('name', 'Unknown')} - {worker.get('city', 'N/A')}")
        
        if auto_experts:
            print(f"\n  AUTOMOBILE EXPERTS ({len(auto_experts)})")
            print("-" * 40)
            for i, expert in enumerate(auto_experts, 1):
                expertise = expert.get('area_of_expertise', 'N/A')
                print(f"  [{i}] {expert.get('name', 'Unknown')} - {expertise}")
        
        print(f"\nTotal approved workers: {len(all_approved)}")
        input("\nPress Enter to continue...")
            
    except Exception as e:
        print(f"  Error: {e}")

def approve_worker(workers):
    """Approve a worker (handles both regular workers and automobile experts)"""
    try:
        choice = input(f"\nEnter worker number (1-{len(workers)}): ").strip()
        
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(workers):
            print("  Invalid selection")
            return
        
        worker = workers[int(choice) - 1]
        worker_id = worker.get('id')
        worker_type = worker.get('worker_type', 'Regular Worker')
        
        print(f"\n  Worker Details:")
        print(f"  Name: {worker.get('name', 'Unknown')}")
        print(f"  Email: {worker.get('email', 'N/A')}")
        print(f"  Phone: {worker.get('phone', 'N/A')}")
        print(f"   Type: {worker_type}")
        
        if worker_type == 'Automobile Expert':
            print(f"  Expertise: {worker.get('area_of_expertise', 'N/A')}")
            print(f"  Experience: {worker.get('experience_years', 0)} years")
            print(f"  Certificate: {' ' if worker.get('certificate_path') else ' '}")
        else:
            print(f"  Role: {worker.get('role', 'N/A')}")
            print(f"   City: {worker.get('city', 'N/A')}")
            print(f"  Experience: {worker.get('experience', 0)} years")
            print(f"  Skills: {worker.get('skills', 'N/A')}")
            
            # Show document status for regular workers
            print(f"\n  Documents:")
            print(f"Profile Photo: {' ' if worker.get('profile_photo') else ' '}")
            print(f"Aadhaar Card: {' ' if worker.get('aadhaar_path') else ' '}")
            print(f"Driving License: {' ' if worker.get('license_path') else ' '}")
            print(f"Certificate: {' ' if worker.get('certificate_path') else ' '}")
            if worker.get('role') in ['Fuel Delivery Agent', 'Tow Truck Operator']:
                print(f"Vehicle RC: {' ' if worker.get('vehicle_rc_path') else ' '}")
            if worker.get('role') == 'Tow Truck Operator':
                print(f"Truck Photos: {' ' if worker.get('truck_photo_path') else ' '}")
        
        confirm = input(f"\n  Approve {worker.get('name')}? (y/n): ").strip().lower()
        
        if confirm == 'y':
            # Update worker status to APPROVED
            if worker_type == 'Automobile Expert':
                response = requests.put(f"{API}/api/automobile-expert/update-status", 
                                      json={"expert_id": worker_id, "status": "APPROVED"})
            else:
                response = requests.put(f"{API}/api/car/service/worker/status", 
                                      json={"worker_id": worker_id, "status": "APPROVED"})
            
            if response.status_code == 200:
                print(f"  {worker_type} {worker.get('name')} approved successfully!")
                print("  Worker can now login and access dashboard")
            else:
                print("  Failed to approve worker")
        else:
            print("  Approval cancelled")
            
    except Exception as e:
        print(f"  Error: {e}")

def reject_worker(workers):
    """Reject a worker (handles both regular workers and automobile experts)"""
    try:
        choice = input(f"\nEnter worker number (1-{len(workers)}): ").strip()
        
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(workers):
            print("  Invalid selection")
            return
        
        worker = workers[int(choice) - 1]
        worker_id = worker.get('id')
        worker_type = worker.get('worker_type', 'Regular Worker')
        
        print(f"\n  Worker Details:")
        print(f"  Name: {worker.get('name', 'Unknown')}")
        print(f"  Email: {worker.get('email', 'N/A')}")
        print(f"   Type: {worker_type}")
        
        if worker_type == 'Automobile Expert':
            print(f"  Expertise: {worker.get('area_of_expertise', 'N/A')}")
        else:
            print(f"  Role: {worker.get('role', 'N/A')}")
        
        confirm = input(f"\n  Reject {worker.get('name')}? (y/n): ").strip().lower()
        
        if confirm == 'y':
            # Update worker status to REJECTED
            if worker_type == 'Automobile Expert':
                response = requests.put(f"{API}/api/automobile-expert/update-status", 
                                      json={"expert_id": worker_id, "status": "REJECTED"})
            else:
                response = requests.put(f"{API}/api/car/service/worker/status", 
                                      json={"worker_id": worker_id, "status": "REJECTED"})
            
            if response.status_code == 200:
                print(f"  {worker_type} {worker.get('name')} rejected")
                print("  Worker will not be able to login")
            else:
                print("  Failed to reject worker")
        else:
            print("  Rejection cancelled")
            
    except Exception as e:
        print(f"  Error: {e}")

def worker_details():
    """Search and view worker details"""
    try:
        worker_id = input("\nEnter Worker ID: ").strip()
        
        if not worker_id.isdigit():
            print("  Invalid Worker ID")
            return
        
        # Get worker details from API
        response = requests.get(f"{API}/api/car/service/workers/approved")
        
        if response.status_code == 200:
            data = response.json()
            workers = data.get("workers", [])
            
            # Find worker by ID
            worker = None
            for w in workers:
                if w.get('id') == int(worker_id):
                    worker = w
                    break
            
            if not worker:
                print("  Worker not found")
                return
            
            print("\n" + "="*60)
            print("  WORKER DETAILS")
            print("="*60)
            print(f"  ID: {worker.get('id')}")
            print(f"  Name: {worker.get('name', 'Unknown')}")
            print(f"  Email: {worker.get('email', 'N/A')}")
            print(f"  Phone: {worker.get('phone', 'N/A')}")
            print(f"  Role: {worker.get('role', 'N/A')}")
            print(f"  Age: {worker.get('age', 'N/A')}")
            print(f"   City: {worker.get('city', 'N/A')}")
            print(f"  Address: {worker.get('address', 'N/A')}")
            print(f"  Experience: {worker.get('experience', 0)} years")
            print(f"  Skills: {worker.get('skills', 'N/A')}")
            print(f"  Status: {worker.get('status', 'N/A')}")
            print(f"  Created: {worker.get('created_at', 'N/A')}")
            print(f"  Online: {'Yes' if worker.get('is_online', 0) else 'No'}")
            
            # Vehicle info if available
            if worker.get('vehicle_number'):
                print(f"\n  Vehicle Information:")
                print(f"Vehicle Number: {worker.get('vehicle_number', 'N/A')}")
                print(f"Vehicle Model: {worker.get('vehicle_model', 'N/A')}")
                print(f"Loading Capacity: {worker.get('loading_capacity', 'N/A')}")
            
            # Document status
            print(f"\n  Documents:")
            print(f"Profile Photo: {'  Uploaded' if worker.get('profile_photo') else '  Missing'}")
            print(f"Aadhaar Card: {'  Uploaded' if worker.get('aadhaar_path') else '  Missing'}")
            print(f"Driving License: {'  Uploaded' if worker.get('license_path') else '  Missing'}")
            print(f"Certificate: {'  Uploaded' if worker.get('certificate_path') else '  Not uploaded'}")
            if worker.get('vehicle_rc_path'):
                print(f"Vehicle RC: {'  Uploaded' if worker.get('vehicle_rc_path') else '  Missing'}")
            if worker.get('truck_photo_path'):
                print(f"Truck Photos: {'  Uploaded' if worker.get('truck_photo_path') else '  Missing'}")
            
            input("\nPress Enter to continue...")
            
        else:
            print("  Failed to fetch worker details")
            
    except Exception as e:
        print(f"  Error: {e}")
