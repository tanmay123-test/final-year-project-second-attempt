"""
Tow Truck Services Logic
"""
from datetime import datetime

def set_online(worker_id): 
    from .db import get_connection 
    conn = get_connection() 
    cursor = conn.cursor() 
 
    cursor.execute(""" 
        UPDATE tow_operator_profiles 
        SET is_online = 1 
        WHERE worker_id = ? 
    """, (worker_id,)) 
 
    conn.commit() 
    conn.close() 
 
def set_offline(worker_id): 
    from .db import get_connection 
    conn = get_connection() 
    cursor = conn.cursor() 
 
    cursor.execute(""" 
        UPDATE tow_operator_profiles 
        SET is_online = 0, is_busy = 0 
        WHERE worker_id = ? 
    """, (worker_id,)) 
 
    conn.commit() 
    conn.close() 

def fetch_requests(): 
    from .db import get_connection 
    conn = get_connection() 
    cursor = conn.cursor() 
 
    cursor.execute(""" 
        SELECT id, pickup_location, drop_location, vehicle_type, distance, estimated_earning 
        FROM tow_requests 
        WHERE status = 'SEARCHING' 
    """) 
 
    rows = cursor.fetchall() 
    conn.close() 
 
    return [ 
         { 
             "id": r[0], 
             "pickup": r[1], 
             "drop": r[2], 
             "vehicle": r[3], 
             "distance": r[4], 
             "earning": r[5] 
         } 
         for r in rows 
     ] 

def fetch_active_jobs(worker_id):
    from .db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, request_id, user_name, pickup_location, drop_location, status
        FROM tow_active_jobs
        WHERE operator_id = ? AND status != 'COMPLETED'
    """, (worker_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": r[0],
            "request_id": r[1],
            "user": r[2],
            "pickup": r[3],
            "drop": r[4],
            "status": r[5]
        }
        for r in rows
    ]

def fetch_earnings(worker_id):
    from .db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(final_amount) FROM tow_earnings WHERE operator_id = ?
    """, (worker_id,))
    total = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT SUM(final_amount) FROM tow_earnings 
        WHERE operator_id = ? AND DATE(created_at) = DATE('now')
    """, (worker_id,))
    today = cursor.fetchone()[0] or 0
    
    conn.close()
    return {"total": total, "today": today}

def accept_job(worker_id, request_id):
    from .db import get_connection
    import random
    otp = str(random.randint(1000, 9999))
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Update request status
        cursor.execute("UPDATE tow_requests SET status = 'ASSIGNED', assigned_operator_id = ? WHERE id = ?", (worker_id, request_id))
        
        # Get user details from request
        cursor.execute("SELECT user_id, pickup_location, drop_location FROM tow_requests WHERE id = ?", (request_id,))
        req = cursor.fetchone()
        
        if req:
            user_id, pickup, drop = req
            # Create active job
            cursor.execute("""
                INSERT INTO tow_active_jobs (request_id, operator_id, pickup_location, drop_location, status, otp)
                VALUES (?, ?, ?, ?, 'ACCEPTED', ?)
            """, (request_id, worker_id, pickup, drop, otp))
            
            # Update operator status
            cursor.execute("UPDATE tow_operator_profiles SET is_busy = 1 WHERE worker_id = ?", (worker_id,))
            
            conn.commit()
            return {"success": True, "otp": otp}
        return {"success": False, "error": "Request not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

def start_job(worker_id, job_id, otp):
    from .db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT otp FROM tow_active_jobs WHERE id = ?", (job_id,))
        res = cursor.fetchone()
        if res and res[0] == otp:
            cursor.execute("UPDATE tow_active_jobs SET status = 'IN_PROGRESS', start_time = ? WHERE id = ?", (str(datetime.now()), job_id))
            conn.commit()
            return {"success": True}
        return {"success": False, "error": "Invalid OTP"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

def complete_job(worker_id, job_id):
    from .db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE tow_active_jobs SET status = 'COMPLETED', completion_time = ? WHERE id = ?", (str(datetime.now()), job_id))
        
        # Free up operator
        cursor.execute("UPDATE tow_operator_profiles SET is_busy = 0 WHERE worker_id = ?", (worker_id,))
        
        # Create earnings entry
        cursor.execute("SELECT request_id FROM tow_active_jobs WHERE id = ?", (job_id,))
        req_id = cursor.fetchone()[0]
        cursor.execute("SELECT estimated_earning FROM tow_requests WHERE id = ?", (req_id,))
        earning = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO tow_earnings (operator_id, job_id, base_amount, final_amount)
            VALUES (?, ?, ?, ?)
        """, (worker_id, job_id, earning, earning))
        
        conn.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

def get_job_status(request_id):
    from .db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT status, otp FROM tow_active_jobs WHERE request_id = ?", (request_id,))
        res = cursor.fetchone()
        if res:
            return {"status": res[0], "otp": res[1]}
        return {"status": "SEARCHING"}
    except Exception:
        return {"status": "UNKNOWN"}
    finally:
        conn.close()

