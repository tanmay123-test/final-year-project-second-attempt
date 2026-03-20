import logging
from datetime import datetime, timedelta
import random
from services.housekeeping.models.database import housekeeping_db
from worker_db import WorkerDB
from user_db import UserDB
from availability_db import AvailabilityDB
from notification_service import notify_user, notify_worker

class BookingService:
    def __init__(self):
        self.db = housekeeping_db
        self.worker_db = WorkerDB()
        self.user_db = UserDB()
        self.availability_db = AvailabilityDB()

    def get_service_types(self, worker_id=None):
        """
        Get all available service types.
        """
        if worker_id:
            return self.db.get_services_for_worker(worker_id)
        return self.db.get_all_services_with_base()

    def get_top_cleaners(self):
        """
        Get all housekeeping workers, sorted by online status.
        """
        # Get all workers with 'housekeeping' service
        # Note: WorkerDB.get_workers_by_service might return dicts
        workers = self.worker_db.get_workers_by_service('housekeeping')
        
        # Enrich with online status
        for w in workers:
            w['is_online'] = self.db.get_worker_online_status(w['id'])
        
        # Sort by online status (online first)
        workers.sort(key=lambda x: x.get('is_online', False), reverse=True)
        return workers

    def get_aggregated_slots(self, service_type, date, worker_id=None):
        """
        Get available time slots for a given date and service type.
        """
        slots = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
        available_slots = []
        
        for time in slots:
            workers = self.check_availability(service_type, date, time, None, worker_id=worker_id)
            if workers:
                available_slots.append(time)
                
        return available_slots

    def check_availability(self, service_type, date, time, address, worker_id=None, booking_type='schedule'):
        """
        Check which workers are available for a given slot.
        """
        if worker_id:
            worker = self.worker_db.get_worker_by_id(worker_id)
            if not worker: 
                return []
            candidates = [worker]
        else:
            candidates = self.worker_db.get_workers_by_service('housekeeping')

        available_workers = []
        for worker in candidates:
            # check if worker is online
            is_online = self.db.get_worker_online_status(worker['id'])
            
            # RULE 1: For instant booking, worker MUST be online
            if booking_type == 'instant' and not is_online:
                continue
                
            # RULE 2: For scheduled (available) booking, online workers are reserved for instant ONLY
            # (as per user requirement to prevent available booking for online workers)
            if booking_type == 'schedule' and is_online:
                continue

            # RULE 3: For scheduled (available) booking, worker must have marked this slot as available
            if booking_type == 'schedule':
                slots = self.availability_db.get_availability(worker['id'], date)
                is_available = any(s['time_slot'] == time for s in slots)
                if not is_available:
                    continue

            # check if worker has a booking at this time
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT count(*) FROM bookings 
                WHERE worker_id = ? AND booking_date = ? AND time_slot = ? 
                AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
            """, (worker['id'], date, time))
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                worker['is_online'] = is_online
                available_workers.append(worker)
                
        return available_workers

    def create_booking_request(self, user_id, service_type, address, date, time, worker_id=None, home_size=None, add_ons=None, booking_type='schedule'):
        """
        Create a booking request.
        """
        # Calculate price (worker-specific if applicable). Supports size/area tiers.
        def compute_worker_price(w_id, svc_name, home_size, add_ons_text):
            import json as _json
            # Quick exit if no config
            # Try find detailed config
            conn = self.db.get_conn()
            cur = conn.cursor()
            try:
                cur.execute("SELECT id FROM services WHERE name = ?", (svc_name,))
                srow = cur.fetchone()
                if not srow:
                    return self.db.get_service_price(svc_name)
                sid = srow[0]
                cur.execute("SELECT price, pricing_json FROM worker_services WHERE worker_id = ? AND service_id = ? AND active = 1", (w_id, sid))
                ws = cur.fetchone()
                if not ws:
                    return self.db.get_service_price(svc_name)
                default_price = ws[0] or 0.0
                cfg = None
                if ws[1]:
                    try:
                        cfg = _json.loads(ws[1])
                    except Exception:
                        cfg = None
                if not cfg:
                    return default_price if default_price > 0 else self.db.get_service_price(svc_name)
                # Size-based
                sizes = (cfg.get('sizes') or {})
                custom_cfg = (cfg.get('custom') or {})
                if home_size:
                    if home_size in sizes and sizes[home_size].get('enabled'):
                        p = float(sizes[home_size].get('price', 0))
                        if p > 0:
                            return p
                    # custom area
                    if home_size.startswith('Custom') and custom_cfg.get('enabled'):
                        # Expect pattern "Custom: <area> sqft"
                        import re
                        m = re.search(r'(\d+(\.\d+)?)', home_size)
                        if m:
                            area = float(m.group(1))
                            rate = float(custom_cfg.get('per_sqft', 0))
                            if rate > 0 and area > 0:
                                return round(rate * area, 2)
                # fallback
                return default_price if default_price > 0 else self.db.get_service_price(svc_name)
            finally:
                conn.close()

        if worker_id:
            if not self.db.worker_offers_service(worker_id, service_type):
                return {"error": "Selected worker does not offer this service"}
            
            is_online = self.db.get_worker_online_status(worker_id)
            
            # RULE 1: For instant booking, worker MUST be online
            if booking_type == 'instant':
                if not is_online:
                    return {"error": "Worker is currently offline and unavailable for instant booking"}
            
            # RULE 2: For scheduled (available) booking, online workers are reserved for instant ONLY
            if booking_type == 'schedule':
                if is_online:
                    return {"error": "This worker is currently online for instant booking. Please use Instant Booking or choose another worker."}
                
                # RULE 3: For scheduled (available) booking, worker must have marked this slot as available
                slots = self.availability_db.get_availability(worker_id, date)
                if not any(s['time_slot'] == time for s in slots):
                    return {"error": "Worker has not listed availability for this time slot"}

            # Check for conflicting bookings
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT count(*) FROM bookings 
                WHERE worker_id = ? AND booking_date = ? AND time_slot = ? 
                AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
            """, (worker_id, date, time))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return {"error": "Worker already has a booking for this time slot"}
            conn.close()

            price = compute_worker_price(worker_id, service_type, home_size, add_ons)
        else:
            price = self.db.get_service_price(service_type)
        # Add-ons logic could be added here
        
        status = 'REQUESTED' if worker_id else 'PENDING'
        
        booking_id, msg = self.db.create_booking_atomic(
            user_id, service_type, address, date, time, price, 
            worker_id=worker_id, status=status,
            home_size=home_size, add_ons=add_ons, booking_type=booking_type
        )
        
        if booking_id:
            # Notify worker if assigned
            if worker_id:
                self._notify_worker(worker_id, booking_id, "New Booking Request", f"You have a new booking request for {service_type} on {date} at {time}.")
            
            return {
                "success": True, 
                "booking_id": booking_id, 
                "status": status, 
                "worker_id": worker_id,
                "price": price,
                "message": "Booking created successfully"
            }
        else:
            return {"error": msg}

    def cancel_booking(self, booking_id, user_id):
        """
        Cancel a booking.
        """
        booking = self.db.get_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found"
        if str(booking.get('user_id')) != str(user_id):
            return False, "Unauthorized: You do not own this booking"
        if booking.get('status') in ('CANCELLED', 'COMPLETED'):
            return False, f"Cannot cancel a {booking.get('status').lower()} booking"
        updated = self.db.update_booking_status(booking_id, 'CANCELLED')
        if not updated:
            return False, "Failed to cancel booking"
        # Notify worker
        if booking.get('worker_id'):
            try:
                self._notify_worker(booking['worker_id'], booking_id, "Booking Cancelled", f"Booking #{booking_id} has been cancelled by the user.")
            except Exception:
                pass
        return True, "Booking cancelled"

    def update_booking_status_by_worker(self, booking_id, worker_id, status):
        """
        Update booking status by worker (Accept/Decline).
        """
        booking = self.db.get_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found", None
            
        if status == 'ACCEPTED':
            # Verify assignment
            if booking['worker_id'] and str(booking['worker_id']) != str(worker_id):
                 return False, "This booking is assigned to another worker", None
            
            if self.db.update_booking_status(booking_id, 'ACCEPTED', worker_id=worker_id):
                # Notify User
                self._notify_user(booking['user_id'], booking_id, "Booking Accepted", f"Your booking #{booking_id} has been accepted by the worker.")
                return True, "Booking accepted", 'ACCEPTED'
                
        elif status == 'DECLINED':
            if self.db.update_booking_status(booking_id, 'DECLINED'):
                # Notify User
                self._notify_user(booking['user_id'], booking_id, "Booking Declined", f"Your booking #{booking_id} has been declined by the worker.")
                return True, "Booking declined", 'DECLINED'
                
        return False, "Invalid status update", None

    def start_job(self, booking_id, worker_id):
        """
        Worker starts the job.
        1. Validate booking and worker.
        2. Generate OTP.
        3. Update status to IN_PROGRESS.
        4. Store OTP and started_at.
        5. Notify User with OTP.
        """
        booking = self.db.get_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found", None
        
        if str(booking['worker_id']) != str(worker_id):
            return False, "Unauthorized worker", None
            
        if booking['status'] != 'ACCEPTED':
            return False, f"Cannot start job in '{booking['status']}' state. Must be ACCEPTED.", None
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        started_at = datetime.now().isoformat()
        
        # Update DB
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            UPDATE bookings 
            SET status = 'IN_PROGRESS', otp = ?, started_at = ?, retry_count = 0
            WHERE id = ?
            """, (otp, started_at, booking_id))
            conn.commit()
            
            # Notify User
            user_msg = f"Your housekeeping service has started. Please share this OTP with the worker to complete the job: {otp}"
            self._notify_user(booking['user_id'], booking_id, "Service Started - OTP Inside", user_msg)
            
            logging.info(f"[AUDIT] Job started for booking {booking_id} by worker {worker_id} at {started_at}")
            return True, "Job started successfully", otp
        except Exception as e:
            logging.error(f"[ERROR] Error starting job for booking {booking_id}: {e}")
            return False, str(e), None
        finally:
            conn.close()

    def complete_job(self, booking_id, worker_id, provided_otp):
        """
        Worker completes the job using OTP.
        1. Validate booking and worker.
        2. Verify OTP.
        3. Update status to COMPLETED.
        """
        booking = self.db.get_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found"
        
        if str(booking['worker_id']) != str(worker_id):
            return False, "Unauthorized worker"
            
        if booking['status'] != 'IN_PROGRESS':
            return False, f"Cannot complete job in '{booking['status']}' state. Must be IN_PROGRESS."
        
        if not booking.get('otp'):
            return False, "System Error: No OTP found for this active job."
            
        # Check Retry Count
        retry_count = booking.get('retry_count', 0)
        if retry_count >= 5:
            return False, "Too many failed attempts. Please contact support."
        
        # Check OTP Expiry (8 hours)
        if booking.get('started_at'):
            started_at = datetime.fromisoformat(booking['started_at'])
            if datetime.now() > started_at + timedelta(hours=8):
                 return False, "OTP has expired. Please contact support or request manual completion."
        
        # Verify OTP
        if str(booking['otp']).strip() != str(provided_otp).strip():
            # Increment retry count
            conn = self.db.get_conn()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE bookings SET retry_count = retry_count + 1 WHERE id = ?", (booking_id,))
                conn.commit()
            finally:
                conn.close()
            
            logging.warning(f"[AUDIT] Invalid OTP attempt for booking {booking_id} by worker {worker_id}. Retry count: {retry_count + 1}")
            return False, f"Invalid OTP. {4 - retry_count} attempts remaining."
        
        # Update DB
        if self.db.update_booking_status(booking_id, 'COMPLETED'):
             self._notify_user(booking['user_id'], booking_id, "Service Completed", "Your housekeeping service has been marked as completed. Thank you!")
             logging.info(f"[AUDIT] Job completed successfully for booking {booking_id} by worker {worker_id}")
             return True, "Job completed successfully"
        else:
             logging.error(f"[ERROR] Database error updating status to COMPLETED for booking {booking_id}")
             return False, "Database error updating status"

    def _notify_user(self, user_id, booking_id, subject, message):
        """
        Send notification to user.
        """
        try:
            user = self.user_db.get_user_by_id(user_id)
            if user and user.get('email'):
                notify_user(user['email'], subject, message)
                logging.info(f"[AUDIT] Notification sent to user {user_id} for booking {booking_id}: {subject}")
            else:
                logging.warning(f"[AUDIT] Failed to notify user {user_id}: User or email not found")
        except Exception as e:
            logging.error(f"[ERROR] Failed to notify user {user_id}: {e}")

    def _notify_worker(self, worker_id, booking_id, subject, message):
        """
        Send notification to worker.
        """
        try:
            worker = self.worker_db.get_worker_by_id(worker_id)
            if worker and worker.get('email'):
                notify_worker(worker['email'], subject, message)
                logging.info(f"[AUDIT] Notification sent to worker {worker_id} for booking {booking_id}: {subject}")
        except Exception as e:
            logging.error(f"[ERROR] Failed to notify worker {worker_id}: {e}")
