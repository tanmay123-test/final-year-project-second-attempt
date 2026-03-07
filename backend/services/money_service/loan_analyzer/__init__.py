"""
Smart Loan Analyzer Module

A comprehensive loan analysis system that helps users:
- Calculate EMI and loan metrics
- Analyze loan affordability and risk
- Compare multiple loan offers
- Simulate early repayment scenarios
- Generate detailed repayment schedules
"""

from .emi_calculator import EMICalculator
from .loan_risk import LoanRiskAnalyzer
from .repayment_simulator import RepaymentSimulator
from .loan_engine import LoanEngine
from .loan_api import LoanAPI, create_loan_api

__all__ = [
    'EMICalculator',
    'LoanRiskAnalyzer', 
    'RepaymentSimulator',
    'LoanEngine',
    'LoanAPI',
    'create_loan_api'
]

__version__ = '1.0.0'
__description__ = 'Smart Loan Analyzer - Comprehensive loan analysis and risk assessment system'
