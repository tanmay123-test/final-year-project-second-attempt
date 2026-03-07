import sqlite3
import random
import time
import os
from config import OTP_DB, OTP_EXPIRY_MINUTES
from email_service import send_email

os.makedirs("data", exist_ok=True)

MAX_ATTEMPTS = 3


def init_otp_db():
    conn = sqlite3.connect(OTP_DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS otps (
        email TEXT PRIMARY KEY,
        otp TEXT,
        expiry INTEGER,
        attempts INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()


init_otp_db()


def send_otp(email):
    otp = str(random.randint(100000, 999999))
    expiry = int(time.time()) + OTP_EXPIRY_MINUTES * 60

    conn = sqlite3.connect(OTP_DB)
    c = conn.cursor()

    c.execute("DELETE FROM otps WHERE email=?", (email,))
    c.execute(
        "INSERT INTO otps (email, otp, expiry, attempts) VALUES (?, ?, ?, 0)",
        (email, otp, expiry)
    )
    conn.commit()
    conn.close()

    body = f"Your ExpertEase OTP is {otp}. It expires in {OTP_EXPIRY_MINUTES} minutes."
    send_email(email, "ExpertEase OTP Verification", body)


def verify_otp(email, user_otp):
    conn = sqlite3.connect(OTP_DB)
    c = conn.cursor()

    c.execute(
        "SELECT otp, expiry, attempts FROM otps WHERE email=?",
        (email,)
    )
    row = c.fetchone()

    if not row:
        conn.close()
        return False, "OTP not found"

    otp, expiry, attempts = row

    if attempts >= MAX_ATTEMPTS:
        conn.close()
        return False, "Too many wrong attempts"

    if time.time() > expiry:
        conn.close()
        return False, "OTP expired"

    if otp != user_otp:
        c.execute(
            "UPDATE otps SET attempts = attempts + 1 WHERE email=?",
            (email,)
        )
        conn.commit()
        conn.close()
        return False, f"Invalid OTP ({MAX_ATTEMPTS - attempts - 1} attempts left)"

    # OTP correct → cleanup
    c.execute("DELETE FROM otps WHERE email=?", (email,))
    conn.commit()
    conn.close()
    return True, "OTP verified"
