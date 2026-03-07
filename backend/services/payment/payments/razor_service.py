import razorpay, os
from dotenv import load_dotenv
load_dotenv()

client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

def create_order(amount, receipt):
    return client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "receipt": receipt,
        "payment_capture": 1
    })
