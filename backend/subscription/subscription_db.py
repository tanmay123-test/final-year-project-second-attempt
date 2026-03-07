import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class SubscriptionDB:
    def __init__(self):
        from config import WORKER_DB
        self.conn = sqlite3.connect(WORKER_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.insert_default_plans()
    
    def create_tables(self):
        """Create subscription-related tables"""
        cursor = self.conn.cursor()
        
        # Check if workers table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workers'")
        workers_exists = cursor.fetchone() is not None
        
        # subscription_plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                duration_days INTEGER NOT NULL,
                daily_appointment_limit INTEGER NOT NULL,
                is_trial INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # worker_subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                plan_id INTEGER NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                status TEXT DEFAULT 'active',
                razorpay_order_id TEXT,
                razorpay_payment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers(id),
                FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
            )
        """)
        
        # subscription_usage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                date DATE NOT NULL,
                appointments_count INTEGER DEFAULT 0,
                daily_limit INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers(id),
                UNIQUE(worker_id, date)
            )
        """)
        
        # Add subscription fields to workers table if it exists
        if workers_exists:
            cursor.execute("PRAGMA table_info(workers)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'subscription_status' not in columns:
                cursor.execute("ALTER TABLE workers ADD COLUMN subscription_status TEXT DEFAULT 'none'")
            
            if 'trial_used' not in columns:
                cursor.execute("ALTER TABLE workers ADD COLUMN trial_used INTEGER DEFAULT 0")
        
        self.conn.commit()
    
    def insert_default_plans(self):
        """Insert default subscription plans"""
        cursor = self.conn.cursor()
        
        # Check if plans already exist
        cursor.execute("SELECT COUNT(*) FROM subscription_plans")
        if cursor.fetchone()[0] > 0:
            return
        
        # Insert default plans
        plans = [
            ("Trial", 0, 30, 3, 1),      # Trial plan
            ("Basic", 499, 30, 5, 0),    # Basic plan
            ("Professional", 999, 30, 15, 0),  # Professional plan
            ("Enterprise", 1999, 30, 999, 0)   # Enterprise plan (999 = unlimited)
        ]
        
        cursor.executemany("""
            INSERT INTO subscription_plans (name, price, duration_days, daily_appointment_limit, is_trial)
            VALUES (?, ?, ?, ?, ?)
        """, plans)
        
        self.conn.commit()
        print("✅ Default subscription plans inserted")
    
    def assign_free_trial(self, worker_id: int) -> bool:
        """Assign free trial to a new worker"""
        cursor = self.conn.cursor()
        
        # Check if trial already used
        cursor.execute("SELECT trial_used FROM workers WHERE id = ?", (worker_id,))
        result = cursor.fetchone()
        
        if not result or result[0] == 1:
            return False
        
        # Get trial plan
        cursor.execute("SELECT id FROM subscription_plans WHERE is_trial = 1")
        trial_plan = cursor.fetchone()
        
        if not trial_plan:
            return False
        
        # Calculate trial end date (30 days from now)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        # Create subscription
        cursor.execute("""
            INSERT INTO worker_subscriptions (worker_id, plan_id, start_date, end_date, status)
            VALUES (?, ?, ?, ?, 'active')
        """, (worker_id, trial_plan[0], start_date, end_date))
        
        # Update worker record
        cursor.execute("""
            UPDATE workers 
            SET subscription_status = 'active', trial_used = 1
            WHERE id = ?
        """, (worker_id,))
        
        self.conn.commit()
        return True
    
    def get_current_subscription(self, worker_id: int) -> Optional[Dict]:
        """Get worker's current active subscription"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ws.*, sp.name as plan_name, sp.price, sp.daily_appointment_limit, sp.is_trial
            FROM worker_subscriptions ws
            JOIN subscription_plans sp ON ws.plan_id = sp.id
            WHERE ws.worker_id = ? AND ws.status = 'active'
            ORDER BY ws.created_at DESC, ws.id DESC
            LIMIT 1
        """, (worker_id,))
        
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def get_subscription_plans(self, include_trial: bool = False) -> List[Dict]:
        """Get all available subscription plans"""
        cursor = self.conn.cursor()
        
        if include_trial:
            cursor.execute("SELECT * FROM subscription_plans ORDER BY is_trial DESC, price ASC")
        else:
            cursor.execute("SELECT * FROM subscription_plans WHERE is_trial = 0 ORDER BY price ASC")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def create_subscription_order(self, worker_id: int, plan_id: int) -> Optional[Dict]:
        """Create a new subscription order"""
        cursor = self.conn.cursor()
        
        # Get plan details
        cursor.execute("SELECT * FROM subscription_plans WHERE id = ?", (plan_id,))
        plan = cursor.fetchone()
        
        if not plan:
            return None
        
        # Calculate subscription dates
        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan['duration_days'])
        
        # Create subscription record
        cursor.execute("""
            INSERT INTO worker_subscriptions (worker_id, plan_id, start_date, end_date, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (worker_id, plan_id, start_date, end_date))
        
        subscription_id = cursor.lastrowid
        self.conn.commit()
        
        return {
            "subscription_id": subscription_id,
            "plan": dict(plan),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    
    def confirm_subscription_payment(self, worker_id: int, order_id: str, payment_id: str) -> bool:
        """Confirm subscription payment and activate subscription"""
        cursor = self.conn.cursor()
        
        # Check if this is an upgrade (worker has existing active subscription)
        current_sub = self.get_current_subscription(worker_id)
        
        if current_sub and current_sub['status'] == 'active':
            # End previous subscription for upgrade
            cursor.execute("""
                UPDATE worker_subscriptions 
                SET status = 'ended', end_date = CURRENT_TIMESTAMP
                WHERE worker_id = ? AND status = 'active'
            """, (worker_id,))
            print(f"🔄 Ending previous subscription for upgrade")
        
        # Update new subscription with payment details
        cursor.execute("""
            UPDATE worker_subscriptions 
            SET status = 'active', razorpay_order_id = ?, razorpay_payment_id = ?
            WHERE worker_id = ? AND status = 'pending'
        """, (order_id, payment_id, worker_id))
        
        # Update worker subscription status
        cursor.execute("""
            UPDATE workers 
            SET subscription_status = 'active'
            WHERE id = ?
        """, (worker_id,))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def check_subscription_validity(self, worker_id: int) -> Dict[str, Any]:
        """Check if worker's subscription is valid for accepting appointments"""
        subscription = self.get_current_subscription(worker_id)
        
        if not subscription:
            return {
                "valid": False,
                "error": "No active subscription. Please subscribe to continue.",
                "subscription": None
            }
        
        # Check if subscription has expired
        if subscription['end_date']:
            end_date = datetime.fromisoformat(subscription['end_date'])
            if datetime.now() > end_date:
                return {
                    "valid": False,
                    "error": "Your subscription has expired. Please renew to continue.",
                    "subscription": subscription
                }
        
        # Check daily usage limit
        today = datetime.now().date()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT appointments_count, daily_limit 
            FROM subscription_usage 
            WHERE worker_id = ? AND date = ?
        """, (worker_id, today))
        
        usage = cursor.fetchone()
        
        if usage:
            appointments_count, daily_limit = usage
            if appointments_count >= daily_limit:
                return {
                    "valid": False,
                    "error": f"Daily appointment limit reached ({appointments_count}/{daily_limit}). Upgrade your plan.",
                    "subscription": subscription
                }
        
        return {
            "valid": True,
            "error": None,
            "subscription": subscription
        }
    
    def track_appointment_usage(self, worker_id: int) -> bool:
        """Track appointment usage for a worker"""
        cursor = self.conn.cursor()
        today = datetime.now().date()
        
        # Get daily limit from current subscription
        subscription = self.get_current_subscription(worker_id)
        if not subscription:
            return False
        
        daily_limit = subscription['daily_appointment_limit']
        
        # Insert or update usage record
        cursor.execute("""
            INSERT OR REPLACE INTO subscription_usage (worker_id, date, appointments_count, daily_limit)
            VALUES (?, ?, 
                    COALESCE((SELECT appointments_count FROM subscription_usage WHERE worker_id = ? AND date = ?), 0) + 1,
                    ?)
        """, (worker_id, today, worker_id, today, daily_limit))
        
        self.conn.commit()
        return True
    
    def get_usage_stats(self, worker_id: int) -> Optional[Dict]:
        """Get usage statistics for a worker"""
        subscription = self.get_current_subscription(worker_id)
        
        if not subscription:
            return None
        
        today = datetime.now().date()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT appointments_count, daily_limit 
            FROM subscription_usage 
            WHERE worker_id = ? AND date = ?
        """, (worker_id, today))
        
        usage = cursor.fetchone()
        
        if usage:
            appointments_count, daily_limit = usage
        else:
            appointments_count, daily_limit = 0, subscription['daily_appointment_limit']
        
        return {
            "plan_name": subscription['plan_name'],
            "end_date": subscription['end_date'],
            "daily_limit": daily_limit,
            "today_usage": appointments_count,
            "remaining_today": max(0, daily_limit - appointments_count),
            "is_trial": subscription['is_trial'] == 1
        }
    
    def cancel_subscription(self, worker_id: int) -> bool:
        """Cancel worker's subscription"""
        cursor = self.conn.cursor()
        
        # Update subscription status
        cursor.execute("""
            UPDATE worker_subscriptions 
            SET status = 'cancelled', end_date = CURRENT_TIMESTAMP
            WHERE worker_id = ? AND status = 'active'
        """, (worker_id,))
        
        # Update worker status
        cursor.execute("""
            UPDATE workers 
            SET subscription_status = 'cancelled'
            WHERE id = ?
        """, (worker_id,))
        
        self.conn.commit()
        return cursor.rowcount > 0

# Global instance
subscription_db = SubscriptionDB()
