from datetime import datetime, timedelta
from .uplan_database import UPlanDatabase

class BudgetGamification:
    def __init__(self):
        self.db = UPlanDatabase()
    
    def check_budget_master_reward(self, user_id):
        """Check if user qualifies for Budget Master reward"""
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        # Get budget status for all categories
        budgets = self.db.get_budget_status(user_id, month, year)
        
        if not budgets:
            return False, "No budgets set"
        
        # Check if all categories are within budget
        all_within_budget = all(budget['spent'] <= budget['budget_amount'] for budget in budgets)
        
        if all_within_budget and len(budgets) > 0:
            # Check if reward already given this month
            existing_reward = self._check_existing_reward(user_id, "Budget Master", month, year)
            if not existing_reward:
                self.db.add_reward(user_id, "Budget Master", f"Stayed within all budgets for {month} {year}")
                return True, f"  Budget Master achieved for {month} {year}!"
        
        return False, "Keep working to stay within all budgets"
    
    def check_savings_hero_reward(self, user_id):
        """Check if user qualifies for Savings Hero reward"""
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        # Get financial plan
        plan = self.db.get_financial_plan(user_id)
        if not plan:
            return False, "No financial plan set"
        
        # Get actual savings (money not spent from disposable income)
        budgets = self.db.get_budget_status(user_id, month, year)
        total_spent = sum(budget['spent'] for budget in budgets) if budgets else 0
        
        # Calculate actual savings
        actual_savings = plan['disposable_income'] - total_spent
        
        if actual_savings >= 5000:  # Target savings threshold
            # Check if reward already given this month
            existing_reward = self._check_existing_reward(user_id, "Savings Hero", month, year)
            if not existing_reward:
                self.db.add_reward(user_id, "Savings Hero", f"Saved  {actual_savings:.2f} in {month} {year}")
                return True, f"     Savings Hero achieved! Saved  {actual_savings:.2f} in {month} {year}"
        
        return False, f"Save  {5000 - actual_savings:.2f} more to qualify for Savings Hero"
    
    def check_discipline_streak_reward(self, user_id):
        """Check if user has a 7-day transaction logging streak"""
        # Get recent transactions (last 7 days)
        transactions = self._get_recent_transactions(user_id, 7)
        
        # Check if there are transactions for each of the last 7 days
        days_with_transactions = set()
        
        for trans in transactions:
            transaction_date = datetime.strptime(trans['date'], '%Y-%m-%d').date()
            days_with_transactions.add(transaction_date)
        
        # Check if we have 7 consecutive days
        today = datetime.now().date()
        consecutive_days = 0
        
        for i in range(7):
            check_date = today - timedelta(days=i)
            if check_date in days_with_transactions:
                consecutive_days += 1
            else:
                break
        
        if consecutive_days >= 7:
            # Check if reward already given
            existing_reward = self._check_existing_reward(user_id, "Discipline Streak", None, None)
            if not existing_reward:
                self.db.add_reward(user_id, "Discipline Streak", "Logged transactions for 7 consecutive days")
                return True, "  Discipline Streak achieved! 7 days of consistent tracking!"
        
        return False, f"Keep logging! Current streak: {consecutive_days} days"
    
    def check_consistency_champion_reward(self, user_id):
        """Check if user has consistent spending patterns"""
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        # Get spending data for the month
        spending_data = self.db.get_monthly_spending_data(user_id, month, year)
        
        if not spending_data or len(spending_data) < 3:
            return False, "Need more spending data to evaluate consistency"
        
        # Calculate daily spending variance
        days_in_month = self._get_days_in_month(current_date.month, current_date.year)
        total_spending = sum(item['total'] for item in spending_data)
        daily_average = total_spending / days_in_month
        
        # Check if variance is low (consistent spending)
        # This is a simplified check - could be enhanced with more sophisticated analysis
        budgets = self.db.get_budget_status(user_id, month, year)
        
        if budgets:
            # Check if spending is close to budget expectations
            within_expectations = 0
            for budget in budgets:
                expected_spending = budget['budget_amount'] * (current_date.day / days_in_month)
                if abs(budget['spent'] - expected_spending) <= (expected_spending * 0.2):  # Within 20%
                    within_expectations += 1
            
            if within_expectations == len(budgets):
                # Check if reward already given this month
                existing_reward = self._check_existing_reward(user_id, "Consistency Champion", month, year)
                if not existing_reward:
                    self.db.add_reward(user_id, "Consistency Champion", f"Maintained consistent spending in {month} {year}")
                    return True, "  Consistency Champion achieved! Great spending consistency!"
        
        return False, "Maintain steady spending patterns to earn this reward"
    
    def get_user_rewards(self, user_id):
        """Get all rewards for a user"""
        rewards = self.db.get_rewards(user_id)
        
        # Group rewards by type
        reward_summary = {}
        for reward in rewards:
            reward_type = reward['reward_type']
            if reward_type not in reward_summary:
                reward_summary[reward_type] = []
            reward_summary[reward_type].append(reward)
        
        return {
            'total_rewards': len(rewards),
            'reward_summary': reward_summary,
            'recent_rewards': rewards[:10]  # Last 10 rewards
        }
    
    def display_reward_dashboard(self, user_id):
        """Display comprehensive reward dashboard"""
        print(f"\n" + "="*70)
        print("  BUDGET GAMIFICATION DASHBOARD")
        print("="*70)
        
        # Check potential rewards
        print(f"\n  POTENTIAL REWARDS")
        print("-" * 50)
        
        # Budget Master
        achieved, message = self.check_budget_master_reward(user_id)
        status = "  ACHIEVED" if achieved else "  IN PROGRESS"
        print(f"  Budget Master: {status}")
        if not achieved:
            print(f"     {message}")
        
        # Savings Hero
        achieved, message = self.check_savings_hero_reward(user_id)
        status = "  ACHIEVED" if achieved else "  IN PROGRESS"
        print(f"     Savings Hero: {status}")
        if not achieved:
            print(f"     {message}")
        
        # Discipline Streak
        achieved, message = self.check_discipline_streak_reward(user_id)
        status = "  ACHIEVED" if achieved else "  IN PROGRESS"
        print(f"  Discipline Streak: {status}")
        if not achieved:
            print(f"     {message}")
        
        # Consistency Champion
        achieved, message = self.check_consistency_champion_reward(user_id)
        status = "  ACHIEVED" if achieved else "  IN PROGRESS"
        print(f"  Consistency Champion: {status}")
        if not achieved:
            print(f"     {message}")
        
        # Display earned rewards
        rewards_data = self.get_user_rewards(user_id)
        
        print(f"\n  EARNED REWARDS")
        print("-" * 50)
        print(f"  Total Rewards Earned: {rewards_data['total_rewards']}")
        
        if rewards_data['reward_summary']:
            for reward_type, rewards in rewards_data['reward_summary'].items():
                print(f"\n{self._get_reward_icon(reward_type)} {reward_type} ({len(rewards)} times)")
                for reward in rewards[-3:]:  # Show last 3
                    date_achieved = datetime.strptime(reward['achieved_at'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
                    print(f"     {date_achieved}: {reward['description']}")
        else:
            print("  No rewards earned yet. Start tracking to earn rewards!")
        
        # Reward progress tips
        print(f"\n  REWARD TIPS")
        print("-" * 50)
        print("  Budget Master: Stay within all category budgets for a month")
        print("     Savings Hero: Save at least  5,000 in one month")
        print("  Discipline Streak: Log transactions for 7 consecutive days")
        print("  Consistency Champion: Maintain steady spending patterns")
    
    def _check_existing_reward(self, user_id, reward_type, month, year):
        """Check if reward already exists for given period"""
        rewards = self.db.get_rewards(user_id)
        
        for reward in rewards:
            if reward['reward_type'] == reward_type:
                reward_date = datetime.strptime(reward['achieved_at'], '%Y-%m-%d %H:%M:%S')
                
                if month and year:
                    # Check if reward was given in the same month
                    if reward_date.month == datetime.strptime(month, '%B').month and reward_date.year == year:
                        return True
                else:
                    # For streak rewards, check if given in last 30 days
                    if (datetime.now() - reward_date).days <= 30:
                        return True
        
        return False
    
    def _get_recent_transactions(self, user_id, days):
        """Get recent transactions for streak checking"""
        # This would need to be implemented based on the transaction database structure
        # For now, return empty list
        return []
    
    def _get_reward_icon(self, reward_type):
        """Get icon for reward type"""
        icons = {
            'Budget Master': ' ',
            'Savings Hero': '    ',
            'Discipline Streak': ' ',
            'Consistency Champion': ' '
        }
        return icons.get(reward_type, ' ')
    
    def _get_days_in_month(self, month, year):
        """Get number of days in a month"""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        else:  # February
            return 29 if (year % 400 == 0 or (year % 100 != 0 and year % 4 == 0)) else 28
