import logging
from datetime import datetime, timedelta
import random
from housekeeping.models.database import housekeeping_db
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

    def _normalize_date(self, date_str):
        """
        Normalize date string to 'YYYY-MM-DD' format
        """
        if not date_str:
            return ""
        try:
            # HTML5 date inputs are YYYY-MM-DD, but let's be robust
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
        except Exception as e:
            logging.error(f"Error normalizing date '{date_str}': {e}")
            
        return date_str

    def _normalize_time(self, time_str):
        """
        Normalize time string to 'HH:MM AM/PM' format (e.g., '9:00 AM' -> '09:00 AM')
        """
        if not time_str:
            return ""
        try:
            # Try to parse the time string
            # It could be '9:00 AM', '09:00 AM', '13:00', etc.
            t = None
            time_str = time_str.strip().upper()
            
            if 'AM' in time_str or 'PM' in time_str:
                # Handle AM/PM format
                try:
                    t = datetime.strptime(time_str, "%I:%M %p")
                except ValueError:
                    t = datetime.strptime(time_str, "%H:%M %p")
            else:
                # Handle 24h format
                t = datetime.strptime(time_str, "%H:%M")
                
            if t:
                return t.strftime("%I:%M %p")
        except Exception as e:
            logging.error(f"Error normalizing time '{time_str}': {e}")
            
        return time_str

    def get_aggregated_slots(self, service_type, date, worker_id=None):
        """
        Get available time slots for a given date and service type.
        Returns a list of dicts: [{"time": "09:00 AM", "count": 2}, ...]
        """
        date = self._normalize_date(date)
        # Define standard slots
        standard_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
        
        all_potential_slots = set(standard_slots)
        
        if worker_id:
            # Specific worker: only their slots + standard
            worker_slots = self.availability_db.get_availability(worker_id, date)
            for s in worker_slots:
                all_potential_slots.add(self._normalize_time(s['time_slot']))
        else:
            # General discovery: include ALL custom slots from ALL workers who offer this service
            # This ensures that if a worker added '08:30 AM', it shows up in the general list.
            workers = self.worker_db.get_workers_by_service('housekeeping')
            for w in workers:
                if self.db.worker_offers_service(w['id'], service_type):
                    w_slots = self.availability_db.get_availability(w['id'], date)
                    for s in w_slots:
                        all_potential_slots.add(self._normalize_time(s['time_slot']))
        
        # Convert to sorted list
        # Sorting "09:00 AM", "10:00 AM" correctly requires a bit of logic
        def sort_key(t_str):
            try:
                return datetime.strptime(t_str, "%I:%M %p")
            except:
                return datetime.min

        slots_to_check = sorted(list(all_potential_slots), key=sort_key)
        
        available_slots = []
        for time in slots_to_check:
            workers = self.check_availability(service_type, date, time, None, worker_id=worker_id)
            if workers:
                available_slots.append({
                    "time": time,
                    "count": len(workers)
                })
                
        return available_slots

    def check_availability(self, service_type, date, time, address, worker_id=None, booking_type='schedule'):
        """
        Check which workers are available for a given slot.
        """
        date = self._normalize_date(date)
        time = self._normalize_time(time)

        if worker_id:
            worker = self.worker_db.get_worker_by_id(worker_id)
            if not worker: 
                return []
            candidates = [worker]
        else:
            candidates = self.worker_db.get_workers_by_service('housekeeping')

        available_workers = []
        for worker in candidates:
            # 1. Check if worker offers the specific service
            if not self.db.worker_offers_service(worker['id'], service_type):
                continue

            # 2. Check online status
            is_online = self.db.get_worker_online_status(worker['id'])
            
            # For instant booking, worker MUST be online
            if booking_type == 'instant' and not is_online:
                continue

            # 3. Check for conflict in bookings
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT count(*) FROM bookings 
                WHERE worker_id = %s AND booking_date = %s AND time_slot = %s 
                AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
            """, (worker['id'], date, time))
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                continue

            # 4. Check explicit availability slots from provider
            # For scheduled bookings, we check if they've marked the slot as available
            # For instant bookings, being online is usually enough (on-demand), 
            # but let's check slots if they exist to be safe, or just online if no slots.
            worker_slots = self.availability_db.get_availability(worker['id'], date)
            
            # Normalize and check
            has_explicit_slot = any(self._normalize_time(s['time_slot']) == time for s in worker_slots)
            
            # If they have slots but NOT this one, skip (only for scheduled)
            if booking_type == 'schedule' and not has_explicit_slot:
                continue
            
            # If instant booking, and they have slots for today, they should have this slot or at least be online
            # Actually, most systems treat 'online' as 'available right now'.
            # If they are online, we include them for instant.
            
            worker['is_online'] = is_online
            available_workers.append(worker)
                
        return available_workers

    def create_booking_request(self, user_id, service_type, address, date, time, worker_id=None, home_size=None, add_ons=None, booking_type='schedule'):
        """
        Create a booking request.
        """
        # Normalize date and time
        date = self._normalize_date(date)
        time = self._normalize_time(time)
        
        # Calculate price (worker-specific if applicable). Supports size/area tiers.
        def compute_worker_price(w_id, svc_name, home_size, add_ons_text):
            import json as _json
            # Quick exit if no config
            # Try find detailed config
            conn = self.db.get_conn()
            cur = conn.cursor()
            try:
                cur.execute("SELECT id FROM services WHERE name = %s", (svc_name,))
                srow = cur.fetchone()
                if not srow:
                    return self.db.get_service_price(svc_name)
                sid = srow[0]
                cur.execute("SELECT price, pricing_json FROM worker_services WHERE worker_id = %s AND service_id = %s AND active = TRUE", (w_id, sid))
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
            SET status = 'IN_PROGRESS', otp = %s, started_at = %s, retry_count = 0
            WHERE id = %s
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
                cursor.execute("UPDATE bookings SET retry_count = retry_count + 1 WHERE id = %s", (booking_id,))
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
