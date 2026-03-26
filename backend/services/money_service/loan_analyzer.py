import math
from datetime import datetime
from .money_db import MoneyServiceDB

class LoanAnalyzer:
    def __init__(self):
        self.db = MoneyServiceDB()

    def calculate_emi(self, principal, annual_rate, tenure_months):
        """
        Calculate EMI using the formula:
        EMI = [P x R x (1+R)^N] / [(1+R)^N-1]
        where P = Principal, R = Monthly interest rate, N = Tenure in months
        """
        monthly_rate = annual_rate / 12 / 100
        if monthly_rate == 0:
            return principal / tenure_months
        
        emi = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months) / (math.pow(1 + monthly_rate, tenure_months) - 1)
        return emi

    def analyze_loan(self, user_id):
        print("\n" + "="*50)
        print("  SMART LOAN ANALYZER - EMI CALCULATOR")
        print("="*50)
        
        try:
            loan_amount = float(input("Loan Amount ( ): ").strip())
            if loan_amount <= 0:
                print("  Loan amount must be positive")
                return False
                
            interest_rate = float(input("Annual Interest Rate (%): ").strip())
            if interest_rate < 0:
                print("  Interest rate cannot be negative")
                return False
                
            tenure_months = int(input("Tenure (months): ").strip())
            if tenure_months <= 0:
                print("  Tenure must be positive")
                return False
                
        except ValueError:
            print("  Invalid input")
            return False
        
        # Calculate EMI
        monthly_emi = self.calculate_emi(loan_amount, interest_rate, tenure_months)
        total_payment = monthly_emi * tenure_months
        total_interest = total_payment - loan_amount
        
        # Save calculation
        self.db.save_loan_calculation(
            user_id, loan_amount, interest_rate, tenure_months,
            monthly_emi, total_interest, total_payment
        )
        
        # Display results
        print("\n" + "="*50)
        print("  LOAN ANALYSIS RESULTS")
        print("="*50)
        print(f"  Loan Amount:  {loan_amount:,.2f}")
        print(f"  Interest Rate: {interest_rate}% per annum")
        print(f"  Tenure: {tenure_months} months ({tenure_months/12:.1f} years)")
        print("-" * 50)
        print(f"  Monthly EMI:  {monthly_emi:,.2f}")
        print(f"  Total Interest:  {total_interest:,.2f}")
        print(f"  Total Payment:  {total_payment:,.2f}")
        print("-" * 50)
        
        # Additional insights
        interest_percentage = (total_interest / loan_amount) * 100
        print(f"  Interest as % of Principal: {interest_percentage:.1f}%")
        
        # Monthly payment breakdown for first 6 months
        print(f"\n  Payment Schedule (First 6 months):")
        print("-" * 50)
        remaining_principal = loan_amount
        monthly_rate = interest_rate / 12 / 100
        
        for month in range(1, min(7, tenure_months + 1)):
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_emi - interest_payment
            remaining_principal -= principal_payment
            
            print(f"Month {month:2d}: Principal  {principal_payment:,.2f} | Interest  {interest_payment:,.2f} | Balance  {remaining_principal:,.2f}")
        
        return True

    def view_loan_history(self, user_id):
        print("\n" + "="*50)
        print("  LOAN ANALYSIS HISTORY")
        print("="*50)
        
        history = self.db.get_loan_history(user_id)
        
        if not history:
            print("  No previous loan calculations found")
            return
        
        print(f"\nPrevious Calculations: {len(history)}\n")
        
        for idx, calc in enumerate(history, 1):
            print(f"[{idx}] Loan Analysis from {calc[8]}")
            print(f"      Amount:  {calc[2]:,.2f}")
            print(f"      Rate: {calc[3]}% | Tenure: {calc[4]} months")
            print(f"      EMI:  {calc[5]:,.2f}")
            print(f"      Total Interest:  {calc[6]:,.2f}")
            print("-" * 40)

    def show_menu(self, user_id):
        while True:
            print("\n" + "="*50)
            print("  SMART LOAN ANALYZER")
            print("="*50)
            print("1.   Calculate EMI")
            print("2.   View History")
            print("3.    Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.analyze_loan(user_id)
            elif choice == "2":
                self.view_loan_history(user_id)
            elif choice == "3":
                return
            else:
                print("  Invalid choice")
            
            input("\nPress Enter to continue...")
