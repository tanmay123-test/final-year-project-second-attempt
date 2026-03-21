import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime, timedelta
from .money_db import MoneyServiceDB

load_dotenv()

class AdvancedFinnyDB(MoneyServiceDB):
    def __init__(self):
        super().__init__()
        self.create_advanced_tables()
    
    def create_advanced_tables(self):
        """Create advanced financial intelligence tables"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Monthly budgets table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_budgets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                category TEXT,
                budget_amount FLOAT,
                month TEXT,
                year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category, month, year)
            )
            """)
            
            # Merchant-category learning table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS merchant_category_learning (
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                score INTEGER,
                budget_adherence FLOAT,
                spending_stability FLOAT,
                category_balance FLOAT,
                month TEXT,
                year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Spending predictions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS spending_predictions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                category TEXT,
                current_spending FLOAT,
                predicted_spending FLOAT,
                prediction_date TEXT,
                month TEXT,
                year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def set_monthly_budget(self, user_id, category, budget_amount, month, year):
        """Set monthly budget for a category"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO monthly_budgets (user_id, category, budget_amount, month, year)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, category, month, year) DO UPDATE SET
            budget_amount = EXCLUDED.budget_amount
            RETURNING id
            """, (user_id, category, budget_amount, month, year))
            budget_id = cursor.fetchone()[0]
            conn.commit()
            return budget_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_monthly_budgets(self, user_id, month, year):
        """Get all budgets for a month"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
            SELECT category, budget_amount FROM monthly_budgets 
            WHERE user_id=%s AND month=%s AND year=%s
            """, (user_id, month, year))
            return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_budget_status(self, user_id, category, month_str, year):
        """Get budget status with current spending"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Get budget
            cursor.execute("""
            SELECT budget_amount FROM monthly_budgets 
            WHERE user_id=%s AND category=%s AND month=%s AND year=%s
            """, (user_id, category, month_str, year))
            budget_result = cursor.fetchone()
            
            if not budget_result:
                return None, 0, 0
            
            budget_amount = budget_result[0]
            
            # Map month name to number for PostgreSQL TO_CHAR check
            month_map = {
                'January': '01', 'February': '02', 'March': '03', 'April': '04',
                'May': '05', 'June': '06', 'July': '07', 'August': '08',
                'September': '09', 'October': '10', 'November': '11', 'December': '12'
            }
            month_num = month_map.get(month_str, '01')
            
            # Get current spending
            cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE user_id=%s AND category=%s AND TO_CHAR(date::DATE, 'MM')=%s AND TO_CHAR(date::DATE, 'YYYY')=%s
            """, (user_id, category, month_num, str(year)))
            current_spending = cursor.fetchone()[0]
            
            # Calculate percentage
            percentage = (current_spending / budget_amount * 100) if budget_amount > 0 else 0
            
            return budget_amount, current_spending, percentage
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def learn_merchant_category(self, merchant, category):
        """Learn merchant-category mapping"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO merchant_category_learning (merchant, category, confidence, usage_count, last_used)
            VALUES (%s, %s, 1, 1, CURRENT_TIMESTAMP)
            ON CONFLICT (merchant, category) DO UPDATE SET
            confidence = merchant_category_learning.confidence + 1,
            usage_count = merchant_category_learning.usage_count + 1,
            last_used = CURRENT_TIMESTAMP
            """, (merchant, category))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_learned_category(self, merchant):
        """Get learned category for a merchant"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT category FROM merchant_category_learning 
            WHERE merchant=%s 
            ORDER BY confidence DESC, usage_count DESC 
            LIMIT 1
            """, (merchant,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_weekly_spending(self, user_id, year, month):
        """Get weekly spending breakdown for a month"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
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
                    next_month = month % 12 + 1
                    next_year = year + (1 if month == 12 else 0)
                    week_end = datetime(next_year, next_month, 1) - timedelta(days=1)
                
                cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE user_id=%s AND date::DATE >= %s AND date::DATE <= %s
                """, (user_id, week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")))
                
                week_total = cursor.fetchone()[0]
                weekly_data.append({
                    'week': week,
                    'total': week_total,
                    'start_date': week_start.strftime("%Y-%m-%d"),
                    'end_date': week_end.strftime("%Y-%m-%d")
                })
            
            return weekly_data
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_month_comparison(self, user_id, category, current_month, current_year):
        """Compare current month spending with previous month"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Current month spending
            cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE user_id=%s AND category=%s AND TO_CHAR(date::DATE, 'MM')=%s AND TO_CHAR(date::DATE, 'YYYY')=%s
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
            WHERE user_id=%s AND category=%s AND TO_CHAR(date::DATE, 'MM')=%s AND TO_CHAR(date::DATE, 'YYYY')=%s
            """, (user_id, category, f"{prev_month:02d}", str(prev_year)))
            prev_spending = cursor.fetchone()[0]
            
            # Calculate percentage change
            if prev_spending > 0:
                change_percent = ((current_spending - prev_spending) / prev_spending) * 100
            else:
                change_percent = 100 if current_spending > 0 else 0
            
            return prev_spending, current_spending, change_percent
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_top_merchant(self, user_id, month, year):
        """Get top merchant by spending for a month"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT merchant, SUM(amount) as total_spending
            FROM transactions 
            WHERE user_id=%s AND TO_CHAR(date::DATE, 'MM')=%s AND TO_CHAR(date::DATE, 'YYYY')=%s
            GROUP BY merchant
            ORDER BY total_spending DESC
            LIMIT 1
            """, (user_id, f"{month:02d}", str(year)))
            result = cursor.fetchone()
            return result if result else (None, 0)
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def predict_monthly_spending(self, user_id, category, month, year):
        """Predict end-of-month spending based on current rate"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Get current spending
            cursor.execute("""
            SELECT COALESCE(SUM(amount), 0), COUNT(*) as transaction_count
            FROM transactions 
            WHERE user_id=%s AND category=%s AND TO_CHAR(date::DATE, 'MM')=%s AND TO_CHAR(date::DATE, 'YYYY')=%s
            """, (user_id, category, f"{month:02d}", str(year)))
            current_data = cursor.fetchone()
            current_spending = current_data[0]
            transaction_count = current_data[1]
            
            if transaction_count == 0:
                return current_spending, current_spending
            
            # Get days passed in month
            current_date = datetime.now()
            days_passed = current_date.day
            # Simplified days in month
            days_in_month = 31 if month in [1,3,5,7,8,10,12] else (30 if month != 2 else 28)
            
            # Calculate daily average
            daily_average = current_spending / days_passed if days_passed > 0 else 0
            
            # Predict end-of-month spending
            remaining_days = days_in_month - days_passed
            predicted_spending = current_spending + (daily_average * remaining_days)
            
            # Save prediction using primary key or unique constraint if exists, 
            # or just insert since there's no unique constraint on spending_predictions in original
            cursor.execute("""
            INSERT INTO spending_predictions 
            (user_id, category, current_spending, predicted_spending, prediction_date, month, year)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, category, current_spending, predicted_spending, 
                  current_date.strftime("%Y-%m-%d"), str(month), year))
            
            conn.commit()
            return current_spending, predicted_spending
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def detect_duplicate_transaction(self, user_id, amount, category, merchant, date, time_window_minutes=5):
        """Detect potential duplicate transactions"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Get recent transactions within same date and same details
            cursor.execute("""
            SELECT id, amount, category, merchant, date
            FROM transactions 
            WHERE user_id=%s AND amount=%s AND category=%s AND merchant=%s AND date=%s
            ORDER BY created_at DESC
            LIMIT 5
            """, (user_id, amount, category, merchant, date))
            
            recent_transactions = cursor.fetchall()
            
            # Check for exact duplicates
            for trans in recent_transactions:
                # This is a potential duplicate
                return trans[0]  # Return transaction ID
            
            return None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def calculate_financial_health_score(self, user_id, month, year):
        """Calculate comprehensive financial health score"""
        # Get all budgets for the month
        # Convert month number to month name for get_monthly_budgets if needed
        month_names = ["", "January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        month_name = month_names[month]
        
        budgets = self.get_monthly_budgets(user_id, month_name, year)
        
        if not budgets:
            return 50, 50, 50, 50  # Default score if no budgets set
        
        # Budget Adherence Score (0-100)
        budget_adherence_total = 0
        budget_count = 0
        
        for budget in budgets:
            category = budget['category']
            _, current_spending, percentage = self.get_budget_status(user_id, category, month_name, year)
            
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
            stability_score = max(20, 100 - (variance / (avg_spending + 1) * 100)) if avg_spending > 0 else 50
        else:
            stability_score = 50
        
        # Category Balance Score (based on distribution)
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM transactions 
            WHERE user_id=%s AND TO_CHAR(date::DATE, 'MM')=%s AND TO_CHAR(date::DATE, 'YYYY')=%s
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
            INSERT INTO financial_health_scores 
            (user_id, score, budget_adherence, spending_stability, category_balance, month, year)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, int(overall_score), budget_adherence_score, stability_score, balance_score, month_name, year))
            
            conn.commit()
            return int(overall_score), budget_adherence_score, stability_score, balance_score
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
