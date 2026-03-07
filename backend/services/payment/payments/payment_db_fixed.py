import sqlite3
DB="database.db"

def save_payment(order_id, booking_id, amount):
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    # Fix: Add missing closing quote for status value
    cur.execute("INSERT INTO payments (booking_id, razorpay_order_id, amount, status) VALUES (?,?,?,?)",
                (booking_id,order_id,amount,"created"))
    conn.commit()
    conn.close()

def mark_paid(order_id, payment_id):
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    # Fix: Add missing opening quote for status value
    cur.execute("UPDATE payments SET status='paid', razorpay_payment_id=? WHERE razorpay_order_id=?",
                (payment_id,order_id))
    conn.commit()
    conn.close()
