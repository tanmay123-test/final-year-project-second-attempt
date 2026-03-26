from .goal_engine import GoalEngine
from .goal_simulator import GoalSimulator
from .goal_progress import GoalProgress
from .notification_service import NotificationService
from datetime import datetime, timedelta

class SmartG:
    """Main interface for Smart Goal Jar"""
    
    def __init__(self):
        self.goal_engine = GoalEngine()
        self.goal_simulator = GoalSimulator()
        self.goal_progress = GoalProgress()
        self.notification_service = NotificationService()
    
    def show_menu(self, user_id):
        """Main menu for Smart Goal Jar"""
        while True:
            print("\n" + "="*70)
            print("  SMART GOAL JAR")
            print("="*70)
            print("1.   Create New Goal")
            print("2.   View All Goals")
            print("3.   Add Savings to Goal")
            print("4.   Goal Progress Tracker")
            print("5.   Goal Timeline Simulation")
            print("6.   Savings Growth Projection")
            print("7.   Transfer Leftover Budget")
            print("8.   Goal Acceleration Insights")
            print("9.   Goal Notifications")
            print("10.    Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._create_new_goal(user_id)
            elif choice == "2":
                self._view_all_goals(user_id)
            elif choice == "3":
                self._add_savings_to_goal(user_id)
            elif choice == "4":
                self._track_goal_progress(user_id)
            elif choice == "5":
                self._simulate_goal_timeline(user_id)
            elif choice == "6":
                self._project_savings_growth(user_id)
            elif choice == "7":
                self._transfer_leftover_budget(user_id)
            elif choice == "8":
                self._get_acceleration_insights(user_id)
            elif choice == "9":
                self._manage_notifications(user_id)
            elif choice == "10":
                return
            else:
                print("  Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def _create_new_goal(self, user_id):
        """Create a new goal"""
        print("\n" + "="*60)
        print("  CREATE NEW GOAL")
        print("="*60)
        
        try:
            # Get goal details
            goal_name = input("  Enter goal name: ").strip()
            target_amount = float(input("  Enter target amount:  "))
            monthly_contribution = float(input("  Enter monthly contribution:  "))
            
            # Optional target date
            target_date_input = input("  Enter target date (YYYY-MM-DD) or press Enter for auto-calculation: ").strip()
            target_date = target_date_input if target_date_input else None
            
            # Validate inputs
            if target_amount <= 0 or monthly_contribution <= 0:
                print("  Target amount and monthly contribution must be positive")
                return
            
            # Calculate feasibility
            feasibility = self.goal_simulator.calculate_goal_feasibility(
                target_amount, monthly_contribution, target_date
            )
            
            if feasibility['feasible']:
                # Create the goal
                goal_id = self.goal_engine.create_goal(
                    user_id, goal_name, target_amount, monthly_contribution, target_date
                )
                
                print(f"\n  Goal '{goal_name}' created successfully!")
                print(f"  Goal ID: {goal_id}")
                
                # Schedule notifications
                self.notification_service.schedule_goal_notifications(user_id, goal_id)
                
            else:
                print(f"\n  Goal creation failed. Please review the recommendations:")
                for rec in feasibility['recommendations']:
                    print(f"     {rec}")
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _view_all_goals(self, user_id):
        """View all goals"""
        self.goal_progress.display_goal_dashboard(user_id)
    
    def _add_savings_to_goal(self, user_id):
        """Add savings to a specific goal"""
        print("\n" + "="*60)
        print("  ADD SAVINGS TO GOAL")
        print("="*60)
        
        try:
            # Get user's goals
            goals = self.goal_engine.get_user_goals(user_id)
            
            if not goals:
                print("  No goals found. Create a goal first.")
                return
            
            # Display goals for selection
            print(f"\n  YOUR GOALS:")
            for i, goal in enumerate(goals, 1):
                status = self.goal_progress._get_goal_status(goal)
                print(f"{i}. {goal['goal_name']} - {status} ( {goal['current_amount']:,.2f}/ {goal['target_amount']:,.2f})")
            
            # Select goal
            try:
                idx = int(input("\n  Select goal number: ")) - 1
                if 0 <= idx < len(goals):
                    selected_goal = goals[idx]
                    goal_id = selected_goal['id']
                else:
                    print("  Invalid selection")
                    return
            except ValueError:
                print("  Please enter a valid number")
                return
            
            # Get amount to add
            amount = float(input(f"  Enter amount to add to '{selected_goal['goal_name']}':  "))
            
            if amount <= 0:
                print("  Amount must be positive")
                return
            
            # Payment method
            print("\n  Payment Method:")
            print("1.   Online Payment")
            print("2.   Cash Deposit")
            print("3.   Bank Transfer")
            
            payment_choice = input("Select payment method (1-3): ").strip()
            payment_methods = {'1': 'online', '2': 'cash', '3': 'bank_transfer'}
            payment_method = payment_methods.get(payment_choice, 'manual')
            
            notes = input("  Add notes (optional): ").strip()
            
            # Add savings
            success = self.goal_engine.add_savings(
                user_id, goal_id, amount, payment_method, notes
            )
            
            if success:
                print(f"\n  Successfully added  {amount:.2f} to '{selected_goal['goal_name']}'")
                print(f"  Payment Method: {payment_method}")
                
                # Update progress
                updated_goal = self.goal_engine.get_goal_progress(user_id, goal_id)
                if updated_goal:
                    print(f"  New Progress: {updated_goal['progress_percentage']:.1f}%")
                    print(f"  New Total:  {updated_goal['current_amount']:,.2f}")
            else:
                print("  Failed to add savings")
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _track_goal_progress(self, user_id):
        """Track progress for a specific goal"""
        print("\n" + "="*60)
        print("  GOAL PROGRESS TRACKER")
        print("="*60)
        
        try:
            # Get user's goals
            goals = self.goal_engine.get_user_goals(user_id)
            
            if not goals:
                print("  No goals found")
                return
            
            # Display goals for selection
            print(f"\n  YOUR GOALS:")
            for i, goal in enumerate(goals, 1):
                status = self.goal_progress._get_goal_status(goal)
                print(f"{i}. {goal['goal_name']} - {status}")
            
            # Select goal
            try:
                choice = int(input("\n  Select goal to track: ")) - 1
                if 1 <= choice <= len(goals):
                    goal_id = goals[choice - 1]['id']
                else:
                    print("  Invalid selection")
                    return
            except ValueError:
                print("  Please enter a valid number")
                return
            
            # Display detailed progress
            self.goal_progress.display_single_goal_progress(user_id, goal_id)
            
        except Exception as e:
            print(f"  Error: {e}")
    
    def _simulate_goal_timeline(self, user_id):
        """Simulate goal timeline scenarios"""
        print("\n" + "="*60)
        print("  GOAL TIMELINE SIMULATION")
        print("="*60)
        
        try:
            # Get existing goal for reference
            goals = self.goal_engine.get_user_goals(user_id)
            
            if goals:
                print("  Use existing goal as reference:")
                for i, goal in enumerate(goals[:3], 1):  # Show first 3 goals
                    print(f"{i}. {goal['goal_name']} ( {goal['target_amount']:,.2f})")
            
            # Get simulation parameters
            target_amount = float(input("\n  Enter target amount:  "))
            monthly_contribution = float(input("  Enter monthly contribution:  "))
            
            if target_amount <= 0 or monthly_contribution <= 0:
                print("  Invalid input values")
                return
            
            # Run simulation
            timelines = self.goal_simulator.simulate_goal_timeline(target_amount, monthly_contribution)
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _project_savings_growth(self, user_id):
        """Project savings growth over time"""
        print("\n" + "="*60)
        print("  SAVINGS GROWTH PROJECTION")
        print("="*60)
        
        try:
            # Get user's goals
            goals = self.goal_engine.get_user_goals(user_id)
            
            if not goals:
                print("  No goals found")
                return
            
            # Display goals for selection
            print(f"\n  YOUR GOALS:")
            for i, goal in enumerate(goals, 1):
                progress = self.goal_progress._get_goal_status(goal)
                print(f"{i}. {goal['goal_name']} - {progress}")
            
            # Select goal
            try:
                choice = int(input("\n  Select goal to project: ")) - 1
                if 1 <= choice <= len(goals):
                    goal_id = goals[choice - 1]['id']
                else:
                    print("  Invalid selection")
                    return
            except ValueError:
                print("  Please enter a valid number")
                return
            
            # Get projection period
            try:
                months = int(input("\n  Enter projection period in months (default 24): ") or "24")
            except ValueError:
                months = 24
            
            # Generate projection
            projections = self.goal_simulator.project_savings_growth(user_id, goal_id, months)
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _transfer_leftover_budget(self, user_id):
        """Transfer leftover budget to goals"""
        print("\n" + "="*60)
        print("  TRANSFER LEFTOVER BUDGET")
        print("="*60)
        
        try:
            # Get user's goals
            goals = self.goal_engine.get_user_goals(user_id)
            
            if not goals:
                print("  No goals found. Create a goal first.")
                return
            
            # Display goals for selection
            print(f"\n  YOUR GOALS:")
            for i, goal in enumerate(goals, 1):
                print(f"{i}. {goal['goal_name']} (Target:  {goal['target_amount']:,.2f})")
            
            # Select goal
            try:
                choice = int(input("\n  Select goal to transfer to: ")) - 1
                if 1 <= choice <= len(goals):
                    goal_id = goals[choice - 1]['id']
                    selected_goal = goals[choice - 1]
                else:
                    print("  Invalid selection")
                    return
            except ValueError:
                print("  Please enter a valid number")
                return
            
            # Get transfer details
            amount = float(input(f"  Enter amount to transfer to '{selected_goal['goal_name']}':  "))
            
            if amount <= 0:
                print("  Amount must be positive")
                return
            
            # Get source category
            print("\n  Source Categories:")
            print("1.   Food & Dining")
            print("2.   Transport")
            print("3.   Shopping")
            print("4.   Entertainment")
            print("5.   Other")
            
            try:
                category_choice = int(input("Select source category (1-5): ")) - 1
                categories = ['Food & Dining', 'Transport', 'Shopping', 'Entertainment', 'Other']
                if 1 <= category_choice <= len(categories):
                    source_category = categories[category_choice - 1]
                else:
                    print("  Invalid selection")
                    return
            except ValueError:
                print("  Please enter a valid number")
                return
            
            # Perform transfer
            success = self.goal_engine.transfer_leftover_to_goal(user_id, goal_id, amount, source_category)
            
            if success:
                print(f"\n  Successfully transferred  {amount:.2f} from {source_category} to '{selected_goal['goal_name']}'")
                
                # Update goal progress
                updated_goal = self.goal_engine.get_goal_progress(user_id, goal_id)
                if updated_goal:
                    print(f"  New Progress: {updated_goal['progress_percentage']:.1f}%")
                    print(f"  New Total:  {updated_goal['current_amount']:,.2f}")
            else:
                print("  Transfer failed")
            
        except ValueError:
            print("  Please enter valid numeric values")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _get_acceleration_insights(self, user_id):
        """Get goal acceleration suggestions"""
        print("\n" + "="*60)
        print("  GOAL ACCELERATION INSIGHTS")
        print("="*60)
        
        try:
            suggestions = self.goal_engine.get_goal_acceleration_suggestions(user_id)
            
            if not suggestions:
                print("  No acceleration suggestions available")
                return
            
            print(f"\n  SPENDING REDUCTION OPPORTUNITIES:")
            print("-" * 60)
            
            for suggestion in suggestions:
                print(f"\n  {suggestion['category'].upper()}:")
                print(f"     Current Monthly Avg:  {suggestion['current_monthly_avg']:,.2f}")
                print(f"     Suggested Monthly:  {suggestion['suggested_monthly']:,.2f}")
                print(f"     Monthly Savings:  {suggestion['monthly_savings']:,.2f}")
                print(f"     Strategy: {suggestion['strategy']}")
            
            print(f"\n  RECOMMENDATIONS:")
            print("-" * 60)
            print("     Implement the suggested reductions to accelerate your goals")
            print("     Track your spending weekly to identify patterns")
            print("     Set up automatic transfers to your goal jars")
            print("     Review and adjust your goals monthly")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    def _manage_notifications(self, user_id):
        """Manage goal notifications"""
        print("\n" + "="*60)
        print("  GOAL NOTIFICATIONS")
        print("="*60)
        
        try:
            # Get notification summary
            summary = self.notification_service.get_notification_summary(user_id)
            
            print(f"\n  NOTIFICATION SUMMARY:")
            print(f"     Total Scheduled: {summary['total_scheduled']}")
            print(f"     Pending: {summary['pending_count']}")
            
            if summary['notification_stats']:
                print(f"\n  NOTIFICATION TYPES:")
                print("-" * 60)
                for stat in summary['notification_stats']:
                    print(f"     {stat['notification_type'].replace('_', ' ').title()}: {stat['count']} notifications")
                    print(f"     Last Created: {stat['last_created']}")
            
            # Notification options
            print(f"\n  NOTIFICATION OPTIONS:")
            print("1.   Schedule Deadline Reminders")
            print("2.   Schedule Milestone Notifications")
            print("3.   Process Pending Notifications")
            print("4.    Back")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._schedule_deadline_notifications(user_id)
            elif choice == "2":
                self._schedule_milestone_notifications(user_id)
            elif choice == "3":
                count = self.notification_service.process_pending_notifications()
                print(f"\n  Processed {count} notifications")
            elif choice == "4":
                return
            else:
                print("  Invalid choice")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    def _schedule_deadline_notifications(self, user_id):
        """Schedule deadline notifications for all goals"""
        try:
            count = self.notification_service.create_deadline_notifications(user_id)
            print(f"\n  Scheduled {count} deadline notifications")
        except Exception as e:
            print(f"  Error: {e}")
    
    def _schedule_milestone_notifications(self, user_id):
        """Schedule milestone notifications for all goals"""
        try:
            count = self.notification_service.create_milestone_notifications(user_id)
            print(f"\n  Scheduled milestone notifications for {count} goals")
        except Exception as e:
            print(f"  Error: {e}")
