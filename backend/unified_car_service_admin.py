"""
Unified Car Service Admin Menu
Uses the main workers database instead of fragmented databases
"""

def car_service_admin_menu():
    """Car Service worker admin management"""
    from worker_db import WorkerDB
    
    worker_db = WorkerDB()
    
    while True:
        print("\n" + "="*60)
        print("👷 CAR SERVICE WORKER ADMIN")
        print("="*60)
        print("1. 📋 List Pending Workers")
        print("2. ✅ Approve Worker")
        print("3. ❌ Reject Worker")
        print("4. 👥 List All Workers")
        print("5. 📊 Worker Statistics")
        print("6. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            # List pending car service workers
            workers = worker_db.get_pending_workers('car_service')
            if workers:
                print(f"\n📋 Pending Car Service Workers ({len(workers)}):")
                for worker in workers:
                    print(f"ID: {worker['id']} | Name: {worker['full_name']} | Email: {worker['email']} | Specialization: {worker['specialization']}")
            else:
                print("\n✅ No pending car service workers found!")
                
        elif choice == "2":
            # Approve worker
            worker_id = input("Enter worker ID to approve: ").strip()
            if worker_id.isdigit():
                success = worker_db.update_worker_status(int(worker_id), 'approved')
                if success:
                    print(f"✅ Car service worker {worker_id} approved successfully!")
                else:
                    print(f"❌ Failed to approve worker {worker_id}")
            else:
                print("❌ Invalid worker ID")
                
        elif choice == "3":
            # Reject worker
            worker_id = input("Enter worker ID to reject: ").strip()
            if worker_id.isdigit():
                success = worker_db.update_worker_status(int(worker_id), 'rejected')
                if success:
                    print(f"❌ Car service worker {worker_id} rejected successfully!")
                else:
                    print(f"❌ Failed to reject worker {worker_id}")
            else:
                print("❌ Invalid worker ID")
                
        elif choice == "4":
            # List all car service workers
            workers = worker_db.get_approved_workers('car_service')
            if workers:
                print(f"\n👥 All Approved Car Service Workers ({len(workers)}):")
                for worker in workers:
                    print(f"ID: {worker['id']} | Name: {worker['full_name']} | Email: {worker['email']} | Specialization: {worker['specialization']} | Rating: {worker['rating']}")
            else:
                print("\n❌ No approved car service workers found!")
                
        elif choice == "5":
            # Worker statistics
            all_workers = worker_db.get_all_workers_unfiltered()
            car_workers = [w for w in all_workers if w['service'] == 'car_service']
            pending_workers = [w for w in car_workers if w['status'] == 'pending']
            approved_workers = [w for w in car_workers if w['status'] == 'approved']
            rejected_workers = [w for w in car_workers if w['status'] == 'rejected']
            
            print(f"\n📊 CAR SERVICE WORKER STATISTICS")
            print(f"Total Workers: {len(car_workers)}")
            print(f"Pending: {len(pending_workers)}")
            print(f"Approved: {len(approved_workers)}")
            print(f"Rejected: {len(rejected_workers)}")
            
            if approved_workers:
                avg_rating = sum(w['rating'] or 0 for w in approved_workers) / len(approved_workers)
                print(f"Average Rating: {avg_rating:.1f}/5.0")
                
        elif choice == "6":
            break
        else:
            print("❌ Invalid choice")

def fuel_delivery_admin_menu():
    """Fuel Delivery agent admin management"""
    from worker_db import WorkerDB
    
    worker_db = WorkerDB()
    
    while True:
        print("\n" + "="*60)
        print("⛽ FUEL DELIVERY AGENT ADMIN")
        print("="*60)
        print("1. 📋 List Pending Agents")
        print("2. ✅ Approve Agent")
        print("3. ❌ Reject Agent")
        print("4. 👥 List All Agents")
        print("5. 📊 Agent Statistics")
        print("6. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            # List pending fuel delivery agents
            workers = worker_db.get_pending_workers('fuel_delivery')
            if workers:
                print(f"\n📋 Pending Fuel Delivery Agents ({len(workers)}):")
                for worker in workers:
                    print(f"ID: {worker['id']} | Name: {worker['full_name']} | Email: {worker['email']} | Phone: {worker['phone']}")
            else:
                print("\n✅ No pending fuel delivery agents found!")
                
        elif choice == "2":
            # Approve agent
            worker_id = input("Enter agent ID to approve: ").strip()
            if worker_id.isdigit():
                success = worker_db.update_worker_status(int(worker_id), 'approved')
                if success:
                    print(f"✅ Fuel delivery agent {worker_id} approved successfully!")
                else:
                    print(f"❌ Failed to approve agent {worker_id}")
            else:
                print("❌ Invalid agent ID")
                
        elif choice == "3":
            # Reject agent
            worker_id = input("Enter agent ID to reject: ").strip()
            if worker_id.isdigit():
                success = worker_db.update_worker_status(int(worker_id), 'rejected')
                if success:
                    print(f"❌ Fuel delivery agent {worker_id} rejected successfully!")
                else:
                    print(f"❌ Failed to reject agent {worker_id}")
            else:
                print("❌ Invalid agent ID")
                
        elif choice == "4":
            # List all fuel delivery agents
            workers = worker_db.get_approved_workers('fuel_delivery')
            if workers:
                print(f"\n👥 All Approved Fuel Delivery Agents ({len(workers)}):")
                for worker in workers:
                    print(f"ID: {worker['id']} | Name: {worker['full_name']} | Email: {worker['email']} | Phone: {worker['phone']} | Rating: {worker['rating']}")
            else:
                print("\n❌ No approved fuel delivery agents found!")
                
        elif choice == "5":
            # Agent statistics
            all_workers = worker_db.get_all_workers_unfiltered()
            fuel_workers = [w for w in all_workers if w['service'] == 'fuel_delivery']
            pending_workers = [w for w in fuel_workers if w['status'] == 'pending']
            approved_workers = [w for w in fuel_workers if w['status'] == 'approved']
            rejected_workers = [w for w in fuel_workers if w['status'] == 'rejected']
            
            print(f"\n📊 FUEL DELIVERY AGENT STATISTICS")
            print(f"Total Agents: {len(fuel_workers)}")
            print(f"Pending: {len(pending_workers)}")
            print(f"Approved: {len(approved_workers)}")
            print(f"Rejected: {len(rejected_workers)}")
            
            if approved_workers:
                avg_rating = sum(w['rating'] or 0 for w in approved_workers) / len(approved_workers)
                print(f"Average Rating: {avg_rating:.1f}/5.0")
                
        elif choice == "6":
            break
        else:
            print("❌ Invalid choice")

def truck_operator_admin_menu():
    """Truck Operator admin management"""
    from worker_db import WorkerDB
    
    worker_db = WorkerDB()
    
    while True:
        print("\n" + "="*60)
        print("🚚 TRUCK OPERATOR ADMIN")
        print("="*60)
        print("1. 📋 List Pending Operators")
        print("2. ✅ Approve Operator")
        print("3. ❌ Reject Operator")
        print("4. 👥 List All Operators")
        print("5. 📊 Operator Statistics")
        print("6. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            # List pending truck operators
            workers = worker_db.get_pending_workers('truck_operator')
            if workers:
                print(f"\n📋 Pending Truck Operators ({len(workers)}):")
                for worker in workers:
                    print(f"ID: {worker['id']} | Name: {worker['full_name']} | Email: {worker['email']} | Specialization: {worker['specialization']}")
            else:
                print("\n✅ No pending truck operators found!")
                
        elif choice == "2":
            # Approve operator
            worker_id = input("Enter operator ID to approve: ").strip()
            if worker_id.isdigit():
                success = worker_db.update_worker_status(int(worker_id), 'approved')
                if success:
                    print(f"✅ Truck operator {worker_id} approved successfully!")
                else:
                    print(f"❌ Failed to approve operator {worker_id}")
            else:
                print("❌ Invalid operator ID")
                
        elif choice == "3":
            # Reject operator
            worker_id = input("Enter operator ID to reject: ").strip()
            if worker_id.isdigit():
                success = worker_db.update_worker_status(int(worker_id), 'rejected')
                if success:
                    print(f"❌ Truck operator {worker_id} rejected successfully!")
                else:
                    print(f"❌ Failed to reject operator {worker_id}")
            else:
                print("❌ Invalid operator ID")
                
        elif choice == "4":
            # List all truck operators
            workers = worker_db.get_approved_workers('truck_operator')
            if workers:
                print(f"\n👥 All Approved Truck Operators ({len(workers)}):")
                for worker in workers:
                    print(f"ID: {worker['id']} | Name: {worker['full_name']} | Email: {worker['email']} | Specialization: {worker['specialization']} | Rating: {worker['rating']}")
            else:
                print("\n❌ No approved truck operators found!")
                
        elif choice == "5":
            # Operator statistics
            all_workers = worker_db.get_all_workers_unfiltered()
            truck_workers = [w for w in all_workers if w['service'] == 'truck_operator']
            pending_workers = [w for w in truck_workers if w['status'] == 'pending']
            approved_workers = [w for w in truck_workers if w['status'] == 'approved']
            rejected_workers = [w for w in truck_workers if w['status'] == 'rejected']
            
            print(f"\n📊 TRUCK OPERATOR STATISTICS")
            print(f"Total Operators: {len(truck_workers)}")
            print(f"Pending: {len(pending_workers)}")
            print(f"Approved: {len(approved_workers)}")
            print(f"Rejected: {len(rejected_workers)}")
            
            if approved_workers:
                avg_rating = sum(w['rating'] or 0 for w in approved_workers) / len(approved_workers)
                print(f"Average Rating: {avg_rating:.1f}/5.0")
                
        elif choice == "6":
            break
        else:
            print("❌ Invalid choice")
