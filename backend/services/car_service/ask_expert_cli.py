import os
import requests
from datetime import datetime
import time

API = "http://127.0.0.1:5000"

def ask_expert_menu(user_id, token):
    """Ask Expert main menu"""
    while True:
        print("\n" + "="*60)
        print("🧠 ASK EXPERT")
        print("="*60)
        print("1. 🆕 Start Conversation")
        print("2. 💬 My Conversations")
        print("3. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            start_conversation(user_id, token)
        elif choice == "2":
            my_conversations(user_id, token)
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")

def start_conversation(user_id, token):
    """Start a new expert conversation with category selection like healthcare module"""
    print("\n" + "="*60)
    print("🆕 START CONVERSATION")
    print("="*60)
    
    try:
        # Step 1: Show category selection
        print("\n📋 Select Expert Category:")
        print("1. 🚗 Body & Interior Expert")
        print("2. 🛑 Brake & Suspension Expert") 
        print("3. ⚡ Electrical Expert")
        print("4. 🔧 Engine Expert")
        print("5. 🔧 General Expert")
        print("6. ⬅️ Back")
        
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
            print("❌ Invalid category selection")
            input("\nPress Enter to continue...")
            return
        
        selected_category = category_mapping[category_choice]
        
        # Step 2: Get online experts for selected category
        print(f"\n🔄 Loading {selected_category}s...")
        response = requests.get(f"{API}/api/car/expert/online-experts", 
                               headers={'Authorization': f'Bearer {token}'},
                               params={'category': selected_category})
        
        if response.status_code != 200:
            print("❌ Failed to load experts")
            input("\nPress Enter to continue...")
            return
        
        experts = response.json().get("experts", [])
        
        print(f"\n� AVAILABLE {selected_category.upper()}S")
        print("="*60)
        
        if not experts:
            print(f"📭 No {selected_category.lower()}s online right now.")
            print("💡 Please try again later or select a different category.")
            input("\nPress Enter to continue...")
            return
        
        # Display experts with detailed information
        for idx, expert in enumerate(experts, 1):
            print(f"\n[{idx}] 👤 {expert.get('name', 'Unknown')}")
            print(f"    🎯 Specialization: {expert.get('specialization', 'N/A')}")
            print(f"    ⭐ Rating: {expert.get('rating', 0)}/5.0")
            print(f"    💼 Experience: {expert.get('experience', 0)} years")
            print(f"    📊 Status: 🟢 Online")
        
        # Step 3: Expert selection
        print(f"\n" + "="*60)
        sel = input(f"Select {selected_category.lower()} number (1-{len(experts)}): ").strip()
        
        if not sel.isdigit() or int(sel) < 1 or int(sel) > len(experts):
            print("❌ Invalid selection")
            input("\nPress Enter to continue...")
            return
        
        expert = experts[int(sel) - 1]
        expert_id = expert["id"]
        
        print(f"\n✅ Selected: {expert.get('name', 'Unknown')}")
        print(f"🎯 {selected_category}")
        
        # Step 4: Problem description
        print("\n" + "="*60)
        print("📝 DESCRIBE YOUR PROBLEM")
        print("="*60)
        print("Please describe your car issue in detail:")
        description = input("> ").strip()
        
        if not description:
            print("❌ Problem description is required")
            input("\nPress Enter to continue...")
            return
        
        # Step 5: Image upload (optional)
        print("\n" + "="*60)
        print("📷 ADD IMAGES (Optional)")
        print("="*60)
        print("Enter image path or type 'skip' to continue:")
        img_path = input("> ").strip()
        
        files = None
        if img_path.lower() != "skip" and img_path != "":
            if not os.path.isfile(img_path):
                print("❌ File does not exist, skipping image.")
            else:
                try:
                    files = {'images': open(img_path, 'rb')}
                    print("✅ Image added successfully")
                except Exception as e:
                    print(f"❌ Could not open file: {e}")
                    files = None
        
        # Step 6: Create request
        print("\n🔄 Creating consultation request...")
        
        data = {
            'user_id': str(user_id),
            'expert_category': selected_category,
            'description': description
        }
        
        try:
            response = requests.post(
                f"{API}/api/car/expert/start-request",
                data=data,
                files=files,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Close file if opened
            if files:
                files['images'].close()
                
        except Exception as e:
            # Close file on error too
            if files:
                try:
                    files['images'].close()
                except:
                    pass
            print(f"❌ Error creating request: {e}")
            input("\nPress Enter to continue...")
            return
        
        if response.status_code == 200:
            result = response.json().get('data', {})
            request_id = result.get('request_id')
            status = result.get('status')
            expert_name = expert.get('name', 'Expert')
            queue_position = result.get('queue_position')
            
            print(f"\n✅ Request created successfully!")
            print(f"📋 Request ID: {request_id}")
            print(f"👨‍🔧 Expert: {expert_name}")
            print(f"🎯 Category: {selected_category}")
            print(f"📊 Status: {status}")
            
            if status == 'ASSIGNED':
                print("🎉 Expert connected! You can start chatting now.")
                # Enter conversation mode
                conversation_detail_with_expert(user_id, token, request_id, expert_name)
            elif status == 'WAITING_QUEUE':
                print(f"⏳ Queue Position: {queue_position}")
                print("🔄 Expert will connect soon. You'll be notified when assigned.")
                print("💡 You can check status in 'My Conversations'")
            
        else:
            error = response.json().get('error', 'Failed to create request')
            print(f"❌ {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")

def my_conversations(user_id, token):
    """View and manage user conversations"""
    print("\n" + "="*60)
    print("💬 MY CONVERSATIONS")
    print("="*60)
    
    try:
        response = requests.get(
            f"{API}/api/car/expert/my-conversations",
            params={'user_id': user_id},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code != 200:
            print("❌ Failed to load conversations")
            input("\nPress Enter to continue...")
            return
        
        conversations = response.json().get('conversations', [])
        
        if not conversations:
            print("📭 No conversations found")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n📊 Total Conversations: {len(conversations)}\n")
        
        # Display conversations
        for i, conv in enumerate(conversations, 1):
            status_emoji = {
                'WAITING_QUEUE': '⏳',
                'ASSIGNED': '👨‍🔧',
                'IN_PROGRESS': '💬',
                'RESOLVED': '✅'
            }.get(conv['status'], '📋')
            
            print(f"{i}. {status_emoji} {conv['category_name']}")
            print(f"   📋 ID: {conv['id']}")
            print(f"   📊 Status: {conv['status']}")
            print(f"   📅 Created: {conv['created_at']}")
            if conv['expert_name']:
                print(f"   👨‍🔧 Expert: {conv['expert_name']}")
            print(f"   📝 {conv['problem_description'][:100]}{'...' if len(conv['problem_description']) > 100 else ''}")
            print()
        
        # Select conversation
        try:
            choice = int(input("Select conversation (0 to cancel): ").strip())
            if choice == 0:
                return
            if choice < 1 or choice > len(conversations):
                print("❌ Invalid selection")
                input("\nPress Enter to continue...")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            input("\nPress Enter to continue...")
            return
        
        selected_conv = conversations[choice - 1]
        conversation_detail(user_id, token, selected_conv['id'])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")

def conversation_detail(user_id, token, request_id):
    """Show conversation details and allow chatting"""
    try:
        response = requests.get(
            f"{API}/api/car/expert/request/{request_id}",
            params={'user_id': user_id},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code != 200:
            print("❌ Failed to load conversation details")
            input("\nPress Enter to continue...")
            return
        
        details = response.json().get('data', {})
        
        while True:
            print("\n" + "="*60)
            print(f"💬 CONVERSATION - {details['category_name']}")
            print("="*60)
            print(f"📋 Request ID: {details['id']}")
            print(f"📊 Status: {details['status']}")
            print(f"📅 Created: {details['created_at']}")
            
            if details['expert']:
                print(f"👨‍🔧 Expert: {details['expert']['name']}")
                print(f"🟢 Expert Status: {details['expert']['online_status']}")
            
            print(f"\n📝 Problem: {details['problem_description']}")
            
            # Show images if any
            if details['images']:
                print(f"\n📷 Images ({len(details['images'])}):")
                for img in details['images']:
                    print(f"   📄 {img['image_path']}")
            
            # Show messages
            if details['status'] in ['ASSIGNED', 'IN_PROGRESS']:
                # Get messages from consultation session
                try:
                    session_response = requests.get(f"{API}/api/consultation-session/active/{details['expert']['id'] if details.get('expert') else 'unknown'}")
                    if session_response.status_code == 200:
                        session_data = session_response.json()
                        session_id = session_data.get('session_id')
                        if session_id:
                            messages_response = requests.get(f"{API}/api/consultation-session/{session_id}/messages")
                            if messages_response.status_code == 200:
                                messages = messages_response.json().get('messages', [])
                            else:
                                messages = []
                        else:
                            messages = []
                    else:
                        messages = []
                except:
                    messages = []
            else:
                # Get messages from ask_expert database
                messages = details.get('messages', [])
            
            if messages:
                print(f"\n💬 Messages ({len(messages)}):")
                print("-" * 40)
                for msg in messages:
                    sender = "👤 You" if msg.get('sender_type') == 'USER' or msg.get('sender_type') == 'USER' else f"👨‍🔧 Expert"
                    timestamp = msg.get('created_at', msg.get('timestamp', 'Unknown'))[:19] if msg.get('created_at') or msg.get('timestamp') else 'Unknown'
                    message_text = msg.get('message_text', msg.get('message', ''))
                    print(f"{sender} [{timestamp}]:")
                    print(f"   {message_text}")
                    print()
            
            # Show typing indicator
            typing_status = details.get('typing_status')
            if typing_status and typing_status.get('expert_typing'):
                print("👨‍🔧 Expert is typing...")
            
            # Action menu
            print("\n" + "-" * 40)
            if details['status'] in ['ASSIGNED', 'IN_PROGRESS']:
                print("1. 💬 Send Message")
                print("2. 📞 Start Call")
                print("3. ✅ Mark Resolved")
            print("4. 🔄 Refresh")
            print("5. ⬅️ Back")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1" and details['status'] in ['ASSIGNED', 'IN_PROGRESS']:
                send_message(user_id, token, request_id)
            elif choice == "2" and details['status'] in ['ASSIGNED', 'IN_PROGRESS']:
                start_call_in_conversation(user_id, token, request_id)
            elif choice == "3" and details['status'] in ['ASSIGNED', 'IN_PROGRESS']:
                resolve_conversation(user_id, token, request_id)
                return
            elif choice == "4":
                # Refresh conversation details
                response = requests.get(
                    f"{API}/api/car/expert/request/{request_id}",
                    params={'user_id': user_id},
                    headers={'Authorization': f'Bearer {token}'}
                )
                if response.status_code == 200:
                    details = response.json().get('data', {})
            elif choice == "5":
                return
            else:
                print("❌ Invalid choice or action not available")
                input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")

def send_message(user_id, token, request_id):
    """Send a message to the expert"""
    try:
        message = input("\n💬 Enter your message: ").strip()
        if not message:
            print("❌ Message cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        # Get session details first
        session_response = requests.get(f"{API}/api/consultation-session/active/2")  # Expert ID 2 for now
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data.get('session_id')
            
            if session_id:
                # Send message to consultation session
                response = requests.post(
                    f"{API}/api/consultation-session/{session_id}/message",
                    json={'user_id': user_id, 'message': message, 'sender_type': 'USER'},
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                if response.status_code == 200:
                    print("✅ Message sent successfully")
                else:
                    error = response.json().get('error', 'Failed to send message')
                    print(f"❌ {error}")
            else:
                print("❌ No active session found")
        else:
            print("❌ Failed to get session details")
        
        response = requests.post(
            f"{API}/api/car/expert/request/{request_id}/message",
            json={'user_id': user_id, 'message': message},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            return message
        else:
            print("❌ Failed to send message")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def take_call_note():
    """Take note during call"""
    try:
        note = input("📝 Note: ").strip()
        if not note:
            return None
        return note
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def show_call_info(start_time, messages, notes):
    """Show detailed call information"""
    duration = int(time.time() - start_time)
    duration_str = f"{duration // 3600:02d}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
    
    print(f"\n📊 CALL ANALYTICS")
    print("="*40)
    print(f"⏱️ Duration: {duration_str}")
    print(f"💬 Messages: {len(messages)}")
    print(f"📝 Notes: {len(notes)}")
    
    if messages:
        print(f"\n💬 MESSAGE HISTORY:")
        for i, msg in enumerate(messages[-5:], 1):  # Show last 5 messages
            print(f"  {i}. [{msg['timestamp']}] {msg['sender']}: {msg['message']}")
    
    if notes:
        print(f"\n📝 CALL NOTES:")
        for i, note in enumerate(notes[-3:], 1):  # Show last 3 notes
            print(f"  {i}. [{note['timestamp']}] {note['note']}")
    
    input("\nPress Enter to continue...")

def confirm_end_call():
    """Confirm ending the call"""
    try:
        confirm = input("⚠️ Are you sure you want to end this call? (y/N): ").strip().lower()
        return confirm == 'y'
    except:
        return False

def end_call_session(user_id, token, request_id, start_time, notes):
    """End call session and save summary"""
    try:
        duration = int(time.time() - start_time)
        
        # End the call
        response = requests.post(
            f"{API}/api/car/expert/request/{request_id}/resolve",
            json={'user_id': user_id},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            print("✅ Call session ended successfully")
            
            # Save call summary (could be enhanced to save to database)
            call_summary = {
                'request_id': request_id,
                'duration_seconds': duration,
                'notes_count': len(notes),
                'ended_at': datetime.now().isoformat()
            }
            
            print(f"📊 Call summary saved")
        else:
            print("❌ Failed to end call session")
    
    except Exception as e:
        print(f"❌ Error ending call: {e}")

def pause_call_session(user_id, token, request_id):
    """Pause call session"""
    try:
        print("⏸️ Pausing call...")
        # Could implement actual pause logic here
        pass
    except Exception as e:
        print(f"❌ Error pausing call: {e}")

def resume_call_session(user_id, token, request_id):
    """Resume paused call session"""
    try:
        print("▶️ Resuming call...")
        # Could implement actual resume logic here
        pass
    except Exception as e:
        print(f"❌ Error resuming call: {e}")

def conversation_detail_with_expert(user_id, token, request_id, expert_name):
    """Handle conversation with a specific expert"""
    while True:
        print("\n" + "="*60)
        print(f"💬 CONVERSATION WITH {expert_name.upper()}")
        print("="*60)
        print("1. 📋 View Conversation")
        print("2. 💬 Send Message")
        print("3. 📊 Check Status")
        print("4. 📞 Start Call")
        print("5. ✅ Mark Resolved")
        print("6. ❌ Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_conversation_messages(user_id, token, request_id, expert_name)
        elif choice == "2":
            send_message_in_conversation(user_id, token, request_id)
        elif choice == "3":
            check_conversation_status(user_id, token, request_id)
        elif choice == "4":
            start_call_in_conversation(user_id, token, request_id)
        elif choice == "5":
            if resolve_conversation_in_chat(user_id, token, request_id):
                break
        elif choice == "6":
            break
        else:
            print("❌ Invalid choice")
            input("\nPress Enter to continue...")

def view_conversation_messages(user_id, token, request_id, expert_name):
    """View conversation messages"""
    try:
        response = requests.get(f"{API}/api/car/expert/request/{request_id}/messages", 
                               headers={'Authorization': f'Bearer {token}'})
        if response.status_code == 200:
            messages = response.json().get('messages', [])
            print("\n--- CONVERSATION ---")
            if not messages:
                print("📭 No messages yet")
            else:
                for msg in messages:
                    prefix = "👤 You" if msg.get("sender_type") == "USER" else f"👨‍🔧 {expert_name}"
                    timestamp = msg.get('created_at', 'Unknown time')
                    print(f"{prefix} ({timestamp}): {msg.get('message','')}")
        else:
            print("❌ Failed to load messages")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def send_message_in_conversation(user_id, token, request_id):
    """Send a message to the expert"""
    try:
        msg = input("💬 Your message: ").strip()
        if not msg:
            print("❌ Message cannot be empty")
            return
        
        response = requests.post(
            f"{API}/api/car/expert/request/{request_id}/message",
            headers={'Authorization': f'Bearer {token}'},
            json={"user_id": str(user_id), "message": msg},
        )
        
        if response.status_code in (200, 201):
            print("✅ Message sent successfully")
        else:
            print("❌ Failed to send message")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def check_conversation_status(user_id, token, request_id):
    """Check request status"""
    try:
        response = requests.get(f"{API}/api/car/expert/request/{request_id}", 
                               headers={'Authorization': f'Bearer {token}'})
        if response.status_code == 200:
            req = response.json().get('data', {})
            print(f"\n📊 Request Status: {req.get('status','Unknown')}")
            print(f"🗂️ Category: {req.get('expert_category','Unknown')}")
            print(f"⏰ Created: {req.get('created_at','Unknown')}")
            
            if req.get("status") == "RESOLVED":
                print("✅ Consultation completed")
            elif req.get("status") == "IN_PROGRESS":
                print("🔄 Consultation in progress")
            else:
                print("⏳ Waiting for expert response")
        else:
            print("❌ Failed to load request status")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def start_call_in_conversation(user_id, token, request_id):
    """Start a call session"""
    try:
        print("🔄 Initiating call...")
        response = requests.post(
            f"{API}/api/car/expert/request/{request_id}/call",
            headers={'Authorization': f'Bearer {token}'},
            json={"user_id": str(user_id)},
        )
        
        if response.status_code == 200:
            print("✅ Call session started")
            print("📞 Expert will join the call shortly")
        else:
            print("❌ Failed to start call")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def resolve_conversation_in_chat(user_id, token, request_id):
    """Mark request as resolved"""
    try:
        confirm = input("⚠️ Are you sure you want to mark this as resolved? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
        
        response = requests.post(
            f"{API}/api/car/expert/request/{request_id}/resolve",
            headers={'Authorization': f'Bearer {token}'},
            json={"user_id": str(user_id)},
        )
        
        if response.status_code == 200:
            print("✅ Request marked as resolved")
            print("🙏 Thank you for using our expert service!")
            return True
        else:
            print("❌ Failed to resolve request")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")
    return False
