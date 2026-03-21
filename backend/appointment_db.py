# appointment_db.py
import os
import psycopg2
import psycopg2.extras
import random
import string
from dotenv import load_dotenv
from availability_db import AvailabilityDB
from datetime import datetime, timedelta

load_dotenv()

class AppointmentDB:

    def __init__(self):
        print("🔥 AppointmentDB LOADED")
        self.availability_db = AvailabilityDB()
        self.create_table()

    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    # =========================================================
    # CREATE TABLE (VIDEO + CLINIC SUPPORTED)
    # =========================================================
    def create_table(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                worker_id INTEGER,
                user_name TEXT,
                patient_symptoms TEXT,
                booking_date TEXT,
                time_slot TEXT,
                appointment_type TEXT,
                status TEXT DEFAULT 'pending',

                meeting_link TEXT,
                doctor_otp TEXT,
                otp_verified BOOLEAN DEFAULT FALSE,
                
                -- Video consultation specific fields
                video_room TEXT,
                video_status TEXT DEFAULT 'ready',
                prescription_file TEXT,
                insurance_details TEXT,
                
                -- Payment fields
                payment_status TEXT DEFAULT 'pending',
                payment_amount INTEGER,
                razorpay_order_id TEXT,
                razorpay_payment_id TEXT,
                payout_status TEXT DEFAULT 'pending',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # UTIL FUNCTIONS
    # =========================================================
    def _generate_meeting_link(self):
        code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"https://expertease.app/meet/{code}"

    def _generate_otp(self):
        return str(random.randint(100000, 999999))

    # =========================================================
    # VIDEO REQUEST (USER SIDE)
    # =========================================================
    def book_video(self, user_id, worker_id, user_name, symptoms, insurance_details=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Set booking_date to today and time_slot to a default for video consultations
            today = datetime.now().strftime('%Y-%m-%d')
            default_time = "ASAP (Video Call)"
            
            # Generate unique video room
            room_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            video_room = f"room_{room_code}"

            cursor.execute("""
            INSERT INTO appointments
            (user_id, worker_id, user_name, patient_symptoms,
             booking_date, time_slot, appointment_type, status, video_room, video_status, insurance_details)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (user_id, worker_id, user_name, symptoms, today, default_time, 'video', 'pending', video_room, 'ready', insurance_details))

            apt_id = cursor.fetchone()[0]
            conn.commit()
            
            print(f"📹 Video consultation booked with ID: {apt_id}")
            print(f"📅 Date: {today}")
            print(f"⏰ Time: {default_time}")
            print(f"🔗 Video Room: {video_room}")
            
            return apt_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # CLINIC BOOKING (ENHANCED)
    # =========================================================
    def book_clinic(self, user_id, worker_id, user_name, symptoms, date, time_slot, insurance_details=None):
        """
        Book clinic appointment with enhanced slot matching and logging
        Returns (success, result) where result is appointment_id or error message
        """
        print(f"📅 Attempting clinic booking for user {user_id}, worker {worker_id}")
        print(f"📅 Date: {date}, Time Slot: '{time_slot}'")
        
        # Normalize time slot
        time_slot = time_slot.strip()
        print(f"📅 Normalized time slot: '{time_slot}'")

        # Check availability with proper normalization
        slots = self.availability_db.get_availability(worker_id, date)
        if not slots:
            print(f"❌ No availability found for worker {worker_id} on {date}")
            return False, "No availability found for this date"

        print(f"📅 Available slots: {[s['time_slot'].strip() for s in slots]}")
        
        # Check if slot exists (with proper normalization)
        slot_found = False
        for slot in slots:
            available_slot = slot["time_slot"].strip()
            if available_slot == time_slot:
                slot_found = True
                break
        
        if not slot_found:
            print(f"❌ Slot '{time_slot}' not found or already booked")
            return False, "Selected time slot is not available"

        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()

        try:
            # Check for double booking
            cursor.execute("""
            SELECT id FROM appointments 
            WHERE worker_id = %s AND booking_date = %s AND time_slot = %s AND status != 'cancelled'
            """, (worker_id, date, time_slot))
            
            if cursor.fetchone():
                print(f"❌ Double booking detected for {date} at {time_slot}")
                return False, "This slot has just been booked by another patient"

            # Book appointment
            cursor.execute("""
            INSERT INTO appointments
            (user_id, worker_id, user_name, patient_symptoms,
             booking_date, time_slot, appointment_type, status, insurance_details)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (user_id, worker_id, user_name, symptoms, date, time_slot, 'clinic', 'pending', insurance_details))
            
            apt_id = cursor.fetchone()[0]
            
            # Remove availability
            self.availability_db.remove_availability(worker_id, date, time_slot)
            
            conn.commit()
            print(f"✅ Clinic appointment booked with ID: {apt_id}")
            return True, apt_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Database error: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # FETCH REQUESTS FOR DOCTOR
    # =========================================================
    def get_pending_for_worker(self, worker_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
            SELECT * FROM appointments
            WHERE worker_id=%s AND status='pending'
            ORDER BY created_at DESC
            """, (worker_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # GET APPOINTMENTS BY WORKER
    # =========================================================
    def get_by_worker(self, worker_id):
        """
        Get all appointments for a specific worker
        """
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
            SELECT * FROM appointments
            WHERE worker_id=%s
            ORDER BY created_at DESC
            """, (worker_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # GET APPOINTMENTS BY USER
    # =========================================================
    def get_by_user(self, user_id):
        """
        Get all appointments for a specific user
        """
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
            SELECT * FROM appointments
            WHERE user_id=%s
            ORDER BY created_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # GET APPOINTMENT BY ID
    # =========================================================
    def get_by_id(self, appointment_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM appointments WHERE id=%s", (appointment_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # ACCEPT / REJECT
    # =========================================================
    def respond(self, appointment_id, status):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE appointments SET status=%s WHERE id=%s",
                (status, appointment_id)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # SAVE MEETING LINK + OTP (WHEN DOCTOR ACCEPTS)
    # =========================================================
    def set_video_details(self, appointment_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Get current video room
            cursor.execute("SELECT video_room FROM appointments WHERE id=%s", (appointment_id,))
            result = cursor.fetchone()
            
            meeting_link = self._generate_meeting_link()
            otp = self._generate_otp()
            video_room = result[0] if result else f"room_{appointment_id}"

            cursor.execute("""
            UPDATE appointments
            SET meeting_link=%s, doctor_otp=%s, video_status='ready'
            WHERE id=%s
            """, (meeting_link, otp, appointment_id))

            conn.commit()
            
            print(f"🔧 Setting video details for appointment {appointment_id}")
            print(f"🔗 Meeting Link: {meeting_link}")
            print(f"🔐 Generated OTP: {otp}")
            print(f"🏠 Video Room: {video_room}")
            
            return meeting_link, otp, video_room
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # VERIFY OTP (DOCTOR STARTING CALL)
    # =========================================================
    def verify_otp(self, appointment_id, otp):
        """
        Verify doctor's OTP and mark consultation as started
        Returns True if OTP is correct, False otherwise
        """
        print(f"🔐 Verifying OTP for appointment {appointment_id}")
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT doctor_otp FROM appointments WHERE id=%s", (appointment_id,))
            row = cursor.fetchone()

            if not row or row[0] != otp:
                print(f"❌ OTP verification failed for appointment {appointment_id}")
                return False

            cursor.execute("""
            UPDATE appointments
            SET status='in_consultation', otp_verified=TRUE
            WHERE id=%s
            """, (appointment_id,))

            conn.commit()
            print(f"✅ OTP verified successfully for appointment {appointment_id}")
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # START VIDEO SESSION (ENHANCED)
    # =========================================================
    def start_video_session(self, appointment_id, otp):
        """
        Start video session by verifying OTP and updating status
        Returns True if successful, False otherwise
        """
        print(f"🎥 Starting video session for appointment {appointment_id}")
        
        if self.verify_otp(appointment_id, otp):
            # Additional session setup if needed
            return True
        return False

    # =========================================================
    # DOCTOR STARTS CALL (LEGACY METHOD)
    # =========================================================
    def verify_doctor_otp(self, appointment_id, otp):
        """Legacy method - use verify_otp instead"""
        return self.verify_otp(appointment_id, otp)

    # =========================================================
    # USER JOINS CALL
    # =========================================================
    def get_meeting_link(self, appointment_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT meeting_link, otp_verified
            FROM appointments
            WHERE id=%s
            """, (appointment_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                "meeting_link": row[0],
                "otp_verified": bool(row[1])
            }
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =========================================================
    # EMAIL DATA FETCH
    # =========================================================
    def get_email_details(self, appointment_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT user_id, worker_id, user_name,
                       booking_date, time_slot, appointment_type
                FROM appointments WHERE id=%s
            """, (appointment_id,))

            row = cursor.fetchone()
            if not row:
                return None

            user_id, worker_id, user_name, date, time_slot, appt_type = row

            # In PostgreSQL, we query the same database for user and worker details
            cursor.execute("SELECT email FROM users WHERE id=%s", (user_id,))
            user_row = cursor.fetchone()
            user_email = user_row[0] if user_row else None
            
            cursor.execute("SELECT email FROM workers WHERE id=%s", (worker_id,))
            worker_row = cursor.fetchone()
            worker_email = worker_row[0] if worker_row else None

            return {
                "user_name": user_name,
                "date": date,
                "time_slot": time_slot,
                "appointment_type": appt_type,
                "user_email": user_email,
                "worker_email": worker_email
            }
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
