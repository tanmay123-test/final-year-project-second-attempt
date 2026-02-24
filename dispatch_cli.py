"""
Dispatch System CLI Testing Interface
Production-grade CLI for testing the smart dispatch system
"""

import requests
import json
import time
import uuid
from datetime import datetime

class DispatchCLI:
    """CLI interface for testing dispatch system"""
    
    def __init__(self, api_base="http://127.0.0.1:5001"):
        self.api_base = api_base
        self.current_user_id = 1
        self.current_mechanic_id = 1
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🚗 {title}")
        print(f"{'='*60}")
    
    def print_menu(self, options):
        """Print menu options"""
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("0. Exit")
    
    def get_input(self, prompt):
        """Get user input"""
        return input(f"\n{prompt}: ").strip()
    
    def create_job_request(self):
        """Create a new job request"""
        self.print_header("CREATE JOB REQUEST")
        
        # Get job details
        issue = self.get_input("Describe your car issue")
        
        print("\nLocation Options:")
        print("1. Enter coordinates (latitude, longitude)")
        print("2. Enter location name")
        
        location_choice = self.get_input("Select location option")
        
        if location_choice == "1":
            try:
                latitude = float(self.get_input("Enter latitude"))
                longitude = float(self.get_input("Enter longitude"))
                location_data = {"latitude": latitude, "longitude": longitude}
            except ValueError:
                print("❌ Invalid coordinates")
                return
        else:
            location_name = self.get_input("Enter location name")
            location_data = {"location_name": location_name}
        
        # Service type
        print("\nService Types:")
        print("1. MECHANIC")
        print("2. FUEL_DELIVERY")
        print("3. TOW_TRUCK")
        print("4. EXPERT")
        
        service_choice = self.get_input("Select service type")
        service_types = {
            "1": "MECHANIC",
            "2": "FUEL_DELIVERY", 
            "3": "TOW_TRUCK",
            "4": "EXPERT"
        }
        
        service_type = service_types.get(service_choice, "MECHANIC")
        
        # Urgency
        urgency = self.get_input("Is this urgent? (y/n)").lower() == 'y'
        
        # Create job request
        job_data = {
            "user_id": self.current_user_id,
            "issue": issue,
            "service_type": service_type,
            "urgency": urgency,
            **location_data
        }
        
        try:
            response = requests.post(f"{self.api_base}/api/dispatch/job/create", json=job_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Job request created successfully!")
                print(f"🆔 Job ID: {result['job_id']}")
                print(f"📊 Status: {result['status']}")
                print(f"🔧 Service: {service_type}")
                print(f"🚨 Urgent: {'Yes' if urgency else 'No'}")
                print(f"⏰ Created: {datetime.now().strftime('%H:%M:%S')}")
                
                return result['job_id']
            else:
                print(f"❌ Error: {response.json().get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        return None
    
    def check_job_status(self):
        """Check job status"""
        self.print_header("CHECK JOB STATUS")
        
        job_id = self.get_input("Enter Job ID")
        
        try:
            response = requests.get(f"{self.api_base}/api/dispatch/job/status/{job_id}")
            
            if response.status_code == 200:
                job_data = response.json()
                
                print(f"\n📋 Job Details:")
                print(f"🆔 Job ID: {job_data['job_id']}")
                print(f"📊 Status: {job_data['status']}")
                print(f"🔧 Issue: {job_data['issue']}")
                print(f"🏷️ Service: {job_data['service_type']}")
                print(f"🚨 Urgent: {'Yes' if job_data['urgency'] else 'No'}")
                print(f"⏰ Created: {job_data['created_at']}")
                
                # Mechanic info
                if 'mechanic' in job_data:
                    mechanic = job_data['mechanic']
                    print(f"\n👨‍🔧 Assigned Mechanic:")
                    print(f"👤 Name: {mechanic['name']}")
                    print(f"📱 Phone: {mechanic['phone']}")
                    print(f"🔧 Specialization: {mechanic['specialization']}")
                    print(f"⭐ Rating: {mechanic['rating']}")
                
                # Tracking info
                if 'tracking' in job_data:
                    tracking = job_data['tracking']
                    print(f"\n📍 Live Tracking:")
                    print(f"🗺️ Distance: {tracking['distance_km']:.2f} km")
                    print(f"⏱️ ETA: {tracking['eta_minutes']} minutes")
                    print(f"📍 Current: {tracking['current_location']['latitude']:.4f}, {tracking['current_location']['longitude']:.4f}")
                
                # OTP info
                if 'otp' in job_data:
                    otp = job_data['otp']
                    print(f"\n🔐 OTP Information:")
                    print(f"⏰ Time Remaining: {int(otp['time_remaining'] // 60)} minutes")
                    print(f"📅 Generated: {otp['generated_at']}")
                
            else:
                print(f"❌ Error: {response.json().get('error', 'Job not found')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    def simulate_mechanic_responses(self):
        """Simulate mechanic accepting/rejecting offers"""
        self.print_header("SIMULATE MECHANIC RESPONSES")
        
        print("This will simulate mechanic responses to job offers...")
        
        # Get active offers
        try:
            response = requests.get(f"{self.api_base}/api/dispatch/admin/jobs/active")
            
            if response.status_code == 200:
                jobs_data = response.json()
                active_jobs = jobs_data.get('jobs', [])
                
                if not active_jobs:
                    print("📭 No active jobs found")
                    return
                
                print(f"\n📋 Active Jobs: {len(active_jobs)}")
                
                for i, job in enumerate(active_jobs, 1):
                    print(f"\n{i}. Job {job['job_id'][:8]}")
                    print(f"   📊 Status: {job['status']}")
                    print(f"   🔧 Issue: {job['issue']}")
                    print(f"   🏷️ Service: {job['service_type']}")
                
                job_choice = self.get_input("Select job to simulate response for")
                
                if job_choice.isdigit() and 1 <= int(job_choice) <= len(active_jobs):
                    selected_job = active_jobs[int(job_choice) - 1]
                    
                    print(f"\n🎯 Simulating response for Job {selected_job['job_id'][:8]}")
                    
                    # Simulate acceptance (70% chance)
                    import random
                    accept = random.random() < 0.7
                    
                    if accept:
                        print("🤖 Simulating MECHANIC ACCEPTANCE...")
                        
                        # In real system, mechanic would receive offer and respond
                        # For simulation, we'll directly accept
                        print(f"✅ Mechanic would accept job {selected_job['job_id'][:8]}")
                        
                    else:
                        print("🤖 Simulating MECHANIC REJECTION...")
                        print(f"❌ Mechanic would reject job {selected_job['job_id'][:8]}")
                    
                else:
                    print("❌ Invalid selection")
            else:
                print("❌ Error fetching active jobs")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def update_mechanic_location(self):
        """Update mechanic location for testing"""
        self.print_header("UPDATE MECHANIC LOCATION")
        
        mechanic_id = self.get_input("Enter Mechanic ID (1-5)")
        
        print("\nLocation Options:")
        print("1. Use sample coordinates")
        print("2. Enter custom coordinates")
        
        choice = self.get_input("Select option")
        
        if choice == "1":
            # Sample coordinates around Mumbai
            locations = [
                (19.2183, 72.9781, "Asalpha"),
                (19.2200, 72.9800, "Ghatkopar"),
                (19.2150, 72.9750, "Vikhroli"),
                (19.2250, 72.9850, "Bhandup"),
                (19.2100, 72.9700, "Kanjurmarg")
            ]
            
            print("\nSample Locations:")
            for i, (lat, lon, name) in enumerate(locations, 1):
                print(f"{i}. {name} ({lat:.4f}, {lon:.4f})")
            
            loc_choice = self.get_input("Select location")
            
            if loc_choice.isdigit() and 1 <= int(loc_choice) <= len(locations):
                lat, lon, address = locations[int(loc_choice) - 1]
                location_data = {"latitude": lat, "longitude": lon, "address": address}
            else:
                print("❌ Invalid selection")
                return
        else:
            try:
                latitude = float(self.get_input("Enter latitude"))
                longitude = float(self.get_input("Enter longitude"))
                address = self.get_input("Enter address (optional)")
                location_data = {"latitude": latitude, "longitude": longitude}
                if address:
                    location_data["address"] = address
            except ValueError:
                print("❌ Invalid coordinates")
                return
        
        location_data["mechanic_id"] = int(mechanic_id)
        
        try:
            response = requests.put(f"{self.api_base}/api/dispatch/mechanic/location/update", json=location_data)
            
            if response.status_code == 200:
                print(f"\n✅ Mechanic {mechanic_id} location updated successfully!")
                print(f"📍 New Location: {location_data['latitude']:.4f}, {location_data['longitude']:.4f}")
                if 'address' in location_data:
                    print(f"🏠 Address: {location_data['address']}")
            else:
                print(f"❌ Error: {response.json().get('error', 'Update failed')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    def verify_otp(self):
        """Verify OTP for job"""
        self.print_header("VERIFY OTP")
        
        job_id = self.get_input("Enter Job ID")
        otp_code = self.get_input("Enter 6-digit OTP")
        
        try:
            response = requests.post(f"{self.api_base}/api/dispatch/otp/verify", json={
                "job_id": job_id,
                "otp_code": otp_code
            })
            
            if response.status_code == 200:
                print("\n✅ OTP verified successfully!")
                print("🔧 Work can now begin!")
            else:
                print(f"❌ Error: {response.json().get('error', 'Invalid OTP')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    def complete_job(self):
        """Complete a job"""
        self.print_header("COMPLETE JOB")
        
        job_id = self.get_input("Enter Job ID")
        proof_notes = self.get_input("Enter completion notes (optional)")
        
        try:
            response = requests.post(f"{self.api_base}/api/dispatch/job/complete", json={
                "job_id": job_id,
                "proof_notes": proof_notes
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Job completed successfully!")
                print(f"💰 Total Fee: ₹{result['total_fee']}")
                print(f"🔧 Mechanic Earnings: ₹{result['mechanic_earnings']}")
                print(f"🏢 Platform Commission: ₹{result['platform_commission']}")
            else:
                print(f"❌ Error: {response.json().get('error', 'Completion failed')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    def view_mechanic_wallet(self):
        """View mechanic wallet"""
        self.print_header("MECHANIC WALLET")
        
        mechanic_id = self.get_input("Enter Mechanic ID (1-5)")
        
        try:
            response = requests.get(f"{self.api_base}/api/dispatch/mechanic/wallet/{mechanic_id}")
            
            if response.status_code == 200:
                wallet = response.json()
                print(f"\n💰 Mechanic {mechanic_id} Wallet:")
                print(f"💵 Current Balance: ₹{wallet['current_balance']}")
                print(f"💸 Total Earned: ₹{wallet['total_earned']}")
                print(f"💳 Total Withdrawn: ₹{wallet['total_withdrawn']}")
                print(f"📅 Last Updated: {wallet['last_updated']}")
            else:
                print(f"❌ Error: {response.json().get('error', 'Wallet not found')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    def view_mechanic_metrics(self):
        """View mechanic performance metrics"""
        self.print_header("MECHANIC METRICS")
        
        mechanic_id = self.get_input("Enter Mechanic ID (1-5)")
        
        try:
            response = requests.get(f"{self.api_base}/api/dispatch/mechanic/metrics/{mechanic_id}")
            
            if response.status_code == 200:
                metrics = response.json()
                print(f"\n📊 Mechanic {mechanic_id} Performance:")
                print(f"📋 Total Jobs: {metrics['total_jobs']}")
                print(f"✅ Completed Jobs: {metrics['completed_jobs']}")
                print(f"❌ Cancelled Jobs: {metrics['cancelled_jobs']}")
                print(f"⭐ Average Rating: {metrics['average_rating']}")
                print(f"💰 Total Earnings: ₹{metrics['total_earnings']}")
                print(f"📈 Acceptance Rate: {metrics['acceptance_rate']:.2%}")
                print(f"⚖️ Fairness Score: {metrics['fairness_score']}")
            else:
                print(f"❌ Error: {response.json().get('error', 'Metrics not found')}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    def run(self):
        """Main CLI loop"""
        while True:
            self.print_header("DISPATCH SYSTEM CLI")
            
            options = [
                "Create Job Request",
                "Check Job Status",
                "Simulate Mechanic Responses",
                "Update Mechanic Location",
                "Verify OTP",
                "Complete Job",
                "View Mechanic Wallet",
                "View Mechanic Metrics",
                "View Active Jobs (Admin)"
            ]
            
            self.print_menu(options)
            
            choice = self.get_input("Select option")
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                self.create_job_request()
            elif choice == "2":
                self.check_job_status()
            elif choice == "3":
                self.simulate_mechanic_responses()
            elif choice == "4":
                self.update_mechanic_location()
            elif choice == "5":
                self.verify_otp()
            elif choice == "6":
                self.complete_job()
            elif choice == "7":
                self.view_mechanic_wallet()
            elif choice == "8":
                self.view_mechanic_metrics()
            elif choice == "9":
                self.view_active_jobs()
            else:
                print("❌ Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def view_active_jobs(self):
        """View all active jobs"""
        self.print_header("ACTIVE JOBS (ADMIN)")
        
        try:
            response = requests.get(f"{self.api_base}/api/dispatch/admin/jobs/active")
            
            if response.status_code == 200:
                jobs_data = response.json()
                active_jobs = jobs_data.get('jobs', [])
                
                if not active_jobs:
                    print("📭 No active jobs found")
                    return
                
                print(f"\n📋 Active Jobs: {len(active_jobs)}")
                
                for job in active_jobs:
                    print(f"\n🆔 Job: {job['job_id'][:8]}")
                    print(f"📊 Status: {job['status']}")
                    print(f"🔧 Issue: {job['issue']}")
                    print(f"🏷️ Service: {job['service_type']}")
                    print(f"🚨 Urgent: {'Yes' if job['urgency'] else 'No'}")
                    print(f"👤 User ID: {job['user_id']}")
                    
                    if 'mechanic' in job:
                        mechanic = job['mechanic']
                        print(f"👨‍🔧 Mechanic: {mechanic['name']} ({mechanic['id']})")
                    
                    print(f"⏰ Created: {job['created_at']}")
                    print("-" * 40)
            else:
                print("❌ Error fetching active jobs")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    cli = DispatchCLI()
    cli.run()
