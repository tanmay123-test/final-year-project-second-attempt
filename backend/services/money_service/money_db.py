import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class MoneyServiceDB:
    def __init__(self):
        self.create_tables()

    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    def create_tables(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Transactions table for Finny
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                amount FLOAT,
                category TEXT,
                merchant TEXT,
                date TEXT,
                description TEXT,
                type TEXT DEFAULT 'expense',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Budgets table for Smart Budget Planner
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                category TEXT,
                monthly_limit FLOAT,
                current_spending FLOAT DEFAULT 0,
                month TEXT,
                year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category, month, year)
            )
            """)
            
            # Goal Jars table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS goal_jars (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                goal_name TEXT,
                target_amount FLOAT,
                current_amount FLOAT DEFAULT 0,
                monthly_saving FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Loan calculations table (for history)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_calculations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                loan_amount FLOAT,
                interest_rate FLOAT,
                tenure_months INTEGER,
                monthly_emi FLOAT,
                total_interest FLOAT,
                total_repayment FLOAT,
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

    # Finny - Transaction Management
    def add_transaction(self, user_id, amount, category, merchant, date, description="", type="expense"):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO transactions (user_id, amount, category, merchant, date, description, type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (user_id, amount, category, merchant, date, description, type))
            transaction_id = cursor.fetchone()[0]
            conn.commit()
            
            # Update budget spending
            self.update_budget_spending(user_id, category, amount)
            
            return transaction_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_transactions(self, user_id, month=None, year=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if month and year:
                cursor.execute("""
                SELECT * FROM transactions WHERE user_id=%s AND TO_CHAR(date::DATE, 'MM')=%s AND TO_CHAR(date::DATE, 'YYYY')=%s
                ORDER BY date DESC
                """, (user_id, f"{month:02d}", str(year)))
            else:
                cursor.execute("""
                SELECT * FROM transactions WHERE user_id=%s ORDER BY date DESC
                """, (user_id,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_monthly_summary(self, user_id, month, year):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM transactions 
            WHERE user_id=%s AND TO_CHAR(date::DATE, 'MM')=%s AND TO_CHAR(date::DATE, 'YYYY')=%s
            GROUP BY category
            ORDER BY total DESC
            """, (user_id, f"{month:02d}", str(year)))
            return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # Smart Budget Planner
    def create_budget(self, user_id, category, monthly_limit, month, year):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO budgets (user_id, category, monthly_limit, month, year)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, category, month, year) DO UPDATE SET
            monthly_limit = EXCLUDED.monthly_limit
            RETURNING id
            """, (user_id, category, monthly_limit, month, year))
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

    def get_budgets(self, user_id, month, year):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
            SELECT * FROM budgets WHERE user_id=%s AND month=%s AND year=%s
            """, (user_id, month, year))
            return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_budget_spending(self, user_id, category, amount):
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().year
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            UPDATE budgets 
            SET current_spending = current_spending + %s
            WHERE user_id=%s AND category=%s AND month=%s AND year=%s
            """, (amount, user_id, category, current_month, current_year))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # Goal Jar
    def create_goal_jar(self, user_id, goal_name, target_amount, monthly_saving):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO goal_jars (user_id, goal_name, target_amount, monthly_saving)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """, (user_id, goal_name, target_amount, monthly_saving))
            jar_id = cursor.fetchone()[0]
            conn.commit()
            return jar_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_goal_jars(self, user_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
            SELECT * FROM goal_jars WHERE user_id=%s ORDER BY created_at DESC
            """, (user_id,))
            return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_goal_jar(self, jar_id, amount_to_add):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            UPDATE goal_jars 
            SET current_amount = current_amount + %s
            WHERE id=%s
            """, (amount_to_add, jar_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    # Loan Analyzer
    def save_loan_calculation(self, user_id, loan_amount, interest_rate, tenure_months, monthly_emi, total_interest, total_repayment):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO loan_calculations 
            (user_id, loan_amount, interest_rate, tenure_months, monthly_emi, total_interest, total_repayment)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (user_id, loan_amount, interest_rate, tenure_months, monthly_emi, total_interest, total_repayment))
            calc_id = cursor.fetchone()[0]
            conn.commit()
            return calc_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_loan_history(self, user_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
            SELECT * FROM loan_calculations WHERE user_id=%s ORDER BY created_at DESC
            """, (user_id,))
            return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
