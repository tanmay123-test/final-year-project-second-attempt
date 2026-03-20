from .goal_engine import GoalEngine
from datetime import datetime, timedelta

class GoalSimulator:
    """Simulate goal timelines and scenarios"""
    
    def __init__(self):
        self.goal_engine = GoalEngine()
    
    def simulate_goal_timeline(self, target_amount, monthly_contribution):
        """Simulate different saving timelines"""
        print("\n" + "="*60)
        print("⏰ GOAL TIMELINE SIMULATION")
        print("="*60)
        
        if monthly_contribution <= 0:
            print("❌ Monthly contribution must be greater than 0")
            return None
        
        # Calculate base timeline
        base_months = int(target_amount / monthly_contribution)
        base_years = base_months / 12
        
        print(f"\n📊 BASE TIMELINE:")
        print(f"   💰 Target Amount: ₹{target_amount:,.2f}")
        print(f"   💳 Monthly Saving: ₹{monthly_contribution:,.2f}")
        print(f"   📅 Time Required: {base_months} months ({base_years:.1f} years)")
        
        # Check feasibility
        if base_months > 60:
            print(f"   ⚠️ WARNING: Saving period exceeds 5 years!")
            print(f"   💡 Consider increasing monthly savings to ₹{target_amount/60:,.2f}")
        elif base_months < 6:
            print(f"   ✅ EXCELLENT: You'll reach your goal in under 6 months!")
        
        # Alternative scenarios
        print(f"\n🎯 ALTERNATIVE SCENARIOS:")
        timelines = self.goal_engine.simulate_timeline(target_amount, monthly_contribution)
        
        for timeline in timelines:
            print(f"\n   💳 ₹{timeline['monthly_contribution']:.0f}/month:")
            print(f"      📅 {timeline['months_required']} months ({timeline['years_required']:.1f} years)")
            print(f"      📝 {timeline['description']}")
        
        # Recommendation
        if len(timelines) > 0:
            best_option = min(timelines, key=lambda x: x['months_required'])
            print(f"\n🏆 RECOMMENDATION:")
            print(f"   💳 Save ₹{best_option['monthly_contribution']:.0f}/month")
            print(f"   📅 Reach goal in {best_option['months_required']} months")
            print(f"   💰 Save {base_months - best_option['months_required']} months!")
        
        print("="*60)
        return timelines
    
    def calculate_goal_feasibility(self, target_amount, monthly_contribution, target_date=None):
        """Calculate goal feasibility analysis"""
        print("\n" + "="*60)
        print("🎯 GOAL FEASIBILITY ANALYSIS")
        print("="*60)
        
        if monthly_contribution <= 0:
            print("❌ Invalid monthly contribution")
            return {'feasible': False}
        
        months_required = int(target_amount / monthly_contribution)
        years_required = months_required / 12
        
        print(f"\n📊 CALCULATION:")
        print(f"   💰 Target Amount: ₹{target_amount:,.2f}")
        print(f"   💳 Monthly Saving: ₹{monthly_contribution:,.2f}")
        print(f"   📅 Time Required: {months_required} months ({years_required:.1f} years)")
        
        # Feasibility checks
        feasible = True
        warnings = []
        recommendations = []
        
        if months_required > 60:
            feasible = False
            warnings.append("Saving period exceeds 5 years")
            recommendations.append("Consider increasing monthly savings amount")
        
        if monthly_contribution < 1000:
            warnings.append("Monthly saving is quite low")
            recommendations.append("Consider increasing savings for faster goal achievement")
        
        # Target date analysis
        if target_date:
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d')
            available_months = (target_date_obj - datetime.now()).days // 30
            available_months = max(0, available_months)
            
            required_months = months_required
            can_achieve = available_months >= required_months
            
            print(f"\n📅 TARGET DATE ANALYSIS:")
            print(f"   🎯 Target Date: {target_date}")
            print(f"   📊 Months Available: {available_months}")
            print(f"   📊 Months Required: {required_months}")
            print(f"   {'✅ ACHIEVABLE' if can_achieve else '❌ NOT ACHIEVABLE'}")
            
            if not can_achieve:
                feasible = False
                shortage_months = required_months - available_months
                additional_saving = (target_amount - (monthly_contribution * available_months)) / shortage_months
                recommendations.append(f"Save additional ₹{additional_saving:.2f}/month to reach goal on time")
        
        # Display results
        print(f"\n🎯 FEASIBILITY: {'✅ FEASIBLE' if feasible else '❌ NOT FEASIBLE'}")
        
        if warnings:
            print(f"\n⚠️ WARNINGS:")
            for warning in warnings:
                print(f"   • {warning}")
        
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        print("="*60)
        
        return {
            'feasible': feasible,
            'months_required': months_required,
            'years_required': years_required,
            'warnings': warnings,
            'recommendations': recommendations,
            'target_date_achievable': target_date and feasible
        }
    
    def project_savings_growth(self, user_id, goal_id, projection_months=24):
        """Project savings growth over time"""
        print("\n" + "="*60)
        print("📈 SAVINGS GROWTH PROJECTION")
        print("="*60)
        
        # Get goal details
        goal = self.goal_engine.get_goal_progress(user_id, goal_id)
        
        if not goal:
            print("❌ Goal not found")
            return None
        
        monthly_contribution = goal['monthly_contribution']
        current_amount = goal['current_amount']
        
        print(f"\n📊 CURRENT STATUS:")
        print(f"   🎯 Goal: {goal['goal_name']}")
        print(f"   💰 Target: ₹{goal['target_amount']:,.2f}")
        print(f"   💵 Saved: ₹{current_amount:,.2f}")
        print(f"   📊 Progress: {goal['progress_percentage']:.1f}%")
        print(f"   💳 Monthly: ₹{monthly_contribution:,.2f}")
        
        # Calculate projections
        projections = self.goal_engine.calculate_savings_projection(user_id, goal_id, projection_months)
        
        print(f"\n📈 PROJECTIONS:")
        print(f"{'Months':<10} {'Amount':<15} {'Date':<12} {'Progress':<12}")
        print("-" * 60)
        
        for projection in projections:
            progress = (projection['future_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            print(f"{projection['months']:<10} ₹{projection['future_amount']:>14,.2f} {projection['projection_date']:<12} {progress:>10.1f}%")
        
        # Calculate completion date
        remaining_amount = goal['target_amount'] - current_amount
        if monthly_contribution > 0:
            months_to_complete = int(remaining_amount / monthly_contribution)
            completion_date = datetime.now() + timedelta(days=months_to_complete * 30)
            
            print(f"\n🎯 COMPLETION FORECAST:")
            print(f"   📅 Estimated Completion: {completion_date.strftime('%B %d, %Y')}")
            print(f"   📊 Months Remaining: {months_to_complete}")
            print(f"   💰 Amount Remaining: ₹{remaining_amount:,.2f}")
        
        print("="*60)
        return projections
    
    def analyze_saving_patterns(self, user_id):
        """Analyze user's saving patterns"""
        print("\n" + "="*60)
        print("📊 SAVING PATTERN ANALYSIS")
        print("="*60)
        
        # Get goals
        goals = self.goal_engine.get_user_goals(user_id)
        
        if not goals:
            print("📭 No goals found for analysis")
            return None
        
        # Analyze patterns
        total_monthly_target = sum(goal['monthly_contribution'] for goal in goals)
        total_current_saved = sum(goal['current_amount'] for goal in goals)
        total_target = sum(goal['target_amount'] for goal in goals)
        
        print(f"\n📊 OVERALL SAVINGS:")
        print(f"   💳 Monthly Target: ₹{total_monthly_target:,.2f}")
        print(f"   💵 Current Saved: ₹{total_current_saved:,.2f}")
        print(f"   🎯 Total Target: ₹{total_target:,.2f}")
        print(f"   📊 Overall Progress: {(total_current_saved/total_target*100) if total_target > 0 else 0:.1f}%")
        
        # Goal-wise analysis
        print(f"\n📋 GOAL BREAKDOWN:")
        print(f"{'Goal Name':<20} {'Target':<12} {'Saved':<12} {'Progress':<10} {'Monthly':<10} {'Remaining':<12}")
        print("-" * 80)
        
        for goal in goals:
            remaining = goal['target_amount'] - goal['current_amount']
            print(f"{goal['goal_name']:<20} ₹{goal['target_amount']:>11,.2f} ₹{goal['current_amount']:>11,.2f} {goal['progress_percentage']:>9.1f}% ₹{goal['monthly_contribution']:>9.0f} ₹{remaining:>11,.2f}")
        
        # Identify best and worst performing goals
        if goals:
            best_progress = max(goals, key=lambda x: x['progress_percentage'])
            worst_progress = min(goals, key=lambda x: x['progress_percentage'])
            
            print(f"\n🏆 BEST PERFORMING GOAL:")
            print(f"   🎯 {best_progress['goal_name']}: {best_progress['progress_percentage']:.1f}% complete")
            
            print(f"\n⚠️ GOAL NEEDING ATTENTION:")
            print(f"   🎯 {worst_progress['goal_name']}: {worst_progress['progress_percentage']:.1f}% complete")
        
        print("="*60)
        return {
            'total_monthly_target': total_monthly_target,
            'total_current_saved': total_current_saved,
            'total_target': total_target,
            'goals': goals
        }
