import sqlite3

DB="database.db"

def create_payment_database():
    """Create the missing payments table"""
    
    print("🔧 CREATING PAYMENT DATABASE")
    print("="*40)
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # Create payments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT NOT NULL,
            razorpay_order_id TEXT NOT NULL,
            razorpay_payment_id TEXT,
            amount INTEGER NOT NULL,
            status TEXT DEFAULT 'created',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Payments table created successfully!")
    print(f"📁 Database: {DB}")
    print("📋 Table: payments")
    
    # Verify table creation
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    
    print(f"\n📊 Tables in database:")
    for table in tables:
        print(f"   📁 {table[0]}")
    
    conn.close()

if __name__ == "__main__":
    create_payment_database()
