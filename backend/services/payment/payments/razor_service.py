import razorpay, os
import sys

# Ensure backend root is in path for config
_backend = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _backend not in sys.path:
    sys.path.insert(0, _backend)

try:
    from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
except ImportError:
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

client = razorpay.Client(auth=(
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET
))

def create_order(amount, receipt):
    return client.order.create({
        "amount": int(amount) * 100,
        "currency": "INR",
        "receipt": str(receipt),
        "payment_capture": 1
    })
