"""
Enhanced Ask Expert CLI with Category Selection
Similar to healthcare module's specialization area
"""

import os
import requests
from .models import UPLOAD_DIR

API = "http://127.0.0.1:5000"

def ask_expert_flow_with_category(token, user_id):
    """Enhanced ask expert flow with category selection like healthcare module"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Show category selection
    print("\n" + "="*60)
    print("  SELECT EXPERT CATEGORY")
    print("="*60)
    print("1.   Body & Interior Expert")
    print("2.   Brake & Suspension Expert") 
    print("3.   Electrical Expert")
    print("4.   Engine Expert")
    print("5.   General Expert")
    print("6.    Back")
    
    category_choice = input("\nSelect category: ").strip()
    
    category_mapping = {
        '1': 'Body & Interior Expert',
        '2': 'Brake & Suspension Expert',
        '3': 'Electrical Expert', 
        '4': 'Engine Expert',
        '5': 'General Expert'
    }
    
    if category_choice == '6':
        return
    elif category_choice not in category_mapping:
        print("  Invalid category selection")
        input("\nPress Enter to continue...")
        return
    
    selected_category = category_mapping[category_choice]
    
    # Step 2: Get online experts for selected category
    print(f"\n  Loading {selected_category}s...")
    r = requests.get(f"{API}/api/car/expert/online-experts", 
                    headers=headers, 
                    params={'category': selected_category})
    
    if r.status_code != 200:
        print("  Failed to load experts")
        return
    
    experts = r.json().get("experts", [])
    
    print(f"\n  AVAILABLE {selected_category.upper()}S")
    print("="*60)
    
    if not experts:
        print(f"  No {selected_category.lower()}s online right now.")
        print("  Please try again later or select a different category.")
        input("\nPress Enter to continue...")
        return
    
    # Display experts with detailed information
    for idx, expert in enumerate(experts, 1):
        print(f"\n[{idx}]   {expert.get('name', 'Unknown')}")
        print(f"      Specialization: {expert.get('specialization', 'N/A')}")
        print(f"      Rating: {expert.get('rating', 0)}/5.0")
        print(f"      Experience: {expert.get('experience', 0)} years")
        print(f"      Status:   Online")
    
    # Step 3: Expert selection
    print(f"\n" + "="*60)
    sel = input(f"Select {selected_category.lower()} number (1-{len(experts)}): ").strip()
    
    if not sel.isdigit() or int(sel) < 1 or int(sel) > len(experts):
        print("  Invalid selection")
        input("\nPress Enter to continue...")
        return
    
    expert = experts[int(sel) - 1]
    expert_id = expert["id"]
    
    print(f"\n  Selected: {expert.get('name', 'Unknown')}")
    print(f"  {selected_category}")
    
    # Step 4: Problem description
    print("\n" + "="*60)
    print("  DESCRIBE YOUR PROBLEM")
    print("="*60)
    print("Please describe your car issue in detail:")
    desc = input("> ").strip()
    
    if not desc:
        print("  Problem description is required")
        input("\nPress Enter to continue...")
        return
    
    # Step 5: Image upload (optional)
    print("\n" + "="*60)
    print("  ADD IMAGES (Optional)")
    print("="*60)
    print("Enter image path or type 'skip' to continue:")
    img_path = input("> ").strip()
    
    files = None
    use_files = False
    if img_path.lower() != "skip" and img_path != "":
        if not os.path.isfile(img_path):
            print("  File does not exist, skipping image.")
        else:
            try:
                files = {"images": open(img_path, "rb")}
                use_files = True
                print("  Image added successfully")
            except Exception:
                print("  Could not open file, skipping image.")
    
    # Step 6: Create request
    print("\n  Creating consultation request...")
    
    # Use the new start-request endpoint
    data = {
        "user_id": str(user_id),
        "expert_category": selected_category,
        "description": desc
    }
    
    if use_files:
        resp = requests.post(f"{API}/api/car/expert/start-request", 
                           headers=headers, 
                           files=files, 
                           data=data)
        files["images"].close()
    else:
        resp = requests.post(f"{API}/api/car/expert/start-request", 
                           headers=headers, 
                           json=data)
    
    if resp.status_code not in (200, 201):
        print("  Failed to create expert request")
        error = resp.json().get('error', 'Unknown error')
        print(f"Error: {error}")
        input("\nPress Enter to continue...")
        return
    
    result = resp.json()
    request_id = result.get('data', {}).get('request_id')
    
    if not request_id:
        print("  Failed to get request ID")
        input("\nPress Enter to continue...")
        return
    
    print("\n  Request sent successfully!")
    print(f"  Request ID: {request_id}")
    print(f"    Expert: {expert.get('name', 'Unknown')}")
    print(f"  Category: {selected_category}")
    print("  Waiting for expert response...")
    
    # Step 7: Conversation management
    conversation_menu(request_id, user_id, headers, expert.get('name', 'Expert'))

def conversation_menu(request_id, user_id, headers, expert_name):
    """Manage conversation after request is created"""
    while True:
        print("\n" + "="*60)
        print(f"  CONVERSATION WITH {expert_name.upper()}")
        print("="*60)
        print("1.   View Conversation")
        print("2.   Send Message")
        print("3.   Check Status")
        print("4.   Start Call")
        print("5.   Mark Resolved")
        print("6.   Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_conversation(request_id, headers)
        elif choice == "2":
            send_message(request_id, user_id, headers)
        elif choice == "3":
            check_status(request_id, headers)
        elif choice == "4":
            start_call(request_id, user_id, headers)
        elif choice == "5":
            resolve_request(request_id, user_id, headers)
        elif choice == "6":
            break
        else:
            print("  Invalid choice")

def view_conversation(request_id, headers):
    """View conversation messages"""
    try:
        mr = requests.get(f"{API}/api/car/expert/request/{request_id}/messages", headers=headers)
        if mr.status_code == 200:
            msgs = mr.json().get('messages', [])
            print("\n--- CONVERSATION ---")
            if not msgs:
                print("  No messages yet")
            else:
                for m in msgs:
                    prefix = "  You" if m.get("sender_type") == "USER" else f"    Expert"
                    timestamp = m.get('created_at', 'Unknown time')
                    print(f"{prefix} ({timestamp}): {m.get('message','')}")
        else:
            print("  Failed to load messages")
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def send_message(request_id, user_id, headers):
    """Send a message to the expert"""
    try:
        msg = input("  Your message: ").strip()
        if not msg:
            print("  Message cannot be empty")
            return
        
        pr = requests.post(
            f"{API}/api/car/expert/request/{request_id}/message",
            headers=headers,
            json={"user_id": str(user_id), "message": msg},
        )
        
        if pr.status_code in (200, 201):
            print("  Message sent successfully")
        else:
            print("  Failed to send message")
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def check_status(request_id, headers):
    """Check request status"""
    try:
        sr = requests.get(f"{API}/api/car/expert/request/{request_id}", headers=headers)
        if sr.status_code == 200:
            req = sr.json().get('data', {})
            print(f"\n  Request Status: {req.get('status','Unknown')}")
            print(f"   Category: {req.get('expert_category','Unknown')}")
            print(f"  Created: {req.get('created_at','Unknown')}")
            
            if req.get("status") == "COMPLETED":
                print("  Consultation completed")
            elif req.get("status") == "IN_PROGRESS":
                print("  Consultation in progress")
            else:
                print("  Waiting for expert response")
        else:
            print("  Failed to load request status")
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def start_call(request_id, user_id, headers):
    """Start a call session"""
    try:
        print("  Initiating call...")
        cr = requests.post(
            f"{API}/api/car/expert/request/{request_id}/call",
            headers=headers,
            json={"user_id": str(user_id)},
        )
        
        if cr.status_code == 200:
            print("  Call session started")
            print("  Expert will join the call shortly")
        else:
            print("  Failed to start call")
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")

def resolve_request(request_id, user_id, headers):
    """Mark request as resolved"""
    try:
        confirm = input("   Are you sure you want to mark this as resolved? (y/n): ").strip().lower()
        if confirm != 'y':
            return
        
        rr = requests.post(
            f"{API}/api/car/expert/request/{request_id}/resolve",
            headers=headers,
            json={"user_id": str(user_id)},
        )
        
        if rr.status_code == 200:
            print("  Request marked as resolved")
            print("  Thank you for using our expert service!")
        else:
            print("  Failed to resolve request")
    except Exception as e:
        print(f"  Error: {e}")
    
    input("\nPress Enter to continue...")
