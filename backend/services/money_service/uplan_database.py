import sqlite3
from datetime import datetime

class UPlanDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('expertease.db')
        self.conn.row_factory = sqlite3.Row
        self.create_uplan_tables()
    
    def create_uplan_tables(self):
        """Create U-Plan financial planning tables"""
        cursor = self.conn.cursor()
        
        # U-Plan main table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS uplan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            monthly_income REAL,
            fixed_expenses_total REAL,
            disposable_income REAL,
            savings_target REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Fixed expenses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixed_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            expense_name TEXT,
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Budgets table (enhanced for U-Plan)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS uplan_budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            budget_amount REAL,
            budget_type TEXT, -- 'needs', 'wants', 'savings'
            month TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, category, month, year)
        )
        """)
        
        # Budget rewards table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            reward_type TEXT,
            description TEXT,
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Goal jars table (enhanced)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS uplan_goal_jars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_name TEXT,
            target_amount REAL,
            current_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Budget tracking table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            spent_amount REAL DEFAULT 0,
            remaining_budget REAL DEFAULT 0,
            month TEXT,
            year INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, category, month, year)
        )
        """)
        
        self.conn.commit()
    
    def create_financial_plan(self, user_id, monthly_income, fixed_expenses):
        """Create U-Plan financial plan"""
        cursor = self.conn.cursor()
        
        # Calculate total fixed expenses
        total_fixed = sum(exp['amount'] for exp in fixed_expenses)
        disposable_income = monthly_income - total_fixed
        
        # Insert main plan
        cursor.execute("""
        INSERT OR REPLACE INTO uplan 
        (user_id, monthly_income, fixed_expenses_total, disposable_income, savings_target)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, monthly_income, total_fixed, disposable_income, disposable_income * 0.2))
        
        # Clear and insert fixed expenses
        cursor.execute("DELETE FROM fixed_expenses WHERE user_id=?", (user_id,))
        for expense in fixed_expenses:
            cursor.execute("""
            INSERT INTO fixed_expenses (user_id, expense_name, amount)
            VALUES (?, ?, ?)
            """, (user_id, expense['name'], expense['amount']))
        
        self.conn.commit()
        return {
            'monthly_income': monthly_income,
            'fixed_expenses_total': total_fixed,
            'disposable_income': disposable_income,
            'savings_target': disposable_income * 0.2
        }
    
    def get_financial_plan(self, user_id):
        """Get user's financial plan"""
        cursor = self.conn.cursor()
        
        # Get main plan
        cursor.execute("""
        SELECT monthly_income, fixed_expenses_total, disposable_income, savings_target
        FROM uplan WHERE user_id=?
        """, (user_id,))
        plan = cursor.fetchone()
        
        if not plan:
            return None
        
        # Get fixed expenses
        cursor.execute("""
        SELECT expense_name, amount FROM fixed_expenses WHERE user_id=?
        """, (user_id,))
        fixed_expenses = [dict(row) for row in cursor.fetchall()]
        
        return {
            'monthly_income': plan['monthly_income'],
            'fixed_expenses_total': plan['fixed_expenses_total'],
            'disposable_income': plan['disposable_income'],
            'savings_target': plan['savings_target'],
            'fixed_expenses': fixed_expenses
        }
    
    def create_category_budgets(self, user_id, budgets, month, year):
        """Create category budgets based on U-Plan allocation"""
        cursor = self.conn.cursor()
        
        for budget in budgets:
            cursor.execute("""
            INSERT OR REPLACE INTO uplan_budgets 
            (user_id, category, budget_amount, budget_type, month, year)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, budget['category'], budget['amount'], 
                  budget['type'], month, year))
        
        self.conn.commit()
    
    def get_category_budgets(self, user_id, month, year):
        """Get category budgets for a month"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT category, budget_amount, budget_type FROM uplan_budgets 
        WHERE user_id=? AND month=? AND year=?
        """, (user_id, month, year))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_budget_tracking(self, user_id, category, spent_amount, month, year):
        """Update budget tracking with spent amount"""
        cursor = self.conn.cursor()
        
        # Get budget amount
        cursor.execute("""
        SELECT budget_amount FROM uplan_budgets 
        WHERE user_id=? AND category=? AND month=? AND year=?
        """, (user_id, category, month, year))
        budget_result = cursor.fetchone()
        
        if budget_result:
            budget_amount = budget_result[0]
            remaining = budget_amount - spent_amount
            
            cursor.execute("""
            INSERT OR REPLACE INTO budget_tracking 
            (user_id, category, spent_amount, remaining_budget, month, year, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, category, spent_amount, remaining, month, year))
            
            self.conn.commit()
            return remaining
        return 0
    
    def get_budget_status(self, user_id, month, year):
        """Get budget status for all categories"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT b.category, b.budget_amount, b.budget_type,
               COALESCE(t.spent_amount, 0) as spent,
               COALESCE(t.remaining_budget, b.budget_amount) as remaining
        FROM uplan_budgets b
        LEFT JOIN budget_tracking t ON b.user_id = t.user_id AND b.category = t.category 
                                    AND b.month = t.month AND b.year = t.year
        WHERE b.user_id=? AND b.month=? AND b.year=?
        """, (user_id, month, year))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def add_reward(self, user_id, reward_type, description):
        """Add budget reward"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO budget_rewards (user_id, reward_type, description)
        VALUES (?, ?, ?)
        """, (user_id, reward_type, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_rewards(self, user_id):
        """Get user's rewards"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT reward_type, description, achieved_at 
        FROM budget_rewards WHERE user_id=?
        ORDER BY achieved_at DESC
        """, (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def create_goal_jar(self, user_id, goal_name, target_amount):
        """Create goal jar"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO uplan_goal_jars (user_id, goal_name, target_amount)
            VALUES (?, ?, ?)
        """, (user_id, goal_name, target_amount))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_goal_jar(self, user_id, goal_name, amount):
        """Update goal jar amount"""
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE uplan_goal_jars 
        SET current_amount = current_amount + ?
        WHERE user_id=? AND goal_name=?
        """, (amount, user_id, goal_name))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_goal_jars(self, user_id):
        """Get user's goal jars"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT goal_name, target_amount, current_amount,
               (current_amount / target_amount * 100) as percentage
        FROM uplan_goal_jars WHERE user_id=?
        ORDER BY created_at DESC
        """, (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_monthly_spending_data(self, user_id, month, year):
        """Get monthly spending data from transactions"""
        cursor = self.conn.cursor()
        
        # Convert month name to month number if needed
        if isinstance(month, str):
            month_names = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            month_num = month_names.get(month, 1)
        else:
            month_num = month
        
        cursor.execute("""
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        GROUP BY category
        ORDER BY total DESC
        """, (user_id, f"{month_num:02d}", str(year)))
        
        return [dict(row) for row in cursor.fetchall()]
