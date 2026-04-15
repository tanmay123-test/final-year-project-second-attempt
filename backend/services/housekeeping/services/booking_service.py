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
            services = self.db.get_services_for_worker(worker_id)
            if services:
                return services
            # Fallback to all services if worker has none configured
            logging.info(f"Worker {worker_id} has no configured services, falling back to defaults")
            
        return self.db.get_all_services_with_base()

    def get_top_cleaners(self):
        """
        Get all housekeeping workers, sorted by online status.
        """
        # Get all workers with 'housekeeping' service
        workers = self.worker_db.get_workers_by_service('housekeeping')
        if not workers:
            # Fallback to general cleaning if no specific housekeeping workers
            workers = self.worker_db.get_workers_by_service('cleaning')
        
        # Enrich with online status
        for w in workers:
            w['is_online'] = self.db.get_worker_online_status(w['id'])
            # Ensure price is available for UI
            if 'price' not in w or not w['price']:
                # Get first active service price or base price
                services = self.db.get_services_for_worker(w['id'])
                if services:
                    w['price'] = services[0]['price']
                else:
                    w['price'] = 500 # Default
        
        # Sort by online status (online first)
        workers.sort(key=lambda x: x.get('is_online', False), reverse=True)
        return workers

    def _normalize_date(self, date_str):
        """
        Normalize date string to 'YYYY-MM-DD' format.
        """
        if not date_str:
            return ""
        
        import re
        if re.match(r'^\d{4}-\d{2}-\d{2}$', str(date_str)):
            return date_str

        try:
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%m-%d-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    res = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                    return res
                except ValueError:
                    continue
        except Exception as e:
            logging.error(f"Error normalizing date '{date_str}': {e}")
            
        return date_str

    def _normalize_time(self, time_str):
        """
        Normalize time string to 'HH:MM AM/PM' format.
        """
        if not time_str:
            return ""
        try:
            t = None
            time_str = time_str.strip().upper()
            
            if 'AM' in time_str or 'PM' in time_str:
                try:
                    t = datetime.strptime(time_str, "%I:%M %p")
                except ValueError:
                    t = datetime.strptime(time_str, "%H:%M %p")
            else:
                t = datetime.strptime(time_str, "%H:%M")
                
            if t:
                return t.strftime("%I:%M %p")
        except Exception as e:
            logging.error(f"Error normalizing time '{time_str}': {e}")
            
        return time_str

    def get_aggregated_slots(self, service_type, date, worker_id=None):
        """
        Get available time slots for a given date and service type.
        """
        date = self._normalize_date(date)
        standard_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
        
        if worker_id:
            worker = self.worker_db.get_worker_by_id(worker_id)
            candidates = [worker] if worker else []
        else:
            candidates = self.worker_db.get_workers_by_service('housekeeping')
            if not candidates:
                candidates = self.worker_db.get_workers_by_service('cleaning')

        if not candidates:
            return []

        worker_ids = [w['id'] for w in candidates]
        online_statuses = {w_id: self.db.get_worker_online_status(w_id) for w_id in worker_ids}

        worker_slots_map = {w_id: [] for w_id in worker_ids}
        try:
            conn = self.availability_db.get_conn()
            cursor = conn.cursor()
            query = "SELECT worker_id, time_slot FROM availability WHERE worker_id IN ({}) AND date = %s".format(','.join(['%s']*len(worker_ids)))
            cursor.execute(query, tuple(worker_ids) + (date,))
            for row in cursor.fetchall():
                worker_slots_map[row[0]].append(self._normalize_time(row[1]))
            conn.close()
        except Exception as e:
            print(f"  Batch availability fetch error: {e}")

        bookings_map = {}
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            query = """
                SELECT worker_id, time_slot FROM bookings 
                WHERE booking_date = %s AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
            """
            cursor.execute(query, (date,))
            for row in cursor.fetchall():
                key = (row[0], self._normalize_time(row[1]))
                bookings_map[key] = bookings_map.get(key, 0) + 1
            conn.close()
        except Exception as e:
            print(f"  Batch bookings fetch error: {e}")

        all_potential_slots = set(standard_slots)
        for w_id, slots in worker_slots_map.items():
            for s in slots:
                all_potential_slots.add(s)

        def sort_key(t_str):
            try: return datetime.strptime(t_str, "%I:%M %p")
            except: return datetime.min

        slots_to_check = sorted(list(all_potential_slots), key=sort_key)
        available_slots = []

        for time in slots_to_check:
            count = 0
            for worker in candidates:
                w_id = worker['id']
                is_online = online_statuses.get(w_id, False)
                w_slots = worker_slots_map.get(w_id, [])
                has_explicit_slot = time in w_slots
                
                if bookings_map.get((w_id, time), 0) > 0:
                    continue

                if worker_id:
                    if not has_explicit_slot:
                        continue
                else:
                    if not has_explicit_slot:
                        continue
                count += 1
            
            if count > 0:
                available_slots.append({"time": time, "count": count})

        return available_slots

    def check_availability(self, service_type, date, time, address=None, worker_id=None, booking_type='schedule'):
        """
        Check which workers are available for a given service, date, and time.
        """
        if time == 'Instant':
            time = datetime.now().strftime("%I:%M %p")
            
        date = self._normalize_date(date)
        time = self._normalize_time(time)

        if worker_id:
            worker = self.worker_db.get_worker_by_id(worker_id)
            candidates = [worker] if worker else []
        else:
            candidates = self.worker_db.get_workers_by_service('housekeeping')
            if not candidates:
                candidates = self.worker_db.get_workers_by_service('cleaning')

        if not candidates:
            return []

        worker_ids = [w['id'] for w in candidates]
        online_statuses = {w_id: self.db.get_worker_online_status(w_id) for w_id in worker_ids}

        worker_slots_map = {w_id: [] for w_id in worker_ids}
        try:
            conn = self.availability_db.get_conn()
            cursor = conn.cursor()
            query = "SELECT worker_id, time_slot FROM availability WHERE worker_id IN ({}) AND date = %s".format(','.join(['%s']*len(worker_ids)))
            cursor.execute(query, tuple(worker_ids) + (date,))
            for row in cursor.fetchall():
                worker_slots_map[row[0]].append(self._normalize_time(row[1]))
            conn.close()
        except Exception as e:
            print(f"  check_availability batch slots error: {e}")

        bookings_map = {}
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT worker_id FROM bookings 
                WHERE booking_date = %s AND time_slot = %s 
                AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
            """, (date, time))
            for row in cursor.fetchall():
                bookings_map[row[0]] = True
            conn.close()
        except Exception as e:
            print(f"  check_availability batch bookings error: {e}")

        available_workers = []
        for worker in candidates:
            w_id = worker['id']
            is_online = online_statuses.get(w_id, False)
            w_slots = worker_slots_map.get(w_id, [])
            has_explicit_slot = time in w_slots

            if bookings_map.get(w_id, 0) > 0:
                continue

            if booking_type == 'instant':
                # For instant booking, accept any worker (online preferred)
                pass
            else:
                if not has_explicit_slot:
                    continue

            worker['is_online'] = is_online
            available_workers.append(worker)

        # For instant booking, prefer online workers but fall back to all if none online
        if booking_type == 'instant' and available_workers:
            online_workers = [w for w in available_workers if w.get('is_online')]
            if online_workers:
                return online_workers

        return available_workers

    def create_booking_request(self, user_id, service_type, address, date, time, worker_id=None, home_size=None, add_ons=None, booking_type='schedule'):
        """
        Create a booking request.
        """
        if time == 'Instant':
            time = datetime.now().strftime("%I:%M %p")
            
        date = self._normalize_date(date)
        time = self._normalize_time(time)

        def compute_worker_price(w_id, svc_name, home_size, add_ons_text):
            import json as _json
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
                sizes = (cfg.get('sizes') or {})
                custom_cfg = (cfg.get('custom') or {})
                if home_size:
                    if home_size in sizes and sizes[home_size].get('enabled'):
                        p = float(sizes[home_size].get('price', 0))
                        if p > 0:
                            return p
                    if home_size.startswith('Custom') and custom_cfg.get('enabled'):
                        import re
                        m = re.search(r'(\d+(\.\d+)?)', home_size)
                        if m:
                            area = float(m.group(1))
                            rate = float(custom_cfg.get('per_sqft', 0))
                            if rate > 0 and area > 0:
                                return round(rate * area, 2)
                return default_price if default_price > 0 else self.db.get_service_price(svc_name)
            finally:
                conn.close()

        if worker_id:
            if not self.db.worker_offers_service(worker_id, service_type):
                return {"error": "Selected worker does not offer this service"}
            
            is_online = self.db.get_worker_online_status(worker_id)
            slots = self.availability_db.get_availability(worker_id, date)
            has_explicit_slot = any(self._normalize_time(s['time_slot']) == time for s in slots)

            if booking_type != 'instant' and not has_explicit_slot:
                return {"error": "Worker has not listed availability for this time slot"}

            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT count(*) FROM bookings 
                WHERE worker_id = %s AND booking_date = %s AND time_slot = %s 
                AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
            """, (worker_id, date, time))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return {"error": "Worker already has a booking for this time slot"}
            conn.close()

            price = compute_worker_price(worker_id, service_type, home_size, add_ons)
        else:
            price = self.db.get_service_price(service_type)
        
        if worker_id:
            is_online = self.db.get_worker_online_status(worker_id)
            status = 'ASSIGNED' if booking_type == 'instant' and is_online else 'REQUESTED'
        else:
            status = 'PENDING'
        
        booking_id, msg = self.db.create_booking_atomic(
            user_id, service_type, address, date, time, price, 
            worker_id=worker_id, status=status,
            home_size=home_size, add_ons=add_ons, booking_type=booking_type
        )
        
        if booking_id:
            if worker_id and status == 'ASSIGNED':
                self._notify_worker(worker_id, booking_id, "New Booking Assigned", f"You have been assigned a new booking for {service_type} on {date} at {time}.")
            elif worker_id and status == 'REQUESTED':
                self._notify_worker(worker_id, booking_id, "Booking Request", f"You have a new booking request for {service_type} on {date} at {time}. Please accept if you're available.")
            
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
            if booking['worker_id'] and str(booking['worker_id']) != str(worker_id):
                 return False, "This booking is assigned to another worker", None
            
            if self.db.update_booking_status(booking_id, 'ACCEPTED', worker_id=worker_id):
                self._notify_user(booking['user_id'], booking_id, "Booking Accepted", f"Your booking #{booking_id} has been accepted by the worker.")
                return True, "Booking accepted", 'ACCEPTED'
                
        elif status == 'DECLINED':
            if self.db.update_booking_status(booking_id, 'DECLINED'):
                self._notify_user(booking['user_id'], booking_id, "Booking Declined", f"Your booking #{booking_id} has been declined by the worker.")
                return True, "Booking declined", 'DECLINED'
                
        return False, "Invalid status update", None

    def start_job(self, booking_id, worker_id):
        """
        Worker starts the job. Generates OTP and notifies user.
        """
        booking = self.db.get_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found", None

        if str(booking['worker_id']) != str(worker_id):
            return False, "Unauthorized worker", None

        if booking['status'] != 'ACCEPTED':
            return False, f"Cannot start job in '{booking['status']}' state. Must be ACCEPTED.", None

        otp = str(random.randint(100000, 999999))
        started_at = datetime.now().isoformat()

        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            UPDATE bookings
            SET status = 'IN_PROGRESS', otp = %s, started_at = %s, retry_count = 0
            WHERE id = %s
            """, (otp, started_at, booking_id))
            conn.commit()
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            logging.error(f"[ERROR] Error starting job for booking {booking_id}: {e}")
            return False, str(e), None
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

        # Notify user with OTP — done AFTER commit so DB is consistent
        try:
            user_msg = (
                f"Your housekeeping service has started!\n\n"
                f"OTP to complete the job: {otp}\n\n"
                f"Share this OTP with the worker when the job is done."
            )
            self._notify_user(
                booking['user_id'], booking_id,
                "Service Started — Your OTP is Inside", user_msg
            )
        except Exception as e:
            logging.warning(f"[WARN] OTP notification failed for booking {booking_id}: {e}")
            # Don't fail the whole operation — job is started, OTP is in DB

        logging.info(f"[AUDIT] Job started for booking {booking_id} by worker {worker_id} at {started_at}")
        return True, "Job started successfully", otp

    def complete_job(self, booking_id, worker_id, provided_otp):
        """
        Worker completes the job using OTP.
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
            
        retry_count = booking.get('retry_count', 0)
        if retry_count >= 5:
            return False, "Too many failed attempts. Please contact support."
        
        if booking.get('started_at'):
            started_at = datetime.fromisoformat(booking['started_at'])
            if datetime.now() > started_at + timedelta(hours=8):
                 return False, "OTP has expired. Please contact support or request manual completion."
        
        if str(booking['otp']).strip() != str(provided_otp).strip():
            conn = self.db.get_conn()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE bookings SET retry_count = retry_count + 1 WHERE id = %s", (booking_id,))
                conn.commit()
            finally:
                conn.close()
            
            logging.warning(f"[AUDIT] Invalid OTP attempt for booking {booking_id} by worker {worker_id}. Retry count: {retry_count + 1}")
            return False, f"Invalid OTP. {4 - retry_count} attempts remaining."
        
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

    def get_worker_bookings(self, worker_id):
        """
        Get all bookings for a specific worker with user details.
        """
        bookings = self.db.get_worker_bookings(worker_id)
        
        # Enrich with user details (names)
        for b in bookings:
            user = self.user_db.get_user_by_id(b['user_id'])
            if user:
                b['user_name'] = user.get('full_name') or user.get('name') or "Client"
                b['user_phone'] = user.get('phone')
            else:
                b['user_name'] = "Client"
                
        return bookings
