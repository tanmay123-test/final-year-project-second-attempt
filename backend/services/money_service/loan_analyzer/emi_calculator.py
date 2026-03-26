import math

class EMICalculator:
    """Calculate EMI and loan-related metrics"""
    
    @staticmethod
    def calculate_emi(principal, annual_rate, tenure_months):
        """
        Calculate EMI using standard formula
        
        EMI = P   r   (1 + r)^n / ((1 + r)^n - 1)
        
        Where:
        P = Principal (loan amount)
        r = Monthly interest rate
        n = Number of months
        """
        if principal <= 0 or tenure_months <= 0:
            return 0, 0, 0
        
        # Convert annual rate to monthly rate
        monthly_rate = annual_rate / 12 / 100
        
        if monthly_rate == 0:
            # Simple interest case
            emi = principal / tenure_months
            total_interest = 0
        else:
            # Standard EMI formula
            emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months / ((1 + monthly_rate) ** tenure_months - 1)
            total_interest = (emi * tenure_months) - principal
        
        total_repayment = principal + total_interest
        
        return emi, total_interest, total_repayment
    
    @staticmethod
    def calculate_loan_details(loan_amount, interest_rate, loan_tenure):
        """
        Calculate complete loan details
        
        Args:
            loan_amount: Principal amount
            interest_rate: Annual interest rate (percentage)
            loan_tenure: Loan tenure in months
        
        Returns:
            dict: Complete loan analysis
        """
        emi, total_interest, total_repayment = EMICalculator.calculate_emi(
            loan_amount, interest_rate, loan_tenure
        )
        
        return {
            'loan_amount': loan_amount,
            'interest_rate': interest_rate,
            'loan_tenure': loan_tenure,
            'monthly_emi': emi,
            'total_interest': total_interest,
            'total_repayment': total_repayment,
            'interest_percentage': (total_interest / loan_amount * 100) if loan_amount > 0 else 0
        }
    
    @staticmethod
    def format_currency(amount):
        """Format amount as Indian currency"""
        return f" {amount:,.2f}"
    
    @staticmethod
    def display_loan_summary(loan_details):
        """Display formatted loan summary"""
        print("\n" + "="*60)
        print("  LOAN ANALYSIS SUMMARY")
        print("="*60)
        print(f"  Loan Amount: {EMICalculator.format_currency(loan_details['loan_amount'])}")
        print(f"  Interest Rate: {loan_details['interest_rate']:.2f}% per annum")
        print(f"  Loan Tenure: {loan_details['loan_tenure']} months ({loan_details['loan_tenure']/12:.1f} years)")
        print("-" * 60)
        print(f"  Monthly EMI: {EMICalculator.format_currency(loan_details['monthly_emi'])}")
        print(f"  Total Interest: {EMICalculator.format_currency(loan_details['total_interest'])}")
        print(f"  Total Repayment: {EMICalculator.format_currency(loan_details['total_repayment'])}")
        print(f"  Interest as % of Principal: {loan_details['interest_percentage']:.2f}%")
        print("="*60)
    
    @staticmethod
    def get_emi_breakdown(principal, annual_rate, tenure_months):
        """
        Get detailed monthly EMI breakdown (principal and interest components)
        
        Returns:
            list: Monthly breakdown with principal, interest, and balance
        """
        if principal <= 0 or tenure_months <= 0:
            return []
        
        monthly_rate = annual_rate / 12 / 100
        emi, _, _ = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)
        
        breakdown = []
        remaining_balance = principal
        
        for month in range(1, tenure_months + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = emi - interest_payment
            remaining_balance -= principal_payment
            
            breakdown.append({
                'month': month,
                'emi': emi,
                'principal': principal_payment,
                'interest': interest_payment,
                'balance': max(0, remaining_balance)
            })
        
        return breakdown
