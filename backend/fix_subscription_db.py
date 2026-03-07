#!/usr/bin/env python3

import sqlite3
from config import WORKER_DB

def fix_subscription_database():
    """Fix subscription database for worker 4"""
    
    conn = sqlite3.connect(WORKER_DB)
    cursor = conn.cursor()
    
    print("🔧 FIXING SUBSCRIPTION DATABASE")
    print("="*60)
    
    # Delete all subscriptions for worker 4 except the most recent active one
    cursor.execute("""
        DELETE FROM worker_subscriptions 
        WHERE worker_id = 4 AND id NOT IN (
            SELECT ws.id FROM (
                SELECT ws.id FROM worker_subscriptions ws
                WHERE ws.worker_id = 4 AND ws.status = 'active'
                ORDER BY ws.created_at DESC, ws.id DESC
                LIMIT 1
            )
        )
    """)
    
    # Get the remaining active subscription
    cursor.execute("""
        SELECT ws.*, sp.name as plan_name, sp.daily_appointment_limit
        FROM worker_subscriptions ws
        JOIN subscription_plans sp ON ws.plan_id = sp.id
        WHERE ws.worker_id = 4 AND ws.status = 'active'
        ORDER BY ws.created_at DESC, ws.id DESC
        LIMIT 1
    """)
    
    remaining = cursor.fetchone()
    
    if remaining:
        print(f"✅ Remaining subscription:")
        print(f"   ID: {remaining[0]}")
        print(f"   Plan: {remaining[6]}")
        print(f"   Daily Limit: {remaining[8]}")
        print(f"   Status: {remaining[2]}")
    else:
        print("❌ No remaining subscriptions")
    
    changes = conn.total_changes
    conn.commit()
    conn.close()
    
    print(f"✅ Fixed database - {changes} changes made")

if __name__ == "__main__":
    fix_subscription_database()
