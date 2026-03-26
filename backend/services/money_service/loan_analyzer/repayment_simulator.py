import math
from .emi_calculator import EMICalculator

class RepaymentSimulator:
    """Simulate loan repayment scenarios and early repayment options"""
    
    @staticmethod
    def compare_loans(loan1_details, loan2_details):
        """
        Compare two loan offers
        
        Args:
            loan1_details: dict with loan1 parameters
            loan2_details: dict with loan2 parameters
        
        Returns:
            dict: Comparison analysis
        """
        # Calculate details for both loans
        loan1_analysis = EMICalculator.calculate_loan_details(
            loan1_details['amount'], loan1_details['rate'], loan1_details['tenure']
        )
        loan2_analysis = EMICalculator.calculate_loan_details(
            loan2_details['amount'], loan2_details['rate'], loan2_details['tenure']
        )
        
        # Determine cheaper option
        if loan1_analysis['total_repayment'] < loan2_analysis['total_repayment']:
            cheaper = 'Loan 1'
            savings = loan2_analysis['total_repayment'] - loan1_analysis['total_repayment']
        else:
            cheaper = 'Loan 2'
            savings = loan1_analysis['total_repayment'] - loan2_analysis['total_repayment']
        
        return {
            'loan1': loan1_analysis,
            'loan2': loan2_analysis,
            'cheaper_option': cheaper,
            'savings': savings,
            'recommendation': f"Choose {cheaper} to save {EMICalculator.format_currency(savings)}"
        }
    
    @staticmethod
    def simulate_early_repayment(principal, annual_rate, tenure_months, extra_payment):
        """
        Simulate early repayment with extra monthly payment
        
        Args:
            principal: Original loan amount
            annual_rate: Annual interest rate
            tenure_months: Original tenure
            extra_payment: Additional monthly payment
        
        Returns:
            dict: Early repayment analysis
        """
        if extra_payment <= 0:
            return {
                'months_saved': 0,
                'interest_saved': 0,
                'new_tenure': tenure_months,
                'original_interest': 0,
                'new_interest': 0,
                'total_savings': 0
            }
        
        # Original loan details
        original_emi, original_interest, original_repayment = EMICalculator.calculate_emi(
            principal, annual_rate, tenure_months
        )
        
        # Calculate with extra payment
        monthly_rate = annual_rate / 12 / 100
        new_emi = original_emi + extra_payment
        
        # Calculate new tenure using extra payment
        if monthly_rate == 0:
            new_tenure_months = principal / new_emi
        else:
            # Formula for tenure with extra payment
            new_tenure_months = -math.log(1 - (principal * monthly_rate) / new_emi) / math.log(1 + monthly_rate)
        
        new_tenure_months = max(1, new_tenure_months)
        
        # Calculate new total interest
        new_total_repayment = new_emi * new_tenure_months
        new_interest = new_total_repayment - principal
        
        # Calculate savings
        months_saved = tenure_months - new_tenure_months
        interest_saved = original_interest - new_interest
        total_savings = interest_saved
        
        return {
            'months_saved': months_saved,
            'interest_saved': interest_saved,
            'new_tenure': new_tenure_months,
            'original_interest': original_interest,
            'new_interest': new_interest,
            'total_savings': total_savings,
            'original_emi': original_emi,
            'new_emi': new_emi,
            'extra_payment': extra_payment
        }
    
    @staticmethod
    def generate_repayment_schedule(principal, annual_rate, tenure_months, extra_payment=0):
        """
        Generate detailed repayment schedule
        
        Args:
            principal: Loan amount
            annual_rate: Annual interest rate
            tenure_months: Loan tenure
            extra_payment: Extra monthly payment (optional)
        
        Returns:
            list: Monthly payment schedule
        """
        if principal <= 0 or tenure_months <= 0:
            return []
        
        monthly_rate = annual_rate / 12 / 100
        emi, _, _ = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)
        monthly_payment = emi + extra_payment
        
        schedule = []
        remaining_balance = principal
        month = 1
        
        while remaining_balance > 0 and month <= tenure_months * 2:  # Safety limit
            interest_payment = remaining_balance * monthly_rate
            principal_payment = min(monthly_payment - interest_payment, remaining_balance)
            remaining_balance -= principal_payment
            
            schedule.append({
                'month': month,
                'payment': monthly_payment,
                'principal': principal_payment,
                'interest': interest_payment,
                'balance': max(0, remaining_balance),
                'cumulative_interest': sum(p['interest'] for p in schedule) + interest_payment
            })
            
            month += 1
        
        return schedule
    
    @staticmethod
    def calculate_optimal_extra_payment(principal, annual_rate, tenure_months, target_months):
        """
        Calculate optimal extra payment to achieve target tenure
        
        Args:
            principal: Loan amount
            annual_rate: Annual interest rate
            tenure_months: Original tenure
            target_months: Desired tenure in months
        
        Returns:
            float: Required extra monthly payment
        """
        if target_months >= tenure_months:
            return 0
        
        original_emi, _, _ = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)
        monthly_rate = annual_rate / 12 / 100
        
        if monthly_rate == 0:
            required_emi = principal / target_months
        else:
            required_emi = principal * monthly_rate * (1 + monthly_rate) ** target_months / ((1 + monthly_rate) ** target_months - 1)
        
        extra_payment = required_emi - original_emi
        return max(0, extra_payment)
    
    @staticmethod
    def display_loan_comparison(comparison):
        """Display loan comparison results"""
        print("\n" + "="*80)
        print("  LOAN COMPARISON ANALYSIS")
        print("="*80)
        
        print(f"\n{'LOAN 1':^40} {'LOAN 2':^40}")
        print("-" * 80)
        
        loan1 = comparison['loan1']
        loan2 = comparison['loan2']
        
        loan1_rate_str = f"{loan1['interest_rate']:.2f}%"
        loan2_rate_str = f"{loan2['interest_rate']:.2f}%"
        loan1_tenure_str = f"{loan1['loan_tenure']} months"
        loan2_tenure_str = f"{loan2['loan_tenure']} months"
        
        print(f"{'Amount: ' + EMICalculator.format_currency(loan1['loan_amount']):^40} {'Amount: ' + EMICalculator.format_currency(loan2['loan_amount']):^40}")
        print(f"{'Rate: ' + loan1_rate_str:^40} {'Rate: ' + loan2_rate_str:^40}")
        print(f"{'Tenure: ' + loan1_tenure_str:^40} {'Tenure: ' + loan2_tenure_str:^40}")
        print(f"{'EMI: ' + EMICalculator.format_currency(loan1['monthly_emi']):^40} {'EMI: ' + EMICalculator.format_currency(loan2['monthly_emi']):^40}")
        print(f"{'Interest: ' + EMICalculator.format_currency(loan1['total_interest']):^40} {'Interest: ' + EMICalculator.format_currency(loan2['total_interest']):^40}")
        print(f"{'Total: ' + EMICalculator.format_currency(loan1['total_repayment']):^40} {'Total: ' + EMICalculator.format_currency(loan2['total_repayment']):^40}")
        
        print("\n" + "="*80)
        print(f"  RECOMMENDATION: {comparison['recommendation']}")
        print(f"  Total Savings: {EMICalculator.format_currency(comparison['savings'])}")
        print("="*80)
    
    @staticmethod
    def display_early_repayment_analysis(analysis):
        """Display early repayment analysis"""
        print("\n" + "="*70)
        print("  EARLY REPAYMENT SIMULATION")
        print("="*70)
        print(f"  Original EMI: {EMICalculator.format_currency(analysis['original_emi'])}")
        print(f"  Extra Payment: {EMICalculator.format_currency(analysis['extra_payment'])}")
        print(f"  New EMI: {EMICalculator.format_currency(analysis['new_emi'])}")
        print("-" * 70)
        print(f"  Original Tenure: {analysis['new_tenure'] + analysis['months_saved']:.1f} months")
        print(f"  New Tenure: {analysis['new_tenure']:.1f} months")
        print(f"  Months Saved: {analysis['months_saved']:.1f}")
        print("-" * 70)
        print(f"  Original Interest: {EMICalculator.format_currency(analysis['original_interest'])}")
        print(f"  New Interest: {EMICalculator.format_currency(analysis['new_interest'])}")
        print(f"  Interest Saved: {EMICalculator.format_currency(analysis['interest_saved'])}")
        print(f"  Total Savings: {EMICalculator.format_currency(analysis['total_savings'])}")
        print("="*70)
    
    @staticmethod
    def display_repayment_schedule(schedule, show_all=False):
        """Display repayment schedule"""
        if not schedule:
            print("  No schedule available")
            return
        
        print("\n" + "="*80)
        print("  REPAYMENT SCHEDULE")
        print("="*80)
        print(f"{'Month':<8} {'Payment':<12} {'Principal':<12} {'Interest':<12} {'Balance':<12} {'Cumulative Interest':<18}")
        print("-" * 80)
        
        months_to_show = len(schedule) if show_all else min(12, len(schedule))
        
        for i in range(months_to_show):
            payment = schedule[i]
            print(f"{payment['month']:<8} {EMICalculator.format_currency(payment['payment']):<12} "
                  f"{EMICalculator.format_currency(payment['principal']):<12} "
                  f"{EMICalculator.format_currency(payment['interest']):<12} "
                  f"{EMICalculator.format_currency(payment['balance']):<12} "
                  f"{EMICalculator.format_currency(payment['cumulative_interest']):<18}")
        
        if len(schedule) > months_to_show:
            print(f"... and {len(schedule) - months_to_show} more months")
        
        print("="*80)
