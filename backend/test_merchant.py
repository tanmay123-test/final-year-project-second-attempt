#!/usr/bin/env python3
import sqlite3
import os

# Test adding a transaction with merchant
db_path = os.path.join('data', 'money_service.db')

def test_merchant_column():
    """Test inserting and retrieving a transaction with merchant"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Test insert with merchant
            cursor.execute('''
                INSERT INTO transactions (user_id, category, amount, description, merchant, date, type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (1, 'Food', 100.0, 'Test transaction', 'Test Merchant', '2026-03-10', 'expense'))
            
            conn.commit()
            print("✅ Test transaction with merchant added!")
            
            # Test retrieve
            cursor.execute('''
                SELECT * FROM transactions WHERE merchant = ?
            ''', ('Test Merchant',))
            
            result = cursor.fetchone()
            if result:
                print("✅ Transaction with merchant retrieved successfully!")
                print(f"   ID: {result[0]}, User: {result[1]}, Category: {result[2]}, Amount: {result[3]}, Description: {result[4]}, Merchant: {result[5]}, Date: {result[6]}, Type: {result[7]}")
            else:
                print("❌ Could not retrieve test transaction")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_merchant_column()
