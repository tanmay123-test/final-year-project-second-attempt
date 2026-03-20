from flask import Blueprint, request
import os, hmac, hashlib
from payments.payment_db import mark_paid

webhook_bp = Blueprint("webhook", __name__)
SECRET = os.getenv("WEBHOOK_SECRET")

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    received_sig = request.headers.get("X-Razorpay-Signature")

    expected_sig = hmac.new(
        SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()

    if received_sig != expected_sig:
        return "Invalid", 400

    event = request.json["event"]

    if event == "payment.captured":
        payment = request.json["payload"]["payment"]["entity"]
        mark_paid(payment["order_id"], payment["id"])
        print("PAYMENT VERIFIED")

    return "OK", 200
