import os
import requests
from .models import UPLOAD_DIR

API = "http://127.0.0.1:5000"

def ask_expert_flow(token, user_id):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API}/api/car/expert/online-experts", headers=headers)
    if r.status_code != 200:
        print("  Failed to load experts")
        return
    experts = r.json().get("experts", [])
    print("\nAVAILABLE AUTOMOBILE EXPERTS")
    print("================================")
    if not experts:
        print("No experts online right now.")
        return
    for idx, e in enumerate(experts, 1):
        print(f"\n{idx}. {e.get('name','Unknown')}")
        print(f"Specialization: {e.get('specialization','N/A')}")
        print(f"Rating: {e.get('rating',0)}")
    sel = input("\nSelect expert number: ").strip()
    if not sel.isdigit() or int(sel) < 1 or int(sel) > len(experts):
        print("  Invalid selection")
        return
    expert = experts[int(sel) - 1]
    expert_id = expert["id"]
    print("\nEnter image path or type skip:")
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
            except Exception:
                print("  Could not open file, skipping image.")
    print("\nDescribe your problem:")
    desc = input("> ").strip()
    if not desc:
        print("  Problem description is required")
        if files and use_files:
            files["images"].close()
        return
    data = {"expert_id": str(expert_id), "problem_description": desc}
    if use_files:
        resp = requests.post(f"{API}/api/car/expert/request", headers=headers, files=files, data=data)
        files["images"].close()
    else:
        resp = requests.post(f"{API}/api/car/expert/request", headers=headers, json=data)
    if resp.status_code not in (200, 201):
        print("  Failed to create expert request")
        return
    request_id = resp.json().get("request_id")
    print("\nRequest sent successfully.")
    print("Waiting for expert response...")
    while True:
        print("\n1. View Conversation")
        print("2. Send Message")
        print("3. Check Status")
        print("4. Exit")
        choice = input("\nSelect option: ").strip()
        if choice == "1":
            mr = requests.get(f"{API}/api/car/expert/messages/{request_id}", headers=headers)
            if mr.status_code == 200:
                msgs = mr.json().get("messages", [])
                print("\n--- Conversation ---")
                for m in msgs:
                    prefix = "You" if m.get("sender_type") == "USER" else "Expert"
                    print(f"{prefix}: {m.get('message','')}")
            else:
                print("  Failed to load messages")
        elif choice == "2":
            msg = input("You: ").strip()
            if not msg:
                print("  Message cannot be empty")
                continue
            pr = requests.post(
                f"{API}/api/car/expert/message",
                headers=headers,
                json={"request_id": request_id, "message": msg},
            )
            if pr.status_code not in (200, 201):
                print("  Failed to send message")
        elif choice == "3":
            sr = requests.get(f"{API}/api/car/expert/request/{request_id}", headers=headers)
            if sr.status_code == 200:
                req = sr.json().get("request", {})
                print(f"\nStatus: {req.get('status','')}")
                mode = req.get("communication_mode") or "Not decided"
                print(f"Mode: {mode}")
                if req.get("status") == "COMPLETED":
                    print("Consultation completed")
            else:
                print("  Failed to load request status")
        elif choice == "4":
            break
        else:
            print("  Invalid choice")

