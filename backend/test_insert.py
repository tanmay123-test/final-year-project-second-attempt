#!/usr/bin/env python3
import sys
import os
sys.path.append('services/money_service')

from models.money_model import MoneyModel

def test_insert():
    """Test the add_transaction method directly"""
    try:
        model = MoneyModel()
        
        # Test inserting with merchant
        result = model.add_transaction(
            user_id=1,
            category='Food',
            amount=50.0,
            description='Test from model',
            date='2026-03-10',
            type='expense',
            merchant='Test Restaurant'
        )
        
        print(f"✅ Insert successful! Transaction ID: {result}")
        
        # Test retrieving
        transactions = model.get_transactions(user_id=1)
        print(f"✅ Retrieved {len(transactions)} transactions")
        
        for t in transactions:
            print(f"   - {t}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_insert()
