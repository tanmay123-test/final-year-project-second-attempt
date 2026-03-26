# video_db.py
# --------------------------------------------------
# Handles video consultation sessions
# --------------------------------------------------

import os
import psycopg2
import psycopg2.extras
import random
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv

from data.meeting_utils import generate_meeting_link as create_meeting_link

load_dotenv()

class VideoConsultDB:

    def __init__(self):
        print("  VideoConsultDB LOADED")
        self.create_table()

    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    # =====================================================
    # CREATE TABLE
    # =====================================================
    def create_table(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_sessions (
                id SERIAL PRIMARY KEY,
                appointment_id INTEGER UNIQUE,
                worker_id INTEGER,
                user_id INTEGER,
                room_id TEXT,
                meeting_link TEXT,
                doctor_otp TEXT,
                otp_expiry TIMESTAMP,
                status TEXT DEFAULT 'waiting'
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

    # =====================================================
    # GENERATE OTP
    # =====================================================
    def generate_otp(self, length=6):
        return ''.join(random.choices(string.digits, k=length))

    # =====================================================
    # CREATE SESSION (CALLED WHEN DOCTOR ACCEPTS)
    # =====================================================
    def create_session(self, appointment_id, worker_id, user_id):
        """
        Called when doctor ACCEPTS video consultation
        Creates meeting link + doctor OTP
        """
        meeting = create_meeting_link(appointment_id)
        otp = self.generate_otp()
        expiry = datetime.now() + timedelta(minutes=10)

        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO video_sessions
            (appointment_id, worker_id, user_id, room_id,
             meeting_link, doctor_otp, otp_expiry)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (appointment_id) DO UPDATE SET
            worker_id = EXCLUDED.worker_id,
            user_id = EXCLUDED.user_id,
            room_id = EXCLUDED.room_id,
            meeting_link = EXCLUDED.meeting_link,
            doctor_otp = EXCLUDED.doctor_otp,
            otp_expiry = EXCLUDED.otp_expiry,
            status = 'waiting'
            RETURNING id
            """, (
                appointment_id,
                worker_id,
                user_id,
                meeting["room_id"],
                meeting["jitsi_link"],
                otp,
                expiry
            ))
            conn.commit()
            return otp
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =====================================================
    # VERIFY OTP + START CALL (DOCTOR SIDE)
    # =====================================================
    def verify_otp_and_start(self, appointment_id, otp):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT doctor_otp, otp_expiry FROM video_sessions
            WHERE appointment_id=%s
            """, (appointment_id,))
            
            row = cursor.fetchone()
            if not row:
                return False
            
            saved_otp, expiry = row
            # PostgreSQL returns datetime object for TIMESTAMP
            if isinstance(expiry, str):
                expiry = datetime.fromisoformat(expiry)
            
            if datetime.now() > expiry:
                return False
            
            if saved_otp != otp:
                return False

            cursor.execute("""
            UPDATE video_sessions 
            SET status = 'active'
            WHERE appointment_id = %s
            """, (appointment_id,))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # =====================================================
    # GET LINK FOR USER (JOIN CALL)
    # =====================================================
    def get_link(self, appointment_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT meeting_link FROM video_sessions
            WHERE appointment_id=%s AND status='active'
            """, (appointment_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return row[0]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
