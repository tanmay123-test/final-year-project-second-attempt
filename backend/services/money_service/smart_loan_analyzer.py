from .loan_analyzer import LoanEngine, EMICalculator, LoanRiskAnalyzer, RepaymentSimulator

class SmartLoanAnalyzer:
    """Main interface for Smart Loan Analyzer"""
    
    def __init__(self):
        self.loan_engine = LoanEngine()
    
    def show_menu(self, user_id):
        """Main menu for Smart Loan Analyzer"""
        while True:
            print("\n" + "="*70)
            print("  SMART LOAN ANALYZER")
            print("="*70)
            print("1.   Analyze Single Loan")
            print("2.   Compare Two Loans")
            print("3.   Loan Impact Simulation")
            print("4.   Early Repayment Simulation")
            print("5.   Generate Repayment Schedule")
            print("6.   Loan Risk Assessment")
            print("7.   Loan Analysis History")
            print("8.    Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._analyze_single_loan(user_id)
            elif choice == "2":
                self._compare_loans(user_id)
            elif choice == "3":
                self._loan_impact_simulation(user_id)
            elif choice == "4":
                self._early_repayment_simulation()
            elif choice == "5":
                self._generate_repayment_schedule()
            elif choice == "6":
                self._loan_risk_assessment(user_id)
            elif choice == "7":
                self._show_loan_history(user_id)
            elif choice == "8":
                return
            else:
                print("  Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def _analyze_single_loan(self, user_id):
        """Analyze a single loan"""
        print("\n" + "="*60)
        print("  SINGLE LOAN ANALYSIS")
        print("="*60)
        
        try:
            # Get loan parameters
            loan_amount = float(input("  Enter loan amount:  "))
            interest_rate = float(input("  Enter annual interest rate (%): "))
            loan_tenure = int(input("  Enter loan tenure (months): "))
            
            if loan_amount <= 0 or interest_rate < 0 or loan_tenure <= 0:
                print("  Invalid input values")
                return
            
            # Perform comprehensive analysis
            analysis = self.loan_engine.analyze_loan(user_id, loan_amount, interest_rate, loan_tenure)
            
            # Display results
            self.loan_engine.display_comprehensive_analysis(analysis)
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _compare_loans(self, user_id):
        """Compare two loan offers"""
        print("\n" + "="*60)
        print("  LOAN COMPARISON")
        print("="*60)
        
        try:
            print("\n  LOAN 1 DETAILS:")
            loan1_amount = float(input("  Loan 1 amount:  "))
            loan1_rate = float(input("  Loan 1 interest rate (%): "))
            loan1_tenure = int(input("  Loan 1 tenure (months): "))
            
            print("\n  LOAN 2 DETAILS:")
            loan2_amount = float(input("  Loan 2 amount:  "))
            loan2_rate = float(input("  Loan 2 interest rate (%): "))
            loan2_tenure = int(input("  Loan 2 tenure (months): "))
            
            if any(val <= 0 for val in [loan1_amount, loan2_amount]) or any(val < 0 for val in [loan1_rate, loan2_rate]) or any(val <= 0 for val in [loan1_tenure, loan2_tenure]):
                print("  Invalid input values")
                return
            
            # Compare loans
            loan1_params = {'amount': loan1_amount, 'rate': loan1_rate, 'tenure': loan1_tenure}
            loan2_params = {'amount': loan2_amount, 'rate': loan2_rate, 'tenure': loan2_tenure}
            
            comparison = self.loan_engine.compare_loans(user_id, loan1_params, loan2_params)
            
            # Display comparison
            RepaymentSimulator.display_loan_comparison(comparison)
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _loan_impact_simulation(self, user_id):
        """Simulate loan impact on finances"""
        print("\n" + "="*60)
        print("  LOAN IMPACT SIMULATION")
        print("="*60)
        
        try:
            # Get user financial data
            financial_data = self.loan_engine.get_user_financial_data(user_id)
            
            print(f"\n  Current Financial Data:")
            print(f"   Monthly Income: {EMICalculator.format_currency(financial_data['monthly_income'])}")
            print(f"   Fixed Expenses: {EMICalculator.format_currency(financial_data['monthly_fixed_expenses'])}")
            print(f"   Disposable Income: {EMICalculator.format_currency(financial_data['disposable_income'])}")
            
            # Ask if user wants to update financial data
            update_data = input("\n  Update financial data? (yes/no): ").strip().lower()
            
            if update_data in ['yes', 'y']:
                monthly_income = float(input("  Enter monthly income:  "))
                monthly_fixed_expenses = float(input("  Enter monthly fixed expenses:  "))
            else:
                monthly_income = financial_data['monthly_income']
                monthly_fixed_expenses = financial_data['monthly_fixed_expenses']
            
            # Get loan parameters
            loan_amount = float(input("\n  Enter loan amount:  "))
            interest_rate = float(input("  Enter annual interest rate (%): "))
            loan_tenure = int(input("  Enter loan tenure (months): "))
            
            # Calculate EMI
            emi, _, _ = EMICalculator.calculate_emi(loan_amount, interest_rate, loan_tenure)
            
            # Calculate impact
            impact = LoanRiskAnalyzer.calculate_loan_impact(monthly_income, monthly_fixed_expenses, emi)
            
            # Display impact analysis
            LoanRiskAnalyzer.display_impact_analysis(impact)
            
            # Additional insights
            print(f"\n  IMPACT INSIGHTS:")
            if impact['is_sustainable']:
                print("  Loan is sustainable within your financial capacity")
                if impact['remaining_after_emi'] > impact['disposable_income'] * 0.5:
                    print("  You'll have comfortable buffer after EMI payments")
                else:
                    print("   Tight budget after EMI - consider reducing loan amount")
            else:
                print("  Loan exceeds your financial capacity")
                print("  Consider reducing loan amount or increasing tenure")
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _early_repayment_simulation(self):
        """Simulate early repayment scenarios"""
        print("\n" + "="*60)
        print("  EARLY REPAYMENT SIMULATION")
        print("="*60)
        
        try:
            # Get loan parameters
            loan_amount = float(input("  Enter loan amount:  "))
            interest_rate = float(input("  Enter annual interest rate (%): "))
            loan_tenure = int(input("  Enter original loan tenure (months): "))
            extra_payment = float(input("  Enter extra monthly payment:  "))
            
            if loan_amount <= 0 or interest_rate < 0 or loan_tenure <= 0 or extra_payment < 0:
                print("  Invalid input values")
                return
            
            # Simulate early repayment
            simulation = self.loan_engine.simulate_early_repayment(
                loan_amount, interest_rate, loan_tenure, extra_payment
            )
            
            # Display results
            RepaymentSimulator.display_early_repayment_analysis(simulation)
            
            # Additional insights
            if simulation['months_saved'] > 0:
                print(f"\n  BENEFITS:")
                print(f"  You'll save {simulation['months_saved']:.1f} months!")
                print(f"  Total interest savings: {EMICalculator.format_currency(simulation['interest_saved'])}")
                
                # Calculate effective interest rate
                effective_rate = (simulation['new_interest'] / loan_amount * 100 / (simulation['new_tenure']/12))
                original_rate = (simulation['original_interest'] / loan_amount * 100 / (loan_tenure/12))
                print(f"  Effective interest rate reduced from {original_rate:.2f}% to {effective_rate:.2f}%")
            else:
                print(f"\n  Consider increasing extra payment for better savings")
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _generate_repayment_schedule(self):
        """Generate detailed repayment schedule"""
        print("\n" + "="*60)
        print("  REPAYMENT SCHEDULE GENERATOR")
        print("="*60)
        
        try:
            # Get loan parameters
            loan_amount = float(input("  Enter loan amount:  "))
            interest_rate = float(input("  Enter annual interest rate (%): "))
            loan_tenure = int(input("  Enter loan tenure (months): "))
            
            extra_payment_input = input("  Enter extra monthly payment (0 for none):  ").strip()
            extra_payment = float(extra_payment_input) if extra_payment_input else 0
            
            if loan_amount <= 0 or interest_rate < 0 or loan_tenure <= 0 or extra_payment < 0:
                print("  Invalid input values")
                return
            
            # Generate schedule
            schedule = self.loan_engine.generate_repayment_schedule(
                loan_amount, interest_rate, loan_tenure, extra_payment
            )
            
            # Display schedule
            show_all = input("\n  Show complete schedule? (yes/no): ").strip().lower() in ['yes', 'y']
            RepaymentSimulator.display_repayment_schedule(schedule, show_all)
            
            # Summary statistics
            if schedule:
                total_payment = sum(p['payment'] for p in schedule)
                total_interest = sum(p['interest'] for p in schedule)
                
                print(f"\n  SCHEDULE SUMMARY:")
                print(f"  Total Payments: {EMICalculator.format_currency(total_payment)}")
                print(f"  Total Interest: {EMICalculator.format_currency(total_interest)}")
                print(f"  Actual Tenure: {len(schedule)} months")
                
                if extra_payment > 0:
                    original_emi, _, _ = EMICalculator.calculate_emi(loan_amount, interest_rate, loan_tenure)
                    months_saved = loan_tenure - len(schedule)
                    interest_saved = (original_emi * loan_tenure - loan_amount) - total_interest
                    
                    print(f"\n  EARLY REPAYMENT BENEFITS:")
                    print(f"  Months Saved: {months_saved}")
                    print(f"  Interest Saved: {EMICalculator.format_currency(interest_saved)}")
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _loan_risk_assessment(self, user_id):
        """Comprehensive loan risk assessment"""
        print("\n" + "="*60)
        print("  LOAN RISK ASSESSMENT")
        print("="*60)
        
        try:
            # Get user financial data
            financial_data = self.loan_engine.get_user_financial_data(user_id)
            
            print(f"\n  Current Financial Data:")
            print(f"   Monthly Income: {EMICalculator.format_currency(financial_data['monthly_income'])}")
            print(f"   Fixed Expenses: {EMICalculator.format_currency(financial_data['monthly_fixed_expenses'])}")
            print(f"   Disposable Income: {EMICalculator.format_currency(financial_data['disposable_income'])}")
            
            # Get loan parameters
            loan_amount = float(input("\n  Enter loan amount:  "))
            interest_rate = float(input("  Enter annual interest rate (%): "))
            loan_tenure = int(input("  Enter loan tenure (months): "))
            
            # Get existing EMIs
            existing_emi_input = input("  Enter existing monthly EMIs (0 for none):  ").strip()
            existing_emi = float(existing_emi_input) if existing_emi_input else 0
            
            # Calculate EMI
            emi, _, _ = EMICalculator.calculate_emi(loan_amount, interest_rate, loan_tenure)
            
            # Perform risk analysis
            risk_analysis = LoanRiskAnalyzer.calculate_risk_score(
                financial_data['monthly_income'],
                financial_data['monthly_fixed_expenses'],
                emi,
                existing_emi
            )
            
            # Display risk analysis
            LoanRiskAnalyzer.display_risk_analysis(risk_analysis)
            
            # Additional risk factors
            print(f"\n  DETAILED RISK FACTORS:")
            
            # DTI Analysis
            total_emi = emi + existing_emi
            dti = LoanRiskAnalyzer.calculate_dti_ratio(financial_data['monthly_income'], total_emi)
            LoanRiskAnalyzer.display_dti_analysis(dti)
            
            # Affordability Analysis
            affordability = LoanRiskAnalyzer.check_affordability(financial_data['monthly_income'], total_emi)
            LoanRiskAnalyzer.display_affordability_analysis(affordability)
            
            # Recommendations based on risk level
            print(f"\n  RISK-BASED RECOMMENDATIONS:")
            if risk_analysis['risk_score'] < 30:
                print("  LOW RISK - Loan is highly recommended")
                print("  You have good financial capacity for this loan")
            elif risk_analysis['risk_score'] < 60:
                print("   MODERATE RISK - Proceed with caution")
                print("  Consider reducing loan amount or increasing tenure")
                print("  Build emergency fund before taking loan")
            else:
                print("  HIGH RISK - Loan not recommended")
                print("  Improve financial position before applying")
                print("  Consider smaller loan amount or longer tenure")
                print("  Reduce existing debts first")
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _show_loan_history(self, user_id):
        """Show user's loan analysis history"""
        print("\n" + "="*60)
        print("  LOAN ANALYSIS HISTORY")
        print("="*60)
        
        try:
            # Get history
            loan_history = self.loan_engine.get_loan_history(user_id)
            comparison_history = self.loan_engine.get_comparison_history(user_id)
            
            if not loan_history and not comparison_history:
                print("  No loan analysis history found")
                return
            
            # Display loan analysis history
            if loan_history:
                print(f"\n  LOAN ANALYSIS HISTORY:")
                print("-" * 60)
                for i, analysis in enumerate(loan_history, 1):
                    created_at = analysis['created_at']
                    print(f"\n{i}.   {created_at}")
                    print(f"     Amount: {EMICalculator.format_currency(analysis['loan_amount'])}")
                    print(f"     Rate: {analysis['interest_rate']:.2f}%")
                    print(f"     Tenure: {analysis['loan_tenure']} months")
                    print(f"     EMI: {EMICalculator.format_currency(analysis['monthly_emi'])}")
                    print(f"     Risk Score: {analysis['risk_score']:.1f}/100")
                    print(f"     DTI: {analysis['dti_ratio']:.1f}%")
            
            # Display comparison history
            if comparison_history:
                print(f"\n  LOAN COMPARISON HISTORY:")
                print("-" * 60)
                for i, comparison in enumerate(comparison_history, 1):
                    created_at = comparison['created_at']
                    print(f"\n{i}.   {created_at}")
                    print(f"     Loan 1: {EMICalculator.format_currency(comparison['loan1_amount'])} at {comparison['loan1_rate']:.2f}%")
                    print(f"     Loan 2: {EMICalculator.format_currency(comparison['loan2_amount'])} at {comparison['loan2_rate']:.2f}%")
                    print(f"     Recommended: {comparison['recommended_loan']}")
                    print(f"     Savings: {EMICalculator.format_currency(comparison['savings_amount'])}")
            
        except Exception as e:
            print(f"  Error: {e}")
