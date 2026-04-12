import sqlite3
import os
from datetime import datetime, timedelta

class GoalEngine:
    """Main engine for goal jar management"""
    
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'data', 'expertease.db')
        # Fallback to cwd-relative path if data dir doesn't exist
        if not os.path.exists(os.path.dirname(self.db_path)):
            self.db_path = 'expertease.db'
        self._init_tables()

    def get_conn(self):
        """Get a fresh thread-safe SQLite connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Create tables on first run"""
        conn = self.get_conn()
        try:
            self.create_goal_tables(conn)
            self._ensure_goal_schema(conn)
        finally:
            conn.close()

    def create_goal_tables(self, conn=None):
        """Create goal jars tables"""
        close_after = conn is None
        if conn is None:
            conn = self.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS goal_jars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_name TEXT,
            target_amount REAL,
            monthly_contribution REAL,
            current_amount REAL DEFAULT 0,
            target_date DATE,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Goal savings transactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS goal_savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER,
            user_id INTEGER,
            amount REAL,
            transaction_date DATE,
            payment_method TEXT,
            notes TEXT,
            FOREIGN KEY (goal_id) REFERENCES goal_jars (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Goal notifications table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS goal_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_id INTEGER,
            notification_type TEXT,
            message TEXT,
            scheduled_date DATE,
            is_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (goal_id) REFERENCES goal_jars (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        conn.commit()
        if close_after:
            conn.close()
    
    def _ensure_goal_schema(self, conn=None):
        """Safely migrate goal_jars schema if older DB exists without new columns"""
        close_after = conn is None
        if conn is None:
            conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(goal_jars)")
            existing = {row[1] for row in cursor.fetchall()}
            if 'monthly_contribution' not in existing:
                cursor.execute("ALTER TABLE goal_jars ADD COLUMN monthly_contribution REAL DEFAULT 0")
            if 'current_amount' not in existing:
                cursor.execute("ALTER TABLE goal_jars ADD COLUMN current_amount REAL DEFAULT 0")
            if 'updated_at' not in existing:
                cursor.execute("ALTER TABLE goal_jars ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            if 'target_date' not in existing:
                cursor.execute("ALTER TABLE goal_jars ADD COLUMN target_date TEXT")
            conn.commit()
        except Exception:
            pass
        finally:
            cursor.close()
            if close_after:
                conn.close()
    
    def create_goal(self, user_id, goal_name, target_amount, monthly_contribution, target_date=None):
        """Create a new goal"""
        conn = self.get_conn()
        cursor = conn.cursor()
        
        # Calculate feasibility
        months_required = int(target_amount / monthly_contribution) if monthly_contribution > 0 else 999
        
        # Set default target date if not provided
        if not target_date:
            target_date = (datetime.now() + timedelta(days=months_required * 30)).strftime('%Y-%m-%d')
        else:
            try:
                target_date = datetime.strptime(str(target_date), '%Y-%m-%d').strftime('%Y-%m-%d')
            except Exception:
                target_date = str(target_date)
        
        cursor.execute("""
        INSERT INTO goal_jars 
        (user_id, goal_name, target_amount, monthly_contribution, target_date)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, goal_name, target_amount, monthly_contribution, target_date))
        
        conn.commit()
        goal_id = cursor.lastrowid
        conn.close()
        return goal_id
    
    def get_user_goals(self, user_id):
        """Get all goals for a user"""
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM goal_jars 
        WHERE user_id=? 
        ORDER BY created_at DESC
        """, (user_id,))
        
        goals = []
        for row in cursor.fetchall():
            goal = dict(row)
            goal['progress_percentage'] = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            goal['remaining_amount'] = goal['target_amount'] - goal['current_amount']
            goal['months_remaining'] = max(0, int(goal['remaining_amount'] / goal['monthly_contribution'])) if goal['monthly_contribution'] > 0 else 999
            if goal['target_date']:
                try:
                    target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
                    months_passed = max(0, (datetime.now() - target_date).days // 30)
                    goal['months_passed'] = months_passed
                except Exception:
                    goal['months_passed'] = 0
            else:
                goal['months_passed'] = 0
            goals.append(goal)
        
        conn.close()
        return goals
    
    def add_savings(self, user_id, goal_id, amount, payment_method='online', notes=''):
        """Add savings to a goal"""
        conn = self.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO goal_savings 
        (goal_id, user_id, amount, transaction_date, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (goal_id, user_id, amount, datetime.now().date(), payment_method, notes))
        
        cursor.execute("""
        UPDATE goal_jars 
        SET current_amount = current_amount + ?, updated_at = CURRENT_TIMESTAMP
        WHERE id=? AND user_id=?
        """, (amount, goal_id, user_id))
        
        conn.commit()
        conn.close()
        return True
    
    def get_goal_progress(self, user_id, goal_id):
        """Get detailed progress for a specific goal"""
        conn = self.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM goal_jars WHERE id=? AND user_id=?", (goal_id, user_id))
        goal = cursor.fetchone()
        if not goal:
            conn.close()
            return None
        goal = dict(goal)
        cursor.execute("""
        SELECT * FROM goal_savings WHERE goal_id=? AND user_id=? ORDER BY transaction_date DESC
        """, (goal_id, user_id))
        savings_history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        goal['savings_history'] = savings_history
        goal['progress_percentage'] = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
        goal['remaining_amount'] = goal['target_amount'] - goal['current_amount']
        return goal
    
    def simulate_timeline(self, target_amount, monthly_contribution):
        """Simulate different saving timelines"""
        timelines = []
        
        contributions = [
            monthly_contribution * 0.5,  # 50% of planned
            monthly_contribution * 0.75,  # 75% of planned
            monthly_contribution * 1.0,  # 100% of planned
            monthly_contribution * 1.25,  # 125% of planned
            monthly_contribution * 1.5    # 150% of planned
        ]
        
        for contribution in contributions:
            if contribution > 0:
                months_required = int(target_amount / contribution)
                timelines.append({
                    'monthly_contribution': contribution,
                    'months_required': months_required,
                    'years_required': months_required / 12,
                    'description': f" {contribution:.0f}/month"
                })
        
        return timelines
    
    def transfer_leftover_to_goal(self, user_id, goal_id, amount, source_category):
        """Transfer leftover budget to goal"""
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO goal_savings (goal_id, user_id, amount, transaction_date, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (goal_id, user_id, amount, datetime.now().date(), 'budget_transfer', f"Transfer from {source_category}"))
        cursor.execute("""
        UPDATE goal_jars SET current_amount = current_amount + ?, updated_at = CURRENT_TIMESTAMP
        WHERE id=? AND user_id=?
        """, (amount, goal_id, user_id))
        conn.commit()
        conn.close()
        return True
    
    def get_goal_acceleration_suggestions(self, user_id):
        """Analyze spending and suggest goal acceleration"""
        conn = self.get_conn()
        cursor = conn.cursor()
        
        three_months_ago = datetime.now() - timedelta(days=90)
        cursor.execute("""
        SELECT category, SUM(amount) as total_spent, COUNT(*) as transaction_count
        FROM transactions WHERE user_id=? AND date >= ? GROUP BY category ORDER BY total_spent DESC
        """, (user_id, three_months_ago.date()))
        spending_data = cursor.fetchall()
        conn.close()
        suggestions = []
        for spending in spending_data:
            category = spending['category']
            monthly_avg = spending['total_spent'] / 3
            if monthly_avg > 2000:
                reduction_20 = monthly_avg * 0.8
                savings_potential = monthly_avg - reduction_20
                suggestions.append({
                    'category': category,
                    'current_monthly_avg': monthly_avg,
                    'suggested_monthly': reduction_20,
                    'monthly_savings': savings_potential,
                    'strategy': f"Reduce {category} spending by 20%"
                })
        return suggestions
    
    def schedule_goal_notification(self, user_id, goal_id, notification_type, message, scheduled_date):
        """Schedule a goal notification"""
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO goal_notifications (user_id, goal_id, notification_type, message, scheduled_date)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, goal_id, notification_type, message, scheduled_date))
        conn.commit()
        notif_id = cursor.lastrowid
        conn.close()
        return notif_id
    
    def get_pending_notifications(self, user_id):
        """Get pending notifications to send"""
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM goal_notifications 
        WHERE user_id=? AND is_sent=0 AND scheduled_date <= date('now') ORDER BY scheduled_date ASC
        """, (user_id,))
        result = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return result
    
    def mark_notification_sent(self, notification_id):
        """Mark notification as sent"""
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE goal_notifications SET is_sent=1 WHERE id=?", (notification_id,))
        conn.commit()
        conn.close()
        return True
    
    def calculate_savings_projection(self, user_id, goal_id, projection_months=24):
        """Calculate savings projection for a goal"""
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT monthly_contribution, current_amount FROM goal_jars WHERE id=? AND user_id=?
        """, (goal_id, user_id))
        goal = cursor.fetchone()
        conn.close()
        if not goal:
            return None
        monthly_contribution = goal['monthly_contribution']
        current_amount = goal['current_amount']
        projections = []
        for months in [6, 12, 24]:
            future_amount = current_amount + (monthly_contribution * months)
            projections.append({
                'months': months,
                'future_amount': future_amount,
                'projection_date': (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
            })
        return projections
    
    def get_goal_summary(self, user_id):
        """Get summary of all goals"""
        goals = self.get_user_goals(user_id)
        
        if not goals:
            return {
                'total_goals': 0,
                'total_target': 0,
                'total_saved': 0,
                'overall_progress': 0,
                'goals': []
            }
        
        total_target = sum(goal['target_amount'] for goal in goals)
        total_saved = sum(goal['current_amount'] for goal in goals)
        overall_progress = (total_saved / total_target * 100) if total_target > 0 else 0
        
        return {
            'total_goals': len(goals),
            'total_target': total_target,
            'total_saved': total_saved,
            'overall_progress': overall_progress,
            'goals': goals
        }
