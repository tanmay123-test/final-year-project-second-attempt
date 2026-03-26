from flask import Flask, request, jsonify
from .loan_engine import LoanEngine

class LoanAPI:
    """REST API endpoints for loan analysis"""
    
    def __init__(self, app=None):
        self.app = app
        self.loan_engine = LoanEngine()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Flask app with loan API endpoints"""
        self.app = app
        self.register_routes()
    
    def register_routes(self):
        """Register all API routes"""
        
        @self.app.route('/api/loan/analyze', methods=['POST'])
        def analyze_loan():
            """Analyze a single loan"""
            try:
                data = request.get_json()
                
                required_fields = ['user_id', 'loan_amount', 'interest_rate', 'loan_tenure']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                user_id = data['user_id']
                loan_amount = float(data['loan_amount'])
                interest_rate = float(data['interest_rate'])
                loan_tenure = int(data['loan_tenure'])
                
                # Optional financial profile (used for affordability/impact analysis)
                monthly_income = float(data.get('monthly_income', 0))
                monthly_fixed_expenses = float(data.get('monthly_fixed_expenses', 0))
                
                if loan_amount <= 0 or interest_rate < 0 or loan_tenure <= 0:
                    return jsonify({'error': 'Invalid input values'}), 400
                
                # Inject financial data into engine so it doesn't rely on empty DB
                if monthly_income > 0:
                    self.loan_engine._override_financial_data = {
                        'monthly_income': monthly_income,
                        'monthly_fixed_expenses': monthly_fixed_expenses,
                        'disposable_income': monthly_income - monthly_fixed_expenses
                    }
                
                analysis = self.loan_engine.analyze_loan(user_id, loan_amount, interest_rate, loan_tenure)
                
                # Clear override
                self.loan_engine._override_financial_data = None
                
                return jsonify({
                    'success': True,
                    'data': {
                        'loan_details': analysis['loan_details'],
                        'affordability': {
                            'is_affordable': analysis['affordability']['is_affordable'],
                            'emi_percentage': analysis['affordability']['emi_percentage'],
                            'warning': analysis['affordability']['warning']
                        },
                        'dti_analysis': {
                            'dti_percentage': analysis['dti_analysis']['dti_percentage'],
                            'risk_level': analysis['dti_analysis']['risk_level'],
                            'recommendation': analysis['dti_analysis']['recommendation']
                        },
                        'impact_analysis': {
                            'disposable_income': analysis['impact_analysis']['disposable_income'],
                            'remaining_after_emi': analysis['impact_analysis']['remaining_after_emi'],
                            'is_sustainable': analysis['impact_analysis']['is_sustainable']
                        },
                        'risk_analysis': {
                            'risk_score': analysis['risk_analysis']['risk_score'],
                            'risk_level': analysis['risk_analysis']['risk_level'],
                            'recommendation': analysis['risk_analysis']['recommendation']
                        },
                        'recommendation': analysis['recommendation']
                    }
                })
                
            except Exception as e:
                import traceback
                print(f"Loan analyze error: {traceback.format_exc()}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/loan/compare', methods=['POST'])
        def compare_loans():
            """Compare two loan offers"""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['user_id', 'loan1', 'loan2']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                user_id = data['user_id']
                loan1 = data['loan1']
                loan2 = data['loan2']
                
                # Validate loan parameters
                for i, loan in enumerate([loan1, loan2], 1):
                    loan_fields = ['amount', 'rate', 'tenure']
                    for field in loan_fields:
                        if field not in loan:
                            return jsonify({'error': f'Missing field {field} in loan{i}'}), 400
                    
                    if loan['amount'] <= 0 or loan['rate'] < 0 or loan['tenure'] <= 0:
                        return jsonify({'error': f'Invalid values in loan{i}'}), 400
                
                # Perform comparison
                comparison = self.loan_engine.compare_loans(user_id, loan1, loan2)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'loan1': comparison['loan1'],
                        'loan2': comparison['loan2'],
                        'cheaper_option': comparison['cheaper_option'],
                        'savings': comparison['savings'],
                        'recommendation': comparison['recommendation']
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/loan/impact', methods=['POST'])
        def calculate_impact():
            """Calculate loan impact on finances"""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['monthly_income', 'monthly_fixed_expenses', 'loan_amount', 'interest_rate', 'loan_tenure']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                monthly_income = float(data['monthly_income'])
                monthly_fixed_expenses = float(data['monthly_fixed_expenses'])
                loan_amount = float(data['loan_amount'])
                interest_rate = float(data['interest_rate'])
                loan_tenure = int(data['loan_tenure'])
                
                # Calculate EMI
                from .emi_calculator import EMICalculator
                emi, _, _ = EMICalculator.calculate_emi(loan_amount, interest_rate, loan_tenure)
                
                # Calculate impact
                impact = self.loan_engine.loan_risk.calculate_loan_impact(
                    monthly_income, monthly_fixed_expenses, emi
                )
                
                return jsonify({
                    'success': True,
                    'data': {
                        'monthly_emi': emi,
                        'disposable_income': impact['disposable_income'],
                        'remaining_after_emi': impact['remaining_after_emi'],
                        'impact_percentage': impact['impact_percentage'],
                        'is_sustainable': impact['is_sustainable']
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/loan/repayment-simulation', methods=['POST'])
        def repayment_simulation():
            """Simulate early repayment"""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['loan_amount', 'interest_rate', 'loan_tenure', 'extra_payment']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                loan_amount = float(data['loan_amount'])
                interest_rate = float(data['interest_rate'])
                loan_tenure = int(data['loan_tenure'])
                extra_payment = float(data['extra_payment'])
                
                # Perform simulation
                simulation = self.loan_engine.simulate_early_repayment(
                    loan_amount, interest_rate, loan_tenure, extra_payment
                )
                
                return jsonify({
                    'success': True,
                    'data': {
                        'months_saved': simulation['months_saved'],
                        'interest_saved': simulation['interest_saved'],
                        'new_tenure': simulation['new_tenure'],
                        'original_interest': simulation['original_interest'],
                        'new_interest': simulation['new_interest'],
                        'total_savings': simulation['total_savings'],
                        'original_emi': simulation['original_emi'],
                        'new_emi': simulation['new_emi'],
                        'extra_payment': simulation['extra_payment']
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/loan/schedule', methods=['POST'])
        def generate_schedule():
            """Generate repayment schedule"""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['loan_amount', 'interest_rate', 'loan_tenure']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                loan_amount = float(data['loan_amount'])
                interest_rate = float(data['interest_rate'])
                loan_tenure = int(data['loan_tenure'])
                extra_payment = float(data.get('extra_payment', 0))
                
                # Generate schedule
                schedule = self.loan_engine.generate_repayment_schedule(
                    loan_amount, interest_rate, loan_tenure, extra_payment
                )
                
                return jsonify({
                    'success': True,
                    'data': {
                        'schedule': schedule,
                        'total_months': len(schedule)
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/loan/history/<int:user_id>', methods=['GET'])
        def get_loan_history(user_id):
            """Get user's loan analysis history"""
            try:
                history = self.loan_engine.get_loan_history(user_id)
                comparison_history = self.loan_engine.get_comparison_history(user_id)
                
                # Normalize fields for frontend
                for item in history:
                    item['date'] = item.get('created_at', '')[:10] if item.get('created_at') else ''
                    item['amount'] = item.get('loan_amount', 0)
                    item['tenure'] = item.get('loan_tenure', 0)
                    item['emi'] = item.get('monthly_emi', 0)
                    item['dti'] = round(item.get('dti_ratio', 0), 1)
                    item['risk_score'] = round(item.get('risk_score', 0))
                    item['risk_level'] = (
                        'High' if item['risk_score'] > 70 else
                        'Medium' if item['risk_score'] > 40 else 'Low'
                    )
                
                return jsonify({
                    'success': True,
                    'data': {
                        'loan_analyses': history,
                        'analyses': history,  # alias for frontend compatibility
                        'comparisons': comparison_history
                    }
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/loan/quick-analysis', methods=['POST'])
        def quick_analysis():
            """Get quick loan analysis"""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['user_id', 'loan_amount', 'interest_rate', 'loan_tenure']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                user_id = data['user_id']
                loan_amount = float(data['loan_amount'])
                interest_rate = float(data['interest_rate'])
                loan_tenure = int(data['loan_tenure'])
                
                # Get quick analysis
                analysis = self.loan_engine.get_quick_analysis(user_id, loan_amount, interest_rate, loan_tenure)
                
                return jsonify({
                    'success': True,
                    'data': analysis
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

# Helper function to initialize API with Flask app
def create_loan_api(app):
    """Create and initialize loan API with Flask app"""
    api = LoanAPI(app)
    return api
