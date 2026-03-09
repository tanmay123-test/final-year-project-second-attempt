import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "..", "expertease.db")

class MoneyServiceDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Transactions table for Finny
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            merchant TEXT,
            date TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Budgets table for Smart Budget Planner
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            monthly_limit REAL,
            current_spending REAL DEFAULT 0,
            month TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Goal Jars table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS goal_jars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_name TEXT,
            target_amount REAL,
            current_amount REAL DEFAULT 0,
            monthly_saving REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Loan calculations table (for history)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS loan_calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            loan_amount REAL,
            interest_rate REAL,
            tenure_months INTEGER,
            monthly_emi REAL,
            total_interest REAL,
            total_repayment REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        self.conn.commit()

    # Finny - Transaction Management
    def add_transaction(self, user_id, amount, category, merchant, date, description=""):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO transactions (user_id, amount, category, merchant, date, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, amount, category, merchant, date, description))
        self.conn.commit()
        
        # Update budget spending
        self.update_budget_spending(user_id, category, amount)
        
        return cursor.lastrowid

    def get_transactions(self, user_id, month=None, year=None):
        cursor = self.conn.cursor()
        if month and year:
            cursor.execute("""
            SELECT * FROM transactions WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
            ORDER BY date DESC
            """, (user_id, f"{month:02d}", str(year)))
        else:
            cursor.execute("""
            SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC
            """, (user_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def get_monthly_summary(self, user_id, month, year):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        GROUP BY category
        ORDER BY total DESC
        """, (user_id, f"{month:02d}", str(year)))
        return cursor.fetchall()

    # Smart Budget Planner
    def create_budget(self, user_id, category, monthly_limit, month, year):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO budgets (user_id, category, monthly_limit, month, year)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, category, monthly_limit, month, year))
        self.conn.commit()
        return cursor.lastrowid

    def get_budgets(self, user_id, month, year):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM budgets WHERE user_id=? AND month=? AND year=?
        """, (user_id, month, year))
        return cursor.fetchall()

    def update_budget_spending(self, user_id, category, amount):
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().year
        
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE budgets 
        SET current_spending = current_spending + ?
        WHERE user_id=? AND category=? AND month=? AND year=?
        """, (amount, user_id, category, current_month, current_year))
        self.conn.commit()

    # Goal Jar
    def create_goal_jar(self, user_id, goal_name, target_amount, monthly_saving):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO goal_jars (user_id, goal_name, target_amount, monthly_saving)
        VALUES (?, ?, ?, ?)
        """, (user_id, goal_name, target_amount, monthly_saving))
        self.conn.commit()
        return cursor.lastrowid

    def get_goal_jars(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM goal_jars WHERE user_id=? ORDER BY created_at DESC
        """, (user_id,))
        return cursor.fetchall()

    def update_goal_jar(self, jar_id, amount_to_add):
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE goal_jars 
        SET current_amount = current_amount + ?
        WHERE id=?
        """, (amount_to_add, jar_id))
        self.conn.commit()

    # Loan Analyzer
    def save_loan_calculation(self, user_id, loan_amount, interest_rate, tenure_months, monthly_emi, total_interest, total_repayment):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO loan_calculations 
        (user_id, loan_amount, interest_rate, tenure_months, monthly_emi, total_interest, total_repayment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, loan_amount, interest_rate, tenure_months, monthly_emi, total_interest, total_repayment))
        self.conn.commit()
        return cursor.lastrowid

    def get_loan_history(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM loan_calculations WHERE user_id=? ORDER BY created_at DESC
        """, (user_id,))
        return cursor.fetchall()
