from .emi_calculator import EMICalculator

class LoanRiskAnalyzer:
    """Analyze loan risk and affordability"""
    
    @staticmethod
    def check_affordability(monthly_income, monthly_emi):
        """
        Check if EMI exceeds 30% of monthly income
        
        Args:
            monthly_income: User's monthly income
            monthly_emi: Calculated EMI
        
        Returns:
            dict: Affordability analysis
        """
        emi_percentage = (monthly_emi / monthly_income * 100) if monthly_income > 0 else 100
        safe_limit = 30
        is_affordable = emi_percentage <= safe_limit
        
        return {
            'monthly_income': monthly_income,
            'monthly_emi': monthly_emi,
            'emi_percentage': emi_percentage,
            'safe_limit': safe_limit,
            'is_affordable': is_affordable,
            'warning': None if is_affordable else 
                      f"Loan EMI exceeds safe limit. Consider reducing loan amount or increasing tenure."
        }
    
    @staticmethod
    def calculate_dti_ratio(monthly_income, monthly_emi):
        """
        Calculate Debt-to-Income (DTI) ratio
        
        Args:
            monthly_income: User's monthly income
            monthly_emi: Monthly EMI
        
        Returns:
            dict: DTI analysis with risk classification
        """
        dti = (monthly_emi / monthly_income * 100) if monthly_income > 0 else 100
        
        if dti < 20:
            risk_level = "Safe"
            risk_color = " "
        elif dti <= 35:
            risk_level = "Moderate"
            risk_color = " "
        else:
            risk_level = "Risky"
            risk_color = " "
        
        return {
            'dti_percentage': dti,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'recommendation': LoanRiskAnalyzer._get_dti_recommendation(dti)
        }
    
    @staticmethod
    def _get_dti_recommendation(dti):
        """Get recommendation based on DTI"""
        if dti < 20:
            return "Excellent debt level. You have good borrowing capacity."
        elif dti <= 35:
            return "Moderate debt level. Monitor your overall debt carefully."
        else:
            return "High debt level. Consider reducing debt before taking new loans."
    
    @staticmethod
    def calculate_loan_impact(monthly_income, monthly_fixed_expenses, monthly_emi):
        """
        Calculate loan impact on monthly finances
        
        Args:
            monthly_income: User's monthly income
            monthly_fixed_expenses: Monthly fixed expenses
            monthly_emi: Monthly EMI
        
        Returns:
            dict: Financial impact analysis
        """
        disposable_income = monthly_income - monthly_fixed_expenses
        remaining_after_emi = disposable_income - monthly_emi
        
        return {
            'monthly_income': monthly_income,
            'monthly_fixed_expenses': monthly_fixed_expenses,
            'monthly_emi': monthly_emi,
            'disposable_income': disposable_income,
            'remaining_after_emi': remaining_after_emi,
            'impact_percentage': (monthly_emi / disposable_income * 100) if disposable_income > 0 else 100,
            'is_sustainable': remaining_after_emi > 0
        }
    
    @staticmethod
    def calculate_risk_score(monthly_income, monthly_fixed_expenses, monthly_emi, existing_emi=0):
        """
        Calculate comprehensive loan risk score (0-100)
        
        Args:
            monthly_income: Monthly income
            monthly_fixed_expenses: Monthly fixed expenses
            monthly_emi: New loan EMI
            existing_emi: Existing loan EMIs (default 0)
        
        Returns:
            dict: Risk score analysis
        """
        # Calculate DTI with existing and new EMI
        total_emi = monthly_emi + existing_emi
        dti = (total_emi / monthly_income * 100) if monthly_income > 0 else 100
        
        # Calculate disposable income percentage
        disposable_income = monthly_income - monthly_fixed_expenses
        disposable_percentage = (disposable_income / monthly_income * 100) if monthly_income > 0 else 0
        
        # Calculate EMI impact on disposable income
        emi_impact = (monthly_emi / disposable_income * 100) if disposable_income > 0 else 100
        
        # Risk score calculation (0-100, higher = riskier)
        risk_score = 0
        
        # DTI component (40% weight)
        if dti < 20:
            risk_score += 0
        elif dti <= 35:
            risk_score += (dti - 20) * 2  # 0-30 points
        else:
            risk_score += 30 + (dti - 35) * 1.5  # 30-67.5 points
        
        # Disposable income component (30% weight)
        if disposable_percentage >= 50:
            risk_score += 0
        elif disposable_percentage >= 30:
            risk_score += (50 - disposable_percentage) * 1.5  # 0-30 points
        else:
            risk_score += 30 + (30 - disposable_percentage) * 2  # 30-60 points
        
        # EMI impact component (30% weight)
        if emi_impact < 20:
            risk_score += 0
        elif emi_impact <= 50:
            risk_score += (emi_impact - 20) * 1  # 0-30 points
        else:
            risk_score += 30 + (emi_impact - 50) * 0.5  # 30-45 points
        
        # Cap at 100
        risk_score = min(risk_score, 100)
        
        # Risk classification
        if risk_score < 30:
            risk_level = "Low Risk"
            risk_color = " "
        elif risk_score < 60:
            risk_level = "Medium Risk"
            risk_color = " "
        else:
            risk_level = "High Risk"
            risk_color = " "
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'dti': dti,
            'disposable_percentage': disposable_percentage,
            'emi_impact': emi_impact,
            'factors': {
                'dti_component': min((dti - 20) * 2 if dti > 20 else 0, 67.5),
                'disposable_component': min((50 - disposable_percentage) * 1.5 if disposable_percentage < 50 else 0, 60),
                'impact_component': min((emi_impact - 20) * 1 if emi_impact > 20 else 0, 45)
            },
            'recommendation': LoanRiskAnalyzer._get_risk_recommendation(risk_score)
        }
    
    @staticmethod
    def _get_risk_recommendation(risk_score):
        """Get recommendation based on risk score"""
        if risk_score < 30:
            return "Low risk loan. You can proceed with confidence."
        elif risk_score < 60:
            return "Moderate risk. Consider reducing loan amount or increasing tenure."
        else:
            return "High risk loan. Strongly recommend reconsidering or improving financial position."
    
    @staticmethod
    def display_affordability_analysis(affordability):
        """Display affordability analysis"""
        print(f"\n  AFFORDABILITY CHECK")
        print("-" * 40)
        print(f"  EMI as % of Income: {affordability['emi_percentage']:.1f}%")
        print(f"  Safe Limit: {affordability['safe_limit']}%")
        print(f"{' ' if affordability['is_affordable'] else ' '} Status: {'Affordable' if affordability['is_affordable'] else 'Not Affordable'}")
        
        if not affordability['is_affordable']:
            print(f"   Warning: {affordability['warning']}")
    
    @staticmethod
    def display_dti_analysis(dti_analysis):
        """Display DTI analysis"""
        print(f"\n  DEBT-TO-INCOME RATIO ANALYSIS")
        print("-" * 40)
        print(f"  DTI Ratio: {dti_analysis['dti_percentage']:.1f}%")
        print(f"{' ' if dti_analysis['dti_percentage'] < 20 else ' ' if dti_analysis['dti_percentage'] <= 35 else ' '} Risk Level: {dti_analysis['risk_level']}")
        print(f"  Recommendation: {dti_analysis['recommendation']}")
    
    @staticmethod
    def display_impact_analysis(impact):
        """Display loan impact analysis"""
        print(f"\n  LOAN IMPACT SIMULATION")
        print("-" * 40)
        print(f"  Monthly Income: {EMICalculator.format_currency(impact['monthly_income'])}")
        print(f"  Fixed Expenses: {EMICalculator.format_currency(impact['monthly_fixed_expenses'])}")
        print(f"  Disposable Income: {EMICalculator.format_currency(impact['disposable_income'])}")
        print(f"  Loan EMI: {EMICalculator.format_currency(impact['monthly_emi'])}")
        print(f"{' ' if impact['is_sustainable'] else ' '} Remaining Balance: {EMICalculator.format_currency(impact['remaining_after_emi'])}")
        print(f"  Impact on Disposable: {impact['impact_percentage']:.1f}%")
    
    @staticmethod
    def display_risk_analysis(risk_analysis):
        """Display comprehensive risk analysis"""
        print(f"\n  LOAN RISK SCORE")
        print("-" * 40)
        print(f"{' ' if risk_analysis['risk_score'] < 30 else ' ' if risk_analysis['risk_score'] < 60 else ' '} Risk Score: {risk_analysis['risk_score']:.1f}/100")
        print(f"Risk Level: {risk_analysis['risk_level']}")
        print(f"  Recommendation: {risk_analysis['recommendation']}")
        
        print(f"\n  RISK FACTORS:")
        print(f"   DTI Component: {risk_analysis['factors']['dti_component']:.1f} points")
        print(f"   Disposable Component: {risk_analysis['factors']['disposable_component']:.1f} points")
        print(f"   Impact Component: {risk_analysis['factors']['impact_component']:.1f} points")
