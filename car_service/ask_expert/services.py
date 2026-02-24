import os
import shutil
from datetime import datetime
from .models import ask_expert_db
from .category_detector import detect_category
from .assignment_engine import assign_expert
from .summary_generator import generate_summary

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "uploads", "ask_expert")


def ensure_upload_dir():
    """Create upload directory if it doesn't exist"""
    path = os.path.abspath(UPLOAD_DIR)
    os.makedirs(path, exist_ok=True)
    
    # Create subdirectories for better organization
    subdirs = ['pending', 'approved', 'rejected']
    for subdir in subdirs:
        subdir_path = os.path.join(path, subdir)
        os.makedirs(subdir_path, exist_ok=True)
    
    return path


def allowed_image(filename: str) -> bool:
    """Check if file is allowed image type"""
    if not filename:
        return False
    ext = (filename or "").lower().rsplit(".", 1)[-1]
    return ext in ["jpg", "jpeg", "png", "webp", "gif", "bmp"]


def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)  # Convert to MB
    except:
        return 0


def create_request(user_id: int, description: str, user_city: str, images) -> int:
    """Create expert request with image upload and admin approval workflow"""
    category = detect_category(description)
    req_id = ask_expert_db.create_request(user_id, description, category, user_city)

    expert_id = assign_expert()
    if expert_id:
        ask_expert_db.assign_request(req_id, expert_id)
        ask_expert_db.set_busy(expert_id, True)
        ask_expert_db.update_last_assigned(expert_id)

    if images:
        base = ensure_upload_dir()
        pending_dir = os.path.join(base, 'pending', f'req_{req_id}')  # Request-specific pending folder
        
        for i, f in enumerate(images):
            if not f or not getattr(f, "filename", ""):
                continue
            if not allowed_image(f.filename):
                print(f"⚠️ Skipping invalid file: {f.filename}")
                continue
            
            # Generate unique filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            safe_name = f"{timestamp}_{i}_{f.filename}"
            save_path = os.path.join(pending_dir, safe_name)
            
            try:
                # Save file
                f.save(save_path)
                
                # Validate file
                file_size_mb = get_file_size_mb(save_path)
                if file_size_mb > 10:  # 10MB limit
                    os.remove(save_path)
                    print(f"⚠️ File too large ({file_size_mb:.1f}MB): {f.filename}")
                    continue
                
                # Record in database with PENDING status
                image_data = {
                    "file": safe_name,
                    "status": "pending",
                    "upload_time": datetime.utcnow().isoformat()
                }
                ask_expert_db.add_image_with_status(req_id, safe_name, "pending")
                print(f"✅ Image uploaded for admin review: {f.filename} ({file_size_mb:.1f}MB)")
                
            except Exception as e:
                print(f"❌ Error saving {f.filename}: {e}")
                # Clean up if save failed
                if os.path.exists(save_path):
                    os.remove(save_path)

    return req_id


def get_approved_images(request_id: int):
    """Get only approved images for expert viewing"""
    try:
        base = ensure_upload_dir()
        approved_dir = os.path.join(base, 'approved', f'req_{request_id}')
        
        if not os.path.exists(approved_dir):
            return []
        
        approved_images = []
        for filename in os.listdir(approved_dir):
            file_path = os.path.join(approved_dir, filename)
            if os.path.isfile(file_path):
                approved_images.append({
                    "filename": filename,
                    "path": file_path,
                    "size": get_file_size_mb(file_path)
                })
        
        return approved_images
    except Exception as e:
        print(f"Error getting approved images: {e}")
        return []


def get_pending_images_for_admin():
    """Get all pending images for admin review"""
    try:
        base = ensure_upload_dir()
        pending_dir = os.path.join(base, 'pending')
        
        pending_requests = []
        if not os.path.exists(pending_dir):
            return pending_requests
        
        # Scan all request folders in pending
        for folder_name in os.listdir(pending_dir):
            folder_path = os.path.join(pending_dir, folder_name)
            if os.path.isdir(folder_path) and folder_name.startswith('req_'):
                req_id = folder_name.replace('req_', '')
                
                # Get request details
                request_data = ask_expert_db.get_request(int(req_id))
                if request_data:
                    # Get images in this folder
                    images = []
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        if os.path.isfile(file_path):
                            images.append({
                                "filename": filename,
                                "path": file_path,
                                "size": get_file_size_mb(file_path)
                            })
                    
                    pending_requests.append({
                        "request_id": req_id,
                        "user_id": request_data[1],
                        "problem_description": request_data[3],
                        "category": request_data[4],
                        "location": request_data[5],
                        "images": images,
                        "created_at": request_data[7]
                    })
        
        return pending_requests
    except Exception as e:
        print(f"Error getting pending images: {e}")
        return []


def approve_images(request_id: int):
    """Approve images and move to approved folder"""
    try:
        base = ensure_upload_dir()
        pending_dir = os.path.join(base, 'pending', f'req_{request_id}')
        approved_dir = os.path.join(base, 'approved', f'req_{request_id}')
        
        if not os.path.exists(pending_dir):
            return False
        
        # Create approved folder if not exists
        os.makedirs(approved_dir, exist_ok=True)
        
        # Move all images from pending to approved
        moved_count = 0
        for filename in os.listdir(pending_dir):
            pending_path = os.path.join(pending_dir, filename)
            approved_path = os.path.join(approved_dir, filename)
            
            if os.path.isfile(pending_path):
                try:
                    shutil.move(pending_path, approved_path)
                    moved_count += 1
                    # Update database status
                    ask_expert_db.update_image_status(request_id, filename, "approved")
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
        
        # Remove empty pending folder
        if moved_count > 0:
            try:
                os.rmdir(pending_dir)
            except:
                pass
        
        print(f"✅ Approved and moved {moved_count} images for request {request_id}")
        return True
    except Exception as e:
        print(f"Error approving images: {e}")
        return False


def reject_images(request_id: int):
    """Reject images and move to rejected folder"""
    try:
        base = ensure_upload_dir()
        pending_dir = os.path.join(base, 'pending', f'req_{request_id}')
        rejected_dir = os.path.join(base, 'rejected', f'req_{request_id}')
        
        if not os.path.exists(pending_dir):
            return False
        
        # Create rejected folder if not exists
        os.makedirs(rejected_dir, exist_ok=True)
        
        # Move all images from pending to rejected
        moved_count = 0
        for filename in os.listdir(pending_dir):
            pending_path = os.path.join(pending_dir, filename)
            rejected_path = os.path.join(rejected_dir, filename)
            
            if os.path.isfile(pending_path):
                try:
                    shutil.move(pending_path, rejected_path)
                    moved_count += 1
                    # Update database status
                    ask_expert_db.update_image_status(request_id, filename, "rejected")
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
        
        # Remove empty pending folder
        if moved_count > 0:
            try:
                os.rmdir(pending_dir)
            except:
                pass
        
        print(f"❌ Rejected and moved {moved_count} images for request {request_id}")
        return True
    except Exception as e:
        print(f"Error rejecting images: {e}")
        return False


def add_message(request_id: int, sender_type: str, sender_id: int, message_text: str):
    ask_expert_db.add_message(request_id, sender_type.upper(), sender_id, message_text)


def get_messages(request_id: int):
    return ask_expert_db.get_messages(request_id)


def mark_resolved(request_id: int):
    ask_expert_db.mark_resolved(request_id)
    generate_summary(request_id)
