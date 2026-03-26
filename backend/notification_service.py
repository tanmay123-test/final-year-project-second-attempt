# notification_service.py
# Central place for sending notifications
# For now -> EMAIL
# Later -> Firebase / WhatsApp plug-in ready

from email_service import send_email


import logging
import os

# Configure logging
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'notification.log')

logging.basicConfig(
    filename=LOG_FILE, 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ================= USER NOTIFICATION =================
def notify_user(email, subject, body):
    """
    Send notification to user.
    Currently email.
    Later we will plug Firebase here.
    """
    return send_email_notification(email, subject, body)


# ================= DOCTOR NOTIFICATION =================
def notify_doctor(email, subject, body):
    """
    Send notification to doctor.
    Currently email.
    Later WhatsApp/Firebase ready.
    """
    return send_email_notification(email, subject, body)


# ================= WORKER NOTIFICATION =================
def notify_worker(email, subject, body):
    """
    Send notification to worker (Housekeeping, etc).
    """
    return send_email_notification(email, subject, body)


# ================= GENERAL EMAIL FUNCTION =================
import time

# Simple in-memory cache for deduplication: {email_subject_body_hash: timestamp}
_email_cache = {}

def send_email_notification(to_email, subject, body):
    """
    General email sending function with error handling and deduplication.
    Prevents sending the exact same email to the same person within 60 seconds.
    """
    # Deduplication logic
    current_time = time.time()
    # Create a unique key for this email content
    email_key = f"{to_email}:{subject}:{body}"
    
    # Check cache
    if email_key in _email_cache:
        last_sent = _email_cache[email_key]
        if current_time - last_sent < 60: # 60 seconds window
            print(f"Duplicate email suppressed to {to_email}")
            logging.info(f"Duplicate email suppressed to: {to_email}")
            return True # Pretend it was sent

    print(f"  Attempting to send email to {to_email}")
    logging.info(f"Attempting to send generic email to: {to_email}")
    try:
        success = send_email(to_email, subject, body)
        if success:
            # Update cache
            _email_cache[email_key] = current_time
            
            # Clean up cache (optional, simple removing old keys)
            # For a long running process, we might want to periodically clear this dict,
            # but for this scope it's fine.
            if len(_email_cache) > 1000:
                _email_cache.clear()
                
            print(f"  Email sent successfully to {to_email}")
            logging.info(f"Successfully sent generic email to: {to_email}")
            return True
        else:
            print(f"  Email sending failed to {to_email}")
            logging.error(f"Failed to send generic email to: {to_email}")
            return False
    except Exception as e:
        print(f"  Email sending failed to {to_email}: {e}")
        logging.error(f"Exception sending generic email to {to_email}: {e}")
        return False
