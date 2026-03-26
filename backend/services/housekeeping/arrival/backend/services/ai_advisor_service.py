import sqlite3
from datetime import datetime, timedelta
from services.housekeeping.models.database import housekeeping_db
from notification_service import notify_user

class AIAdvisorService:
    def __init__(self):
        self.db = housekeeping_db
        self._ensure_schema()

    def _ensure_schema(self):
        """
        Create required tables for AI advisor if missing.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cleaning_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reminder_type TEXT NOT NULL,
                    frequency_type TEXT NOT NULL,
                    next_reminder_date TEXT NOT NULL,
                    repeat INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception:
            # Silent fail to avoid breaking page; operations will still error if schema invalid
            pass
        finally:
            conn.close()

    def get_cleaning_status(self, user_id):
        """
        1   GET /api/ai/cleaning-status
        Logic:
        - Fetch last COMPLETED booking for logged-in user.
        - Calculate days_passed and status.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()
        
        # Fetch last COMPLETED booking
        cursor.execute("""
            SELECT service_type, completed_at, booking_date 
            FROM bookings 
            WHERE user_id = ? AND status = 'COMPLETED'
            ORDER BY booking_date DESC LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()

        today = datetime.now().date()
        
        if not row:
            # No history
            return {
                "last_clean_date": "Never",
                "service_type": "None",
                "days_passed": 0,
                "next_suggested_date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                "status": "Recommended Soon", # Default prompt
                "hygiene_score": 5, # Default
                "recommendation": "Start your hygiene journey with a Deep Clean.",
                "seasonal_tip": self.get_seasonal_tip()
            }

        service_type = row[0]
        # Use completed_at if available, else booking_date
        completion_date_str = row[1] if row[1] else row[2]
        
        try:
            # Handle different date formats if necessary, assuming YYYY-MM-DD
            completion_date = datetime.strptime(completion_date_str.split(' ')[0], "%Y-%m-%d").date()
        except:
            completion_date = today # Fallback

        days_passed = (today - completion_date).days
        
        # Next Date Logic
        if "Deep" in service_type:
            next_date = completion_date + timedelta(days=30)
        else: # Basic or other
            next_date = completion_date + timedelta(days=15)
            
        # Status Logic
        if today > next_date:
            status = "Overdue"
        elif days_passed > 10:
            status = "Recommended Soon"
        else:
            status = "Good"

        # Hygiene Score Logic
        if days_passed <= 10:
            score = 9
            rec_text = "Excellent hygiene! Keep it up."
        elif days_passed <= 20:
            score = 7
            rec_text = "Good, but plan your next clean soon."
        else:
            score = 4
            rec_text = "Hygiene levels dropping. Book immediately."

        return {
            "last_clean_date": completion_date.strftime("%b %d"),
            "service_type": service_type,
            "days_passed": days_passed,
            "next_suggested_date": next_date.strftime("%b %d"),
            "status": status,
            "hygiene_score": score,
            "recommendation": rec_text,
            "seasonal_tip": self.get_seasonal_tip()
        }

    def get_seasonal_tip(self):
        """
        5   GET /api/ai/seasonal-tip
        """
        month = datetime.now().month
        
        if month in [10, 11]: # Oct, Nov
            return "Festival season is approaching. Consider Deep Cleaning for best hygiene results."
        elif month in [6, 7, 8]: # June-Aug (Monsoon)
            return "Monsoon brings humidity. Anti-fungal cleaning prevents mold growth."
        else:
            return "Regular dusting prevents respiratory allergies. Keep windows open for ventilation."

    def get_user_email(self, user_id):
        """
        Get user email from the main users table
        """
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting user email: {e}")
            return None

    def set_reminder(self, user_id, reminder_type, frequency_type, custom_date=None, repeat=False):
        """
        3   POST /api/ai/set-reminder
        Updated to support manual reminders with frequency and repeat toggle.
        """
        today = datetime.now().date()
        next_date = None

        if frequency_type == "custom" and custom_date:
             next_date = datetime.strptime(custom_date, "%Y-%m-%d").date()
        elif frequency_type == "15_days":
             next_date = today + timedelta(days=15)
        elif frequency_type == "30_days":
             next_date = today + timedelta(days=30)
        elif frequency_type == "60_days":
             next_date = today + timedelta(days=60)
        else:
             return None, "Invalid frequency type"

        next_date_str = next_date.strftime("%Y-%m-%d")
        
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            # Insert new reminder (do not deactivate old ones, as user can have multiple manual reminders)
            cursor.execute("""
                INSERT INTO cleaning_reminders (user_id, reminder_type, frequency_type, next_reminder_date, repeat, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (user_id, reminder_type, frequency_type, next_date_str, 1 if repeat else 0))
            
            conn.commit()
            
            # Send confirmation email
            user_email = self.get_user_email(user_id)
            if user_email:
                subject = f"🧹 Cleaning Reminder Set: {reminder_type}"
                body = f"""
Hello! 

Your cleaning reminder has been successfully set:

📅 Reminder Type: {reminder_type}
🗓️ Next Reminder Date: {next_date.strftime("%B %d, %Y")}
🔄 Repeats: {"Yes" if repeat else "No"}
⏰ Frequency: {frequency_type.replace('_', ' ').title()}

You'll receive a reminder email on the scheduled date. 
You can manage your reminders anytime in the Housekeeping AI Chat section.

Keep your space clean and healthy! 🌟

Best regards,
ExpertEase Housekeeping Team
                """
                try:
                    notify_user(user_email, subject, body.strip())
                    print(f"✅ Confirmation email sent to {user_email}")
                except Exception as email_error:
                    print(f"⚠️ Failed to send confirmation email: {email_error}")
            
            return next_date.strftime("%B %d, %Y"), "Reminder set successfully"
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()

    def get_user_reminders(self, user_id):
        """
        Fetch active manual reminders for the user.
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, reminder_type, frequency_type, next_reminder_date, repeat, is_active 
            FROM cleaning_reminders 
            WHERE user_id = ? AND is_active = 1
            ORDER BY next_reminder_date ASC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        reminders = []
        for row in rows:
            reminders.append({
                "id": row[0],
                "reminder_type": row[1],
                "frequency_type": row[2],
                "next_reminder_date": row[3],
                "repeat": bool(row[4]),
                "is_active": bool(row[5])
            })
        return reminders

    def delete_reminder(self, reminder_id):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE cleaning_reminders SET is_active = 0 WHERE id = ?", (reminder_id,))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def get_upgrade_suggestion(self, user_id):
        """
        4   GET /api/ai/upgrade-suggestion
        """
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT service_type FROM bookings 
            WHERE user_id = ? AND status = 'COMPLETED'
            ORDER BY booking_date DESC LIMIT 3
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 3:
            return {"show_upgrade": False}
            
        # Check if all 3 are basic/general
        all_basic = all(["Deep" not in r[0] for r in rows])
        
        if all_basic:
            return {
                "show_upgrade": True,
                "message": "You ve booked Basic Cleaning 3 times. Deep Cleaning is recommended for better hygiene."
            }
        
        return {"show_upgrade": False, "message": ""}

    def chat_with_ai(self, user_id, message):
        """
        AI Chat functionality for housekeeping assistance
        Returns intelligent responses to user queries
        """
        import re
        from datetime import datetime, timedelta
        
        # Convert message to lowercase for easier matching
        msg_lower = message.lower().strip()
        
        # Get user context for personalized responses
        try:
            user_context = self.get_cleaning_status(user_id)
            user_reminders = self.get_user_reminders(user_id)
        except:
            user_context = None
            user_reminders = []
        
        # Smart response patterns
        responses = {
            # Greetings
            r'hello|hi|hey|good morning|good evening': {
                'text': "Hello! I'm your ExpertEase Housekeeping Assistant! 🧹 I can help you with:\n\n• Booking cleaning services\n• Setting cleaning reminders\n• Checking your hygiene score\n• Getting cleaning tips\n• Price estimates\n\nHow can I assist you today?",
                'quick_replies': ['Book Cleaning', 'Check Hygiene Score', 'Set Reminder', 'Get Price Quote']
            },
            
            # Cleaning frequency advice
            r'how often|frequency|when should|regular cleaning': {
                'text': "Here's a recommended cleaning schedule:\n\n🏠 **General Cleaning**: Every 15 days\n🍳 **Kitchen**: Weekly\n🚿 **Bathroom**: Weekly\n🛋️ **Deep Cleaning**: Every 2-3 months\n\nBased on your hygiene score, I can give personalized recommendations. Would you like me to check your current cleaning status?",
                'quick_replies': ['Check My Status', 'Book Deep Cleaning', 'Set Weekly Reminder']
            },
            
            # Service types
            r'what services|service types|cleaning types|deep cleaning|basic cleaning': {
                'text': "We offer several cleaning services:\n\n🧹 **Basic Cleaning**\n• Dusting, sweeping, mopping\n• Kitchen & bathroom cleaning\n• ₹300-500\n\n🌟 **Deep Cleaning**\n• Everything in basic +\n• Inside cabinets, windows, fans\n• Stain removal, sanitization\n• ₹800-1200\n\n🏢 **Post-Construction**\n• Complete cleanup after renovation\n• Starting from ₹1500\n\nWhich service interests you?",
                'quick_replies': ['Book Basic Cleaning', 'Book Deep Cleaning', 'Get Price Quote', 'Compare Services']
            },
            
            # Booking related
            r'book|schedule|appointment|available': {
                'text': "I can help you book a cleaning service! 📅\n\nTo proceed, I'll need:\n• Preferred date and time\n• Service type (Basic/Deep)\n• Your address\n\nOr you can visit the booking section for real-time availability. Would you like me to check available slots?",
                'quick_replies': ['Check Availability', 'Book Basic - ₹300', 'Book Deep - ₹800', 'View Calendar']
            },
            
            # Pricing
            r'price|cost|rates|how much|charge': {
                'text': "💰 **Our Pricing:**\n\n🧹 **Basic Cleaning**: ₹300-500\n• 1-2 BHK: ₹300\n• 3 BHK: ₹400\n• 4+ BHK: ₹500\n\n🌟 **Deep Cleaning**: ₹800-1200\n• 1-2 BHK: ₹800\n• 3 BHK: ₹1000\n• 4+ BHK: ₹1200\n\n🏢 **Post-Construction**: Starting ₹1500\n\nPrices vary based on size and condition. Want a precise quote?",
                'quick_replies': ['Get Exact Quote', 'Book Basic Cleaning', 'Book Deep Cleaning']
            },
            
            # Hygiene score
            r'hygiene score|my score|cleaning score|how clean': {
                'text': f"Let me check your current hygiene score... 📊\n\n{user_context['recommendation'] if user_context else 'Please check your cleaning status first.'}\n\nYour score updates after each cleaning. Regular cleaning helps maintain high scores!",
                'quick_replies': ['Book Cleaning Now', 'View My Bookings', 'Set Cleaning Reminder']
            },
            
            # Reminders
            r'remind|reminder|notify|alert': {
                'text': "I can set up cleaning reminders for you! ⏰\n\nOptions:\n• Every 15 days (Regular)\n• Every 30 days (Monthly)\n• Every 60 days (Bi-monthly)\n• Custom date\n\nYou'll get email notifications! When would you like to be reminded?",
                'quick_replies': ['Set 15-Day Reminder', 'Set 30-Day Reminder', 'Set Custom Date', 'View My Reminders']
            },
            
            # Tips and advice
            r'tips|advice|how to|best way|clean properly': {
                'text': "🧼 **Expert Cleaning Tips:**\n\n🏠 **Daily**: Make bed, wipe surfaces\n📅 **Weekly**: Vacuum, mop, clean bathroom\n🗓️ **Monthly**: Deep clean kitchen, wash windows\n🌟 **Seasonal**: Professional deep cleaning\n\n💡 **Pro Tip**: Clean top to bottom, dry to wet!\n\nNeed specific tips for any area?",
                'quick_replies': ['Kitchen Tips', 'Bathroom Tips', 'Bedroom Tips', 'Book Professional']
            },
            
            # Emergency/urgent
            r'urgent|emergency|asap|today|now': {
                'text': "For urgent cleaning needs, I recommend:\n\n🚀 **Express Service** (Same day)\n• Available in major cities\n• Additional 20% charge\n• Call: 📞 1800-CLEAN-NOW\n\nOr check if we have same-day slots available. Should I check availability for today?",
                "quick_replies": ["Check Today's Slots", "Call Emergency", "Book Tomorrow", "Regular Booking"]
            },
            
            # Payment
            r'payment|pay|cash|card|online': {
                'text': "💳 **Payment Options:**\n\n• **Cash** - Pay after service\n• **Card** - Credit/Debit accepted\n• **UPI** - GPay, PhonePe, PayTM\n• **Online** - Pay during booking\n\nPayment is only confirmed after service completion. Pay directly to the service provider!",
                'quick_replies': ['Book Now Pay Later', 'Pay Online', 'Cash on Service']
            }
        }
        
        # Check for matching patterns
        for pattern, response in responses.items():
            if re.search(pattern, msg_lower):
                return {
                    'message': response['text'],
                    'quick_replies': response['quick_replies'],
                    'type': 'text'
                }
        
        # Context-aware responses
        if user_context:
            days_ago = user_context.get('days_ago', 0)
            if days_ago > 30:
                return {
                    'message': f"I notice it's been {days_ago} days since your last cleaning. Your hygiene score is {user_context.get('hygiene_score', 'N/A')}/10. Would you like to book a cleaning service? I can help you find available slots! 📅",
                    'quick_replies': ['Book Cleaning Now', 'Check Availability', 'Set Reminder', 'View My Status'],
                    'type': 'text'
                }
        
        # Default response
        return {
            'message': "I'm here to help with your housekeeping needs! 🧹\n\nI can assist with:\n• Booking cleaning services\n• Setting reminders\n• Checking your hygiene score\n• Getting cleaning tips\n• Price estimates\n\nWhat would you like to know?",
            'quick_replies': ['Book Cleaning', 'Check Hygiene Score', 'Set Reminder', 'Get Price Quote'],
            'type': 'text'
        }

    def process_due_reminders(self):
        """
        Process and send notifications for due reminders
        This function should be called daily (via cron job or scheduler)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        processed_count = 0
        
        conn = self.db.get_conn()
        cursor = conn.cursor()
        
        try:
            # Get all due reminders
            cursor.execute("""
                SELECT id, user_id, reminder_type, frequency_type, next_reminder_date, repeat
                FROM cleaning_reminders 
                WHERE next_reminder_date <= ? AND is_active = 1
                ORDER BY next_reminder_date ASC
            """, (today,))
            
            due_reminders = cursor.fetchall()
            
            for reminder in due_reminders:
                reminder_id, user_id, reminder_type, frequency_type, next_date, repeat = reminder
                
                # Get user email
                user_email = self.get_user_email(user_id)
                
                if user_email:
                    # Send reminder email
                    subject = f"🧹 Cleaning Reminder: {reminder_type}"
                    body = f"""
Hello! 

This is your friendly cleaning reminder:

📅 Reminder Type: {reminder_type}
🗓️ Scheduled Date: {datetime.strptime(next_date, "%Y-%m-%d").strftime("%B %d, %Y")}
⏰ Frequency: {frequency_type.replace('_', ' ').title()}

Time to keep your space clean and healthy! 🌟

You can book a cleaning service through the ExpertEase platform or manage your reminders in the Housekeeping AI Chat section.

Best regards,
ExpertEase Housekeeping Team
                    """
                    
                    try:
                        notify_user(user_email, subject, body.strip())
                        print(f"✅ Reminder email sent to {user_email} for {reminder_type}")
                        
                        # Update next reminder date if it's a repeating reminder
                        if repeat:
                            if frequency_type == "15_days":
                                next_reminder = datetime.strptime(next_date, "%Y-%m-%d") + timedelta(days=15)
                            elif frequency_type == "30_days":
                                next_reminder = datetime.strptime(next_date, "%Y-%m-%d") + timedelta(days=30)
                            elif frequency_type == "60_days":
                                next_reminder = datetime.strptime(next_date, "%Y-%m-%d") + timedelta(days=60)
                            else:
                                next_reminder = None
                            
                            if next_reminder:
                                cursor.execute("""
                                    UPDATE cleaning_reminders 
                                    SET next_reminder_date = ? 
                                    WHERE id = ?
                                """, (next_reminder.strftime("%Y-%m-%d"), reminder_id))
                        else:
                            # Deactivate non-repeating reminders
                            cursor.execute("UPDATE cleaning_reminders SET is_active = 0 WHERE id = ?", (reminder_id,))
                        
                        processed_count += 1
                        
                    except Exception as email_error:
                        print(f"⚠️ Failed to send reminder email to {user_email}: {email_error}")
                else:
                    print(f"⚠️ No email found for user {user_id}")
            
            conn.commit()
            print(f"📊 Processed {processed_count} due reminders")
            return {"processed": processed_count, "total_due": len(due_reminders)}
            
        except Exception as e:
            print(f"❌ Error processing reminders: {e}")
            return {"processed": 0, "error": str(e)}
        finally:
            conn.close()
        
        return {"show_upgrade": False}
