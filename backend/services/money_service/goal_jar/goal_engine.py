import sqlite3
from datetime import datetime, timedelta

class GoalEngine:
    """Main engine for goal jar management"""
    
    def __init__(self):
        self.conn = sqlite3.connect('expertease.db')
        self.conn.row_factory = sqlite3.Row
        self.create_goal_tables()
        self._ensure_goal_schema()
    
    def create_goal_tables(self):
        """Create goal jars tables"""
        cursor = self.conn.cursor()
        
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
        
        self.conn.commit()
    
    def _ensure_goal_schema(self):
        """Safely migrate goal_jars schema if older DB exists without new columns"""
        cursor = self.conn.cursor()
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
            self.conn.commit()
        except Exception:
            pass
        finally:
            cursor.close()
    
    def create_goal(self, user_id, goal_name, target_amount, monthly_contribution, target_date=None):
        """Create a new goal"""
        cursor = self.conn.cursor()
        
        # Calculate feasibility
        months_required = int(target_amount / monthly_contribution) if monthly_contribution > 0 else 999
        
        # Set default target date if not provided
        if not target_date:
            target_date = (datetime.now() + timedelta(days=months_required * 30)).strftime('%Y-%m-%d')
        else:
            # Normalize provided date to YYYY-MM-DD string
            try:
                target_date = datetime.strptime(str(target_date), '%Y-%m-%d').strftime('%Y-%m-%d')
            except Exception:
                target_date = str(target_date)
        
        cursor.execute("""
        INSERT INTO goal_jars 
        (user_id, goal_name, target_amount, monthly_contribution, target_date)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, goal_name, target_amount, monthly_contribution, target_date))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_goals(self, user_id):
        """Get all goals for a user"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM goal_jars 
        WHERE user_id=? 
        ORDER BY created_at DESC
        """, (user_id,))
        
        goals = []
        for row in cursor.fetchall():
            goal = dict(row)
            # Calculate progress
            goal['progress_percentage'] = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            goal['remaining_amount'] = goal['target_amount'] - goal['current_amount']
            goal['months_remaining'] = max(0, int(goal['remaining_amount'] / goal['monthly_contribution'])) if goal['monthly_contribution'] > 0 else 999
            
            # Calculate months passed
            if goal['target_date']:
                target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
                months_passed = max(0, (datetime.now() - target_date).days // 30)
                goal['months_passed'] = months_passed
            else:
                goal['months_passed'] = 0
            
            goals.append(goal)
        
        return goals
    
    def add_savings(self, user_id, goal_id, amount, payment_method='online', notes=''):
        """Add savings to a goal"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        INSERT INTO goal_savings 
        (goal_id, user_id, amount, transaction_date, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (goal_id, user_id, amount, datetime.now().date(), payment_method, notes))
        
        # Update goal current amount
        cursor.execute("""
        UPDATE goal_jars 
        SET current_amount = current_amount + ?, updated_at = CURRENT_TIMESTAMP
        WHERE id=? AND user_id=?
        """, (amount, goal_id, user_id))
        
        self.conn.commit()
        return True
    
    def get_goal_progress(self, user_id, goal_id):
        """Get detailed progress for a specific goal"""
        cursor = self.conn.cursor()
        
        # Get goal details
        cursor.execute("""
        SELECT * FROM goal_jars 
        WHERE id=? AND user_id=?
        """, (goal_id, user_id))
        goal = cursor.fetchone()
        
        if not goal:
            return None
        
        goal = dict(goal)
        
        # Get savings history
        cursor.execute("""
        SELECT * FROM goal_savings 
        WHERE goal_id=? AND user_id=?
        ORDER BY transaction_date DESC
        """, (goal_id, user_id))
        savings_history = [dict(row) for row in cursor.fetchall()]
        
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
                    'description': f"₹{contribution:.0f}/month"
                })
        
        return timelines
    
    def transfer_leftover_to_goal(self, user_id, goal_id, amount, source_category):
        """Transfer leftover budget to goal"""
        cursor = self.conn.cursor()
        
        # Add to goal savings
        cursor.execute("""
        INSERT INTO goal_savings 
        (goal_id, user_id, amount, transaction_date, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (goal_id, user_id, amount, datetime.now().date(), 'budget_transfer', f"Transfer from {source_category}"))
        
        # Update goal amount
        cursor.execute("""
        UPDATE goal_jars 
        SET current_amount = current_amount + ?, updated_at = CURRENT_TIMESTAMP
        WHERE id=? AND user_id=?
        """, (amount, goal_id, user_id))
        
        self.conn.commit()
        return True
    
    def get_goal_acceleration_suggestions(self, user_id):
        """Analyze spending and suggest goal acceleration"""
        cursor = self.conn.cursor()
        
        # Get recent transactions (last 3 months)
        three_months_ago = datetime.now() - timedelta(days=90)
        cursor.execute("""
        SELECT category, SUM(amount) as total_spent, COUNT(*) as transaction_count
        FROM transactions 
        WHERE user_id=? AND date >= ?
        GROUP BY category
        ORDER BY total_spent DESC
        """, (user_id, three_months_ago.date()))
        
        spending_data = cursor.fetchall()
        
        suggestions = []
        
        for spending in spending_data:
            category = spending['category']
            monthly_avg = spending['total_spent'] / 3  # Average over 3 months
            
            # Suggest reduction strategies
            if monthly_avg > 2000:  # High spending category
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
        cursor = self.conn.cursor()
        
        cursor.execute("""
        INSERT INTO goal_notifications 
        (user_id, goal_id, notification_type, message, scheduled_date)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, goal_id, notification_type, message, scheduled_date))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_pending_notifications(self, user_id):
        """Get pending notifications to send"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT * FROM goal_notifications 
        WHERE user_id=? AND is_sent=0 AND scheduled_date <= date('now')
        ORDER BY scheduled_date ASC
        """, (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_notification_sent(self, notification_id):
        """Mark notification as sent"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        UPDATE goal_notifications 
        SET is_sent=1 
        WHERE id=?
        """, (notification_id,))
        
        self.conn.commit()
        return True
    
    def calculate_savings_projection(self, user_id, goal_id, projection_months=24):
        """Calculate savings projection for a goal"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        SELECT monthly_contribution, current_amount 
        FROM goal_jars 
        WHERE id=? AND user_id=?
        """, (goal_id, user_id))
        
        goal = cursor.fetchone()
        
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
