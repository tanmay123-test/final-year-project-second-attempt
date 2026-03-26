from .emi_calculator import EMICalculator
from .loan_risk import LoanRiskAnalyzer
from .repayment_simulator import RepaymentSimulator
import sqlite3
from datetime import datetime

DB_PATH = 'expertease.db'

def _get_conn():
    """Open a fresh per-request SQLite connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


class LoanEngine:
    """Main loan analysis engine integrating all loan analysis components"""

    def __init__(self):
        self._override_financial_data = None  # set by API when income is passed in request
        self.create_loan_tables()

    def create_loan_tables(self):
        """Create loan analysis tables"""
        conn = _get_conn()
        try:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                loan_amount REAL,
                interest_rate REAL,
                loan_tenure INTEGER,
                monthly_emi REAL,
                total_interest REAL,
                total_repayment REAL,
                risk_score REAL,
                dti_ratio REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                loan1_amount REAL,
                loan1_rate REAL,
                loan1_tenure INTEGER,
                loan2_amount REAL,
                loan2_rate REAL,
                loan2_tenure INTEGER,
                recommended_loan TEXT,
                savings_amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_user_financial_data(self, user_id):
        """Get user's financial data — use request override if available"""
        if self._override_financial_data:
            return self._override_financial_data
        conn = _get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT monthly_income, fixed_expenses_total, disposable_income
            FROM uplan WHERE user_id=? ORDER BY created_at DESC LIMIT 1
            """, (user_id,))
            plan = cursor.fetchone()
            if plan:
                return {
                    'monthly_income': plan['monthly_income'],
                    'monthly_fixed_expenses': plan['fixed_expenses_total'],
                    'disposable_income': plan['disposable_income']
                }
            return {'monthly_income': 50000, 'monthly_fixed_expenses': 20000, 'disposable_income': 30000}
        except Exception as e:
            print(f"Error getting financial data: {e}")
            return {'monthly_income': 50000, 'monthly_fixed_expenses': 20000, 'disposable_income': 30000}
        finally:
            conn.close()

    def analyze_loan(self, user_id, loan_amount, interest_rate, loan_tenure):
        """Comprehensive loan analysis"""
        loan_details = EMICalculator.calculate_loan_details(loan_amount, interest_rate, loan_tenure)
        financial_data = self.get_user_financial_data(user_id)

        affordability = LoanRiskAnalyzer.check_affordability(
            financial_data['monthly_income'], loan_details['monthly_emi']
        )
        dti_analysis = LoanRiskAnalyzer.calculate_dti_ratio(
            financial_data['monthly_income'], loan_details['monthly_emi']
        )
        impact_analysis = LoanRiskAnalyzer.calculate_loan_impact(
            financial_data['monthly_income'],
            financial_data['monthly_fixed_expenses'],
            loan_details['monthly_emi']
        )
        risk_analysis = LoanRiskAnalyzer.calculate_risk_score(
            financial_data['monthly_income'],
            financial_data['monthly_fixed_expenses'],
            loan_details['monthly_emi']
        )

        self.save_loan_analysis(user_id, loan_details, risk_analysis['risk_score'], dti_analysis['dti_percentage'])

        return {
            'loan_details': loan_details,
            'financial_data': financial_data,
            'affordability': affordability,
            'dti_analysis': dti_analysis,
            'impact_analysis': impact_analysis,
            'risk_analysis': risk_analysis,
            'recommendation': self._get_overall_recommendation(affordability, dti_analysis, risk_analysis)
        }

    def compare_loans(self, user_id, loan1_params, loan2_params):
        """Compare two loan offers"""
        comparison = RepaymentSimulator.compare_loans(loan1_params, loan2_params)
        self.save_loan_comparison(user_id, loan1_params, loan2_params, comparison)
        return comparison

    def simulate_early_repayment(self, loan_amount, interest_rate, loan_tenure, extra_payment):
        """Simulate early repayment scenario"""
        return RepaymentSimulator.simulate_early_repayment(
            loan_amount, interest_rate, loan_tenure, extra_payment
        )

    def generate_repayment_schedule(self, loan_amount, interest_rate, loan_tenure, extra_payment=0):
        """Generate detailed repayment schedule"""
        return RepaymentSimulator.generate_repayment_schedule(
            loan_amount, interest_rate, loan_tenure, extra_payment
        )

    def save_loan_analysis(self, user_id, loan_details, risk_score, dti_ratio):
        """Save loan analysis to database"""
        conn = _get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO loan_analysis
            (user_id, loan_amount, interest_rate, loan_tenure, monthly_emi,
             total_interest, total_repayment, risk_score, dti_ratio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, loan_details['loan_amount'], loan_details['interest_rate'],
                loan_details['loan_tenure'], loan_details['monthly_emi'],
                loan_details['total_interest'], loan_details['total_repayment'],
                risk_score, dti_ratio
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def save_loan_comparison(self, user_id, loan1_params, loan2_params, comparison):
        """Save loan comparison to database"""
        conn = _get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO loan_comparisons
            (user_id, loan1_amount, loan1_rate, loan1_tenure,
             loan2_amount, loan2_rate, loan2_tenure, recommended_loan, savings_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, loan1_params['amount'], loan1_params['rate'], loan1_params['tenure'],
                loan2_params['amount'], loan2_params['rate'], loan2_params['tenure'],
                comparison['cheaper_option'], comparison['savings']
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_loan_history(self, user_id, limit=10):
        """Get user's loan analysis history"""
        conn = _get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM loan_analysis
            WHERE user_id=?
            ORDER BY created_at DESC
            LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise e
        finally:
            conn.close()

    def get_comparison_history(self, user_id, limit=10):
        """Get user's loan comparison history"""
        conn = _get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM loan_comparisons
            WHERE user_id=?
            ORDER BY created_at DESC
            LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise e
        finally:
            conn.close()

    def _get_overall_recommendation(self, affordability, dti_analysis, risk_analysis):
        """Get overall loan recommendation"""
        if not affordability['is_affordable']:
            return "❌ NOT RECOMMENDED: Loan EMI exceeds 30% of monthly income"
        if risk_analysis['risk_score'] > 70:
            return "⚠️ HIGH RISK: Consider reducing loan amount or improving financial position"
        if dti_analysis['dti_percentage'] > 35:
            return "⚠️ MODERATE RISK: Monitor debt levels carefully"
        if risk_analysis['risk_score'] < 30:
            return "✅ RECOMMENDED: Low risk loan within affordable limits"
        return "🤔 CONDITIONAL: Proceed with caution and monitor finances"

    def display_comprehensive_analysis(self, analysis):
        """Display complete loan analysis"""
        print("\n" + "="*80)
        print("🏦 COMPREHENSIVE LOAN ANALYSIS")
        print("="*80)
        EMICalculator.display_loan_summary(analysis['loan_details'])
        LoanRiskAnalyzer.display_affordability_analysis(analysis['affordability'])
        LoanRiskAnalyzer.display_dti_analysis(analysis['dti_analysis'])
        LoanRiskAnalyzer.display_impact_analysis(analysis['impact_analysis'])
        LoanRiskAnalyzer.display_risk_analysis(analysis['risk_analysis'])
        print(f"\n🎯 OVERALL RECOMMENDATION:")
        print("-" * 40)
        print(analysis['recommendation'])
        print("="*80)

    def get_quick_analysis(self, user_id, loan_amount, interest_rate, loan_tenure):
        """Get quick loan analysis without detailed display"""
        analysis = self.analyze_loan(user_id, loan_amount, interest_rate, loan_tenure)
        return {
            'emi': analysis['loan_details']['monthly_emi'],
            'total_interest': analysis['loan_details']['total_interest'],
            'total_repayment': analysis['loan_details']['total_repayment'],
            'affordable': analysis['affordability']['is_affordable'],
            'risk_score': analysis['risk_analysis']['risk_score'],
            'risk_level': analysis['risk_analysis']['risk_level'],
            'recommendation': analysis['recommendation']
        }
