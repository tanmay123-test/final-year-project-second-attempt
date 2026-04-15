from flask import Flask, request, jsonify
from .loan_engine import LoanEngine

class LoanAPI:
    """REST API endpoints for loan analysis"""
    
    def __init__(self, blueprint=None):
        self.blueprint = blueprint
        self.loan_engine = LoanEngine()
        if blueprint:
            self.init_blueprint(blueprint)
    
    def init_blueprint(self, blueprint):
        """Initialize Blueprint with loan API endpoints"""
        self.blueprint = blueprint
        self.register_routes()
    
    def register_routes(self):
        """Register all API routes"""
        
        @self.blueprint.route('/api/loan/analyze', methods=['POST'])
        def analyze_loan():
            """Analyze a single loan"""
            try:
                data = request.get_json() or {}
                
                required_fields = ['user_id', 'loan_amount', 'interest_rate', 'loan_tenure']
                for field in required_fields:
                    if field not in data or data.get(field) is None:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                user_id = data['user_id']
                loan_amount = float(data.get('loan_amount') or 0)
                interest_rate = float(data.get('interest_rate') or 0)
                loan_tenure = int(data.get('loan_tenure') or 0)
                
                # Optional financial profile (used for affordability/impact analysis)
                monthly_income = float(data.get('monthly_income') or 0)
                monthly_fixed_expenses = float(data.get('monthly_fixed_expenses') or 0)
                
                if loan_amount <= 0 or interest_rate < 0 or loan_tenure <= 0:
                    return jsonify({'error': 'Invalid input values. Amount and tenure must be positive.'}), 400
                
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
                        'affordability': analysis['affordability'],
                        'dti_analysis': analysis['dti_analysis'],
                        'impact_analysis': analysis['impact_analysis'],
                        'risk_analysis': analysis['risk_analysis'],
                        'recommendation': analysis['recommendation']
                    }
                })
                
            except Exception as e:
                import traceback
                print(f"Loan analyze error: {traceback.format_exc()}")
                return jsonify({'error': str(e)}), 500
        
        @self.blueprint.route('/api/loan/compare', methods=['POST'])
        def compare_loans():
            """Compare two loan offers"""
            try:
                data = request.get_json() or {}
                
                # Validate required fields
                required_fields = ['user_id', 'loan1', 'loan2']
                for field in required_fields:
                    if field not in data or data.get(field) is None:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                user_id = data['user_id']
                loan1 = data['loan1']
                loan2 = data['loan2']
                
                # Validate loan parameters
                for i, loan in enumerate([loan1, loan2], 1):
                    loan_fields = ['amount', 'rate', 'tenure']
                    for field in loan_fields:
                        if field not in loan or loan.get(field) is None:
                            return jsonify({'error': f'Missing field {field} in loan{i}'}), 400
                    
                    if float(loan.get('amount') or 0) <= 0 or float(loan.get('rate') or 0) < 0 or int(loan.get('tenure') or 0) <= 0:
                        return jsonify({'error': f'Invalid values in loan{i}'}), 400
                
                comparison = self.loan_engine.compare_loans(user_id, loan1, loan2)
                
                return jsonify({
                    'success': True,
                    'data': comparison
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.blueprint.route('/api/loan/impact', methods=['POST'])
        def simulate_impact():
            """Simulate how a loan affects monthly budget"""
            try:
                data = request.get_json() or {}
                
                required_fields = ['user_id', 'loan_amount', 'interest_rate', 'loan_tenure']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                user_id = data['user_id']
                loan_amount = float(data['loan_amount'])
                interest_rate = float(data['interest_rate'])
                loan_tenure = int(data['loan_tenure'])
                
                # Financial data can be provided or fetched from DB
                monthly_income = data.get('monthly_income')
                monthly_expenses = data.get('monthly_expenses')
                
                if monthly_income:
                    self.loan_engine._override_financial_data = {
                        'monthly_income': float(monthly_income),
                        'monthly_fixed_expenses': float(monthly_expenses or 0),
                        'disposable_income': float(monthly_income) - float(monthly_expenses or 0)
                    }
                
                # Explicitly call analyze_loan_impact on the engine
                impact = self.loan_engine.analyze_loan_impact(user_id, loan_amount, interest_rate, loan_tenure)
                
                # Clear override
                self.loan_engine._override_financial_data = None
                
                return jsonify({
                    'success': True,
                    'data': impact
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.blueprint.route('/api/loan/repayment-simulation', methods=['POST'])
        def simulate_early_repayment():
            """Simulate how extra payments reduce loan tenure/interest"""
            try:
                data = request.get_json() or {}
                
                required_fields = ['loan_amount', 'interest_rate', 'loan_tenure', 'extra_payment']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                sim = self.loan_engine.simulate_early_repayment(
                    float(data['loan_amount']),
                    float(data['interest_rate']),
                    int(data['loan_tenure']),
                    float(data['extra_payment'])
                )
                
                return jsonify({
                    'success': True,
                    'data': sim
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.blueprint.route('/api/loan/schedule', methods=['POST'])
        def get_amortization_schedule():
            """Get full month-by-month repayment schedule"""
            try:
                data = request.get_json() or {}
                
                required_fields = ['loan_amount', 'interest_rate', 'loan_tenure']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                schedule = self.loan_engine.get_amortization_schedule(
                    float(data['loan_amount']),
                    float(data['interest_rate']),
                    int(data['loan_tenure'])
                )
                
                return jsonify({
                    'success': True,
                    'data': schedule
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.blueprint.route('/api/loan/history/<int:user_id>', methods=['GET'])
        def get_loan_history(user_id):
            """Get user's previous loan analysis history"""
            try:
                # Explicitly call get_analysis_history on the engine
                history = self.loan_engine.get_analysis_history(user_id)
                return jsonify({
                    'success': True,
                    'data': history
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.blueprint.route('/api/loan/quick-analysis', methods=['POST'])
        def quick_analysis():
            """Minimal analysis without user context"""
            try:
                data = request.get_json() or {}
                required = ['amount', 'rate', 'tenure']
                if not all(k in data for k in required):
                    return jsonify({'error': 'Missing parameters'}), 400
                
                from .emi_calculator import EMICalculator
                calc = EMICalculator()
                emi = calc.calculate_emi(float(data['amount']), float(data['rate']), int(data['tenure']))
                total_payment = emi * int(data['tenure'])
                total_interest = total_payment - float(data['amount'])
                
                return jsonify({
                    'success': True,
                    'data': {
                        'emi': emi,
                        'total_payment': total_payment,
                        'total_interest': total_interest
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

# Helper function to initialize API with Flask app
def create_loan_api(app):
    """Create and initialize loan API with Flask app"""
    api = LoanAPI(app)
    return api
