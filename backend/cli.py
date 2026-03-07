import requests
import sys
import random
import time

API = "http://127.0.0.1:5000"
TOKEN = None
USER_ID = None

def tts_speak(text, lang=None):
    try:
        from ai_engine import speak as _speak
        if lang is not None:
            _speak(text, lang)
        else:
            _speak(text)
    except Exception:
        try:
            print(f"🔊 {text}")
        except Exception:
            pass
def check_server_connection():
    """Check if Flask server is running"""
    try:
        _ = requests.get(f"{API}/services", timeout=2)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False

# ==================================================
# ================= USER FLOW ======================
# ==================================================

def user_signup():
    print("\n👤 User Signup (Email OTP)")
    name = input("Name: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    email = input("Email: ").strip()

    r = requests.post(f"{API}/signup", json={
        "name": name,
        "username": username,
        "password": password,
        "email": email
    })

    if r.status_code != 201:
        print("❌ Signup failed:", r.json())
        return

    print(f"📨 OTP sent to {email}")

    while True:
        print("\n1. Enter OTP")
        print("2. Cancel")
        c = input("Choice: ").strip()

        if c == "1":
            otp = input("OTP: ").strip()
            vr = requests.post(f"{API}/verify-otp", json={
                "email": email,
                "otp": otp
            })

            if vr.status_code == 200:
                print("✅ Account verified")
                return
            else:
                print("❌", vr.json().get("error"))

        elif c == "2":
            return


def user_login():
    global TOKEN, USER_ID
    print("\n🔐 User Login")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    r = requests.post(f"{API}/login", json={
        "username": username,
        "password": password
    })

    if r.status_code == 200:
        data = r.json()
        TOKEN = data["token"]
        USER_ID = data.get("user_id")
        print("✅ Logged in successfully")
        service_selection()
    else:
        print("❌ Login failed:", r.json().get("error"))


def service_selection():
    """Service Selection Screen - User selects from 5 services"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*50)
        print("🏠 EXPERTEASE - SELECT A SERVICE")
        print("="*50)
        print("1. 🏥 Healthcare")
        print("2. 🏠 Housekeeping")
        print("3. 📦 Resource Management")
        print("4. 🚗 Car Services")
        print("5. 💰 Money Management")
        print("6. 👋 Logout")
        
        choice = input("\nSelect service: ").strip()
        
        if choice == "1":
            healthcare_navigation()
        elif choice == "2":
            print("🚧 Housekeeping service coming soon!")
        elif choice == "3":
            print("🚧 Resource Management service coming soon!")
        elif choice == "4":
            open_car_service()
        elif choice == "5":
            from services.money_service.money_service_cli import money_service_menu
            money_service_menu(USER_ID, "user")
        elif choice == "6":
            TOKEN = None
            USER_ID = None
            print("👋 Logged out")
            return
        else:
            print("❌ Invalid choice")

def open_car_service():
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    from car_service.home_cli import show_car_home
    if not USER_ID:
        r = requests.get(f"{API}/user/info", headers={"Authorization": f"Bearer {TOKEN}"})
        if r.status_code == 200:
            USER_ID = r.json().get("user_id")
        else:
            print("❌ Could not fetch user info")
            return
    pr = requests.get(f"{API}/api/car/profile", headers={"Authorization": f"Bearer {TOKEN}"})
    if pr.status_code == 404:
        print("\n" + "="*60)
        print("🚗 CAR SERVICE SETUP")
        print("="*60)
        city = input("Enter City: ").strip()
        address = input("Enter Address: ").strip()
        emergency_name = input("Enter Emergency Contact Name: ").strip()
        emergency_phone = input("Enter Emergency Contact Phone: ").strip()
        print("\nAdd Car:")
        brand = input("Enter Brand: ").strip()
        model = input("Enter Model: ").strip()
        year = input("Enter Year: ").strip()
        fuel = input("Enter Fuel Type: ").strip()
        reg = input("Enter Registration Number: ").strip()
        data = {
            "city": city,
            "address": address,
            "emergency_contact_name": emergency_name,
            "emergency_contact_phone": emergency_phone,
            "brand": brand,
            "model": model,
            "year": int(year) if year.isdigit() else year,
            "fuel_type": fuel,
            "registration_number": reg
        }
        sr = requests.post(f"{API}/api/car/setup-profile", json=data, headers={"Authorization": f"Bearer {TOKEN}"})
        if sr.status_code not in (200, 201):
            print("❌ Failed to setup car service profile")
            return
        print("✅ Car service profile created")
    elif pr.status_code != 200:
        print(" Failed to load profile")
        return
    while True:
        print("\n" + "="*60)
        print("🚗 CAR SERVICE")
        print("="*60)
        print("1. 🏠 Home")
        print("2. 🔧 Book Mechanic")
        print("3. 🤖 AI Mechanic")
        print("4. 🚗 My Garage")
        print("5. 📅 My Bookings")
        print("6. 👤 Profile")
        print("7. 🧠 ASK EXPERT")
        print("8. 👋 Logout")
        print("9. ⬅️ Back")
        c = input("\nSelect option: ").strip()
        if c == "1":
            from car_service.home_cli import show_car_home
            show_car_home(USER_ID)
        elif c == "2":
            from car_service.book_mechanic_cli import book_mechanic
            book_mechanic(USER_ID)
        elif c == "3":
            from car_service.trip_planner_cli import trip_planner_menu
            trip_planner_menu(USER_ID, TOKEN)
        elif c == "4":
            show_my_garage(USER_ID)
        elif c == "5":
            from car_service.my_bookings_cli import show_my_bookings
            show_my_bookings(USER_ID, TOKEN)
        elif c == "6":
            from car_service.profile_cli import car_profile_screen
            car_profile_screen(TOKEN)
        elif c == "7":
            from car_service.ask_expert_cli import ask_expert_menu
            ask_expert_menu(USER_ID, TOKEN)
        elif c == "8":
            TOKEN = None
            USER_ID = None
            print("👋 Logged out successfully")
            return
        elif c == "9":
            return
        else:
            print("❌ Invalid choice")

def show_my_garage(user_id):
    from car_service.car_profile_db import car_profile_db
    while True:
        cars = car_profile_db.get_user_cars(user_id)
        print("\n" + "="*50)
        print("🚗 MY GARAGE")
        print("="*50)
        print(f"\nTotal Cars: {len(cars)}\n")
        for idx, car in enumerate(cars, 1):
            print(f"[{idx}]")
            print(f"Brand: {car.get('brand','')}")
            print(f"Model: {car.get('model','')}")
            print(f"Year: {car.get('year','')}")
            print(f"Fuel: {car.get('fuel_type','')}")
            print(f"Registration: {car.get('registration_number','')}")
            if car.get('is_default') == 1:
                print("⭐ DEFAULT")
            print("")
        print("----------------------------------------")
        print("\nOptions:")
        print("1. Add Car")
        print("2. Set Default")
        print("3. Back")
        ch = input("\nSelect option: ").strip()
        if ch == "1":
            brand = input("Enter Brand: ").strip()
            model = input("Enter Model: ").strip()
            year = input("Enter Year: ").strip()
            fuel = input("Enter Fuel Type: ").strip()
            reg = input("Enter Registration Number: ").strip()
            if not all([brand, model, year, fuel, reg]) or not year.isdigit():
                print("❌ Invalid inputs")
                continue
            data = {"brand": brand, "model": model, "year": int(year), "fuel_type": fuel, "registration_number": reg}
            ar = requests.post(f"{API}/api/car/add-car", json=data, headers={"Authorization": f"Bearer {TOKEN}"})
            if ar.status_code in (200, 201):
                print("✅ Car added")
            else:
                print("❌ Failed to add car")
        elif ch == "2":
            if not cars:
                print("❌ No cars to set as default")
                continue
            sel = input("Enter car number to set default: ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(cars):
                print("❌ Invalid selection")
                continue
            car_id = cars[int(sel)-1]['id']
            from car_service.car_profile_db import car_profile_db
            car_profile_db.set_default_car(user_id, car_id)
            print("✅ Default car updated successfully")
        elif ch == "3":
            return
        else:
            print("❌ Invalid choice")



def show_online_experts():
    """Show online experts by category"""
    try:
        # Get categories first
        r = requests.get(f"{API}/expert/categories")
        if r.status_code != 200:
            print("❌ Failed to load categories")
            return
        
        categories = r.json().get("categories", [])
        if not categories:
            print("📭 No expert categories available")
            return
        
        print("\n" + "="*60)
        print("📂 EXPERT CATEGORIES")
        print("="*60)
        for idx, category in enumerate(categories, 1):
            print(f"[{idx}] {category}")
        print(f"[{len(categories) + 1}] All Categories")
        print(f"[{len(categories) + 2}] Back")
        
        choice = input("\nSelect category: ").strip()
        if not choice.isdigit():
            print("❌ Invalid choice")
            return
        
        choice_num = int(choice)
        if choice_num == len(categories) + 2:
            return
        elif choice_num == len(categories) + 1:
            category = None
        elif 1 <= choice_num <= len(categories):
            category = categories[choice_num - 1]
        else:
            print("❌ Invalid choice")
            return
        
        # Get online experts
        params = {}
        if category:
            params["category"] = category
        
        r = requests.get(f"{API}/expert/online", params=params)
        if r.status_code != 200:
            print("❌ Failed to load experts")
            return
        
        experts = r.json().get("experts", [])
        if not experts:
            print("📭 No online experts found")
            return
        
        print("\n" + "="*70)
        print(f"🟢 ONLINE EXPERTS{' - ' + category if category else ''}")
        print("="*70)
        for idx, expert in enumerate(experts, 1):
            print(f"\n[{idx}] {expert.get('full_name', 'Unknown')}  ⭐ {expert.get('rating', 0):.1f}/5.0")
            print(f"   🎓 {expert.get('category', 'Unknown')}")
            if expert.get('subcategory'):
                print(f"   📚 {expert['subcategory']}")
            print(f"   💰 Rate: ₹{expert.get('hourly_rate', 0)}/hr")
            print(f"   ✅ {expert.get('total_jobs', 0)} jobs completed")
            print(f"   🆔 Expert ID: {expert.get('id', 'Unknown')}")
        
        expert_choice = input("\nSelect expert to request (or 0 to go back): ").strip()
        if expert_choice == "0":
            return
        
        if not expert_choice.isdigit() or int(expert_choice) < 1 or int(expert_choice) > len(experts):
            print("❌ Invalid selection")
            return
        
        selected_expert = experts[int(expert_choice) - 1]
        create_expert_request(selected_expert)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def browse_all_experts():
    """Browse all experts by category"""
    try:
        # Get categories first
        r = requests.get(f"{API}/expert/categories")
        if r.status_code != 200:
            print("❌ Failed to load categories")
            return
        
        categories = r.json().get("categories", [])
        if not categories:
            print("📭 No expert categories available")
            return
        
        print("\n" + "="*60)
        print("📂 EXPERT CATEGORIES")
        print("="*60)
        for idx, category in enumerate(categories, 1):
            print(f"[{idx}] {category}")
        print(f"[{len(categories) + 1}] All Categories")
        print(f"[{len(categories) + 2}] Back")
        
        choice = input("\nSelect category: ").strip()
        if not choice.isdigit():
            print("❌ Invalid choice")
            return
        
        choice_num = int(choice)
        if choice_num == len(categories) + 2:
            return
        elif choice_num == len(categories) + 1:
            category = None
        elif 1 <= choice_num <= len(categories):
            category = categories[choice_num - 1]
        else:
            print("❌ Invalid choice")
            return
        
        # Get all experts
        params = {}
        if category:
            params["category"] = category
        
        r = requests.get(f"{API}/expert/all", params=params)
        if r.status_code != 200:
            print("❌ Failed to load experts")
            return
        
        experts = r.json().get("experts", [])
        if not experts:
            print("📭 No experts found")
            return
        
        print("\n" + "="*70)
        print(f"👥 ALL EXPERTS{' - ' + category if category else ''}")
        print("="*70)
        for idx, expert in enumerate(experts, 1):
            status = "🟢 Online" if expert.get('is_online') else "🔴 Offline"
            print(f"\n[{idx}] {expert.get('full_name', 'Unknown')}  ⭐ {expert.get('rating', 0):.1f}/5.0")
            print(f"   🎓 {expert.get('category', 'Unknown')}")
            if expert.get('subcategory'):
                print(f"   📚 {expert['subcategory']}")
            print(f"   💰 Rate: ₹{expert.get('hourly_rate', 0)}/hr")
            print(f"   ✅ {expert.get('total_jobs', 0)} jobs completed")
            print(f"   📊 Status: {status}")
            print(f"   🆔 Expert ID: {expert.get('id', 'Unknown')}")
        
        expert_choice = input("\nSelect expert to request (or 0 to go back): ").strip()
        if expert_choice == "0":
            return
        
        if not expert_choice.isdigit() or int(expert_choice) < 1 or int(expert_choice) > len(experts):
            print("❌ Invalid selection")
            return
        
        selected_expert = experts[int(expert_choice) - 1]
        create_expert_request(selected_expert)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def search_experts():
    """Search experts by name or specialization"""
    try:
        query = input("Enter search query (name, category, or keywords): ").strip()
        if not query:
            print("❌ Search query is required")
            return
        
        # Optional category filter
        r = requests.get(f"{API}/expert/categories")
        if r.status_code == 200:
            categories = r.json().get("categories", [])
            if categories:
                print("\nOptional: Filter by category")
                for idx, category in enumerate(categories, 1):
                    print(f"[{idx}] {category}")
                print(f"[{len(categories) + 1}] No filter")
                
                cat_choice = input("\nSelect category filter (optional): ").strip()
                category = None
                if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                    category = categories[int(cat_choice) - 1]
        
        params = {"q": query}
        if category:
            params["category"] = category
        
        r = requests.get(f"{API}/expert/search", params=params)
        if r.status_code != 200:
            print("❌ Failed to search experts")
            return
        
        experts = r.json().get("experts", [])
        if not experts:
            print("📭 No experts found matching your search")
            return
        
        print(f"\n🔍 Found {len(experts)} expert(s) matching '{query}'")
        print("="*70)
        for idx, expert in enumerate(experts, 1):
            status = "🟢 Online" if expert.get('is_online') else "🔴 Offline"
            print(f"\n[{idx}] {expert.get('full_name', 'Unknown')}  ⭐ {expert.get('rating', 0):.1f}/5.0")
            print(f"   🎓 {expert.get('category', 'Unknown')}")
            if expert.get('subcategory'):
                print(f"   📚 {expert['subcategory']}")
            print(f"   💰 Rate: ₹{expert.get('hourly_rate', 0)}/hr")
            print(f"   ✅ {expert.get('total_jobs', 0)} jobs completed")
            print(f"   📊 Status: {status}")
            print(f"   🆔 Expert ID: {expert.get('id', 'Unknown')}")
        
        expert_choice = input("\nSelect expert to request (or 0 to go back): ").strip()
        if expert_choice == "0":
            return
        
        if not expert_choice.isdigit() or int(expert_choice) < 1 or int(expert_choice) > len(experts):
            print("❌ Invalid selection")
            return
        
        selected_expert = experts[int(expert_choice) - 1]
        create_expert_request(selected_expert)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def create_expert_request(expert):
    """Create a request for selected expert"""
    try:
        print(f"\n📝 Creating request for {expert.get('full_name', 'Unknown')}")
        print("="*60)
        
        title = input("📋 Request Title: ").strip()
        if not title:
            print("❌ Title is required")
            return
        
        description = input("📝 Describe your problem: ").strip()
        if not description:
            print("❌ Description is required")
            return
        
        # Ask if user wants to upload an image
        upload_image = input("📷 Do you want to upload an image? (y/n): ").strip().lower()
        image_url = None
        
        if upload_image == 'y':
            print("📷 Please upload an image using the web interface at:")
            print(f"   {API}/expert/upload")
            print("   (Copy the returned file_url and paste it below)")
            image_url = input("📷 Image URL (or press Enter to skip): ").strip()
        
        priority = input("🚨 Priority (normal/urgent): ").strip().lower()
        if priority not in ['normal', 'urgent']:
            priority = 'normal'
        
        # Create request
        request_data = {
            "expert_id": expert.get('id'),
            "category": expert.get('category'),
            "title": title,
            "description": description,
            "priority": priority
        }
        
        if image_url:
            request_data["image_url"] = image_url
        
        r = requests.post(
            f"{API}/expert/request",
            json=request_data,
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        if r.status_code == 201:
            response = r.json()
            request_id = response.get('request_id')
            print(f"\n✅ Expert request created successfully!")
            print(f"📋 Request ID: {request_id}")
            print(f"👨‍🏫 Expert: {expert.get('full_name', 'Unknown')}")
            print(f"📋 Title: {title}")
            print(f"🚨 Priority: {priority}")
            print("⏳ Status: Pending expert response")
            print("\n📱 You will be notified when the expert responds.")
            print("💬 You can check your requests from the main menu.")
        else:
            error = r.json().get('error', 'Unknown error')
            print(f"❌ Failed to create request: {error}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error creating request: {e}")
        input("\nPress Enter to continue...")


def show_my_requests():
    """Show user's expert requests"""
    try:
        r = requests.get(
            f"{API}/expert/user/requests",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        if r.status_code != 200:
            print("❌ Failed to load requests")
            return
        
        requests = r.json().get("requests", [])
        if not requests:
            print("📭 You haven't made any expert requests yet")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "="*70)
        print("📋 MY EXPERT REQUESTS")
        print("="*70)
        for idx, req in enumerate(requests, 1):
            status_emoji = {"pending": "⏳", "accepted": "✅", "rejected": "❌", "completed": "✨"}
            status = req.get('status', 'unknown')
            print(f"\n[{idx}] {req.get('title', 'Unknown Request')}")
            print(f"   👨‍🏫 Expert: {req.get('expert_name', 'Unknown')}")
            print(f"   🎓 Category: {req.get('category', 'Unknown')}")
            print(f"   📊 Status: {status_emoji.get(status, '❓')} {status.title()}")
            print(f"   📅 Created: {req.get('created_at', 'Unknown')}")
            print(f"   🆔 Request ID: {req.get('id', 'Unknown')}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")


def show_my_chats():
    """Show user's active chat sessions"""
    try:
        r = requests.get(
            f"{API}/expert/chat/rooms/user",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        if r.status_code != 200:
            print("❌ Failed to load chat rooms")
            return
        
        rooms = r.json().get("rooms", [])
        if not rooms:
            print("📭 You don't have any active chat sessions")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "="*70)
        print("💬 MY ACTIVE CHATS")
        print("="*70)
        for idx, room in enumerate(rooms, 1):
            unread = room.get('unread_count', 0)
            unread_text = f" ({unread} unread)" if unread > 0 else ""
            print(f"\n[{idx}] {room.get('expert_name', 'Unknown Expert')}{unread_text}")
            print(f"   💬 Room: {room.get('room_name', 'Unknown')}")
            print(f"   🎓 Category: {room.get('category', 'Unknown')}")
            print(f"   📅 Started: {room.get('created_at', 'Unknown')}")
            print(f"   🆔 Room ID: {room.get('id', 'Unknown')}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to continue...")


 


def healthcare_navigation():
    """Healthcare Navigation - 5 tabs like Instagram bottom nav"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*50)
        print("🏥 HEALTHCARE")
        print("="*50)
        print("1. 🏠 Home")
        print("2. 🤖 AI Care")
        print("3. 🔍 Explore")
        print("4. 📅 Appointments")
        print("5. 🎥 Video Consultation")
        print("6. 👤 Profile")
        print("7. ⬅️  Back to Services")
        
        choice = input("\nSelect tab: ").strip()
        
        if choice == "1":
            healthcare_home_tab()
        elif choice == "2":
            healthcare_ai_care_tab()
        elif choice == "3":
            healthcare_explore_tab()
        elif choice == "4":
            healthcare_appointments_tab()
        elif choice == "5":
            video_menu_user(USER_ID)
        elif choice == "6":
            healthcare_profile_tab()
        elif choice == "7":
            return
        else:
            print("❌ Invalid choice")


def healthcare_home_tab():
    """Healthcare Home Tab - Show specializations, then doctor cards"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    # Get all specializations
    r = requests.get(f"{API}/healthcare/specializations")
    if r.status_code != 200:
        print("❌ Error fetching specializations")
        return
    
    specializations = r.json().get("specializations", [])
    
    # Default specializations if none in DB
    default_specs = [
        "Dentist", "Cardiologist", "Eye Specialist", "ENT", "Orthopedic",
        "Dermatologist", "Neurologist", "Psychiatrist", "Gynecologist",
        "Pediatrician", "General Physician", "Urologist", "Gastroenterologist",
        "Endocrinologist", "Pulmonologist", "Oncologist", "Rheumatologist",
        "Nephrologist", "Hepatologist", "Allergist"
    ]
    
    if not specializations:
        specializations = default_specs
    
    while True:
        print("\n" + "="*60)
        print("🏠 HEALTHCARE HOME")
        print("="*60)
        print("\n📋 Medical Specializations:")
        print("-" * 60)
        
        for idx, spec in enumerate(specializations[:20], 1):  # Show max 20
            print(f"{idx:2}. {spec}")
        
        print(f"\n{len(specializations) + 1}. 🔍 Search within specialization")
        print(f"{len(specializations) + 2}. ⬅️  Back")
        
        choice = input("\nSelect specialization: ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(specializations):
                selected_spec = specializations[choice_num - 1]
                show_doctors_by_specialization(selected_spec)
            elif choice_num == len(specializations) + 1:
                search_within_specialization()
            elif choice_num == len(specializations) + 2:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")



def show_doctors_by_specialization(specialization):
    """Show doctor cards for a selected specialization"""
    global TOKEN, USER_ID
    
    r = requests.get(f"{API}/healthcare/doctors/{specialization}")
    if r.status_code != 200:
        print("❌ Error fetching doctors")
        return
    
    doctors = r.json().get("doctors", [])
    
    if not doctors:
        print(f"\n👨‍⚕️ No {specialization} doctors available at the moment")
        input("\nPress Enter to continue...")
        return
    
    while True:
        print("\n" + "="*70)
        print(f"🏥 {specialization.upper()} - Available Doctors")
        print("="*70)
        
        for idx, doc in enumerate(doctors, 1):
            print(f"\n[{idx}] DOCTOR CARD")
            print("-" * 70)
            print(f"👤 Name: Dr. {doc['full_name']}")
            print(f"⭐ Rating: {doc.get('rating', 0.0):.1f}/5.0")
            print(f"📅 Experience: {doc['experience']} years")
            print(f"📍 Location: {doc.get('clinic_location', 'Location not specified')}")
            print(f"🆔 Doctor ID: {doc['id']}")
            print("-" * 70)
        
        print(f"\n{len(doctors) + 1}. 🔍 Search by doctor name")
        print(f"{len(doctors) + 2}. ⬅️  Back to Specializations")
        
        choice = input("\nSelect doctor (or search/back): ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(doctors):
                selected_doc = doctors[choice_num - 1]
                show_doctor_actions(selected_doc)
            elif choice_num == len(doctors) + 1:
                search_doctor_by_name(doctors)
            elif choice_num == len(doctors) + 2:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def show_doctor_actions(doctor):
    """Show actions for selected doctor: Book Appointment, Audio/Video Call"""
    global TOKEN, USER_ID
    
    while True:
        print("\n" + "="*60)
        print(f"👨‍⚕️ Dr. {doctor['full_name']}")
        print("="*60)
        print(f"Specialization: {doctor['specialization']}")
        print(f"Experience: {doctor['experience']} years")
        print(f"Location: {doctor.get('clinic_location', 'N/A')}")
        print(f"Rating: {doctor.get('rating', 0.0):.1f}/5.0")
        print("="*60)
        print("\n1. 📅 Book Appointment")
        print("2. 📞 Audio / Video Call")
        print("3. ⬅️  Back")
        
        choice = input("\nSelect action: ").strip()
        
        if choice == "1":
            book_appointment_user(doctor['id'])
        elif choice == "2":
            print("🚧 Audio/Video Call feature coming soon!")
            print("💡 This will be available after appointment is accepted")
            input("\nPress Enter to continue...")
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")


def search_within_specialization():
    """Search doctors within a specialization"""
    spec = input("Enter specialization name: ").strip()
    if spec:
        show_doctors_by_specialization(spec)
    else:
        print("❌ Please enter a specialization name")


def search_doctor_by_name(doctors):
    """Search doctor by name within current list"""
    query = input("Enter doctor name to search: ").strip().lower()
    if not query:
        return
    
    matched = [doc for doc in doctors if query in doc['full_name'].lower()]
    
    if not matched:
        print(f"\n❌ No doctors found matching '{query}'")
        input("\nPress Enter to continue...")
        return
    
    print(f"\n✅ Found {len(matched)} doctor(s):")
    for idx, doc in enumerate(matched, 1):
        print(f"{idx}. Dr. {doc['full_name']} - {doc['specialization']}")
    
    if len(matched) == 1:
        show_doctor_actions(matched[0])
    else:
        choice = input("\nSelect doctor number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(matched):
            show_doctor_actions(matched[int(choice) - 1])


def healthcare_ai_care_tab():
    """AI Care Tab - Conversational Medical Triage with Voice Support"""
    global TOKEN, USER_ID

    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    # Import AI engine and voice functions
    try:
        from ai_engine import AIEngine, get_voice_input, speak, reset_session, get_session_info
        ai = AIEngine()
        AI_AVAILABLE = True
        VOICE_AVAILABLE = True
        print("🎥 Voice features available!")
    except ImportError:
        AI_AVAILABLE = False
        VOICE_AVAILABLE = False
        print("⚠️ Voice features not available. Install: pip install SpeechRecognition pyaudio pyttsx3")
        # Create dummy functions
        def reset_session(user_id):
            pass
        def get_voice_input():
            return ""
        def speak(text):
            print(f"🔊 {text}")
        def get_session_info():
            return {}
    
    print("\n" + "="*60)
    print("🤖 AI CARE - Conversational Health Assistant")
    print("="*60)
    print("🎥 NEW: Voice input/output support!")
    print("💬 AI now asks follow-up questions like a real doctor")
    print("🌍 Supports: English, Hindi, Marathi")
    print("-" * 60)
    
    # Reset session for new conversation
    reset_session(str(USER_ID) if USER_ID else "default")
    print("🔄 Started new conversation session")
    
    # Main conversation loop
    while True:
        print("\n" + "="*60)
        print("🗣️ INPUT OPTIONS")
        print("="*60)
        print("1. 💬 Type symptoms")
        if VOICE_AVAILABLE:
            print("2. 🎤 Speak symptoms")
        print("3. 🔄 Reset conversation")
        print("4. ⬅️  Exit")
        print("-" * 60)
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            # Text input
            symptoms = input("💬 Describe your symptoms: ").strip()
            if not symptoms:
                print("❌ Please describe your symptoms")
                continue
                
            # Process conversation
            if not process_ai_conversation(symptoms, str(USER_ID) if USER_ID else "default", VOICE_AVAILABLE):
                break
                
        elif choice == "2" and VOICE_AVAILABLE:
            # Voice input
            print("\n🎤 Voice Input Mode")
            symptoms = get_voice_input()
            if not symptoms:
                print("❌ Could not understand speech. Please try again.")
                continue
                
            # Process conversation
            if not process_ai_conversation(symptoms, str(USER_ID) if USER_ID else "default", VOICE_AVAILABLE):
                break
                
        elif choice == "3":
            # Reset conversation
            reset_session(str(USER_ID) if USER_ID else "default")
            print("🔄 Conversation reset. Starting fresh...")
            
        elif choice == "4":
            print("👋 Ending conversation. Take care!")
            break
            
        else:
            print("❌ Invalid choice")

def process_ai_conversation(symptoms: str, user_id: str, voice_available: bool) -> bool:
    """Process AI conversation and handle response"""
    
    print("\n🤖 AI is analyzing...")
    
    # Send to AI
    r = requests.post(f"{API}/healthcare/ai-care", json={
        "symptoms": symptoms,
        "user_id": user_id,
        "action": "chat"
    })
    
    if r.status_code != 200:
        print("❌ AI Care service unavailable")
        return True  # Continue conversation
    
    data = r.json()
    stage = data.get("stage", "triage")
    
    print("\n" + "="*60)
    print(f"🤖 AI Response (Stage: {stage.upper()})")
    print("="*60)
    
    if stage == "emergency":
        # Emergency response
        message = data.get("message", "")
        print(f"\n🚨 {message}")
        print("\n⚠️ Please seek immediate medical attention!")
        return False  # End conversation
        
    elif stage == "triage":
        # Triage stage - show question and continue
        question = data.get("question", "")
        print(f"\n💬 AI asks: {question}")
        
        # Voice output
        if voice_available:
            try:
                tts_speak(question)
            except ImportError:
                print(f"🔊 {question}")
        
        print("\n🔄 Please answer the question to continue...")
        return True  # Continue conversation
        
    else:  # final stage
        # Show complete analysis
        display_ai_response(data)
        
        # Show doctors if available
        doctors = data.get('recommended_doctors', [])
        if doctors:
            print(f"\n" + "-"*60)
            book_choice = input("Book appointment? (enter number or 0 to skip): ").strip()
            if book_choice.isdigit():
                num = int(book_choice)
                if 1 <= num <= len(doctors[:3]):
                    book_appointment_user(doctors[num-1]["id"])
        
        # End of consultation
        print(f"\n" + "="*60)
        print("🎉 Consultation Complete!")
        
        # Ask to continue
        continue_choice = input("\n💬 Start new conversation? (y/n): ").strip().lower()
        if continue_choice in ['y', 'yes']:
            try:
                from ai_engine import reset_session
                reset_session(user_id)
            except ImportError:
                pass  # reset_session already defined as dummy function above
            print("🔄 Starting new conversation...")
            return True  # Continue with new conversation
        else:
            return False  # End conversation


def display_ai_response(response: dict):
    """Display AI response with enhanced multilingual and dynamic doctor features"""
    stage = response.get("stage", "unknown")
    
    if stage == "triage":
        print("\n" + "="*60)
        print("🤖 AI Response (Stage: TRIAGE)")
        print("="*60)
        print(f"\n💬 AI asks: {response.get('question', '')}")
        
        # Show detected language
        detected_lang = response.get('detected_language', 'en')
        lang_names = {'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi'}
        print(f"🌍 Language: {lang_names.get(detected_lang, 'Unknown')}")
        
        # Voice output
        try:
            tts_speak(response.get('question', ''), detected_lang)
        except:
            pass
            
        print("\n🔄 Please answer the question to continue...")
        
    elif stage == "final":
        print("\n" + "="*60)
        print("🤖 AI Response (Stage: FINAL)")
        print("="*60)
        
        # Show detected language
        detected_lang = response.get('detected_language', 'en')
        lang_names = {'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi'}
        print(f"🌍 Response Language: {lang_names.get(detected_lang, 'English')}")
        
        # Severity indicator
        severity = response.get('severity', 'medium')
        severity_emoji = {
            'low': '🟢', 'mild': '🟡', 'moderate': '🟡', 
            'medium': '🟡', 'high': '🟠', 'severe': '🔴', 'emergency': '🚨'
        }
        print(f"\n{severity_emoji.get(severity, '🟡')} {severity.title()} - Medical consultation advised")
        
        print(f"\n💡 AI Advice: {response.get('advice', '')}")
        
        # Voice output for advice
        try:
            tts_speak(response.get('advice', ''), detected_lang)
        except:
            pass
        
        print(f"\n🏠 First Aid: {response.get('first_aid', '')}")
        
        # Enhanced OTC medicines display
        otc_medicines = response.get('otc_medicines', '')
        if otc_medicines:
            print(f"\n💊 OTC Medicines:")
            print(otc_medicines)
        
        print(f"\n📅 When to Visit Doctor: {response.get('when_to_visit_doctor', '')}")
        
        # Dynamic doctors display
        doctors = response.get('recommended_doctors', [])
        doctors_available = response.get('doctors_available', False)
        ai_analysis = response.get('ai_analysis', {})
        
        # Show AI analysis
        if ai_analysis:
            print(f"\n🧠 AI Medical Analysis:")
            suggested_specs = ai_analysis.get('suggested_specializations', [])
            if suggested_specs:
                print(f"   🎯 Suggested Specialists: {', '.join(suggested_specs)}")
            
            medical_context = ai_analysis.get('medical_context', {})
            if medical_context.get('severity'):
                print(f"   📊 Severity: {medical_context['severity']}")
            if medical_context.get('urgency'):
                print(f"   🚨 Urgency: {medical_context['urgency']}")
            if medical_context.get('body_parts'):
                print(f"   🏥 Affected Areas: {', '.join(medical_context['body_parts'])}")
        
        if doctors_available and doctors:
            print(f"\n👨‍⚕️ Recommended Doctors (from database):")
            for i, doctor in enumerate(doctors, 1):
                print(f"   {i}. Dr. {doctor.get('name', 'Unknown')}")
                print(f"      Specialization: {doctor.get('specialization', 'General')}")
                print(f"      Experience: {doctor.get('experience', 0)} years")
                print(f"      Rating: {doctor.get('rating', 0.0):.1f}/5.0")
                print(f"      Location: {doctor.get('location', 'Not specified')}")
                print(f"      ID: {doctor.get('id', 'N/A')}")
                if i < len(doctors):
                    print()
        elif not doctors_available:
            print(f"\n👨‍⚕️ Doctor Database: Currently unavailable")
            print("   Please check back later for doctor recommendations")
        
        # Follow-up notification
        if response.get('follow_up_created'):
            print(f"\n📅 Follow-up: Check-in notification scheduled for tomorrow")
        
        print("\n" + "="*60)
        print("🎉 Consultation Complete!")
        print("="*60)


def healthcare_explore_tab():
    """Explore Tab - Global doctor search"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*60)
        print("🔍 EXPLORE - Search Doctors")
        print("="*60)
        print("Search by: Doctor name, Specialization, or Location")
        print("-" * 60)
        
        query = input("\n🔍 Enter search query: ").strip()
        
        if not query:
            print("❌ Please enter a search query")
            continue
        
        if query.lower() == "back":
            return
        
        print("\n🔍 Searching...")
        
        r = requests.get(f"{API}/healthcare/search?q={query}")
        
        if r.status_code != 200:
            print("❌ Error:", r.json().get("error", "Search failed"))
            continue
        
        doctors = r.json().get("doctors", [])
        
        if not doctors:
            print(f"\n❌ No doctors found matching '{query}'")
            input("\nPress Enter to continue...")
            continue
        
        print(f"\n✅ Found {len(doctors)} doctor(s):")
        print("="*60)
        
        for idx, doc in enumerate(doctors, 1):
            print(f"\n[{idx}] Dr. {doc['full_name']}")
            print(f"   Specialization: {doc['specialization']}")
            print(f"   Experience: {doc['experience']} years")
            print(f"   Rating: {doc.get('rating', 0.0):.1f}/5.0")
            print(f"   Location: {doc.get('clinic_location', 'N/A')}")
            print(f"   ID: {doc['id']}")
        
        print("\n" + "="*60)
        print(f"{len(doctors) + 1}. 🔍 New Search")
        print(f"{len(doctors) + 2}. ⬅️  Back")
        
        choice = input("\nSelect doctor (or search/back): ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(doctors):
                show_doctor_actions(doctors[choice_num - 1])
            elif choice_num == len(doctors) + 1:
                continue  # New search
            elif choice_num == len(doctors) + 2:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def book_appointment_user(doctor_id=None):
    """Book an appointment with a doctor"""
    global USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    if not USER_ID:
        # Try to get user_id from API
        r = requests.get(f"{API}/user/info", headers={"Authorization": f"Bearer {TOKEN}"})
        if r.status_code == 200:
            USER_ID = r.json().get("user_id")
        else:
            print("❌ Could not get user information. Please login again.")
            return
    
    print("\n" + "="*60)
    print("📅 BOOK APPOINTMENT")
    print("="*60)
    
    if doctor_id:
        worker_id = str(doctor_id)
        print(f"Doctor ID: {worker_id}")
    else:
        worker_id = input("Doctor ID: ").strip()
    
    user_name = input("Your Name: ").strip()
    symptoms = input("Symptoms/Reason: ").strip()
    date = input("Preferred Date (YYYY-MM-DD): ").strip()

    print("\nAppointment Type:")
    print("1. Clinic Visit")
    print("2. Video / Audio Consultation")
    apt_type_choice = input("Choose type (1/2): ").strip()
    if apt_type_choice == "2":
        appointment_type = "video"
    else:
        appointment_type = "clinic"
    
    if not all([worker_id, user_name, symptoms, date]):
        print("❌ All fields are required")
        input("\nPress Enter to continue...")
        return
    
    r = requests.post(f"{API}/book-appointment", json={
        "user_id": int(USER_ID),
        "worker_id": int(worker_id),
        "user_name": user_name,
        "symptoms": symptoms,
        "date": date,
        "appointment_type": appointment_type
    })
    
    if r.status_code == 201:
        data = r.json()
        print("\n✅ Appointment requested successfully!")
        print(f"📋 Appointment ID: {data['id']}")
        if appointment_type == "video":
            print("📹 Type: Video / Audio Consultation")
        else:
            print("🏥 Type: Clinic Visit")
        print("⏳ Waiting for doctor's approval...")
    else:
        print("❌ Error:", r.json().get("error", "Failed to book appointment"))
    
    input("\nPress Enter to continue...")


def healthcare_appointments_tab():
    """Healthcare Appointments Tab - View and manage appointments"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*60)
        print("📅 APPOINTMENTS")
        print("="*60)
        
        r = requests.get(f"{API}/user/appointments", headers={"Authorization": f"Bearer {TOKEN}"})
        
        if r.status_code != 200:
            print("❌ Error:", r.json().get("error", "Failed to fetch appointments"))
            input("\nPress Enter to continue...")
            return
        
        appointments = r.json().get("appointments", [])
        
        if not appointments:
            print("\n📭 No appointments found")
            print("\n1. ⬅️  Back")
            choice = input("\nChoice: ").strip()
            if choice == "1":
                return
            continue
        
        print("\n📋 Your Appointments:")
        print("-" * 60)
        
        for idx, apt in enumerate(appointments, 1):
            status_icon = {
                "pending": "⏳",
                "accepted": "✅",
                "rejected": "❌",
                "payment_pending": "💰",
                "confirmed": "✅",
                "in_consultation": "💬",
                "completed": "✓",
                "cancelled": "🚫"
            }.get(apt["status"], "❓")
            apt_type = apt.get("appointment_type", "clinic")
            type_label = "VIDEO" if apt_type == "video" else "CLINIC"
            
            # Show payment status if available
            payment_info = ""
            if apt.get('payment_status'):
                payment_status = apt['payment_status'].upper()
                if payment_status == 'PENDING':
                    payment_info = f" 💳 PAYMENT PENDING"
                elif payment_status == 'PAID':
                    payment_info = f" ✅ PAID"
            
            print(f"\n[{idx}] {status_icon} {apt['status'].upper()} ({type_label}){payment_info}")
            print(f"    Appointment ID: {apt['id']}")
            print(f"    Doctor ID: {apt['worker_id']}")
            print(f"    Symptoms: {apt['patient_symptoms']}")
            print(f"    Date: {apt['booking_date']}")
            if apt.get('payment_status'):
                print(f"    💰 Payment Status: {apt['payment_status'].upper()}")
            print("-" * 60)
        
        print(f"\n{len(appointments) + 1}. View Appointment Details")
        print(f"{len(appointments) + 2}. Cancel Appointment")
        print(f"{len(appointments) + 3}. 🔐 Join Video Call (Enter OTP)")
        print(f"{len(appointments) + 4}. View Messages")
        print(f"{len(appointments) + 5}. 💳 Make Payment")
        print(f"{len(appointments) + 6}. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(appointments):
                apt = appointments[choice_num - 1]
                view_appointment_detail_user(apt['id'])
            elif choice_num == len(appointments) + 1:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    view_appointment_detail_user(apt_id)
            elif choice_num == len(appointments) + 2:
                apt_id = input("Enter Appointment ID to cancel: ").strip()
                if apt_id:
                    cancel_appointment_user(apt_id)
            elif choice_num == len(appointments) + 3:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    join_video_call(apt_id)
            elif choice_num == len(appointments) + 4:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    view_messages_user(apt_id)
            elif choice_num == len(appointments) + 5:
                # Quick payment option
                apt_id = input("Enter Appointment ID for payment: ").strip()
                if apt_id:
                    make_payment_for_appointment(apt_id)
            elif choice_num == len(appointments) + 6:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def join_video_call(appointment_id):
    """User joins video consultation using OTP"""

    global TOKEN

    print("\n🔐 Enter OTP from email to join call")
    otp = input("OTP: ").strip()

    r = requests.post(
        f"{API}/appointment/video/join",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "appointment_id": int(appointment_id),
            "otp": otp
        }
    )

    if r.status_code != 200:
        print("\n❌", r.json().get("error", "Cannot join call"))
        input("\nPress Enter...")
        return

    print("\n🎉 JOINED VIDEO CONSULTATION")
    print("👨‍⚕️ Doctor is in the call")
    print("💬 Video session ACTIVE (simulated)")
    input("\nPress Enter to leave call...")

def healthcare_profile_tab():
    """Healthcare Profile Tab - User details and appointment history"""
    global TOKEN, USER_ID
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*60)
        print("👤 PROFILE")
        print("="*60)
        
        # Get user info
        r = requests.get(f"{API}/user/info", headers={"Authorization": f"Bearer {TOKEN}"})
        if r.status_code == 200:
            user_info = r.json()
            print(f"\n🆔 User ID: {user_info.get('user_id', 'N/A')}")
        
        # Get appointment history
        r = requests.get(f"{API}/user/appointments", headers={"Authorization": f"Bearer {TOKEN}"})
        if r.status_code == 200:
            appointments = r.json().get("appointments", [])
            
            print(f"\n📊 Appointment Statistics:")
            print("-" * 60)
            status_counts = {}
            for apt in appointments:
                status = apt['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"  {status.upper()}: {count}")
            
            print(f"\n📋 Total Appointments: {len(appointments)}")
        
        print("\n" + "="*60)
        print("1. View Full Appointment History")
        print("2. 👋 Logout")
        print("3. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_full_appointment_history()
        elif choice == "2":
            TOKEN = None
            USER_ID = None
            print("👋 Logged out")
            return
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")


def view_full_appointment_history():
    """View complete appointment history"""
    global TOKEN
    
    r = requests.get(f"{API}/user/appointments", headers={"Authorization": f"Bearer {TOKEN}"})
    if r.status_code != 200:
        print("❌ Error fetching appointments")
        input("\nPress Enter to continue...")
        return
    
    appointments = r.json().get("appointments", [])
    
    if not appointments:
        print("\n📭 No appointment history")
        input("\nPress Enter to continue...")
        return
    
    print("\n" + "="*70)
    print("📋 COMPLETE APPOINTMENT HISTORY")
    print("="*70)
    
    for apt in appointments:
        status_icon = {
            "pending": "⏳",
            "accepted": "✅",
            "rejected": "❌",
            "in_consultation": "💬",
            "completed": "✓",
            "cancelled": "🚫"
        }.get(apt["status"], "❓")
        
        print(f"\n{status_icon} Appointment #{apt['id']} - {apt['status'].upper()}")
        print(f"   Doctor ID: {apt['worker_id']}")
        print(f"   Symptoms: {apt['patient_symptoms']}")
        print(f"   Booking Date: {apt['booking_date']}")
        print(f"   Created: {apt.get('created_at', 'N/A')}")
        print("-" * 70)
    
    input("\nPress Enter to continue...")


def view_user_appointments():
    """Legacy function - redirects to healthcare appointments tab"""
    healthcare_appointments_tab()


def view_appointment_detail_user(appointment_id=None):
    """View detailed information about a specific appointment"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/appointment/{appointment_id}?sender_role=user", 
                     headers={"Authorization": f"Bearer {TOKEN}"})
    
    if r.status_code == 200:
        apt = r.json()
        print("\n" + "="*60)
        print("📄 APPOINTMENT DETAILS")
        print("="*60)
        print(f"ID: {apt['id']}")
        print(f"Status: {apt['status']}")
        
        # Show payment status if available
        if apt.get('payment_status'):
            payment_status = apt['payment_status'].upper()
            if payment_status == 'PENDING':
                print(f"💰 Payment Status: {payment_status} - PAYMENT REQUIRED")
            elif payment_status == 'PAID':
                print(f"💰 Payment Status: {payment_status} - ✅ PAID")
            else:
                print(f"💰 Payment Status: {payment_status}")
        
        print(f"Doctor ID: {apt['worker_id']}")
        print(f"Patient: {apt['user_name']}")
        print(f"Symptoms: {apt['patient_symptoms']}")
        print(f"Booking Date: {apt['booking_date']}")
        print(f"Created: {apt['created_at']}")
        
        # Show payment options if payment is pending
        if apt.get('payment_status') == 'pending' and apt.get('status') in ['accepted', 'payment_pending']:
            print("\n" + "="*60)
            print("💳 PAYMENT OPTIONS")
            print("="*60)
            print("1. 💳 Make Payment")
            print("2. 📋 View Payment Details")
            print("3. ⬅️ Back")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                make_payment_for_appointment(apt['id'])
            elif choice == "2":
                view_payment_details(apt['id'])
        
        print("="*60)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointment"))
    
    input("\nPress Enter to continue...")


def make_payment_for_appointment(appointment_id):
    """Process payment for an appointment"""
    print("\n💳 INITIATING PAYMENT")
    print("="*60)
    
    try:
        # Create payment order
        r = requests.post(f"{API}/api/payment/create-order", 
                        json={"appointment_id": appointment_id},
                        headers={"Authorization": f"Bearer {TOKEN}"})
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Payment order created!")
            print(f"📋 Order ID: {data['order_id']}")
            print(f"💰 Amount: ₹{data['amount']}")
            
            if data.get('pricing_breakdown'):
                breakdown = data['pricing_breakdown']
                print(f"\n📊 PRICE BREAKDOWN:")
                print(f"   Doctor Fee: ₹{breakdown['doctor_fee']}")
                print(f"   Platform Fee: ₹{breakdown['platform_fee']}")
                print(f"   Total Amount: ₹{breakdown['total_amount']}")
            
            print(f"\n🌐 Opening payment gateway...")
            print(f"📱 Please complete payment in browser")
            print(f"🔗 Payment URL: https://razorpay.com/pay/{data['order_id']}")
            
            # Simulate payment completion (in real app, this would be handled by webhook)
            confirm = input(f"\n✅ Payment completed? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', 'Y', 'YES']:
                # For testing, simulate payment confirmation
                payment_id = f"pay_test_{appointment_id}_{int(time.time())}"
                
                r_confirm = requests.post(f"{API}/api/payment/confirm",
                                     json={
                                         "appointment_id": appointment_id,
                                         "razorpay_payment_id": payment_id
                                     },
                                     headers={"Authorization": f"Bearer {TOKEN}"})
                
                if r_confirm.status_code == 200:
                    print("✅ Payment confirmed successfully!")
                    print("📅 Appointment confirmed!")
                    
                    if r_confirm.json().get('video_details'):
                        video = r_confirm.json()['video_details']
                        print(f"\n🎥 VIDEO CONSULTATION DETAILS:")
                        print(f"🔗 Patient URL: {video['patient_url']}")
                        print(f"🔐 OTP: {video['otp']}")
                else:
                    print("❌ Payment confirmation failed")
            else:
                print("❌ Payment cancelled")
        else:
            print("❌ Failed to create payment order")
            print("Error:", r.json().get("error", "Unknown error"))
            
    except Exception as e:
        print(f"❌ Payment error: {e}")
    
    input("\nPress Enter to continue...")


def view_payment_details(appointment_id):
    """View payment details for an appointment"""
    print("\n📋 PAYMENT DETAILS")
    print("="*60)
    
    try:
        r = requests.get(f"{API}/api/payment/status/{appointment_id}",
                       headers={"Authorization": f"Bearer {TOKEN}"})
        
        if r.status_code == 200:
            data = r.json()
            print(f"Appointment ID: {appointment_id}")
            print(f"Payment Status: {data.get('payment_status', 'Unknown')}")
            print(f"Payment Amount: ₹{data.get('payment_amount', 'N/A')}")
            print(f"Razorpay Order ID: {data.get('razorpay_order_id', 'N/A')}")
            print(f"Razorpay Payment ID: {data.get('razorpay_payment_id', 'N/A')}")
            print(f"Payout Status: {data.get('payout_status', 'N/A')}")
        else:
            print("❌ Failed to fetch payment details")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")


def view_messages_user():
    """View messages in an appointment chat"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/messages/{apt_id}?sender_role=user",
                     headers={"Authorization": f"Bearer {TOKEN}"})
    
    if r.status_code == 200:
        data = r.json()
        messages = data.get("messages", [])
        
        if not messages:
            print("\n📭 No messages yet")
            return
        
        print(f"\n💬 Messages for Appointment #{apt_id}:")
        print("-" * 80)
        for msg in messages:
            sender_label = "👤 You" if msg["sender_role"] == "user" else "👨‍⚕️ Doctor"
            print(f"{sender_label} ({msg['timestamp'][:19]}):")
            print(f"  {msg['message']}")
            print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch messages"))


def send_message_user():
    """Send a message in an appointment chat"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    apt_id = input("Appointment ID: ").strip()
    message = input("Message: ").strip()
    
    if not message:
        print("❌ Message cannot be empty")
        return
    
    r = requests.post(f"{API}/messages/send", json={
        "appointment_id": int(apt_id),
        "sender_role": "user",
        "message": message
    }, headers={"Authorization": f"Bearer {TOKEN}"})
    
    if r.status_code == 201:
        print("✅ Message sent successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to send message"))


def cancel_appointment_user(appointment_id=None):
    """Cancel an appointment"""
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    if appointment_id:
        apt_id = str(appointment_id).strip()
    else:
        apt_id = input("Appointment ID: ").strip()
    
    confirm = input("Are you sure you want to cancel? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Cancelled")
        return
    
    r = requests.post(f"{API}/appointment/cancel", json={
        "appointment_id": int(apt_id)
    })
    
    if r.status_code == 200:
        print("✅ Appointment cancelled successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to cancel appointment"))


def user_menu():
    while True:
        print("\n--- USER MENU ---")
        print("1. Signup")
        print("2. Login")
        print("3. Back")

        c = input("Choice: ").strip()

        if c == "1":
            user_signup()
        elif c == "2":
            user_login()
        elif c == "3":
            return


# ==================================================
# ================= WORKER FLOW ====================
# ==================================================

def healthcare_worker_signup():
    print("\n🩺 Healthcare Worker Signup")

    full_name = input("Full Name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    specialization = input("Specialization (Dentist, Eye Specialist, etc): ").strip()
    clinic_location = input("Clinic Location: ").strip()

    while True:
        exp = input("Experience (years - number only): ").strip()
        if exp.isdigit():
            experience = int(exp)
            break
        print("❌ Enter numbers only")

    r = requests.post(f"{API}/worker/healthcare/signup", json={
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "specialization": specialization,
        "experience": experience,
        "clinic_location": clinic_location
    })
    
    print(f"🔍 Status Code: {r.status_code}")
    print(f"🔍 Response: {r.text[:200]}...")  # Show first 200 chars of response

    if r.status_code == 201:
        data = r.json()
        print("\n✅ Worker registered successfully")
        print("🆔 Worker ID:", data["worker_id"])
        print("⏳ Status: Pending approval (2–3 hours)")
        print("📤 Documents will be uploaded via App/UI later")
    else:
        try:
            error_data = r.json()
            print("❌", error_data.get("error", "Registration failed"))
        except:
            print("❌ Registration failed. Server response:", r.text)


def worker_login():
    print("\n🔐 Worker Login (After Approval)")
    email = input("Email: ").strip()

    r = requests.post(f"{API}/worker/login", json={"email": email})

    if r.status_code == 200:
        data = r.json()
        print("\n✅ Login Successful")
        print("Service:", data["service"])
        print("Specialization:", data["specialization"])
        worker_id = data["worker_id"]
        worker_dashboard(worker_id)
    else:
        print("❌", r.json().get("error"))


def worker_dashboard(worker_id):
    """Worker Dashboard - redirects to full doctor menu"""
    # Redirect to full doctor menu with all tabs, not just dashboard tab
    worker_menu(worker_id)


def worker_service_selection():
    """Worker selects which service they belong to"""
    from auth.worker_auth import TOKEN, WORKER_ID
    
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    while True:
        print("\n" + "="*50)
        print("👷 SELECT WORKER SERVICE")
        print("="*50)
        print("1. 🏥 Healthcare")
        print("2. 🏠 Housekeeping")
        print("3. 🚗 Car Services")
        print("4. 📦 Resource Management")
        print("5. 💰 Money Management")
        print("6. ⬅️ Back")

        choice = input("\nSelect service: ").strip()

        if choice == "1":
            healthcare_worker_menu()
        elif choice == "2":
            print("🚧 Housekeeping worker module coming soon")
        elif choice == "3":
            car_service_worker_menu()
        elif choice == "4":
            print("🚧 Resource worker module coming soon")
        elif choice == "5":
            from services.money_service.money_service_cli import money_service_menu
            money_service_menu(WORKER_ID, "worker")
        elif choice == "6":
            return
        else:
            print("❌ Invalid choice")


def car_service_worker_menu():
    """Car service worker selection menu"""
    while True:
        print("\n" + "="*50)
        print("🚗 CAR SERVICE WORKER")
        print("="*50)
        print("1. 🔧 Mechanic")
        print("2. ⛽ Fuel Delivery Agent")
        print("3. 🚛 Tow Truck Operator")
        print("4. 🧠 Automobile Expert")
        print("5. 🚚 Truck Operator")
        print("6. ⬅️ Back")
        
        choice = input("\nSelect worker type: ").strip()
        
        if choice == "1":
            from car_service.unified_mechanic_cli import unified_mechanic_menu
            unified_mechanic_menu()
        elif choice == "2":
            from car_service.fuel_delivery_cli import fuel_delivery_agent_menu
            fuel_delivery_agent_menu()
        elif choice == "3":
            from car_service.worker_cli import tow_truck_operator_signup
            tow_truck_operator_signup()
        elif choice == "4":
            from car_service.automobile_expert_cli import automobile_expert_menu
            automobile_expert_menu()
        elif choice == "5":
            from car_service.truck_operator_cli import truck_operator_signup
            truck_operator_signup()
        elif choice == "6":
            return
        else:
            print("❌ Invalid choice")


def healthcare_worker_menu():
    print("\n🏥 Healthcare Worker Portal")

    while True:
        print("\n--- HEALTHCARE WORKER MENU ---")
        print("1. Healthcare Signup")
        print("2. Worker Login")
        print("3. Back")

        c = input("Choice: ").strip()

        if c == "1":
            healthcare_worker_signup()
        elif c == "2":
            worker_login()
        elif c == "3":
            return


def worker_menu(worker_id):
    """Doctor Dashboard - All tabs"""
    while True:
        print("\n" + "="*60)
        print("👨‍⚕️ DOCTOR DASHBOARD")
        print("="*60)
        print("1. 📊 Dashboard")
        print("2. 📅 Availability")
        print("3.  Consultations")
        print("4. 🎥 Video Consultation")
        print("5. 👤 Profile")
        print("6. 💳 Subscription")
        print("7. 🚪 Logout")

        c = input("\nSelect tab: ").strip()

        if c == "1":
            doctor_dashboard_tab(worker_id)

        elif c == "2":
            doctor_availability_tab(worker_id)

        elif c == "3":
            doctor_consultations_tab(worker_id)

        elif c == "4":
            video_menu_doctor(worker_id)

        elif c == "5":
            should_logout = doctor_profile_tab(worker_id)
            if should_logout:
                return

        elif c == "6":
            doctor_subscription_menu(worker_id)

        elif c == "7":
            print("👋 Logged out")
            return

        else:
            print("❌ Invalid choice")


def doctor_consultations_tab(worker_id):
    """Unified Consultations Module - All consultation lifecycle management"""
    while True:
        print("\n" + "="*60)
        print("📋 CONSULTATIONS")
        print("="*60)
        print("1. 🟡 Pending Requests")
        print("2. 🟢 Accepted / Upcoming")
        print("3. 📹 Video Consultations")
        print("4. ✅ Completed History")
        print("5. ⬅️ Back")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            doctor_pending_requests(worker_id)
        elif choice == "2":
            doctor_accepted_appointments(worker_id)
        elif choice == "3":
            doctor_video_consultations(worker_id)
        elif choice == "4":
            doctor_completed_history(worker_id)
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice")


def doctor_pending_requests(worker_id):
    """Show pending consultation requests and allow doctor to accept/reject"""
    print("\n🔄 Fetching pending requests...")
    
    try:
        r = requests.get(f"{API}/worker/{worker_id}/requests")
        if r.status_code != 200:
            print("❌ Failed to fetch requests")
            input("\nPress Enter to continue...")
            return
        
        pending_requests = r.json().get("requests", [])
        
        if not pending_requests:
            print("\n📭 No pending requests")
            input("\nPress Enter to continue...")
            return
        
        print("\n🟡 PENDING REQUESTS")
        print("-" * 60)
        
        for idx, req in enumerate(pending_requests, 1):
            print(f"\n[{idx}] Appointment ID: {req['id']}")
            print(f"    👤 Patient: {req['user_name']}")
            print(f"    📅 Date: {req.get('booking_date', 'N/A')}")
            print(f"    🩺 Symptoms: {req['patient_symptoms']}")
            print(f"    📝 Type: {req.get('appointment_type', 'clinic').upper()}")
        
        print("\n" + "-" * 60)
        choice = input("\nSelect request number to act on (0 to go back): ").strip()
        
        if choice == "0":
            return
        
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(pending_requests):
            print("❌ Invalid selection")
            input("\nPress Enter to continue...")
            return
        
        selected_request = pending_requests[int(choice) - 1]
        appointment_id = selected_request['id']
        
        print(f"\n📋 Request Details:")
        print(f"   Patient: {selected_request['user_name']}")
        print(f"   Symptoms: {selected_request['patient_symptoms']}")
        print(f"   Type: {selected_request.get('appointment_type', 'clinic').upper()}")
        
        print("\n🤔 Action:")
        print("1. ✅ Accept")
        print("2. ❌ Reject")
        print("0. ⬅️ Back")
        
        action = input("\nChoose action: ").strip()
        
        if action == "1":
            # Accept request
            try:
                r = requests.post(f"{API}/worker/respond", json={
                    "appointment_id": appointment_id,
                    "status": "accepted"
                })
                
                if r.status_code == 200:
                    data = r.json()
                    print("✅ Request accepted successfully!")
                    
                    # Handle new payment flow
                    if data.get('payment_required'):
                        print(f"\n💰 PAYMENT REQUIRED")
                        print(f"📋 Consultation Fee: ₹{data.get('doctor_fee', 'N/A')}")
                        print(f"💳 Patient needs to pay before consultation")
                        print(f"📱 Patient will receive payment prompt")
                        
                        if selected_request.get('appointment_type') == 'video':
                            print(f"\n🎥 Video consultation details will be sent after payment")
                        else:
                            print(f"\n🏥 Clinic appointment confirmed after payment")
                    
                    # Handle old flow for backward compatibility or video details after payment
                    elif selected_request.get('appointment_type') == 'video':
                        if data.get('success') and data.get('otp'):
                            print(f"\n🎥 VIDEO CONSULTATION DETAILS:")
                            print(f"🔐 Doctor OTP: {data.get('otp')}")
                            print(f"🔗 Doctor URL: {data.get('doctor_url')}")
                            print(f"🔗 Patient URL: {data.get('patient_url')}")
                            print(f"\n📧 Share the Patient URL with the patient")
                            print(f"🔐 Use the OTP to start the video call")
                        elif data.get('meeting_link'):
                            print(f"🔗 Meeting Link: {data['meeting_link']}")
                        if data.get('otp_sent'):
                            print("📧 OTP sent to your email")
                    else:
                        print(f"\n📅 Appointment accepted successfully!")
                        
                else:
                    print("❌ Failed to accept request")
                    if r.status_code != 500:
                        error_data = r.json()
                        print("Server says:", error_data.get("error", "Unknown error"))
                        
            except Exception as e:
                print(f"❌ Network error: {e}")
                
        elif action == "2":
            # Reject request
            try:
                r = requests.post(f"{API}/worker/respond", json={
                    "appointment_id": appointment_id,
                    "status": "rejected"
                })
                
                if r.status_code == 200:
                    print("✅ Request rejected successfully!")
                else:
                    print(f"❌ Failed to reject: {r.json().get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Network error: {e}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error fetching requests: {e}")
        input("\nPress Enter to continue...")


def doctor_accepted_appointments(worker_id):
    """Show accepted/upcoming appointments"""
    print("\n🔄 Fetching accepted appointments...")
    
    try:
        r = requests.get(f"{API}/worker/{worker_id}/appointments")
        if r.status_code != 200:
            print("❌ Failed to fetch appointments")
            input("\nPress Enter to continue...")
            return
        
        appointments = r.json().get("appointments", [])
        
        # Filter only accepted appointments
        accepted = [apt for apt in appointments if apt.get('status') == 'accepted']
        
        if not accepted:
            print("\n📭 No accepted appointments")
            input("\nPress Enter to continue...")
            return
        
        print("\n🟢 ACCEPTED / UPCOMING")
        print("-" * 60)
        
        for idx, apt in enumerate(accepted, 1):
            print(f"\n[{idx}] Appointment ID: {apt['id']}")
            print(f"    📅 Date: {apt.get('booking_date', 'N/A')}")
            print(f"    ⏰ Time: {apt.get('time_slot', 'N/A')}")
            print(f"    👤 Patient: {apt['user_name']}")
            print(f"    📝 Type: {apt.get('appointment_type', 'clinic').upper()}")
            
            # Show video consultation option
            if apt.get('appointment_type') == 'video':
                print("    📹 Video Consultation")
        
        print("\n" + "-" * 60)
        choice = input("\nSelect appointment number for details (0 to go back): ").strip()
        
        if choice == "0":
            return
        
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(accepted):
            print("❌ Invalid selection")
            input("\nPress Enter to continue...")
            return
        
        selected_apt = accepted[int(choice) - 1]
        
        print(f"\n📋 Appointment Details:")
        print(f"   Patient: {selected_apt['user_name']}")
        print(f"   Date: {selected_apt.get('booking_date', 'N/A')}")
        print(f"   Time: {selected_apt.get('time_slot', 'N/A')}")
        print(f"   Type: {selected_apt.get('appointment_type', 'clinic').upper()}")
        print(f"   Status: {selected_apt.get('status', 'N/A')}")
        
        if selected_apt.get('appointment_type') == 'video':
            print("\n📹 Video Consultation Options:")
            print("1. 🎥 Start Video Consultation")
            print("0. ⬅️ Back")
            
            video_choice = input("\nChoose option: ").strip()
            if video_choice == "1":
                doctor_start_video_consultation(selected_apt['id'])
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error fetching appointments: {e}")
        input("\nPress Enter to continue...")


def doctor_video_consultations(worker_id):
    """Show video consultations"""
    print("\n🔄 Fetching video consultations...")
    
    try:
        r = requests.get(f"{API}/worker/video_appointments")
        if r.status_code != 200:
            print("❌ Failed to fetch video consultations")
            input("\nPress Enter to continue...")
            return
        
        video_consults = r.json()
        
        if not video_consults:
            print("\n📭 No video consultations")
            input("\nPress Enter to continue...")
            return
        
        print("\n📹 VIDEO CONSULTATIONS")
        print("-" * 60)
        
        for idx, consult in enumerate(video_consults, 1):
            print(f"\n[{idx}] Consult ID: {consult['id']}")
            print(f"    📋 Appointment ID: {consult['id']}")
            print(f"    👤 User Name: {consult['user_name']}")
            print(f"    📊 Status: {consult['status']}")
        
        print("\n" + "-" * 60)
        choice = input("\nSelect consultation number for actions (0 to go back): ").strip()
        
        if choice == "0":
            return
        
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(video_consults):
            print("❌ Invalid selection")
            input("\nPress Enter to continue...")
            return
        
        selected_consult = video_consults[int(choice) - 1]
        
        print(f"\n📋 Video Consultation Details:")
        print(f"   User: {selected_consult['user_name']}")
        print(f"   Status: {selected_consult['status']}")
        
        if selected_consult.get('status') == 'accepted':
            print("\n🎥 Video Options:")
            print("1. 🎥 Start Video Call")
            print("0. ⬅️ Back")
            
            video_choice = input("\nChoose option: ").strip()
            if video_choice == "1":
                doctor_start_video_consultation(selected_consult['id'])
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error fetching video consultations: {e}")
        input("\nPress Enter to continue...")


def doctor_completed_history(worker_id):
    """Show completed consultation history"""
    print("\n🔄 Fetching completed history...")
    
    try:
        r = requests.get(f"{API}/worker/{worker_id}/history")
        if r.status_code != 200:
            print("❌ Failed to fetch history")
            input("\nPress Enter to continue...")
            return
        
        history = r.json().get("history", [])
        
        if not history:
            print("\n📭 No completed consultations")
            input("\nPress Enter to continue...")
            return
        
        print("\n✅ COMPLETED HISTORY")
        print("-" * 60)
        
        for idx, consult in enumerate(history, 1):
            print(f"\n[{idx}] Consultation ID: {consult['id']}")
            print(f"    👤 Patient: {consult['user_name']}")
            print(f"    📅 Date: {consult.get('booking_date', 'N/A')}")
            print(f"    📝 Type: {consult.get('appointment_type', 'clinic').upper()}")
            print(f"    ✅ Completed: {consult.get('completed_date', 'N/A')}")
        
        print("\n" + "-" * 60)
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        input("\nPress Enter to continue...")


def request_video_consultation(worker_id):
    """Request video consultation with a doctor"""
    global USER_ID, TOKEN
    
    if not TOKEN:
        print("⚠️ Please login first")
        return
    
    if not USER_ID:
        print("⚠️ User ID not found")
        return
    
    print("\n" + "="*60)
    print("📹 REQUEST VIDEO CONSULTATION")
    print("="*60)
    
    symptoms = input("🩺 Describe your symptoms: ").strip()
    if not symptoms:
        print("❌ Symptoms are required")
        input("\nPress Enter to continue...")
        return
    
    print("\n🔄 Requesting video consultation...")
    
    try:
        r = requests.post(f"{API}/appointment/video-request", json={
            "user_id": int(USER_ID),
            "worker_id": int(worker_id),
            "user_name": f"User_{USER_ID}",
            "symptoms": symptoms
        }, headers={"Authorization": f"Bearer {TOKEN}"})
        
        if r.status_code == 201:
            data = r.json()
            appointment_id = data.get("appointment_id")
            print(f"✅ Video consultation requested successfully!")
            print(f"📋 Appointment ID: {appointment_id}")
            print("⏳ Waiting for doctor to accept...")
            
            # Generate video call URL for patient
            video_url = f"http://127.0.0.1:5000/video-call/{appointment_id}?role=user"
            print(f"🔗 Join Call URL: {video_url}")
            print("📧 Please save this URL to join when doctor accepts")
            
        else:
            error = r.json().get("error", "Unknown error")
            print(f"❌ Failed to request video consultation: {error}")
            
    except Exception as e:
        print(f"❌ Network error: {e}")
    
    input("\nPress Enter to continue...")


def doctor_start_video_consultation(appointment_id):
    """Start video consultation for given appointment"""
    print(f"\n🎥 Starting video consultation for appointment {appointment_id}")
    
    # Generate video call URL
    video_url = f"http://127.0.0.1:5000/video-call/{appointment_id}?role=doctor"
    
    print(f"🔗 Video Call URL: {video_url}")
    print("📧 Opening video call page in your browser...")
    print("🌐 Please open the URL above to start the consultation")
    
    # Try to open browser automatically (optional)
    try:
        import webbrowser
        webbrowser.open(video_url)
        print("✅ Browser opened automatically")
    except:
        print("⚠️ Could not open browser automatically")
        print(f"💻 Please manually copy and paste: {video_url}")
    
    input("\nPress Enter to continue...")


def doctor_subscription_menu(worker_id):
    """Handle doctor subscription management"""
    while True:
        print("\n" + "="*60)
        print("💳 SUBSCRIPTION MANAGEMENT")
        print("="*60)
        
        # Get current subscription
        r = requests.get(f"{API}/api/subscription/current?worker_id={worker_id}")
        if r.status_code == 200:
            data = r.json()
            subscription = data.get("subscription")
            
            if subscription:
                print(f"\n📋 Current Plan: {subscription['plan_name']}")
                print(f"📅 End Date: {subscription['end_date'][:10] if subscription['end_date'] else 'N/A'}")
                print(f"📝 Features: Basic appointment scheduling, Profile management")
                
                # Get stats
                r_stats = requests.get(f"{API}/api/subscription/stats/{worker_id}")
                if r_stats.status_code == 200:
                    stats = r_stats.json().get("stats")
                    if stats:
                        print(f"📊 Today's Usage: {stats['today_usage']}/{stats['daily_limit']}")
                        print(f"🔄 Remaining Today: {stats['remaining_today']}")
            else:
                print("\n❌ No active subscription")
                print("🔒 Limited features available")
        
        print("\n" + "-"*40)
        print("1. 📋 View Available Plans")
        print("2. 💳 Subscribe to Plan")
        print("3. 📊 View Usage Stats")
        print("4. ❌ Cancel Subscription")
        print("5. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_subscription_plans()
        elif choice == "2":
            subscribe_to_plan(worker_id)
        elif choice == "3":
            view_subscription_stats(worker_id)
        elif choice == "4":
            cancel_subscription(worker_id)
        elif choice == "5":
            break
        else:
            print("❌ Invalid choice")
            input("\nPress Enter to continue...")

def view_subscription_plans():
    """View available subscription plans"""
    r = requests.get(f"{API}/api/subscription/plans")
    if r.status_code == 200:
        data = r.json()
        plans = data.get("plans", [])
        
        print("\n" + "="*60)
        print("📋 AVAILABLE SUBSCRIPTION PLANS")
        print("="*60)
        
        for i, plan in enumerate(plans, 1):
            print(f"\n[{i}] {plan['name']} Plan")
            print(f"💰 Price: ₹{plan['price']}/month")
            print(f"📅 Duration: {plan['duration_days']} days")
            print(f"📊 Max Appointments/Day: {plan['daily_appointment_limit']}")
            print("-" * 40)
    else:
        print("❌ Error fetching plans")
    
    input("\nPress Enter to continue...")

def subscribe_to_plan(worker_id):
    """Subscribe to a plan"""
    # Show available plans
    r = requests.get(f"{API}/api/subscription/plans")
    if r.status_code != 200:
        print("❌ Error fetching plans")
        return
    
    data = r.json()
    plans = data.get("plans", [])
    if not plans:
        print("❌ No plans available")
        return
    
    print("\n" + "="*60)
    print("💳 CHOOSE SUBSCRIPTION PLAN")
    print("="*60)
    
    for i, plan in enumerate(plans, 1):
        print(f"[{i}] {plan['name']} - ₹{plan['price']}/month ({plan['daily_appointment_limit']}/day)")
    
    try:
        choice = int(input("\nSelect plan number: "))
        if choice < 1 or choice > len(plans):
            print("❌ Invalid plan selection")
            return
        
        selected_plan = plans[choice - 1]
        
        print(f"\n📋 Selected: {selected_plan['name']} Plan")
        print(f"💰 Price: ₹{selected_plan['price']}/month")
        print(f"📊 Limit: {selected_plan['daily_appointment_limit']} appointments/day")
        print(f"💰 Price: ${selected_plan['price']}/month")
        
        if selected_plan['price'] > 0:
            print("🔒 Payment integration required")
            print("💳 For demo, we'll simulate payment...")
            payment_id = f"PAY_{random.randint(100000, 999999)}"
        else:
            payment_id = "FREE_PLAN"
        
        confirm = input(f"\nConfirm subscription to {selected_plan['name']}? (y/n): ").lower()
        if confirm == 'y':
            # Create subscription order first
            r_order = requests.post(f"{API}/api/subscription/create-order", json={
                "worker_id": worker_id,
                "plan_id": selected_plan['id']
            })
            
            if r_order.status_code == 201:
                order_data = r_order.json()
                order = order_data.get("order", {})
                
                print(f"\n💳 Payment order created!")
                print(f"📋 Order ID: {order.get('order_id')}")
                print(f"💰 Amount: ₹{order.get('amount')}")
                
                # Simulate payment confirmation
                if selected_plan['price'] > 0:
                    print(f"\n💳 INITIATING PAYMENT")
                    print("="*60)
                    print(f"📋 Order ID: {order.get('order_id')}")
                    print(f"💰 Amount: ₹{order.get('amount')}")
                    print(f"🔑 Razorpay Key: {order.get('key')}")
                    
                    # Use your existing payment system
                    payment_url = f"{API}/create-order"
                    
                    print(f"\n🌐 Using your payment system...")
                    print(f"🔗 Payment API: {payment_url}")
                    
                    # Create payment using your existing system
                    try:
                        payment_data = {
                            "amount": int(order.get('amount') * 100),  # Convert to paise
                            "booking_id": f"subscription_{worker_id}_{order.get('order_id')}"
                        }
                        
                        r_payment = requests.post(payment_url, json=payment_data)
                        
                        if r_payment.status_code == 200:
                            payment_response = r_payment.json()
                            print("✅ Payment order created successfully!")
                            print(f"   Payment Order ID: {payment_response.get('order_id')}")
                            print(f"   Amount: ₹{payment_response.get('amount')}")
                            print(f"   Key: {payment_response.get('key')}")
                            
                            # Build frontend payment URL (using your existing frontend)
                            frontend_url = f"http://127.0.0.1:5001/payment?order_id={payment_response.get('order_id')}&amount={payment_response.get('amount')}&key={payment_response.get('key')}"
                            
                            print(f"\n🌐 Opening payment page...")
                            print(f"🔗 Payment URL: {frontend_url}")
                            
                            # Open browser for payment (using your frontend)
                            try:
                                import webbrowser
                                webbrowser.open(frontend_url)
                                print("📱 Payment page opened in browser")
                            except:
                                print("⚠️ Could not open browser automatically")
                                print(f"📱 Please visit: {frontend_url}")
                            
                            print("\n💡 Instructions:")
                            print("1. Complete payment on your payment page")
                            print("2. After payment, enter 'y' to confirm")
                            print("3. Or enter 'n' to cancel")
                            
                            payment_confirmed = input("\n✅ Payment completed? (y/n): ").lower().strip()
                            
                            if payment_confirmed in ['y', 'yes', 'Y', 'YES']:
                                # Get payment ID from user (in real implementation, this would come from webhook)
                                payment_id = input("💳 Enter Payment ID (or press Enter for demo): ").strip()
                                if not payment_id:
                                    payment_id = f"PAY_{random.randint(100000, 999999)}"
                                
                                # Confirm payment
                                r_confirm = requests.post(f"{API}/api/subscription/confirm", json={
                                    "worker_id": worker_id,
                                    "order_id": order.get('order_id'),
                                    "payment_id": payment_id
                                })
                                
                                if r_confirm.status_code == 200:
                                    confirm_data = r_confirm.json()
                                    print("✅ Subscription created successfully!")
                                    print(f"📋 Plan: {selected_plan['name']}")
                                    print(f"💳 Payment ID: {payment_id}")
                                    print(f"🎉 {confirm_data.get('message', 'Subscription activated!')}")
                                else:
                                    print("❌ Payment confirmation failed")
                                    print(r_confirm.json().get("error", "Unknown error"))
                            else:
                                print("❌ Payment cancelled")
                        else:
                            print("❌ Failed to create payment order")
                            print(r_payment.json())
                            
                    except Exception as e:
                        print(f"❌ Payment system error: {e}")
                        print("🔄 Falling back to demo mode...")
                        payment_id = f"PAY_{random.randint(100000, 999999)}"
                        
                        # Confirm payment
                        r_confirm = requests.post(f"{API}/api/subscription/confirm", json={
                            "worker_id": worker_id,
                            "order_id": order.get('order_id'),
                            "payment_id": payment_id
                        })
                        
                        if r_confirm.status_code == 200:
                            confirm_data = r_confirm.json()
                            print("✅ Subscription created successfully! (Demo Mode)")
                            print(f"📋 Plan: {selected_plan['name']}")
                            print(f"💳 Payment ID: {payment_id}")
                            print(f"🎉 {confirm_data.get('message', 'Subscription activated!')}")
                        else:
                            print("❌ Payment confirmation failed")
                            print(r_confirm.json().get("error", "Unknown error"))
                else:
                    print("✅ Free plan activated!")
                    print(f"📋 Plan: {selected_plan['name']}")
            else:
                print("❌ Error creating subscription order")
                print(r_order.json().get("error", "Unknown error"))
        else:
            print("❌ Subscription cancelled")
            
    except ValueError:
        print("❌ Invalid input")
    
    input("\nPress Enter to continue...")

def view_subscription_stats(worker_id):
    """View subscription usage statistics"""
    r = requests.get(f"{API}/api/subscription/stats/{worker_id}")
    if r.status_code == 200:
        data = r.json()
        stats = data.get("stats")
        
        if stats:
            print("\n" + "="*60)
            print("📊 SUBSCRIPTION STATISTICS")
            print("="*60)
            print(f"📋 Current Plan: {stats['plan_name']}")
            print(f"📅 End Date: {stats['end_date'][:10] if stats['end_date'] else 'N/A'}")
            print(f"📊 Daily Limit: {stats['daily_limit']}")
            print(f"📈 Today's Usage: {stats['today_usage']}")
            print(f"🔄 Remaining Today: {stats['remaining_today']}")
            
            # Calculate days remaining
            if stats['end_date']:
                from datetime import datetime
                end_date = datetime.fromisoformat(stats['end_date'])
                days_remaining = (end_date - datetime.now()).days
                print(f"⏰ Days Remaining: {days_remaining}")
        else:
            print("\n❌ No active subscription")
    else:
        print("❌ Error fetching statistics")
    
    input("\nPress Enter to continue...")

def cancel_subscription(worker_id):
    """Cancel current subscription"""
    # Check if user has active subscription
    r = requests.get(f"{API}/api/subscription/current?worker_id={worker_id}")
    if r.status_code == 200:
        data = r.json()
        if not data.get("subscription"):
            print("❌ No active subscription to cancel")
            input("\nPress Enter to continue...")
            return
    
    confirm = input("\n⚠️ Are you sure you want to cancel your subscription? (y/n): ").lower()
    if confirm == 'y':
        r = requests.post(f"{API}/api/subscription/cancel/{worker_id}")
        if r.status_code == 200:
            print("✅ Subscription cancelled successfully")
            print("📅 You can continue using features until the end of your billing period")
        else:
            print("❌ Error cancelling subscription")
    else:
        print("❌ Cancellation cancelled")
    
    input("\nPress Enter to continue...")


def doctor_dashboard_tab(worker_id):
    """Dashboard Tab - Shows today's appointments, pending requests, and status"""
    while True:
        print("\n" + "="*60)
        print("📊 DASHBOARD")
        print("="*60)
        
        # Get dashboard stats
        r = requests.get(f"{API}/worker/{worker_id}/dashboard/stats")
        if r.status_code == 200:
            stats = r.json()
            print(f"\n📥 Pending Requests: {stats.get('pending_requests', 0)}")
            print(f"📅 Today's Appointments: {stats.get('today_appointments', 0)}")
            print(f"✅ Accepted Appointments: {stats.get('accepted_appointments', 0)}")
            print(f"📊 Total Appointments: {stats.get('total_appointments', 0)}")
        else:
            print("❌ Error fetching dashboard stats")
        
        # Get worker status
        r = requests.get(f"{API}/worker/{worker_id}/status")
        if r.status_code == 200:
            status_data = r.json()
            status = status_data.get('status', 'online')
            status_icon = "🟢" if status == "online" else "🔴"
            print(f"\n{status_icon} Status: {status.upper()}")
        
        # Show today's appointments
        r = requests.get(f"{API}/worker/{worker_id}/dashboard/stats")
        if r.status_code == 200:
            stats = r.json()
            today_list = stats.get('today_appointments_list', [])
            if today_list:
                print("\n📅 Today's Appointments:")
                print("-" * 60)
                for apt in today_list:
                    status_icon = {
                        "pending": "⏳",
                        "accepted": "✅",
                        "in_consultation": "💬",
                        "completed": "✓"
                    }.get(apt['status'], "❓")
                    print(f"{status_icon} Appointment #{apt['id']} - {apt['user_name']}")
                    print(f"   Time: {apt['booking_date']}")
                    print(f"   Symptoms: {apt['patient_symptoms'][:50]}...")
                    print("-" * 60)
        
        print("\n" + "="*60)
        print("1. 🔄 Refresh")
        print("2. ⚙️  Change Status")
        print("3. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            continue  # Refresh
        elif choice == "2":
            change_worker_status(worker_id)
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice")


def change_worker_status(worker_id):
    """Change worker online/offline status"""
    print("\n" + "="*60)
    print("⚙️ CHANGE STATUS")
    print("="*60)
    print("1. 🟢 Online")
    print("2. 🔴 Offline")
    print("3. ⬅️  Back")
    
    choice = input("\nSelect status: ").strip()
    
    if choice == "1":
        status = "online"
    elif choice == "2":
        status = "offline"
    elif choice == "3":
        return
    else:
        print("❌ Invalid choice")
        return
    
    r = requests.post(f"{API}/worker/{worker_id}/status", json={"status": status})
    if r.status_code == 200:
        print(f"\n✅ Status changed to {status.upper()}")
    else:
        print("❌ Error changing status")
    
    input("\nPress Enter to continue...")


def doctor_availability_tab(worker_id):
    """Availability Tab - Manage available dates and time slots"""
    while True:
        print("\n" + "="*60)
        print("📅 AVAILABILITY")
        print("="*60)
        print("1. View Availability")
        print("2. Add Time Slot")
        print("3. Remove Time Slot")
        print("4. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_worker_availability(worker_id)
        elif choice == "2":
            add_availability_slot(worker_id)
        elif choice == "3":
            remove_availability_slot(worker_id)
        elif choice == "4":
            return
        else:
            print("❌ Invalid choice")


def view_worker_availability(worker_id):
    """View worker's availability"""
    print("\n" + "="*60)
    print("📅 YOUR AVAILABILITY")
    print("="*60)
    
    date_filter = input("Enter date to filter (YYYY-MM-DD) or press Enter for all: ").strip()
    
    url = f"{API}/worker/{worker_id}/availability"
    if date_filter:
        url += f"?date={date_filter}"
    
    r = requests.get(url)
    
    if r.status_code == 200:
        availability = r.json().get("availability", [])
        
        if not availability:
            print("\n📭 No availability set")
        else:
            # Group by date
            by_date = {}
            for slot in availability:
                date = slot['date']
                if date not in by_date:
                    by_date[date] = []
                by_date[date].append(slot['time_slot'])
            
            for date in sorted(by_date.keys()):
                print(f"\n📅 {date}")
                print("-" * 60)
                for time_slot in sorted(by_date[date]):
                    print(f"  ⏰ {time_slot}")
    else:
        print("❌ Error fetching availability")
    
    input("\nPress Enter to continue...")


def add_availability_slot(worker_id):
    """Add a new availability time slot"""
    print("\n" + "="*60)
    print("➕ ADD AVAILABILITY")
    print("="*60)
    
    date = input("Date (YYYY-MM-DD): ").strip()
    time_slot = input("Time Slot (e.g., 09:00-10:00): ").strip()
    
    if not date or not time_slot:
        print("❌ Date and time slot are required")
        input("\nPress Enter to continue...")
        return
    
    r = requests.post(f"{API}/worker/{worker_id}/availability", json={
        "date": date,
        "time_slot": time_slot
    })
    
    if r.status_code == 200:
        print("\n✅ Availability added successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to add availability"))
    
    input("\nPress Enter to continue...")


def remove_availability_slot(worker_id):
    """Remove an availability time slot"""
    print("\n" + "="*60)
    print("➖ REMOVE AVAILABILITY")
    print("="*60)
    
    date = input("Date (YYYY-MM-DD): ").strip()
    time_slot = input("Time Slot (e.g., 09:00-10:00): ").strip()
    
    if not date or not time_slot:
        print("❌ Date and time slot are required")
        input("\nPress Enter to continue...")
        return
    
    r = requests.delete(f"{API}/worker/{worker_id}/availability", json={
        "date": date,
        "time_slot": time_slot
    })
    
    if r.status_code == 200:
        print("\n✅ Availability removed successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to remove availability"))
    
    input("\nPress Enter to continue...")


def doctor_requests_tab(worker_id):
    """Requests Tab - View and respond to appointment requests"""
    while True:
        print("\n" + "="*60)
        print("📥 REQUESTS")
        print("="*60)
        
        r = requests.get(f"{API}/worker/{worker_id}/requests")
        
        if r.status_code != 200:
            print("❌ Error fetching requests")
            input("\nPress Enter to continue...")
            return
        
        requests_list = r.json().get("requests", [])
        
        if not requests_list:
            print("\n📭 No pending requests")
            print("\n1. 🔄 Refresh")
            print("2. ⬅️  Back")
            
            choice = input("\nSelect option: ").strip()
            if choice == "1":
                continue
            elif choice == "2":
                return
            continue
        
        print(f"\n📥 Pending Requests: {len(requests_list)}")
        print("-" * 60)
        
        for idx, req in enumerate(requests_list, 1):
            print(f"\n[{idx}] Appointment #{req['id']}")
            print(f"    Patient: {req['user_name']}")
            print(f"    Date: {req['booking_date']}")
            print(f"    Symptoms: {req['patient_symptoms']}")
            print("-" * 60)
        
        print(f"\n{len(requests_list) + 1}. 🔄 Refresh")
        print(f"{len(requests_list) + 2}. ⬅️  Back")
        
        choice = input("\nSelect request to respond (or refresh/back): ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(requests_list):
                respond_to_appointment(worker_id, requests_list[choice_num - 1]['id'])
            elif choice_num == len(requests_list) + 1:
                continue  # Refresh
            elif choice_num == len(requests_list) + 2:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def doctor_appointments_tab(worker_id):
    """Appointments Tab - Manage accepted appointments"""
    while True:
        print("\n" + "="*60)
        print("📋 APPOINTMENTS")
        print("="*60)
        
        r = requests.get(f"{API}/worker/{worker_id}/accepted-appointments")
        
        if r.status_code != 200:
            print("❌ Error fetching appointments")
            input("\nPress Enter to continue...")
            return
        
        appointments = r.json().get("appointments", [])
        
        if not appointments:
            print("\n📭 No accepted appointments")
            print("\n1. 🔄 Refresh")
            print("2. ⬅️  Back")
            
            choice = input("\nSelect option: ").strip()
            if choice == "1":
                continue
            elif choice == "2":
                return
            continue
        
        print(f"\n📋 Accepted Appointments: {len(appointments)}")
        print("-" * 60)
        
        for idx, apt in enumerate(appointments, 1):
            status_icon = {
                "accepted": "✅",
                "in_consultation": "💬",
                "completed": "✓"
            }.get(apt['status'], "❓")
            apt_type = apt.get("appointment_type", "clinic")
            type_label = "VIDEO" if apt_type == "video" else "CLINIC"
            
            print(f"\n[{idx}] {status_icon} Appointment #{apt['id']} - {apt['status'].upper()} ({type_label})")
            print(f"    Patient: {apt['user_name']}")
            print(f"    Date: {apt['booking_date']}")
            print(f"    Symptoms: {apt['patient_symptoms']}")
            print("-" * 60)
        
        print(f"\n{len(appointments) + 1}. View Details")
        print(f"{len(appointments) + 2}. 🔐 Start Video Call (Enter OTP)")
        print(f"{len(appointments) + 3}. Join Video Call")
        print(f"{len(appointments) + 4}. Complete Appointment")
        print(f"{len(appointments) + 5}. View Messages")
        print(f"{len(appointments) + 6}. 🔄 Refresh")
        print(f"{len(appointments) + 7}. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(appointments):
                apt_id = appointments[choice_num - 1]['id']
                view_appointment_detail_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 1:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    view_appointment_detail_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 2:
                apt_id = input("Enter Appointment ID to start consultation: ").strip()
                if apt_id:
                    start_consultation_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 3:
                apt_id = input("Enter Appointment ID to join video call: ").strip()
                if apt_id:
                    join_video_call_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 4:
                apt_id = input("Enter Appointment ID to complete: ").strip()
                if apt_id:
                    complete_appointment_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 5:
                apt_id = input("Enter Appointment ID: ").strip()
                if apt_id:
                    view_messages_worker(worker_id, apt_id)
            elif choice_num == len(appointments) + 6:
                continue  # Refresh
            elif choice_num == len(appointments) + 7:
                return
            else:
                print("❌ Invalid choice")
        else:
            print("❌ Please enter a number")


def join_video_call_worker(worker_id, appointment_id):
    """Join video/audio call as doctor (simulated). Uses backend for status-based rules."""
    r = requests.get(
        f"{API}/appointment/{appointment_id}/video-eligible?sender_role=worker&worker_id={worker_id}"
    )
    if r.status_code in (401, 403, 404):
        print("\n❌", r.json().get("error", "Not authorized or appointment not found"))
        input("\nPress Enter to continue...")
        return
    if r.status_code != 200:
        print("\n❌ Could not check video eligibility")
        input("\nPress Enter to continue...")
        return

    j = r.json()
    if not j.get("can_join"):
        print("\n❌", j.get("reason", "Video call is not available."))
        input("\nPress Enter to continue...")
        return

    status = j.get("status", "")
    print("\n" + "="*60)
    print("📹 JOINING VIDEO / AUDIO CONSULTATION (SIMULATED)")
    print("="*60)
    print(f"Appointment ID: {appointment_id}")
    print(f"Status: {status}")

    if status == "accepted":
        print("\n⏳ You can start the consultation to begin the video session.")
    elif status == "in_consultation":
        print("\n✅ Video consultation started (simulated).")

    print("\n💬 This is a simulation. In the real app, a video SDK would open here.")
    input("\nPress Enter to leave the call...")


def doctor_profile_tab(worker_id):
    """Profile Tab - Doctor personal details and settings"""
    while True:
        print("\n" + "="*60)
        print("👤 PROFILE")
        print("="*60)
        
        # Get worker info - we'll need to fetch from appointments or create an endpoint
        # For now, show basic info
        print(f"\n🆔 Worker ID: {worker_id}")
        print("📋 Verification Status: Approved")
        print("💡 Full profile details coming soon")
        print("\nThis will show:")
        print("  - Name")
        print("  - Email")
        print("  - Specialization")
        print("  - Experience")
        print("  - Clinic Location")
        print("  - Rating")
        
        print("\n" + "="*60)
        print("1. View Full Details")
        print("2. 👋 Logout")
        print("3. ⬅️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            view_worker_full_profile(worker_id)
        elif choice == "2":
            print("👋 Logged out")
            return True  # Signal logout
        elif choice == "3":
            return False
        else:
            print("❌ Invalid choice")


def view_worker_full_profile(worker_id):
    """View complete worker profile"""
    print("\n" + "="*60)
    print("👤 DOCTOR PROFILE")
    print("="*60)
    print("💡 Full profile view coming soon")
    print("This will show: Name, Email, Specialization, Experience, Location, Rating")
    input("\nPress Enter to continue...")


def respond_to_appointment(worker_id, appointment_id=None):
    """Accept or reject an appointment request"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    print("\n" + "="*60)
    print("📥 RESPOND TO REQUEST")
    print("="*60)
    print("1. ✅ Accept")
    print("2. ❌ Reject")
    print("3. ⬅️  Cancel")
    
    choice = input("\nSelect action: ").strip()
    
    if choice == "1":
        status = "accepted"
    elif choice == "2":
        status = "rejected"
    elif choice == "3":
        return
    else:
        print("❌ Invalid choice")
        return
    
    r = requests.post(f"{API}/worker/respond", json={

        "appointment_id": int(appointment_id),
        "status": status
    })
    
    if r.status_code == 200:
        print(f"\n✅ Appointment {status} successfully")
    else:
        if r.status_code == 200:
         print(f"\n✅ Appointment {status} successfully")
        else:
         print("\n❌ Failed to update appointment")
         print("Server response:", r.text)

    
    input("\nPress Enter to continue...")


def view_appointment_detail_worker(worker_id, appointment_id=None):
    """View detailed information about a specific appointment"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/appointment/{appointment_id}?sender_role=worker&worker_id={worker_id}")
    
    if r.status_code == 200:
        apt = r.json()
        print("\n" + "="*60)
        print("📄 APPOINTMENT DETAILS")
        print("="*60)
        print(f"ID: {apt['id']}")
        print(f"Status: {apt['status']}")
        print(f"Patient: {apt['user_name']}")
        print(f"Symptoms: {apt['patient_symptoms']}")
        print(f"Booking Date: {apt['booking_date']}")
        print(f"Created: {apt['created_at']}")
        print("="*60)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointment"))
    
    input("\nPress Enter to continue...")


def start_consultation_worker(worker_id, appointment_id=None):
    """Doctor starts video consultation using OTP"""

    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()

    print("\n🔐 Doctor OTP Verification")
    otp = input("Enter OTP sent to patient email: ").strip()

    r = requests.post(f"{API}/appointment/video/start", json={
        "appointment_id": int(appointment_id),
        "otp": otp
    })

    if r.status_code == 200:
        print("\n🎉 VIDEO CONSULTATION STARTED")
        print("💬 Patient can now join the call")
    else:
        print("❌ Error:", r.json().get("error", "Invalid OTP"))

    input("\nPress Enter to continue...")


    
    if r.status_code == 200:
        print("\n✅ Consultation started successfully")
        print("💬 Chat is now available for this appointment")
        print("📹 If this is a video appointment, the video/audio session is now considered ACTIVE (simulated).")
    else:
        print("❌ Error:", r.json().get("error", "Failed to start consultation"))
    
    input("\nPress Enter to continue...")


def complete_appointment_worker(worker_id, appointment_id=None):
    """Mark an appointment as completed"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    r = requests.post(f"{API}/appointment/complete", json={
        "appointment_id": int(appointment_id)
    })
    
    if r.status_code == 200:
        print("\n✅ Appointment marked as completed")
        print("📹 Any associated video/audio consultation is now considered ENDED (simulated).")
    else:
        print("❌ Error:", r.json().get("error", "Failed to complete appointment"))
    
    input("\nPress Enter to continue...")


def view_messages_worker(worker_id, appointment_id=None):
    """View messages in an appointment chat"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/messages/{appointment_id}?sender_role=worker&worker_id={worker_id}")
    
    if r.status_code == 200:
        data = r.json()
        messages = data.get("messages", [])
        
        if not messages:
            print("\n📭 No messages yet")
        else:
            print(f"\n💬 Messages for Appointment #{appointment_id}:")
            print("-" * 60)
            for msg in messages:
                sender_label = "👤 You" if msg["sender_role"] == "worker" else "👨‍⚕️ Patient"
                print(f"{sender_label} ({msg['timestamp'][:19]}):")
                print(f"  {msg['message']}")
                print("-" * 60)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch messages"))
    
    input("\nPress Enter to continue...")


def send_message_worker(worker_id, appointment_id=None):
    """Send a message in an appointment chat"""
    if not appointment_id:
        appointment_id = input("Appointment ID: ").strip()
    
    message = input("Message: ").strip()
    
    if not message:
        print("❌ Message cannot be empty")
        return
    
    r = requests.post(f"{API}/messages/send", json={
        "appointment_id": int(appointment_id),
        "sender_role": "worker",
        "worker_id": worker_id,
        "message": message
    })
    
    if r.status_code == 201:
        print("✅ Message sent successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to send message"))
    
    input("\nPress Enter to continue...")


def view_worker_appointments(worker_id):
    """Legacy function - redirects to appointments tab"""
    doctor_appointments_tab(worker_id)


def view_worker_appointments(worker_id):
    """View all appointments for the worker"""
    r = requests.get(f"{API}/worker/appointments/{worker_id}")
    
    if r.status_code == 200:
        appointments = r.json()
        if not appointments:
            print("\n📭 No appointments found")
            return
        
        print("\n📋 Your Appointments:")
        print("-" * 80)
        for apt in appointments:
            status_icon = {
                "pending": "⏳",
                "accepted": "✅",
                "rejected": "❌",
                "in_consultation": "💬",
                "completed": "✓",
                "cancelled": "🚫"
            }.get(apt["status"], "❓")
            
            print(f"ID: {apt['id']} | {status_icon} {apt['status'].upper()}")
            print(f"  Patient: {apt['user_name']}")
            print(f"  Symptoms: {apt['patient_symptoms']}")
            print(f"  Date: {apt['booking_date']}")
            print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointments"))


def view_appointment_detail_worker_legacy(worker_id):
    """View detailed information about a specific appointment"""
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/appointment/{apt_id}?sender_role=worker&worker_id={worker_id}")
    
    if r.status_code == 200:
        apt = r.json()
        print("\n📄 Appointment Details:")
        print("-" * 80)
        print(f"ID: {apt['id']}")
        print(f"Status: {apt['status']}")
        print(f"Patient: {apt['user_name']}")
        print(f"Symptoms: {apt['patient_symptoms']}")
        print(f"Booking Date: {apt['booking_date']}")
        print(f"Created: {apt['created_at']}")
        print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch appointment"))


def respond_to_appointment_legacy(worker_id):
    """Accept or reject an appointment"""
    apt_id = input("Appointment ID: ").strip()
    
    print("\n1. Accept")
    print("2. Reject")
    choice = input("Choice: ").strip()
    
    if choice == "1":
        status = "accepted"
    elif choice == "2":
        status = "rejected"
    else:
        print("❌ Invalid choice")
        return
    
    r = requests.post(f"{API}/worker/respond-appointment", json={
    "appointment_id": int(apt_id),
    "status": status
})

    
    if r.status_code == 200:
        print(f"✅ Appointment {status} successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to update appointment"))


def start_consultation_worker_legacy(worker_id):
    """Start consultation for an accepted appointment"""
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.post(f"{API}/appointment/start-consultation", json={
        "appointment_id": int(apt_id)
    })
    
    if r.status_code == 200:
        print("✅ Consultation started successfully")
        print("💬 Chat is now available for this appointment")
    else:
        print("❌ Error:", r.json().get("error", "Failed to start consultation"))


def complete_appointment_worker_legacy(worker_id):
    """Mark an appointment as completed"""
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.post(f"{API}/appointment/complete", json={
        "appointment_id": int(apt_id)
    })
    
    if r.status_code == 200:
        print("✅ Appointment marked as completed")
    else:
        print("❌ Error:", r.json().get("error", "Failed to complete appointment"))


def cancel_appointment_worker_legacy(worker_id):
    """Cancel an appointment"""
    apt_id = input("Appointment ID: ").strip()
    
    confirm = input("Are you sure you want to cancel? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Cancelled")
        return
    
    r = requests.post(f"{API}/appointment/cancel", json={
        "appointment_id": int(apt_id)
    })
    
    if r.status_code == 200:
        print("✅ Appointment cancelled successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to cancel appointment"))


def view_messages_worker_legacy(worker_id):
    """View messages in an appointment chat"""
    apt_id = input("Appointment ID: ").strip()
    
    r = requests.get(f"{API}/messages/{apt_id}?sender_role=worker&worker_id={worker_id}")
    
    if r.status_code == 200:
        data = r.json()
        messages = data.get("messages", [])
        
        if not messages:
            print("\n📭 No messages yet")
            return
        
        print(f"\n💬 Messages for Appointment #{apt_id}:")
        print("-" * 80)
        for msg in messages:
            sender_label = "👤 You" if msg["sender_role"] == "worker" else "👨‍⚕️ Patient"
            print(f"{sender_label} ({msg['timestamp'][:19]}):")
            print(f"  {msg['message']}")
            print("-" * 80)
    else:
        print("❌ Error:", r.json().get("error", "Failed to fetch messages"))


def send_message_worker_legacy(worker_id):
    """Send a message in an appointment chat"""
    apt_id = input("Appointment ID: ").strip()
    message = input("Message: ").strip()
    
    if not message:
        print("❌ Message cannot be empty")
        return
    
    r = requests.post(f"{API}/messages/send", json={
        "appointment_id": int(apt_id),
        "sender_role": "worker",
        "worker_id": worker_id,
        "message": message
    })
    
    if r.status_code == 201:
        print("✅ Message sent successfully")
    else:
        print("❌ Error:", r.json().get("error", "Failed to send message"))

def doctor_start_video_call(token):
# ==================================================
# ================= ADMIN DASHBOARD ================
# ==================================================

    def admin_login():
     print("\n🔐 Admin Login")

    u = input("Username: ").strip()
    p = input("Password: ").strip()

    if u == "admin" and p == "admin123":
        print("✅ Admin logged in")
        admin_menu()
    else:
        print("❌ Invalid credentials")


def admin_menu():
    while True:
        print("\n=== ADMIN DASHBOARD ===")
        print("1. 👷 Car Service Workers")
        print("2. 🏥 Healthcare Workers")
        print("3. ⛽ Fuel Delivery Agents")
        print("4. 🚚 Truck Operators")
        print("5. 👋 Logout")

        c = input("Choice: ").strip()

        if c == "1":
            from car_service.worker_admin_cli import worker_admin_menu
            worker_admin_menu()
        elif c == "2":
            healthcare_admin_menu()
        elif c == "3":
            fuel_delivery_admin_menu()
        elif c == "4":
            truck_operator_admin_menu()
        elif c == "5":
            return
        else:
            print("❌ Invalid choice")

def fuel_delivery_admin_menu():
    """Fuel delivery agent admin management"""
    while True:
        print("\n" + "="*60)
        print("⛽ FUEL DELIVERY AGENT ADMIN")
        print("="*60)
        print("1. 📋 Pending Agents")
        print("2. ✅ Approved Agents")
        print("3. 🔍 Agent Details")
        print("4. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            fuel_delivery_pending_agents()
        elif choice == "2":
            fuel_delivery_approved_agents()
        elif choice == "3":
            fuel_delivery_agent_details()
        elif choice == "4":
            return
        else:
            print("❌ Invalid choice")
            time.sleep(1)

def fuel_delivery_pending_agents():
    """Show pending fuel delivery agents"""
    print("\n" + "="*60)
    print("📋 PENDING FUEL DELIVERY AGENTS")
    print("="*60)
    
    try:
        response = requests.get(f"{API}/api/fuel-delivery/admin/pending")
        
        if response.status_code == 200:
            agents = response.json()
            
            if not agents:
                print("📭 No pending fuel delivery agents found")
            else:
                for idx, agent in enumerate(agents, 1):
                    print(f"\n[{idx}] 📋 Agent ID: {agent['id']}")
                    print(f"    👤 Name: {agent['name']}")
                    print(f"    📧 Email: {agent['email']}")
                    print(f"    📱 Phone: {agent['phone_number']}")
                    print(f"    🏙️ City: {agent['city']}")
                    print(f"    🚗 Vehicle: {agent['vehicle_type']} - {agent['vehicle_number']}")
                    print(f"    📅 Applied: {agent['created_at']}")
                    print(f"    📊 Status: {agent['approval_status']}")
                
                print("\n" + "-"*60)
                choice = input("\nSelect agent number for actions (0 to go back): ").strip()
                
                if choice == "0":
                    return
                
                if choice.isdigit() and int(choice) >= 1 and int(choice) <= len(agents):
                    selected_agent = agents[int(choice) - 1]
                    fuel_delivery_agent_actions(selected_agent)
                else:
                    print("❌ Invalid selection")
                    time.sleep(1)
        else:
            print("❌ Failed to fetch pending agents")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def fuel_delivery_approved_agents():
    """Show approved fuel delivery agents"""
    print("\n" + "="*60)
    print("✅ APPROVED FUEL DELIVERY AGENTS")
    print("="*60)
    
    try:
        response = requests.get(f"{API}/api/fuel-delivery/admin/approved")
        
        if response.status_code == 200:
            agents = response.json()
            
            if not agents:
                print("📭 No approved fuel delivery agents found")
            else:
                for idx, agent in enumerate(agents, 1):
                    print(f"\n[{idx}] 📋 Agent ID: {agent['id']}")
                    print(f"    👤 Name: {agent['name']}")
                    print(f"    📧 Email: {agent['email']}")
                    print(f"    📱 Phone: {agent['phone_number']}")
                    print(f"    🏙️ City: {agent['city']}")
                    print(f"    🚗 Vehicle: {agent['vehicle_type']} - {agent['vehicle_number']}")
                    print(f"    📅 Approved: {agent['approved_at']}")
            
        else:
            print("❌ Failed to fetch approved agents")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def fuel_delivery_agent_details():
    """Search for specific fuel delivery agent"""
    print("\n" + "="*60)
    print("🔍 FUEL DELIVERY AGENT DETAILS")
    print("="*60)
    
    try:
        agent_id = input("Enter Agent ID: ").strip()
        
        if not agent_id:
            print("❌ Agent ID is required")
            input("\nPress Enter to continue...")
            return
        
        response = requests.get(f"{API}/api/fuel-delivery/admin/agent/{agent_id}")
        
        if response.status_code == 200:
            agent = response.json()
            
            print(f"\n📋 Agent Details:")
            print(f"    🆔 ID: {agent['id']}")
            print(f"    👤 Name: {agent['name']}")
            print(f"    📧 Email: {agent['email']}")
            print(f"    📱 Phone: {agent['phone_number']}")
            print(f"    🏙️ City: {agent['city']}")
            print(f"    🚗 Vehicle Type: {agent['vehicle_type']}")
            print(f"    🔢 Vehicle Number: {agent['vehicle_number']}")
            print(f"    📊 Status: {agent['approval_status']}")
            print(f"    📅 Created: {agent['created_at']}")
            
            if agent.get('approved_at'):
                print(f"    ✅ Approved: {agent['approved_at']}")
                
        else:
            print("❌ Agent not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def fuel_delivery_agent_actions(agent):
    """Actions for fuel delivery agent"""
    while True:
        print(f"\n" + "="*60)
        print(f"⚡ AGENT ACTIONS - {agent['name']}")
        print("="*60)
        print("1. ✅ Approve Agent")
        print("2. ❌ Reject Agent")
        print("3. 📄 View Documents")
        print("4. ⬅️ Back")
        
        choice = input("\nSelect action: ").strip()
        
        if choice == "1":
            fuel_delivery_approve_agent(agent['id'])
            return
        elif choice == "2":
            fuel_delivery_reject_agent(agent['id'])
            return
        elif choice == "3":
            fuel_delivery_view_documents(agent)
        elif choice == "4":
            return
        else:
            print("❌ Invalid choice")
            time.sleep(1)

def fuel_delivery_approve_agent(agent_id):
    """Approve fuel delivery agent"""
    try:
        response = requests.post(f"{API}/api/fuel-delivery/admin/approve", json={
            "agent_id": agent_id
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Agent approved successfully!")
            else:
                print(f"❌ Approval failed: {result.get('error', 'Unknown error')}")
        else:
            print("❌ Failed to approve agent")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def fuel_delivery_reject_agent(agent_id):
    """Reject fuel delivery agent"""
    try:
        response = requests.post(f"{API}/api/fuel-delivery/admin/reject", json={
            "agent_id": agent_id
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("❌ Agent rejected successfully!")
            else:
                print(f"❌ Rejection failed: {result.get('error', 'Unknown error')}")
        else:
            print("❌ Failed to reject agent")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def fuel_delivery_view_documents(agent):
    """View agent documents"""
    print("\n" + "="*60)
    print("📄 AGENT DOCUMENTS")
    print("="*60)
    
    documents = [
        ("Vehicle Photo", agent.get('vehicle_photo_path')),
        ("RC Book", agent.get('rc_book_photo_path')),
        ("Pollution Certificate", agent.get('pollution_certificate_path')),
        ("Fuel Contract", agent.get('fuel_contract_path')),
        ("Employee Proof", agent.get('employee_proof_path')),
        ("Govt ID", agent.get('govt_id_path'))
    ]
    
    for doc_name, doc_path in documents:
        if doc_path:
            print(f"✅ {doc_name}: {doc_path}")
        else:
            print(f"❌ {doc_name}: Not uploaded")
    
    input("\nPress Enter to continue...")

def truck_operator_admin_menu():
    """Truck operator admin management"""
    while True:
        print("\n" + "="*60)
        print("🚚 TRUCK OPERATOR ADMIN")
        print("="*60)
        print("1. 📋 Pending Operators")
        print("2. ✅ Approved Operators")
        print("3. 🔍 Operator Details")
        print("4. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            truck_operator_pending_operators()
        elif choice == "2":
            truck_operator_approved_operators()
        elif choice == "3":
            truck_operator_operator_details()
        elif choice == "4":
            return
        else:
            print("❌ Invalid choice")
            time.sleep(1)

def truck_operator_pending_operators():
    """Show pending truck operators"""
    print("\n" + "="*60)
    print("📋 PENDING TRUCK OPERATORS")
    print("="*60)
    
    try:
        response = requests.get(f"{API}/api/truck-operator/admin/pending")
        
        if response.status_code == 200:
            operators = response.json()
            
            if not operators:
                print("📭 No pending truck operators found")
            else:
                for idx, operator in enumerate(operators, 1):
                    print(f"\n[{idx}] 📋 Operator ID: {operator['id']}")
                    print(f"    👤 Name: {operator['name']}")
                    print(f"    📧 Email: {operator['email']}")
                    print(f"    📱 Phone: {operator['phone']}")
                    print(f"    🏙️ City: {operator['city']}")
                    print(f"    🚗 Vehicle: {operator['vehicle_type']} - {operator['vehicle_number']}")
                    print(f"    📅 Applied: {operator['created_at']}")
                    print(f"    📊 Status: {operator['status']}")
                
                print("\n" + "-"*60)
                choice = input("\nSelect operator number for actions (0 to go back): ").strip()
                
                if choice == "0":
                    return
                
                if choice.isdigit() and int(choice) >= 1 and int(choice) <= len(operators):
                    selected_operator = operators[int(choice) - 1]
                    truck_operator_operator_actions(selected_operator)
                else:
                    print("❌ Invalid selection")
                    time.sleep(1)
        else:
            print("❌ Failed to fetch pending operators")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def truck_operator_approved_operators():
    """Show approved truck operators"""
    print("\n" + "="*60)
    print("✅ APPROVED TRUCK OPERATORS")
    print("="*60)
    
    try:
        response = requests.get(f"{API}/api/truck-operator/admin/approved")
        
        if response.status_code == 200:
            operators = response.json()
            
            if not operators:
                print("📭 No approved truck operators found")
            else:
                for idx, operator in enumerate(operators, 1):
                    print(f"\n[{idx}] 📋 Operator ID: {operator['id']}")
                    print(f"    👤 Name: {operator['name']}")
                    print(f"    📧 Email: {operator['email']}")
                    print(f"    📱 Phone: {operator['phone']}")
                    print(f"    🏙️ City: {operator['city']}")
                    print(f"    🚗 Vehicle: {operator['vehicle_type']} - {operator['vehicle_number']}")
                    print(f"    📅 Approved: {operator['approved_at']}")
            
        else:
            print("❌ Failed to fetch approved operators")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def truck_operator_operator_details():
    """Search for specific truck operator"""
    print("\n" + "="*60)
    print("🔍 TRUCK OPERATOR DETAILS")
    print("="*60)
    
    try:
        operator_id = input("Enter Operator ID: ").strip()
        
        if not operator_id:
            print("❌ Operator ID is required")
            input("\nPress Enter to continue...")
            return
        
        response = requests.get(f"{API}/api/truck-operator/admin/operator/{operator_id}")
        
        if response.status_code == 200:
            operator = response.json()
            
            print(f"\n📋 Operator Details:")
            print(f"    🆔 ID: {operator['id']}")
            print(f"    👤 Name: {operator['name']}")
            print(f"    📧 Email: {operator['email']}")
            print(f"    📱 Phone: {operator['phone']}")
            print(f"    🏙️ City: {operator['city']}")
            print(f"    🚗 Vehicle Type: {operator['vehicle_type']}")
            print(f"    🔢 Vehicle Number: {operator['vehicle_number']}")
            print(f"    📊 Status: {operator['status']}")
            print(f"    📅 Created: {operator['created_at']}")
            
            if operator.get('approved_at'):
                print(f"    ✅ Approved: {operator['approved_at']}")
                
        else:
            print("❌ Operator not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def truck_operator_operator_actions(operator):
    """Actions for truck operator"""
    while True:
        print(f"\n" + "="*60)
        print(f"⚡ OPERATOR ACTIONS - {operator['name']}")
        print("="*60)
        print("1. ✅ Approve Operator")
        print("2. ❌ Reject Operator")
        print("3. 📄 View Documents")
        print("4. ⬅️ Back")
        
        choice = input("\nSelect action: ").strip()
        
        if choice == "1":
            truck_operator_approve_operator(operator['id'])
            return
        elif choice == "2":
            truck_operator_reject_operator(operator['id'])
            return
        elif choice == "3":
            truck_operator_view_documents(operator)
        elif choice == "4":
            return
        else:
            print("❌ Invalid choice")
            time.sleep(1)

def truck_operator_approve_operator(operator_id):
    """Approve truck operator"""
    try:
        response = requests.post(f"{API}/api/truck-operator/admin/approve", json={
            "operator_id": operator_id
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Operator approved successfully!")
            else:
                print(f"❌ Approval failed: {result.get('error', 'Unknown error')}")
        else:
            print("❌ Failed to approve operator")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def truck_operator_reject_operator(operator_id):
    """Reject truck operator"""
    try:
        response = requests.post(f"{API}/api/truck-operator/admin/reject", json={
            "operator_id": operator_id
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("❌ Operator rejected successfully!")
            else:
                print(f"❌ Rejection failed: {result.get('error', 'Unknown error')}")
        else:
            print("❌ Failed to reject operator")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def truck_operator_view_documents(operator):
    """View operator documents"""
    print("\n" + "="*60)
    print("📄 OPERATOR DOCUMENTS")
    print("="*60)
    
    documents = [
        ("Vehicle Photo", operator.get('vehicle_photo_path')),
        ("RC Book", operator.get('rc_book_path')),
        ("Petrol Pump Authorization", operator.get('petrol_pump_authorization_path'))
    ]
    
    for doc_name, doc_path in documents:
        if doc_path:
            print(f"✅ {doc_name}: {doc_path}")
        else:
            print(f"❌ {doc_name}: Not uploaded")
    
    input("\nPress Enter to continue...")

# ==================================================
# ========== HOTFIX EXTENSION (COPY-PASTE) =========
# ==================================================

def safe_json(r):
    try:
        return r.json()
    except Exception:
        return {}

# ---------- LOOKUP APPOINTMENTS (USER) -------------
def lookup_appointment_user():
    print("\n🔎 LOOKUP APPOINTMENT")
    doctor_id = input("Doctor ID (optional): ").strip()
    date = input("Date YYYY-MM-DD (optional): ").strip()

    params = {}
    if doctor_id:
        params["worker_id"] = doctor_id
    if date:
        params["date"] = date

    r = requests.get(
        f"{API}/appointments/lookup",
        params=params,
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    data = safe_json(r)
    appointments = data.get("appointments", [])

    if not appointments:
        print("📭 No matching appointments found")
        input("Press Enter...")
        return

    for a in appointments:
        print("-" * 60)
        print(f"ID: {a['id']}")
        print(f"Doctor ID: {a['worker_id']}")
        print(f"Date: {a['booking_date']}")
        print(f"Slot: {a.get('time_slot','N/A')}")
        print(f"Status: {a['status']}")

    input("Press Enter...")


# ---------- CHECK DOCTOR AVAILABILITY ----------------
def check_doctor_slots(doctor_id, date):
    r = requests.get(
        f"{API}/worker/{doctor_id}/availability",
        params={"date": date}
    )

    data = safe_json(r)
    slots = data.get("availability", [])

    if not slots:
        print("❌ No slots available")
        return []

    print("\n⏰ Available Slots")
    for i, s in enumerate(slots, 1):
        print(f"{i}. {s['time_slot']}")

    return slots


# ---------- SLOT-BASED BOOKING -----------------------
def book_appointment_with_slot(doctor_id):
    global USER_ID, TOKEN

    if not USER_ID or not TOKEN:
        print("❌ Login required")
        return

    # Get user info
    try:
        r = requests.get(f"{API}/user/info", headers={"Authorization": f"Bearer {TOKEN}"})
        if r.status_code != 200:
            print("❌ Could not get user information")
            return
        user_info = r.json()
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return

    date = input("Date (YYYY-MM-DD): ").strip()
    if not date:
        print("❌ Date is required")
        return

    slots = check_doctor_slots(doctor_id, date)
    if not slots:
        input("Press Enter...")
        return

    c = input("Select slot number: ").strip()
    if not c.isdigit() or int(c) < 1 or int(c) > len(slots):
        print("❌ Invalid slot selection")
        return

    slot = slots[int(c) - 1]["time_slot"]
    symptoms = input("Symptoms: ").strip()
    
    if not symptoms:
        print("❌ Symptoms are required")
        return

    print(f"\n📅 Booking appointment...")
    print(f"   Doctor ID: {doctor_id}")
    print(f"   User ID: {USER_ID}")
    print(f"   Date: {date}")
    print(f"   Slot: {slot}")
    print(f"   Symptoms: {symptoms}")

    try:
        r = requests.post(f"{API}/appointment/book", json={
            "user_id": int(USER_ID),
            "worker_id": int(doctor_id),
            "user_name": user_info.get("user_name", f"User_{USER_ID}"),
            "symptoms": symptoms,
            "date": date,
            "time_slot": slot
        })

        print(f"🔍 Response status: {r.status_code}")
        if r.status_code != 201:
            print(f"❌ Response error: {r.text}")

        if r.status_code == 201:
            data = r.json()
            print("✅ Appointment booked successfully!")
            if data.get("success"):
                print(f"📋 Appointment ID: {data.get('appointment_id')}")
            print("⏳ Waiting for doctor's approval...")
        else:
            error_msg = r.json().get("error", "Unknown error")
            print(f"❌ Booking failed: {error_msg}")

    except Exception as e:
        print(f"❌ Network error: {e}")

    input("Press Enter...")


# ---------- OVERRIDE DOCTOR ACTION MENU --------------
def show_doctor_actions(doctor):
    while True:
        print("\n" + "="*60)
        print(f"👨‍⚕️ Dr. {doctor['full_name']}")
        print("="*60)
        print("1. 📅 Check Availability & Book")
        print("2. � Request Video Consultation")
        print("3. ⬅️ Back")

        c = input("\nSelect action: ").strip()

        if c == "1":
            book_appointment_with_slot(doctor['id'])
        elif c == "2":
            request_video_consultation(doctor['id'])
        elif c == "3":
            return
        else:
            print("❌ Invalid choice")


# ---------- OVERRIDE APPOINTMENT TAB -----------------
def healthcare_appointments_tab():
    while True:
        print("\n" + "="*60)
        print("📅 APPOINTMENTS")
        print("="*60)

        r = requests.get(
            f"{API}/user/appointments",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )

        data = safe_json(r)
        appointments = data.get("appointments", [])

        if not appointments:
            print("📭 No appointments")
        else:
            for i, a in enumerate(appointments, 1):
                print(f"[{i}] ID:{a['id']} | {a['status']} | {a['booking_date']}")

        print("\n1. View Details")
        print("2. Join Video Call")
        print("3. Cancel Appointment")
        print("4. 🔎 Lookup Appointment")
        print("5. ⬅️ Back")

        c = input("Choice: ").strip()

        if c == "1":
            view_appointment_detail_user(input("Appointment ID: "))
        elif c == "2":
           join_active_video_call()
        elif c == "3":
            cancel_appointment_user(input("Appointment ID: "))
        elif c == "4":
            lookup_appointment_user()
        elif c == "5":
            return
        
        # ==================================================
# ===== FIX: DOCTOR → ACTION (BOOKING VISIBLE) =====
# ==================================================

def show_doctors_by_specialization(specialization):
    r = requests.get(f"{API}/healthcare/doctors/{specialization}")
    doctors = r.json().get("doctors", [])

    if not doctors:
        print("❌ No doctors available")
        input("Press Enter...")
        return

    while True:
        print("\n" + "=" * 70)
        print(f"🏥 {specialization.upper()} - Available Doctors")
        print("=" * 70)

        for i, doc in enumerate(doctors, 1):
            print(f"\n[{i}] Dr. {doc['full_name']}")
            print(f"    Experience: {doc['experience']} years")
            print(f"    Location: {doc.get('clinic_location','N/A')}")
            print(f"    Doctor ID: {doc['id']}")

        print("\n0. ⬅️ Back")

        choice = input("\nSelect doctor number: ").strip()

        if choice == "0":
            return

        if not choice.isdigit():
            print("❌ Enter a number")
            continue

        idx = int(choice) - 1
        if 0 <= idx < len(doctors):
            # 🔥 THIS WAS MISSING
            show_doctor_actions(doctors[idx])
        else:
            print("❌ Invalid selection")



# ==================================================
# ================= MAIN ===========================
# ==================================================

def request_video_consultation(worker_id):
    global USER_ID

    # 🔐 Ensure USER_ID exists
    if not USER_ID:
        r = requests.get(
            f"{API}/user/info",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        if r.status_code != 200:
            print("❌ Session expired. Please login again.")
            return
        USER_ID = r.json()["user_id"]

    r = requests.post(f"{API}/appointment/video-request", json={
        "user_id": int(USER_ID),
        "worker_id": int(worker_id),
        "user_name": "User",
        "symptoms": "Video consultation requested"
    })

    if r.status_code == 201:
        print("\n✅ Video consultation requested successfully")
        print("⏳ Waiting for doctor to accept")
    else:
        print("❌ Failed to request video consultation")
        print("Server says:", r.text)

    input("Press Enter...")


    if r.status_code == 201:
        print("\n✅ Video consultation requested")
        print("⏳ Waiting for doctor to accept")
    else:
        print("❌ Failed to request video consultation")

    input("Press Enter...")


def join_active_video_call():
    r = requests.get(
        f"{API}/user/appointments",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    if r.status_code != 200:
        print("❌ Could not fetch appointments")
        input("Press Enter...")
        return

    appointments = r.json().get("appointments", [])
    active = [a for a in appointments if a["status"] == "in_consultation"]

    if not active:
        print("❌ No active video consultations right now")
        input("Press Enter...")
        return

    apt = active[0]

    r = requests.get(f"{API}/appointment/{apt['id']}/video-link")
    if r.status_code == 200:
        print("\n🎥 JOINING VIDEO CALL")
        print("Meeting Link:", r.json()["video_link"])
    else:
        print("❌ Video not started yet")

    input("Press Enter...")

def doctor_video_appointments():
    while True:
        print("\n🎥 VIDEO CONSULTATIONS")
        r = requests.get(f"{API}/worker/video_appointments")
        data = r.json()

        if not data:
            print("No accepted video consultations")
            input("Press Enter...")
            return

        for i, apt in enumerate(data, 1):
            print(f"\n[{i}] Appointment #{apt['id']}")
            print("Patient:", apt["user_name"])
            print("Status:", apt["status"])

        print("\n0. Back")
        choice = input("Select appointment: ").strip()

        if choice == "0":
            return

        apt_id = data[int(choice)-1]["id"]

        print("\n🔐 ENTER DOCTOR OTP TO START CALL")
        otp = input("OTP: ").strip()

        r = requests.post(f"{API}/video/start",
            json={"appointment_id": apt_id, "otp": otp}
        )

        if r.status_code != 200:
            print("❌ Invalid OTP")
            input("Press Enter...")
            continue

        meeting = r.json()["meeting_link"]

        print("\n🎉 CALL STARTED SUCCESSFULLY")
        print("🔗 Open this link in browser:")
        print(meeting)
        input("Press Enter...")


def main():
    # Check if server is running
    print("\n🔍 Checking server connection...")
    if not check_server_connection():
        print("\n" + "="*60)
        print("❌ ERROR: Flask server is not running!")
        print("="*60)
        print("\n📋 To fix this:")
        print("1. Open a NEW terminal/command prompt")
        print("2. Navigate to the project folder")
        print("3. Run: python app.py")
        print("4. Wait for: 'Running on http://127.0.0.1:5000'")
        print("5. Then come back here and run: python cli.py")
        print("\n💡 Keep the server running in the background!")
        print("="*60)
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("✅ Server connection successful!")
    
    while True:
        print("\n=== ExpertEase ===")
        print("1. User")
        print("2. Worker")
        print("3. Admin")
        print("4. Exit")

        c = input("Choice: ").strip()

        if c == "1":
            user_menu()
        elif c == "2":
            from auth.worker_auth import worker_menu
            worker_menu()
        elif c == "3":
            admin_menu()
        elif c == "4":
            print("👋 Goodbye")
            break

def doctor_video_appointments(worker_id):
    """Show all accepted VIDEO appointments for doctor"""

    print("\n📹 FETCHING VIDEO APPOINTMENTS...")

    r = requests.get(f"{API}/worker/video_appointments")

    if r.status_code != 200:
        print("❌ Failed to fetch video appointments")
        input("\nPress Enter...")
        return

    appointments = r.json()

    if not appointments:
        print("\n📭 No video consultations ready")
        input("\nPress Enter...")
        return

    while True:
        print("\n" + "="*60)
        print("📹 VIDEO CONSULTATIONS READY")
        print("="*60)

        for idx, apt in enumerate(appointments, 1):
            print(f"\n[{idx}] Appointment #{apt['id']}")
            print(f"Patient: {apt['user_name']}")
            print(f"Status: {apt['status']}")
            print("-"*50)

        print(f"\n{len(appointments)+1}. 🔄 Refresh")
        print(f"{len(appointments)+2}. ⬅️ Back")

        choice = input("\nSelect appointment to START video call: ").strip()

        if not choice.isdigit():
            continue

        choice = int(choice)

        # Start consultation
        if 1 <= choice <= len(appointments):
            apt_id = appointments[choice-1]["id"]
            start_consultation_worker(worker_id, apt_id)

        elif choice == len(appointments)+1:
            return doctor_video_appointments(worker_id)

        elif choice == len(appointments)+2:
            return

def create_video_session_cli(worker_id):
    """Create video session and get OTP"""
    print("\n🎥 CREATE VIDEO SESSION")
    print("="*60)
    
    # Get doctor's appointments
    r = requests.get(f"{API}/worker/appointments/{worker_id}")
    if r.status_code != 200:
        print("❌ Failed to fetch appointments")
        input("\nPress Enter...")
        return
    
    appointments = r.json()
    accepted_appointments = [apt for apt in appointments if apt['status'] == 'accepted']
    
    if not accepted_appointments:
        print("📭 No accepted appointments found")
        input("\nPress Enter...")
        return
    
    print("📋 Select Appointment:")
    for idx, apt in enumerate(accepted_appointments, 1):
        print(f"[{idx}] Appointment #{apt['id']} - {apt['user_name']}")
    
    try:
        choice = int(input("\nSelect appointment: ")) - 1
        if choice < 0 or choice >= len(accepted_appointments):
            print("❌ Invalid selection")
            return
        
        appointment_id = accepted_appointments[choice]['id']
        
        # Create video session
        r = requests.post(f"{API}/video/create-session/{appointment_id}", 
                         json={"doctor_id": worker_id})
        
        if r.status_code == 201:
            data = r.json()
            session = data['session']
            print("✅ Video session created successfully!")
            print(f"📋 Appointment ID: {appointment_id}")
            print(f"🔑 OTP: {session['doctor_otp']}")
            print(f"🏠 Room ID: {session['room_id']}")
            print("\n💡 Save this OTP to start video call!")
        else:
            error_data = r.json()
            print(f"❌ Error: {error_data.get('message', 'Unknown error')}")
            
    except ValueError:
        print("❌ Invalid input")
    
    input("\nPress Enter to continue...")

def start_video_call_cli(worker_id):
    """Start video call with OTP verification"""
    print("\n🎥 START VIDEO CALL")
    print("="*60)
    
    # Get doctor's video sessions
    r = requests.get(f"{API}/worker/appointments/{worker_id}")
    if r.status_code != 200:
        print("❌ Failed to fetch appointments")
        input("\nPress Enter...")
        return
    
    appointments = r.json()
    accepted_appointments = [apt for apt in appointments if apt['status'] in ['accepted', 'in_progress']]
    
    if not accepted_appointments:
        print("📭 No appointments ready for video call")
        input("\nPress Enter...")
        return
    
    print("📋 Select Appointment:")
    for idx, apt in enumerate(accepted_appointments, 1):
        print(f"[{idx}] Appointment #{apt['id']} - {apt['user_name']} ({apt['status']})")
    
    try:
        choice = int(input("\nSelect appointment: ")) - 1
        if choice < 0 or choice >= len(accepted_appointments):
            print("❌ Invalid selection")
            return
        
        appointment_id = accepted_appointments[choice]['id']
        otp = input("🔑 Enter OTP: ").strip()
        
        # Start video call
        r = requests.post(f"{API}/video/start", 
                         json={
                             "appointment_id": appointment_id,
                             "otp": otp,
                             "doctor_id": worker_id
                         })
        
        if r.status_code == 200:
            data = r.json()
            print("✅ Video call started successfully!")
            print(f"🏠 Room ID: {data['room_id']}")
            print(f"📋 Session Status: {data['session']['session_status']}")
            print("\n💡 Patients can now join call!")
            print("🔗 Room is live and ready for WebRTC connections")
        else:
            error_data = r.json()
            print(f"❌ Error: {error_data.get('message', 'Unknown error')}")
            
    except ValueError:
        print("❌ Invalid input")
    
    input("\nPress Enter to continue...")

def end_video_call_cli(worker_id):
    """End video call"""
    print("\n🎥 END VIDEO CALL")
    print("="*60)
    
    # Get active video sessions
    r = requests.get(f"{API}/video/active-sessions")
    if r.status_code != 200:
        print("❌ Failed to fetch active sessions")
        input("\nPress Enter...")
        return
    
    data = r.json()
    sessions = data['sessions']
    
    # Filter sessions for this doctor
    doctor_sessions = []
    for session in sessions:
        # Get appointment details to check doctor
        r_apt = requests.get(f"{API}/appointment/{session['appointment_id']}")
        if r_apt.status_code == 200:
            apt = r_apt.json()
            if str(apt.get('doctor_id')) == str(worker_id):
                doctor_sessions.append(session)
    
    if not doctor_sessions:
        print("📭 No active video sessions found")
        input("\nPress Enter...")
        return
    
    print("📋 Select Active Session:")
    for idx, session in enumerate(doctor_sessions, 1):
        print(f"[{idx}] Room: {session['room_id']} (Status: {session['session_status']})")
    
    try:
        choice = int(input("\nSelect session to end: ")) - 1
        if choice < 0 or choice >= len(doctor_sessions):
            print("❌ Invalid selection")
            return
        
        session = doctor_sessions[choice]
        appointment_id = session['appointment_id']
        
        # End video call
        r = requests.post(f"{API}/video/end", 
                         json={
                             "appointment_id": appointment_id,
                             "user_id": worker_id,
                             "user_type": "doctor"
                         })
        
        if r.status_code == 200:
            data = r.json()
            print("✅ Video call ended successfully!")
            print(f"📋 Session Status: {data['session']['session_status']}")
            print("📊 Appointment marked as completed")
        else:
            error_data = r.json()
            print(f"❌ Error: {error_data.get('message', 'Unknown error')}")
            
    except ValueError:
        print("❌ Invalid input")
    
    input("\nPress Enter to continue...")

def join_video_call_cli(user_id):
    """Patient joins video call"""
    print("\n🎥 JOIN VIDEO CALL")
    print("="*60)
    
    # Get user's appointments
    r = requests.get(f"{API}/user/appointments", headers={"Authorization": f"Bearer {TOKEN}"})
    if r.status_code != 200:
        print("❌ Failed to fetch appointments")
        input("\nPress Enter...")
        return
    
    # Ensure we work with the list of appointments
    appointments = r.json().get("appointments", [])
    # Filter only video consultations that are live/in progress
    video_appointments = [
        apt for apt in appointments
        if apt.get('appointment_type') == 'video' and apt.get('status') in ['in_progress']
    ]
    
    if not video_appointments:
        print("📭 No video calls available to join")
        print("💡 Please wait for doctor to start call")
        input("\nPress Enter...")
        return
    
    print("📋 Select Video Call to Join:")
    for idx, apt in enumerate(video_appointments, 1):
        print(f"[{idx}] Appointment #{apt['id']} - Dr. {apt.get('doctor_name', 'Unknown')}")
    
    try:
        choice = int(input("\nSelect video call: ")) - 1
        if choice < 0 or choice >= len(video_appointments):
            print("❌ Invalid selection")
            return
        
        appointment_id = video_appointments[choice]['id']
        
        # Join video call
        r = requests.get(f"{API}/video/join/{appointment_id}")
        
        if r.status_code == 200:
            data = r.json()
            print("✅ Successfully joined video call!")
            print(f"🏠 Room ID: {data['room_id']}")
            print(f"📋 Session Status: {data['session']['session_status']}")
            print("\n💡 Ready for WebRTC connection!")
            print("🔗 Use this Room ID to establish video connection")
        else:
            error_data = r.json()
            print(f"❌ Error: {error_data.get('message', 'Unknown error')}")
            
    except ValueError:
        print("❌ Invalid input")
    
    input("\nPress Enter to continue...")

def video_menu_doctor(worker_id):
    """Video consultation menu for doctors"""
    while True:
        print("\n" + "="*60)
        print("🎥 VIDEO CONSULTATION")
        print("="*60)
        print("1. 📋 Create Video Session (Get OTP)")
        print("2. 🎥 Start Video Call")
        print("3. 🛑 End Video Call")
        print("4. 📊 View Active Sessions")
        print("5. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            create_video_session_cli(worker_id)
        elif choice == "2":
            start_video_call_cli(worker_id)
        elif choice == "3":
            end_video_call_cli(worker_id)
        elif choice == "4":
            # View active sessions
            r = requests.get(f"{API}/video/active-sessions")
            if r.status_code == 200:
                data = r.json()
                sessions = data['sessions']
                print("\n📊 ACTIVE VIDEO SESSIONS:")
                for session in sessions:
                    print(f"🏠 Room: {session['room_id']}")
                    print(f"📋 Status: {session['session_status']}")
                    print(f"📅 Started: {session['started_at'] or 'Not started'}")
                    print("-"*40)
            else:
                print("❌ Failed to fetch active sessions")
            input("\nPress Enter...")
        elif choice == "5":
            break

def video_menu_user(user_id):
    """Video consultation menu for users"""
    while True:
        print("\n" + "="*60)
        print("🎥 VIDEO CONSULTATION")
        print("="*60)
        print("1. 🎥 Join Live Consultation")
        print("2. 📊 My Video Appointments")
        print("3. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            join_video_call_cli(user_id)
        elif choice == "2":
            # View video appointments
            r = requests.get(f"{API}/user/appointments", headers={"Authorization": f"Bearer {TOKEN}"})
            if r.status_code == 200:
                appointments = r.json().get("appointments", [])
                video_appts = [apt for apt in appointments if apt['status'] in ['accepted', 'in_progress', 'completed']]
                print("\n📋 MY VIDEO APPOINTMENTS:")
                for apt in video_appts:
                    print(f"🏥 Appointment #{apt['id']}")
                    print(f"👨‍⚕️ Doctor: {apt.get('doctor_name', 'Unknown')}")
                    print(f"📋 Status: {apt['status']}")
                    print(f"📅 Date: {apt.get('appointment_date', 'N/A')}")
                    print("-"*40)
            else:
                print("❌ Failed to fetch appointments")
            input("\nPress Enter...")
        elif choice == "3":
            break


if __name__ == "__main__":
    main()
