import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationService:
    """Handle goal notifications and email alerts"""
    
    def __init__(self):
        self.conn = sqlite3.connect('expertease.db')
        self.conn.row_factory = sqlite3.Row
        self.setup_email_config()
    
    def setup_email_config(self):
        """Setup email configuration"""
        # These should be configured based on your email service
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "your-email@gmail.com"
        self.smtp_password = "your-app-password"
        self.from_email = "your-email@gmail.com"
    
    def schedule_goal_notifications(self, user_id, goal_id):
        """Schedule notifications for a goal"""
        cursor = self.conn.cursor()
        
        # Get goal details
        cursor.execute("""
        SELECT * FROM goal_jars 
        WHERE id=? AND user_id=?
        """, (goal_id, user_id))
        
        goal = cursor.fetchone()
        
        if not goal:
            return False
        
        target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d') if goal['target_date'] else None
        
        # Schedule different types of notifications
        
        # 1. Goal deadline reminder (7 days before)
        if target_date:
            reminder_date = target_date - timedelta(days=7)
            if reminder_date > datetime.now():
                self.goal_engine.schedule_goal_notification(
                    user_id, goal_id, 'deadline_reminder',
                    f"Your goal '{goal['goal_name']}' deadline is approaching! 7 days remaining.",
                    reminder_date.strftime('%Y-%m-%d')
                )
        
        # 2. Monthly progress update (1st of each month)
        next_month = datetime.now().replace(day=1) + timedelta(days=32)
        for i in range(6):  # Schedule for next 6 months
            progress_date = next_month + timedelta(days=i*30)
            self.goal_engine.schedule_goal_notification(
                user_id, goal_id, 'monthly_progress',
                f"Monthly progress update for '{goal['goal_name']}': {goal['progress_percentage']:.1f}% complete.",
                progress_date.strftime('%Y-%m-%d')
            )
        
        # 3. Goal achievement celebration
        if target_date:
            achievement_date = target_date
            self.goal_engine.schedule_goal_notification(
                user_id, goal_id, 'goal_achievement',
                f"  Congratulations! You've achieved your goal '{goal['goal_name']}'! Total saved:  {goal['target_amount']:.2f}",
                achievement_date.strftime('%Y-%m-%d')
            )
        
        return True
    
    def send_email_notification(self, to_email, subject, message):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            body = MIMEText(message, 'plain')
            msg.attach(body)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def get_user_email(self, user_id):
        """Get user's email address"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT email FROM users WHERE id=?", (user_id,))
        result = cursor.fetchone()
        return result['email'] if result else None
    
    def process_pending_notifications(self):
        """Process all pending notifications"""
        cursor = self.conn.cursor()
        
        # Get all users with pending notifications
        cursor.execute("""
        SELECT DISTINCT user_id FROM goal_notifications 
        WHERE is_sent=0 AND scheduled_date <= date('now')
        """)
        
        users = cursor.fetchall()
        
        for user in users:
            user_id = user['user_id']
            
            # Get notifications for this user
            notifications = self.goal_engine.get_pending_notifications(user_id)
            
            if notifications:
                user_email = self.get_user_email(user_id)
                
                for notification in notifications:
                    # Send email notification
                    if user_email:
                        subject = f"Goal Jar Notification: {notification['notification_type'].replace('_', ' ').title()}"
                        success = self.send_email_notification(
                            user_email, subject, notification['message']
                        )
                        
                        if success:
                            print(f"  Email sent to {user_email} for notification {notification['id']}")
                        else:
                            print(f"  Failed to send email to {user_email}")
                    
                    # Mark as sent
                    self.goal_engine.mark_notification_sent(notification['id'])
        
        return len(users)
    
    def create_deadline_notifications(self, user_id):
        """Create notifications for approaching deadlines"""
        cursor = self.conn.cursor()
        
        # Get goals with deadlines in next 30 days
        thirty_days_from_now = datetime.now() + timedelta(days=30)
        cursor.execute("""
        SELECT * FROM goal_jars 
        WHERE user_id=? AND target_date BETWEEN date('now') AND ?
        AND target_date > date('now')
        """, (user_id, thirty_days_from_now.strftime('%Y-%m-%d')))
        
        goals = cursor.fetchall()
        
        for goal in goals:
            target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
            days_remaining = (target_date - datetime.now()).days
            
            if days_remaining <= 7 and days_remaining > 0:
                # Urgent notification
                self.goal_engine.schedule_goal_notification(
                    user_id, goal['id'], 'urgent_deadline',
                    f"  URGENT: Your goal '{goal['goal_name']}' deadline is in {days_remaining} days!",
                    datetime.now().strftime('%Y-%m-%d')
                )
            elif days_remaining <= 14:
                # Warning notification
                self.goal_engine.schedule_goal_notification(
                    user_id, goal['id'], 'deadline_warning',
                    f"   Reminder: Your goal '{goal['goal_name']}' deadline is in {days_remaining} days.",
                    datetime.now().strftime('%Y-%m-%d')
                )
        
        return len(goals)
    
    def create_milestone_notifications(self, user_id):
        """Create milestone notifications for goal progress"""
        cursor = self.conn.cursor()
        
        # Get goals with progress > 25%
        cursor.execute("""
        SELECT * FROM goal_jars 
        WHERE user_id=? AND current_amount > 0
        AND (current_amount / target_amount) >= 0.25
        """, (user_id,))
        
        goals = cursor.fetchall()
        
        for goal in goals:
            progress = (goal['current_amount'] / goal['target_amount']) * 100
            
            # Milestone notifications
            milestones = [25, 50, 75, 90]
            
            for milestone in milestones:
                if progress >= milestone and progress < milestone + 5:  # Within 5% of milestone
                    self.goal_engine.schedule_goal_notification(
                        user_id, goal['id'], 'milestone',
                        f"  Great progress! You've reached {milestone}% of your goal '{goal['goal_name']}'!",
                        datetime.now().strftime('%Y-%m-%d')
                    )
        
        return len(goals)
    
    def get_notification_summary(self, user_id):
        """Get summary of notifications for a user"""
        cursor = self.conn.cursor()
        
        # Get notification counts
        cursor.execute("""
        SELECT 
            notification_type,
            COUNT(*) as count,
            MAX(created_at) as last_created
        FROM goal_notifications 
        WHERE user_id=?
        GROUP BY notification_type
        """, (user_id,))
        
        notification_stats = cursor.fetchall()
        
        # Get pending notifications
        pending_count = len(self.goal_engine.get_pending_notifications(user_id))
        
        return {
            'notification_stats': notification_stats,
            'pending_count': pending_count,
            'total_scheduled': sum(stat['count'] for stat in notification_stats)
        }
