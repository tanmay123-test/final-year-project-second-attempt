import sqlite3
import os
from datetime import datetime, timedelta
from .money_db import MoneyServiceDB

class AdvancedFinnyDB(MoneyServiceDB):
    def __init__(self):
        super().__init__()
        self.create_advanced_tables()
    
    def create_advanced_tables(self):
        """Create advanced financial intelligence tables"""
        cursor = self.conn.cursor()
        
        # Monthly budgets table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            budget_amount REAL,
            month TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, category, month, year)
        )
        """)
        
        # Merchant-category learning table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchant_category_learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant TEXT,
            category TEXT,
            confidence INTEGER DEFAULT 1,
            usage_count INTEGER DEFAULT 1,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(merchant, category)
        )
        """)
        
        # Financial health scores table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_health_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            score INTEGER,
            budget_adherence REAL,
            spending_stability REAL,
            category_balance REAL,
            month TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Spending predictions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS spending_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            current_spending REAL,
            predicted_spending REAL,
            prediction_date TEXT,
            month TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        self.conn.commit()
    
    def set_monthly_budget(self, user_id, category, budget_amount, month, year):
        """Set monthly budget for a category"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO monthly_budgets (user_id, category, budget_amount, month, year)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, category, budget_amount, month, year))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_monthly_budgets(self, user_id, month, year):
        """Get all budgets for a month"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT category, budget_amount FROM monthly_budgets 
        WHERE user_id=? AND month=? AND year=?
        """, (user_id, month, year))
        return cursor.fetchall()
    
    def get_budget_status(self, user_id, category, month, year):
        """Get budget status with current spending"""
        cursor = self.conn.cursor()
        
        # Get budget
        cursor.execute("""
        SELECT budget_amount FROM monthly_budgets 
        WHERE user_id=? AND category=? AND month=? AND year=?
        """, (user_id, category, month, year))
        budget_result = cursor.fetchone()
        
        if not budget_result:
            return None, 0, 0
        
        budget_amount = budget_result[0]
        
        # Get current spending
        cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id=? AND category=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        """, (user_id, category, f"{month:02d}", str(year)))
        current_spending = cursor.fetchone()[0]
        
        # Calculate percentage
        percentage = (current_spending / budget_amount * 100) if budget_amount > 0 else 0
        
        return budget_amount, current_spending, percentage
    
    def learn_merchant_category(self, merchant, category):
        """Learn merchant-category mapping"""
        cursor = self.conn.cursor()
        
        # Check if mapping exists
        cursor.execute("""
        SELECT confidence, usage_count FROM merchant_category_learning 
        WHERE merchant=? AND category=?
        """, (merchant, category))
        result = cursor.fetchone()
        
        if result:
            # Update existing mapping
            confidence, usage_count = result
            cursor.execute("""
            UPDATE merchant_category_learning 
            SET confidence = confidence + 1, 
                usage_count = usage_count + 1,
                last_used = CURRENT_TIMESTAMP
            WHERE merchant=? AND category=?
            """, (merchant, category))
        else:
            # Create new mapping
            cursor.execute("""
            INSERT INTO merchant_category_learning (merchant, category, confidence, usage_count)
            VALUES (?, ?, 1, 1)
            """, (merchant, category))
        
        self.conn.commit()
    
    def get_learned_category(self, merchant):
        """Get learned category for a merchant"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT category, confidence FROM merchant_category_learning 
        WHERE merchant=? 
        ORDER BY confidence DESC, usage_count DESC 
        LIMIT 1
        """, (merchant,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_weekly_spending(self, user_id, year, month):
        """Get weekly spending breakdown for a month"""
        cursor = self.conn.cursor()
        
        weekly_data = []
        for week in range(1, 5):
            # Calculate week start and end dates
            first_day = datetime(year, month, 1)
            week_start = first_day + timedelta(weeks=week-1)
            week_end = week_start + timedelta(days=6)
            
            # Adjust for month boundaries
            if week_start.month != month:
                continue
            if week_end.month != month:
                week_end = datetime(year, month, 1) + timedelta(days=32)
                week_end = week_end.replace(day=1) - timedelta(days=1)
            
            cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE user_id=? AND date >= ? AND date <= ?
            """, (user_id, week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")))
            
            week_total = cursor.fetchone()[0]
            weekly_data.append({
                'week': week,
                'total': week_total,
                'start_date': week_start.strftime("%Y-%m-%d"),
                'end_date': week_end.strftime("%Y-%m-%d")
            })
        
        return weekly_data
    
    def get_month_comparison(self, user_id, category, current_month, current_year):
        """Compare current month spending with previous month"""
        cursor = self.conn.cursor()
        
        # Current month spending
        cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id=? AND category=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        """, (user_id, category, f"{current_month:02d}", str(current_year)))
        current_spending = cursor.fetchone()[0]
        
        # Previous month spending
        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year
        
        cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE user_id=? AND category=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        """, (user_id, category, f"{prev_month:02d}", str(prev_year)))
        prev_spending = cursor.fetchone()[0]
        
        # Calculate percentage change
        if prev_spending > 0:
            change_percent = ((current_spending - prev_spending) / prev_spending) * 100
        else:
            change_percent = 100 if current_spending > 0 else 0
        
        return prev_spending, current_spending, change_percent
    
    def get_top_merchant(self, user_id, month, year):
        """Get top merchant by spending for a month"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT merchant, SUM(amount) as total_spending
        FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        GROUP BY merchant
        ORDER BY total_spending DESC
        LIMIT 1
        """, (user_id, f"{month:02d}", str(year)))
        result = cursor.fetchone()
        return result if result else (None, 0)
    
    def predict_monthly_spending(self, user_id, category, month, year):
        """Predict end-of-month spending based on current rate"""
        cursor = self.conn.cursor()
        
        # Get current spending
        cursor.execute("""
        SELECT COALESCE(SUM(amount), 0), COUNT(*) as transaction_count
        FROM transactions 
        WHERE user_id=? AND category=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        """, (user_id, category, f"{month:02d}", str(year)))
        current_data = cursor.fetchone()
        current_spending = current_data[0]
        transaction_count = current_data[1]
        
        if transaction_count == 0:
            return current_spending, current_spending
        
        # Get days passed in month
        current_date = datetime.now()
        days_passed = current_date.day
        days_in_month = 31 if month in [1,3,5,7,8,10,12] else (30 if month != 2 else 28)
        
        # Calculate daily average
        daily_average = current_spending / days_passed if days_passed > 0 else 0
        
        # Predict end-of-month spending
        remaining_days = days_in_month - days_passed
        predicted_spending = current_spending + (daily_average * remaining_days)
        
        # Save prediction
        cursor.execute("""
        INSERT OR REPLACE INTO spending_predictions 
        (user_id, category, current_spending, predicted_spending, prediction_date, month, year)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, category, current_spending, predicted_spending, 
              current_date.strftime("%Y-%m-%d"), month, year))
        self.conn.commit()
        
        return current_spending, predicted_spending
    
    def detect_duplicate_transaction(self, user_id, amount, category, merchant, date, time_window_minutes=5):
        """Detect potential duplicate transactions"""
        cursor = self.conn.cursor()
        
        # Get recent transactions within time window
        cursor.execute("""
        SELECT id, amount, category, merchant, date
        FROM transactions 
        WHERE user_id=? AND amount=? AND category=? AND merchant=? AND date=?
        ORDER BY created_at DESC
        LIMIT 5
        """, (user_id, amount, category, merchant, date))
        
        recent_transactions = cursor.fetchall()
        
        # Check for exact duplicates
        for trans in recent_transactions:
            # This is a potential duplicate
            return trans[0]  # Return transaction ID
        
        return None
    
    def calculate_financial_health_score(self, user_id, month, year):
        """Calculate comprehensive financial health score"""
        cursor = self.conn.cursor()
        
        # Get all budgets for the month
        budgets = self.get_monthly_budgets(user_id, month, year)
        
        if not budgets:
            return 50, 50, 50, 50  # Default score if no budgets set
        
        # Budget Adherence Score (0-100)
        budget_adherence_total = 0
        budget_count = 0
        
        for category, budget_amount in budgets:
            _, current_spending, percentage = self.get_budget_status(user_id, category, month, year)
            
            if percentage <= 80:
                score = 100
            elif percentage <= 100:
                score = 80 - (percentage - 80) * 2  # 80-60 range
            else:
                score = max(20, 60 - (percentage - 100))  # Below 60
            
            budget_adherence_total += score
            budget_count += 1
        
        budget_adherence_score = budget_adherence_total / budget_count if budget_count > 0 else 50
        
        # Spending Stability Score (based on weekly consistency)
        weekly_data = self.get_weekly_spending(user_id, year, month)
        if len(weekly_data) > 1:
            weekly_totals = [w['total'] for w in weekly_data]
            avg_spending = sum(weekly_totals) / len(weekly_totals)
            variance = sum((x - avg_spending) ** 2 for x in weekly_totals) / len(weekly_totals)
            
            # Lower variance = higher stability
            stability_score = max(20, 100 - (variance / avg_spending * 100)) if avg_spending > 0 else 50
        else:
            stability_score = 50
        
        # Category Balance Score (based on distribution)
        cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        GROUP BY category
        """, (user_id, f"{month:02d}", str(year)))
        category_spending = cursor.fetchall()
        
        if len(category_spending) > 1:
            total_spending = sum(cat[1] for cat in category_spending)
            category_percentages = [cat[1] / total_spending * 100 for cat in category_spending]
            
            # Calculate balance (closer to equal distribution = higher score)
            ideal_percentage = 100 / len(category_percentages)
            deviation = sum(abs(p - ideal_percentage) for p in category_percentages)
            balance_score = max(20, 100 - deviation)
        else:
            balance_score = 50
        
        # Overall Financial Health Score
        overall_score = (budget_adherence_score + stability_score + balance_score) / 3
        
        # Save score
        cursor.execute("""
        INSERT OR REPLACE INTO financial_health_scores 
        (user_id, score, budget_adherence, spending_stability, category_balance, month, year)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, int(overall_score), budget_adherence_score, stability_score, balance_score, month, year))
        self.conn.commit()
        
        return int(overall_score), budget_adherence_score, stability_score, balance_score
