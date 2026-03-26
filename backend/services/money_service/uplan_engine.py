from datetime import datetime
from .uplan_database import UPlanDatabase

class UPlanEngine:
    def __init__(self):
        self.db = UPlanDatabase()
    
    def create_financial_plan(self, user_id):
        """Create U-Plan financial plan with user input"""
        print("\n" + "="*70)
        print("  U-PLAN FINANCIAL PLANNING SYSTEM")
        print("="*70)
        print("  Let's create your personalized financial plan!")
        
        # Step 1: Collect Monthly Income
        print("\n  STEP 1 - MONTHLY INCOME")
        print("-" * 40)
        try:
            monthly_income = float(input("  Enter your monthly income:  ").strip())
            if monthly_income <= 0:
                print("  Income must be greater than 0")
                return None
        except ValueError:
            print("  Invalid income amount")
            return None
        
        # Step 2: Collect Fixed Expenses
        print("\n  STEP 2 - FIXED EXPENSES")
        print("-" * 40)
        print("  Enter your fixed monthly expenses (rent, loans, utilities, etc.)")
        
        fixed_expenses = []
        expense_types = [
            "Rent/Mortgage", "Education Loan", "Personal Loan", 
            "Utilities", "Internet", "Transport", "Insurance"
        ]
        
        for expense_type in expense_types:
            try:
                amount = float(input(f"  {expense_type}:  ").strip() or "0")
                if amount > 0:
                    fixed_expenses.append({
                        'name': expense_type,
                        'amount': amount
                    })
            except ValueError:
                print(f"   Skipping {expense_type}")
        
        # Allow custom expenses
        while True:
            custom = input("\n  Add custom expense? (name amount or 'no'): ").strip()
            if custom.lower() in ['no', 'n', '']:
                break
            
            parts = custom.split()
            if len(parts) >= 2:
                try:
                    name = ' '.join(parts[:-1])
                    amount = float(parts[-1])
                    if amount > 0:
                        fixed_expenses.append({'name': name, 'amount': amount})
                        print(f"  Added: {name} -  {amount}")
                except ValueError:
                    print("  Invalid amount")
            else:
                print("  Format: name amount")
        
        # Create plan
        plan = self.db.create_financial_plan(user_id, monthly_income, fixed_expenses)
        
        # Step 3: Calculate and Display Results
        self._display_plan_summary(plan)
        
        # Step 4: Smart Allocation
        print("\n  STEP 3 - SMART ALLOCATION")
        print("-" * 40)
        allocation = self._calculate_smart_allocation(plan['disposable_income'])
        self._display_allocation(allocation)
        
        # Step 5: Generate Category Budgets
        print("\n  STEP 4 - CATEGORY BUDGETS")
        print("-" * 40)
        category_budgets = self._generate_category_budgets(allocation)
        self._display_category_budgets(category_budgets)
        
        # Save budgets
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        self.db.create_category_budgets(user_id, category_budgets, month, year)
        
        # Step 6: Savings Projection
        print("\n  STEP 5 - SAVINGS PROJECTION")
        print("-" * 40)
        self._display_savings_projection(allocation['savings'])
        
        print(f"\n  Financial plan created successfully for {month} {year}!")
        return plan, allocation, category_budgets
    
    def _display_plan_summary(self, plan):
        """Display financial plan summary"""
        print(f"\n  FINANCIAL PLAN SUMMARY")
        print("-" * 40)
        print(f"  Monthly Income:  {plan['monthly_income']:,.2f}")
        print(f"  Fixed Expenses:  {plan['fixed_expenses_total']:,.2f}")
        print(f"  Disposable Income:  {plan['disposable_income']:,.2f}")
        print(f"  Savings Target:  {plan['savings_target']:,.2f}")
        
        # Visual breakdown
        income_percentage = (plan['fixed_expenses_total'] / plan['monthly_income']) * 100
        disposable_percentage = (plan['disposable_income'] / plan['monthly_income']) * 100
        
        print(f"\n  INCOME BREAKDOWN:")
        print(f"   Fixed Expenses: {income_percentage:.1f}%")
        print(f"   Disposable: {disposable_percentage:.1f}%")
    
    def _calculate_smart_allocation(self, disposable_income):
        """Calculate smart allocation using 20/50/30 rule"""
        return {
            'savings': disposable_income * 0.20,
            'needs': disposable_income * 0.50,
            'wants': disposable_income * 0.30
        }
    
    def _display_allocation(self, allocation):
        """Display smart allocation"""
        print(f"\n  SMART ALLOCATION (20/50/30 RULE)")
        print("-" * 40)
        print(f"  Savings (20%):  {allocation['savings']:,.2f}")
        print(f"  Needs (50%):  {allocation['needs']:,.2f}")
        print(f"  Wants (30%):  {allocation['wants']:,.2f}")
        
        # Visual allocation
        total = sum(allocation.values())
        for category, amount in allocation.items():
            percentage = (amount / total) * 100
            bar = " " * int(percentage / 10)
            print(f"   {category.title()}: {bar} {percentage:.0f}%")
    
    def _generate_category_budgets(self, allocation):
        """Generate specific category budgets"""
        category_budgets = []
        
        # Needs categories
        needs_categories = [
            {'category': 'Groceries', 'amount': allocation['needs'] * 0.4, 'type': 'needs'},
            {'category': 'Transport', 'amount': allocation['needs'] * 0.3, 'type': 'needs'},
            {'category': 'Utilities', 'amount': allocation['needs'] * 0.3, 'type': 'needs'}
        ]
        
        # Wants categories
        wants_categories = [
            {'category': 'Shopping', 'amount': allocation['wants'] * 0.5, 'type': 'wants'},
            {'category': 'Entertainment', 'amount': allocation['wants'] * 0.3, 'type': 'wants'},
            {'category': 'Dining Out', 'amount': allocation['wants'] * 0.2, 'type': 'wants'}
        ]
        
        category_budgets.extend(needs_categories)
        category_budgets.extend(wants_categories)
        
        return category_budgets
    
    def _display_category_budgets(self, category_budgets):
        """Display category budgets"""
        print(f"\n  CATEGORY BUDGET BREAKDOWN")
        print("-" * 40)
        
        for budget in category_budgets:
            print(f"  {budget['category']}:  {budget['amount']:,.2f} ({budget['type'].title()})")
    
    def _display_savings_projection(self, monthly_savings):
        """Display savings projection"""
        projections = [
            (6, monthly_savings * 6),
            (12, monthly_savings * 12),
            (24, monthly_savings * 24)
        ]
        
        print(f"  MONTHLY SAVINGS:  {monthly_savings:,.2f}")
        print(f"\n  SAVINGS PROJECTIONS:")
        for months, amount in projections:
            print(f"   {months} months:  {amount:,.2f}")
        
        # Long-term impact
        yearly_savings = monthly_savings * 12
        print(f"\n  ANNUAL IMPACT:")
        print(f"   Yearly Savings:  {yearly_savings:,.2f}")
        print(f"   5-Year Projection:  {yearly_savings * 5:,.2f}")
    
    def get_financial_plan_summary(self, user_id):
        """Get financial plan summary"""
        plan = self.db.get_financial_plan(user_id)
        if not plan:
            return None
        
        allocation = self._calculate_smart_allocation(plan['disposable_income'])
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        category_budgets = self.db.get_category_budgets(user_id, month, year)
        
        return {
            'plan': plan,
            'allocation': allocation,
            'category_budgets': category_budgets
        }
