#!/usr/bin/env python3

import sqlite3
from config import WORKER_DB

def clean_subscriptions():
    """Clean up duplicate subscriptions for worker 4"""
    
    conn = sqlite3.connect(WORKER_DB)
    cursor = conn.cursor()
    
    print("🧹 CLEANING DUPLICATE SUBSCRIPTIONS")
    print("="*60)
    
    # Show current state
    cursor.execute("""
        SELECT ws.id, ws.plan_id, ws.status, ws.created_at, ws.start_date, ws.end_date,
               sp.name as plan_name, sp.daily_appointment_limit
        FROM worker_subscriptions ws
        JOIN subscription_plans sp ON ws.plan_id = sp.id
        WHERE ws.worker_id = 4
        ORDER BY ws.created_at DESC
    """)
    
    subscriptions = cursor.fetchall()
    
    print(f"📊 Found {len(subscriptions)} subscriptions:")
    for sub in subscriptions:
        print(f"   Tuple structure: {sub}")
        print(f"   Length: {len(sub)}")
        if len(sub) >= 9:
            print(f"   ID: {sub[0]} - Plan: {sub[6]} ({sub[8]}/day) - Status: {sub[2]}")
            print(f"      Created: {sub[3]}")
            print(f"      Daily Limit: {sub[8]}")
        else:
            print(f"   Insufficient columns: {sub}")
    
    # Keep only the most recent active subscription
    cursor.execute("""
        DELETE FROM worker_subscriptions 
        WHERE worker_id = 4 AND id NOT IN (
            SELECT id FROM (
                SELECT id FROM worker_subscriptions 
                WHERE worker_id = 4 AND status = 'active'
                ORDER BY created_at DESC, id DESC
                LIMIT 1
            )
        )
    """)
    
    changes = conn.total_changes
    conn.commit()
    conn.close()
    
    print(f"✅ Cleaned up {changes} duplicate subscriptions")
    
    # Check result
    conn = sqlite3.connect(WORKER_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ws.*, sp.name as plan_name, sp.daily_appointment_limit
        FROM worker_subscriptions ws
        JOIN subscription_plans sp ON ws.plan_id = sp.id
        WHERE ws.worker_id = 4 AND ws.status = 'active'
        ORDER BY ws.created_at DESC, ws.id DESC
        LIMIT 1
    """)
    
    current = cursor.fetchone()
    if current:
        print(f"✅ Current Active Subscription:")
        print(f"   Plan: {current[6]}")
        print(f"   Daily Limit: {current[8]}")
    else:
        print("❌ No active subscription")
    
    conn.close()

if __name__ == "__main__":
    clean_subscriptions()
