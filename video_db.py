# video_db.py
# --------------------------------------------------
# Handles video consultation sessions
# --------------------------------------------------

import sqlite3
import random
import string
from datetime import datetime, timedelta

from meeting_utils import create_meeting_link

DB_PATH = "data/expertease.db"


class VideoConsultDB:

    def __init__(self):
        print("🔥 VideoConsultDB LOADED")
        self.create_table()

    def get_conn(self):
        return sqlite3.connect(DB_PATH)

    # =====================================================
    # CREATE TABLE
    # =====================================================
    def create_table(self):
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER,
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

        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO video_sessions
        (appointment_id, worker_id, user_id, room_id,
         meeting_link, doctor_otp, otp_expiry)
        VALUES (?, ?, ?, ?, ?, ?, ?)
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
        conn.close()

        return otp  # returned so email can send it

    # =====================================================
    # VERIFY OTP + START CALL (DOCTOR SIDE)
    # =====================================================
    def verify_otp_and_start(self, appointment_id, otp):
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT doctor_otp, otp_expiry FROM video_sessions
        WHERE appointment_id=?
        """, (appointment_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        saved_otp, expiry = row
        expiry = datetime.fromisoformat(expiry)

        if datetime.now() > expiry:
            conn.close()
            return False

        if saved_otp != otp:
            conn.close()
            return False

        # Mark session live
        cursor.execute("""
        UPDATE video_sessions
        SET status='live'
        WHERE appointment_id=?
        """, (appointment_id,))

        conn.commit()
        conn.close()
        return True

    # =====================================================
    # GET LINK FOR USER (JOIN CALL)
    # =====================================================
    def get_link(self, appointment_id):
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT meeting_link FROM video_sessions
        WHERE appointment_id=? AND status='live'
        """, (appointment_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return row[0]
