"""
Car Service Worker CLI Interface
Handles worker signup, login, and dashboard access
"""

import os
import requests
import time
from datetime import datetime

API = "http://127.0.0.1:5000"

def worker_menu():
    """Main worker menu"""
    while True:
        print("\n" + "="*50)
        print("  WORKER MENU")
        print("="*50)
        print("1.   Signup")
        print("2.   Login")
        print("3.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            worker_signup()
        elif choice == "2":
            worker_login()
        elif choice == "3":
            return
        else:
            print("  Invalid choice")

def worker_signup():
    """Worker signup process"""
    print("\n" + "="*60)
    print("  WORKER SIGNUP")
    print("="*60)
    
    try:
        # Role selection first
        print("\n  Select Worker Type:")
        print("1.   Healthcare")
        print("2.   Housekeeping")
        print("3.   Resource Management")
        print("4.   Car Services")
        print("5.   Money Management")
        
        choice = input("\nSelect service (1-5): ").strip()
        
        if choice == "1":
            healthcare_worker_menu()
        elif choice == "2":
            housekeeping_worker_menu()
        elif choice == "3":
            resource_management_menu()
        elif choice == "4":
            car_service_worker_menu()
        elif choice == "5":
            money_management_menu()
        else:
            print("  Invalid choice")
            time.sleep(1)
    except Exception as e:
        print(f"  Error: {e}")
        time.sleep(1)

def car_service_worker_menu():
    """Car service worker submenu"""
    print("\n" + "="*60)
    print("  CAR SERVICE WORKER")
    print("="*60)
    print("1.   Mechanic")
    print("2.   Fuel Delivery Agent")
    print("3.   Tow Truck Operator")
    print("4.   Automobile Expert")
    print("5.   Truck Operator")
    print("6.    Back")
    
    choice = input("\nSelect worker type (1-6): ").strip()
        
    if choice == "1":
        mechanic_signup()
    elif choice == "2":
        fuel_delivery_agent_menu()
    elif choice == "3":
        tow_truck_operator_signup()
    elif choice == "4":
        automobile_expert_signup()
    elif choice == "5":
        from .truck_operator_cli import truck_operator_signup
        truck_operator_signup()
    elif choice == "6":
        return
    else:
        print("  Invalid choice")
        time.sleep(1)

def fuel_delivery_agent_menu():
    """Fuel delivery agent main menu"""
    while True:
        print("\n" + "="*60)
        print("  FUEL DELIVERY AGENT")
        print("="*60)
        print("1.   Signup")
        print("2.   Login")
        print("3.    Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            from fuel_delivery_cli import fuel_delivery_agent_signup
            fuel_delivery_agent_signup()
        elif choice == "2":
            from fuel_delivery_cli import fuel_delivery_agent_login
            fuel_delivery_agent_login()
        elif choice == "3":
            return
        else:
            print("  Invalid choice")
            time.sleep(1)

def worker_login():
    """Worker login process"""
    print("\n" + "="*50)
    print("  WORKER LOGIN")
    print("="*50)
    
    try:
        email = input("  Email: ").strip()
        
        if not email:
            print("  Email is required")
            return
        
        # Call API with email only
        response = requests.post(f"{API}/api/car/worker/login", json={
            "email": email
        })
        
        if response.status_code == 200:
            result = response.json()
            worker = result.get("worker", {})
            token = result.get("token")
            
            print(f"\n  Login successful!")
            print(f"  Welcome, {worker.get('name', 'Worker')}!")
            print(f"  Role: {worker.get('role', 'Unknown')}")
            print(f"   City: {worker.get('city', 'Unknown')}")
            print(f"  Experience: {worker.get('experience', 0)} years")
            
            # Redirect to role-specific dashboard
            role = worker.get('role')
            if role == "Mechanic":
                mechanic_dashboard(worker, token)
            elif role == "Fuel Delivery Agent":
                from fuel_delivery_cli import fuel_delivery_agent_dashboard
                fuel_delivery_agent_dashboard(worker, token)
            elif role == "Tow Truck Operator":
                tow_dashboard(worker, token)
            elif role == "Automobile Expert":
                expert_dashboard(worker, token)
            elif role == "Truck Operator":
                from .truck_operator_cli import truck_operator_dashboard
                truck_operator_dashboard(worker)
            else:
                print("  Dashboard not available for this role yet")
                
        elif response.status_code == 401:
            print("  Invalid email")
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

# Placeholder functions for other worker types
def healthcare_worker_menu():
    print("  Healthcare worker signup - Coming soon!")
    time.sleep(1)

def housekeeping_worker_menu():
    print("  Housekeeping worker signup - Coming soon!")
    time.sleep(1)

def resource_management_menu():
    print("  Resource management worker signup - Coming soon!")
    time.sleep(1)

def money_management_menu():
    print("  Money management worker signup - Coming soon!")
    time.sleep(1)

def mechanic_signup():
    print("  Mechanic signup - Coming soon!")
    time.sleep(1)

def tow_truck_operator_signup():
    print("  Tow truck operator signup - Coming soon!")
    time.sleep(1)

def automobile_expert_signup():
    print("  Automobile expert signup - Coming soon!")
    time.sleep(1)

def mechanic_dashboard(worker, token):
    print("  Mechanic dashboard - Coming soon!")
    time.sleep(1)

def tow_dashboard(worker, token):
    print("  Tow truck dashboard - Coming soon!")
    time.sleep(1)

def expert_dashboard(worker, token):
    print("  Expert dashboard - Coming soon!")
    time.sleep(1)
