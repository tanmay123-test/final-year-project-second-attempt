from flask import Blueprint, request, jsonify
from .razor_service import create_order
from .payment_db import save_payment
import os

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/create-order", methods=["POST"])
def create_payment():
    data = request.json
    amount = data["amount"]
    booking_id = data["booking_id"]

    # Fix: Pass correct parameters to create_order
    order = create_order(amount, booking_id)
    save_payment(order["id"], booking_id, amount)

    return jsonify({
        "order_id": order["id"],
        "amount": amount,
        "key": os.getenv("RAZORPAY_KEY_ID")
    })
