import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from config import (
    EMAIL_ADDRESS,
    EMAIL_PASSWORD,
    SMTP_SERVER,
    SMTP_PORT
)

# ==================================================
# ================ EMAIL SERVICE ===================
# ==================================================
# NOTE:
# - This uses Gmail SMTP
# - If Gmail blocks login, system will NOT crash
# - Email content will still be printed to console
# - Safe for college submission & demo

def is_valid_email(email):
    # Basic regex for email validation
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def send_email(to_email, subject, body):
    print("\n📨 EMAIL EVENT TRIGGERED")
    print("To      :", to_email)
    print("Subject :", subject)
    print("Body    :", body)

    if not is_valid_email(to_email):
        print(f"❌ Invalid email format: {to_email}")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("✅ Email successfully sent via SMTP\n")
        return True

    except Exception as e:
        # IMPORTANT: Do NOT crash app on email failure
        print("⚠️ Email sending failed (continuing execution)")
        print("Reason:", str(e))
        print("📧 Email content logged above for verification\n")
        return False
