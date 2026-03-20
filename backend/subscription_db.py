# Simple subscription module without complex SQL
import sqlite3
from datetime import datetime, timedelta
from config import WORKER_DB

class SubscriptionDB:
    def __init__(self):
        self.conn = sqlite3.connect(WORKER_DB, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_simple_tables()
        self.insert_default_plans()

    def create_simple_tables(self):
        # Simple subscription plans table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS subs_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            duration_days INTEGER NOT NULL,
            features TEXT NOT NULL,
            max_appointments INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
        ''')
        
        # Simple doctor subscriptions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS doc_subs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT DEFAULT 'active'
        )
        ''')
        
        self.conn.commit()

    def insert_default_plans(self):
        # Check if plans already exist
        self.cursor.execute("SELECT COUNT(*) FROM subs_plans")
        if self.cursor.fetchone()[0] > 0:
            return
        
        # Insert default subscription plans
        plans = [
            ('Basic', 0, 30, 'Maximum 2 appointments per day, Basic profile visibility', 2),
            ('Professional', 29.99, 30, 'Maximum 10 appointments per day, Enhanced profile visibility, AI symptom analysis', 10),
            ('Premium', 59.99, 30, 'Unlimited appointments, Premium profile visibility, AI symptom analysis, Video calls, Priority support', 999),
            ('Enterprise', 99.99, 30, 'Unlimited appointments, Premium profile visibility, AI symptom analysis, Video calls, Priority support, Analytics dashboard, Multi-clinic support', 999)
        ]
        
        for plan in plans:
            self.cursor.execute('''
            INSERT INTO subs_plans (name, price, duration_days, features, max_appointments)
            VALUES (?, ?, ?, ?, ?)
            ''', plan)
        
        self.conn.commit()

    def get_all_plans(self):
        self.cursor.execute("SELECT * FROM subs_plans WHERE is_active = 1")
        results = self.cursor.fetchall()
        keys = [d[0] for d in self.cursor.description]
        return [dict(zip(keys, r)) for r in results]

    def get_doctor_subscription(self, worker_id):
        self.cursor.execute('''
        SELECT ds.*, sp.name as plan_name, sp.features, sp.max_appointments
        FROM doc_subs ds
        JOIN subs_plans sp ON ds.plan_id = sp.id
        WHERE ds.worker_id = ? AND ds.status = 'active' AND ds.end_date > ?
        ORDER BY ds.end_date DESC LIMIT 1
        ''', (worker_id, datetime.now().isoformat()))
        
        result = self.cursor.fetchone()
        if result:
            keys = [d[0] for d in self.cursor.description]
            return dict(zip(keys, result))
        return None

    def create_subscription(self, worker_id, plan_id, payment_id=None):
        # Get plan details
        self.cursor.execute("SELECT duration_days FROM subs_plans WHERE id = ?", (plan_id,))
        plan = self.cursor.fetchone()
        if not plan:
            return False, "Plan not found"
        
        # Calculate end date
        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan[0])
        
        # Deactivate existing subscriptions
        self.cursor.execute("UPDATE doc_subs SET status = 'expired' WHERE worker_id = ?", (worker_id,))
        
        # Create new subscription
        self.cursor.execute('''
        INSERT INTO doc_subs (worker_id, plan_id, start_date, end_date)
        VALUES (?, ?, ?, ?)
        ''', (worker_id, plan_id, start_date.isoformat(), end_date.isoformat()))
        
        self.conn.commit()
        return True, self.cursor.lastrowid

    def check_appointment_limit(self, worker_id):
        subscription = self.get_doctor_subscription(worker_id)
        if not subscription:
            # For demo/testing: Allow booking even without subscription
            # In production, you might want to require doctors to have subscriptions
            print(f"⚠️ Doctor {worker_id} has no subscription, allowing booking for demo")
            return True, "Demo mode - No subscription required"
        
        max_appointments = subscription['max_appointments']
        if max_appointments >= 999:  # Unlimited
            return True, "Unlimited appointments"
        
        # For demo, always allow booking
        return True, f"{max_appointments} appointments allowed per day"

    def update_subscription_usage(self, worker_id, plan_id):
        # For demo, just log the usage
        pass

    def get_subscription_stats(self, worker_id):
        subscription = self.get_doctor_subscription(worker_id)
        if not subscription:
            return None
        
        today_usage = 0  # Replace with actual usage
        return {
            'plan_name': subscription['plan_name'],
            'end_date': subscription['end_date'],
            'max_appointments_per_day': subscription['max_appointments'],
            'today_usage': today_usage,
            'remaining_today': subscription['max_appointments'] - today_usage if subscription['max_appointments'] < 999 else 'Unlimited'
        }

    def cancel_subscription(self, worker_id):
        self.cursor.execute('''
        UPDATE doc_subs 
        SET status = 'cancelled', end_date = ? 
        WHERE worker_id = ? AND status = 'active'
        ''', (datetime.now().isoformat(), worker_id))
        
        self.conn.commit()
        return True
