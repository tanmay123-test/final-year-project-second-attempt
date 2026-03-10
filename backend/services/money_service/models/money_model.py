import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class MoneyModel:
    def __init__(self, db_path=None):
        if db_path is None:
            # Use the same path as other services
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'money_service.db')
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    merchant TEXT,
                    date DATE NOT NULL,
                    type TEXT DEFAULT 'expense',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Add merchant column if it doesn't exist (for existing tables)
            try:
                cursor.execute('''
                    ALTER TABLE transactions ADD COLUMN merchant TEXT
                ''')
            except sqlite3.OperationalError:
                # Column already exists, ignore error
                pass
            
            # Budgets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    period TEXT DEFAULT 'monthly',
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Goals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL DEFAULT 0,
                    deadline DATE,
                    category TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    icon TEXT,
                    color TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default categories
            default_categories = [
                ('Food', '#FF6B6B'),
                ('Shopping', '#4ECDC4'),
                ('Bills', '#45B7D1'),
                ('Transport', '#96CEB4'),
                ('Entertainment', '#FFEAA7'),
                ('Healthcare', '#DDA0DD'),
                ('Education', '#87CEEB'),
                ('Other', '#A0A0A0')
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)
            ''', default_categories)
            
            conn.commit()
    
    def add_transaction(self, user_id, category, amount, description, date, type='expense', merchant=''):
        """Add a new transaction"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (user_id, category, amount, description, date, type, merchant)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, category, amount, description, date, type, merchant))
            conn.commit()
            return cursor.lastrowid
    
    def get_transactions(self, user_id, limit=None, category=None, start_date=None, end_date=None):
        """Get transactions with filters"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT t.*, c.color as category_color
                FROM transactions t
                LEFT JOIN categories c ON t.category = c.name
                WHERE t.user_id = ?
            '''
            params = [user_id]
            
            if category:
                query += ' AND t.category = ?'
                params.append(category)
            
            if start_date:
                query += ' AND t.date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND t.date <= ?'
                params.append(end_date)
            
            query += ' ORDER BY t.date DESC, t.created_at DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_recent_transactions(self, user_id, limit=5):
        """Get recent transactions"""
        return self.get_transactions(user_id, limit=limit)
    
    def get_monthly_spending(self, user_id, month):
        """Get spending by category for a specific month"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.category, SUM(t.amount) as amount, c.color
                FROM transactions t
                LEFT JOIN categories c ON t.category = c.name
                WHERE t.user_id = ? AND strftime('%Y-%m', t.date) = ? AND t.type = 'expense'
                GROUP BY t.category
                ORDER BY amount DESC
            ''', (user_id, month))
            
            results = cursor.fetchall()
            return [
                {'category': row[0], 'amount': row[1], 'color': row[2]}
                for row in results
            ]
    
    def set_budget(self, user_id, category, amount, period='monthly'):
        """Set a budget for a category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Calculate start and end dates based on period
            now = datetime.now()
            if period == 'monthly':
                start_date = now.replace(day=1)
                if now.month == 12:
                    end_date = now.replace(year=now.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = now.replace(month=now.month+1, day=1) - timedelta(days=1)
            elif period == 'weekly':
                start_date = now - timedelta(days=now.weekday())
                end_date = start_date + timedelta(days=6)
            elif period == 'yearly':
                start_date = now.replace(month=1, day=1)
                end_date = now.replace(month=12, day=31)
            else:
                raise ValueError(f"Invalid period: {period}")
            
            # Deactivate existing budget for this category and period
            cursor.execute('''
                UPDATE budgets SET is_active = 0
                WHERE user_id = ? AND category = ? AND period = ? AND is_active = 1
            ''', (user_id, category, period))
            
            # Create new budget
            cursor.execute('''
                INSERT INTO budgets (user_id, category, amount, period, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, category, amount, period, start_date, end_date))
            conn.commit()
            return cursor.lastrowid
    
    def get_budgets(self, user_id):
        """Get user budgets"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.*, c.color as category_color,
                       (SELECT COALESCE(SUM(t.amount), 0) 
                        FROM transactions t 
                        WHERE t.user_id = b.user_id 
                        AND t.category = b.category 
                        AND t.date BETWEEN b.start_date AND b.end_date 
                        AND t.type = 'expense') as spent
                FROM budgets b
                LEFT JOIN categories c ON b.category = c.name
                WHERE b.user_id = ? AND b.is_active = 1
                ORDER BY b.created_at DESC
            ''', (user_id,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_active_budgets(self, user_id):
        """Get active budgets"""
        return self.get_budgets(user_id)
    
    def get_budget_for_category(self, user_id, category):
        """Get active budget for a specific category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM budgets 
                WHERE user_id = ? AND category = ? AND is_active = 1
                AND date('now') BETWEEN start_date AND end_date
                LIMIT 1
            ''', (user_id, category))
            
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_category_spending(self, user_id, category, period='monthly'):
        """Get spending for a category in the current period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if period == 'monthly':
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE user_id = ? AND category = ? AND type = 'expense'
                    AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
                ''', (user_id, category))
            elif period == 'weekly':
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE user_id = ? AND category = ? AND type = 'expense'
                    AND date >= date('now', 'weekday 0', '-7 days')
                ''', (user_id, category))
            else:
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0)
                    FROM transactions
                    WHERE user_id = ? AND category = ? AND type = 'expense'
                    AND strftime('%Y', date) = strftime('%Y', 'now')
                ''', (user_id, category))
            
            return cursor.fetchone()[0]
    
    def create_goal(self, user_id, name, target_amount, current_amount=0, deadline=None, category=None):
        """Create a savings goal"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO goals (user_id, name, target_amount, current_amount, deadline, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, target_amount, current_amount, deadline, category))
            conn.commit()
            return cursor.lastrowid
    
    def get_goals(self, user_id):
        """Get user goals"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT g.*, c.color as category_color,
                       ROUND((g.current_amount / g.target_amount) * 100, 2) as progress_percentage
                FROM goals g
                LEFT JOIN categories c ON g.category = c.name
                WHERE g.user_id = ? AND g.is_active = 1
                ORDER BY g.created_at DESC
            ''', (user_id,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_active_goals(self, user_id):
        """Get active goals"""
        return self.get_goals(user_id)
    
    def get_monthly_analytics(self, user_id, months=6):
        """Get monthly analytics for the past months"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get monthly income vs expenses
            cursor.execute('''
                SELECT strftime('%Y-%m', date) as month,
                       SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
                       SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expenses,
                       COUNT(*) as transaction_count
                FROM transactions
                WHERE user_id = ? AND date >= date('now', '-{} months')
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month DESC
            '''.format(months), (user_id,))
            
            monthly_data = cursor.fetchall()
            
            # Get top categories
            cursor.execute('''
                SELECT category, SUM(amount) as total_amount
                FROM transactions
                WHERE user_id = ? AND type = 'expense' 
                AND date >= date('now', '-{} months')
                GROUP BY category
                ORDER BY total_amount DESC
                LIMIT 5
            '''.format(months), (user_id,))
            
            top_categories = cursor.fetchall()
            
            return {
                'monthly_summary': [
                    {
                        'month': row[0],
                        'income': row[1],
                        'expenses': row[2],
                        'transaction_count': row[3]
                    }
                    for row in monthly_data
                ],
                'top_categories': [
                    {'category': row[0], 'total_amount': row[1]}
                    for row in top_categories
                ]
            }
    
    def get_user_financial_summary(self, user_id):
        """Get comprehensive financial summary for AI context"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Current month spending
            current_month = datetime.now().strftime('%Y-%m')
            cursor.execute('''
                SELECT category, SUM(amount) as amount
                FROM transactions
                WHERE user_id = ? AND strftime('%Y-%m', date) = ? AND type = 'expense'
                GROUP BY category
            ''', (user_id, current_month))
            
            monthly_spending = dict(cursor.fetchall())
            
            # Active budgets
            budgets = self.get_budgets(user_id)
            
            # Active goals
            goals = self.get_goals(user_id)
            
            # Recent transactions
            recent = self.get_recent_transactions(user_id, limit=10)
            
            return {
                'monthly_spending': monthly_spending,
                'budgets': budgets,
                'goals': goals,
                'recent_transactions': recent
            }
