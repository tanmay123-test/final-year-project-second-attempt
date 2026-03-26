from .goal_engine import GoalEngine
from datetime import datetime, timedelta

class GoalProgress:
    """Track and display goal progress"""
    
    def __init__(self):
        self.goal_engine = GoalEngine()
    
    def display_goal_dashboard(self, user_id):
        """Display comprehensive goal dashboard"""
        print("\n" + "="*80)
        print("  GOAL JAR DASHBOARD")
        print("="*80)
        
        # Get goal summary
        summary = self.goal_engine.get_goal_summary(user_id)
        
        if summary['total_goals'] == 0:
            print("  No goals created yet")
            print("\n  GETTING STARTED:")
            print("     Create your first savings goal")
            print("     Set a realistic target amount")
            print("     Choose an achievable monthly contribution")
            print("     Start tracking your progress today!")
            return
        
        # Overall summary
        print(f"\n  OVERALL SUMMARY:")
        print(f"     Total Goals: {summary['total_goals']}")
        print(f"     Total Target:  {summary['total_target']:,.2f}")
        print(f"     Total Saved:  {summary['total_saved']:,.2f}")
        print(f"     Overall Progress: {summary['overall_progress']:.1f}%")
        
        # Progress bar
        bar_length = 50
        filled_length = int(summary['overall_progress'] / 100 * bar_length)
        progress_bar = ' ' * filled_length + ' ' * (bar_length - filled_length)
        print(f"     Progress: [{progress_bar}] {summary['overall_progress']:.1f}%")
        
        # Individual goals
        print(f"\n  INDIVIDUAL GOALS:")
        print("-" * 80)
        print(f"{'Goal Name':<20} {'Target':<12} {'Saved':<12} {'Progress':<10} {'Monthly':<10} {'Status':<12} {'Deadline':<12}")
        print("-" * 80)
        
        for goal in summary['goals']:
            status = self._get_goal_status(goal)
            deadline = "N/A"
            
            if goal['target_date']:
                target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
                days_remaining = (target_date - datetime.now()).days
                deadline = f"{days_remaining} days"
                
                if days_remaining <= 30:
                    deadline = f"   {days_remaining} days"
                if days_remaining <= 7:
                    deadline = f"  {days_remaining} days"
            
            # Progress bar for individual goal
            goal_bar_length = 20
            goal_filled = int(goal['progress_percentage'] / 100 * goal_bar_length)
            goal_progress_bar = ' ' * goal_filled + ' ' * (goal_bar_length - goal_filled)
            
            print(f"{goal['goal_name']:<20}  {goal['target_amount']:>11,.2f}  {goal['current_amount']:>11,.2f} {goal['progress_percentage']:>9.1f}%  {goal['monthly_contribution']:>9.0f} {status:<12} {deadline:<12}")
            print(f"{'':<20} {'':<12} [{goal_progress_bar}] {'':<10} {'':<10} {status:<12} {deadline:<12}")
        
        # Motivational messages
        self._display_motivational_messages(summary)
        
        print("="*80)
    
    def display_single_goal_progress(self, user_id, goal_id):
        """Display detailed progress for a single goal"""
        print("\n" + "="*70)
        print("  GOAL PROGRESS TRACKER")
        print("="*70)
        
        # Get goal details
        goal = self.goal_engine.get_goal_progress(user_id, goal_id)
        
        if not goal:
            print("  Goal not found")
            return
        
        print(f"\n  GOAL DETAILS:")
        print(f"     Goal Name: {goal['goal_name']}")
        print(f"     Target Amount:  {goal['target_amount']:,.2f}")
        print(f"     Current Amount:  {goal['current_amount']:,.2f}")
        print(f"     Progress: {goal['progress_percentage']:.1f}%")
        print(f"     Monthly Contribution:  {goal['monthly_contribution']:,.2f}")
        
        if goal['target_date']:
            target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
            print(f"     Target Date: {target_date.strftime('%B %d, %Y')}")
            
            days_remaining = (target_date - datetime.now()).days
            months_remaining = max(0, int(days_remaining / 30))
            
            print(f"     Time Remaining: {months_remaining} months, {days_remaining % 30} days")
        
        # Progress visualization
        print(f"\n  PROGRESS VISUAL:")
        bar_length = 40
        filled_length = int(goal['progress_percentage'] / 100 * bar_length)
        progress_bar = ' ' * filled_length + ' ' * (bar_length - filled_length)
        
        print(f"   [{progress_bar}] {goal['progress_percentage']:.1f}% Complete")
        
        # Savings history
        if goal.get('savings_history'):
            print(f"\n  RECENT SAVINGS:")
            print("-" * 70)
            print(f"{'Date':<12} {'Amount':<12} {'Method':<12} {'Notes':<20}")
            print("-" * 70)
            
            recent_savings = goal['savings_history'][:10]  # Show last 10 transactions
            for savings in recent_savings:
                date_str = datetime.strptime(savings['transaction_date'], '%Y-%m-%d').strftime('%b %d')
                print(f"{date_str:<12}  {savings['amount']:>11,.2f} {savings['payment_method']:<12} {savings['notes']:<20}")
        
        # Insights and recommendations
        self._display_goal_insights(goal)
        self._display_goal_recommendations(goal)
        
        print("="*70)
    
    def _get_goal_status(self, goal):
        """Get goal status based on progress"""
        if goal['progress_percentage'] >= 100:
            return "  COMPLETED"
        elif goal['progress_percentage'] >= 75:
            return "  ON TRACK"
        elif goal['progress_percentage'] >= 50:
            return "  HALF WAY"
        elif goal['progress_percentage'] >= 25:
            return "  STARTED"
        else:
            return "  JUST STARTED"
    
    def _display_goal_insights(self, goal):
        """Display insights about goal progress"""
        print(f"\n  GOAL INSIGHTS:")
        
        # Completion rate analysis
        if goal['months_passed'] > 0:
            monthly_average = goal['current_amount'] / goal['months_passed']
            expected_amount = goal['monthly_contribution'] * goal['months_passed']
            
            if monthly_average >= goal['monthly_contribution']:
                print(f"     Great! You're saving  {monthly_average - goal['monthly_contribution']:.2f} more than planned!")
            else:
                shortfall = goal['monthly_contribution'] - monthly_average
                print(f"      You're saving  {shortfall:.2f} less than planned each month")
        
        # Time-based insights
        if goal['target_date']:
            target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
            total_days = (target_date - datetime.now()).days
            passed_days = (datetime.now() - datetime.strptime(goal['created_at'], '%Y-%m-%d %H:%M:%S')).days
            
            if passed_days > 0:
                daily_required = goal['remaining_amount'] / total_days
                print(f"     To reach goal on time, save  {daily_required:.2f} daily")
        
        # Progress consistency
        if goal['months_remaining'] > 0:
            if goal['progress_percentage'] > 80:
                print(f"     Excellent progress! You're ahead of schedule!")
            elif goal['progress_percentage'] > 60:
                print(f"     Good progress! Keep up the great work!")
            elif goal['progress_percentage'] < 40:
                print(f"      Consider increasing monthly savings to stay on track")
    
    def _display_goal_recommendations(self, goal):
        """Display personalized recommendations"""
        print(f"\n  RECOMMENDATIONS:")
        
        # Based on progress
        if goal['progress_percentage'] < 25:
            print(f"     Start with small, consistent amounts")
            print(f"     Set up automatic transfers from your account")
        
        elif goal['progress_percentage'] < 50:
            print(f"     You're making good progress!")
            print(f"     Consider increasing savings slightly to reach goal faster")
        
        elif goal['progress_percentage'] < 75:
            print(f"     Great progress! You're more than halfway there!")
            print(f"     Keep maintaining current savings rate")
        
        else:
            print(f"     Almost there! Final push needed!")
            print(f"     Consider a one-time bonus contribution to complete sooner")
        
        # Based on remaining time
        if goal['months_remaining'] > 0 and goal['months_remaining'] <= 3:
            print(f"     Deadline approaching! Consider extra contribution")
        
        # Motivational tips
        print(f"\n  MOTIVATION TIPS:")
        tips = [
            "Visualize your goal achievement daily",
            "Celebrate small milestones along the way",
            "Set up automatic savings transfers",
            "Track your progress weekly",
            "Share your goal with friends for accountability",
            "Review and adjust your goal monthly"
        ]
        
        for i, tip in enumerate(tips, 1):
            print(f"   {i}. {tip}")
    
    def _display_motivational_messages(self, summary):
        """Display overall motivational messages"""
        print(f"\n  OVERALL MOTIVATION:")
        
        if summary['overall_progress'] >= 75:
            print("     OUTSTANDING! You're crushing your savings goals!")
        elif summary['overall_progress'] >= 50:
            print("     GREAT PROGRESS! You're well on your way to financial success!")
        elif summary['overall_progress'] >= 25:
            print("     GOOD START! Keep building momentum!")
        else:
            print("     EVERY JOURNEY BEGINS WITH A SINGLE STEP!")
        
        # General encouragement
        print(f"\n  REMEMBER:")
        print("     Small consistent savings lead to big results")
        print("     Your future self will thank you for starting today")
        print("     Every rupee saved is a step towards financial freedom")
        print("     You're capable of achieving amazing things!")
    
    def calculate_goal_completion_forecast(self, user_id, goal_id):
        """Calculate when goal will be completed"""
        goal = self.goal_engine.get_goal_progress(user_id, goal_id)
        
        if not goal:
            return None
        
        if goal['monthly_contribution'] <= 0:
            return None
        
        remaining_amount = goal['target_amount'] - goal['current_amount']
        months_to_complete = int(remaining_amount / goal['monthly_contribution'])
        
        completion_date = datetime.now() + timedelta(days=months_to_complete * 30)
        
        return {
            'months_to_complete': months_to_complete,
            'completion_date': completion_date,
            'remaining_amount': remaining_amount
        }
