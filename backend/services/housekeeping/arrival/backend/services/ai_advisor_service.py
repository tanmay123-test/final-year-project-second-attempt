import sqlite3
from datetime import datetime, timedelta
from services.housekeeping.models.database import housekeeping_db
from notification_service import notify_user
from ai.gemini_client import GeminiClient

class AIAdvisorService:
    def __init__(self):
        self.db = housekeeping_db
        self.gemini_client = GeminiClient()
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

    def chat_with_ai(self, user_id: str, message: str):
        try:
            prompt = f"""You are a smart home assistant for a housekeeping service app. 
The user has asked: "{message}" 

Respond helpfully and specifically to exactly what they asked. 
- If it is a recipe request, give the actual recipe with ingredients and steps. 
- If it is a cleaning problem, give specific cleaning solution for that exact problem. 
- If it is a home hack or tip, give practical actionable advice. 
- If it relates to booking a service, recommend the most relevant housekeeping service. 

Detect and return the mode as one of: cooking, cleaning, general, service. 
Format your response clearly with numbered steps where applicable. 
Use **bold** for key terms. Add a 💡 Pro tip at the end where relevant. 
Keep response concise and practical.""" 

            response_text = self.gemini_client.generate_response(prompt)

            # Detect mode from message content 
            lower = message.lower() 
            if any(word in lower for word in ["recipe", "cook", "make", "food", "dish", "ingredients"]): 
                mode = "cooking" 
            elif any(word in lower for word in ["clean", "stain", "wash", "scrub", "remove", "dirt", "dust"]): 
                mode = "cleaning" 
            elif any(word in lower for word in ["book", "service", "dirty", "schedule", "hire"]): 
                mode = "service" 
            else: 
                mode = "general" 

            # Secondary fallback if Gemini is hitting rate limits (429)
            if "too many requests" in response_text.lower() or "technical difficulties" in response_text.lower():
                # Specialized fallback based on query content
                if any(word in lower for word in ["coffee", "tea", "drink"]):
                    response_text = "**Coffee Stain Removal** ☕\n\n1. Blot the stain with a **dry cloth** (don't rub!)\n2. Mix **dish soap, white vinegar, & water**\n3. Sponge the solution onto the stain\n4. Blot until the liquid is absorbed\n5. Rinse with cold water and dry\n\n💡 *Pro tip: Act fast! Fresh stains are 90% easier to remove.*"
                elif any(word in lower for word in ["carpet", "rug"]):
                    response_text = "**Carpet Cleaning Tip** 🧹\n\n1. Sprinkle **baking soda** over the area\n2. Let it sit for 15-20 minutes\n3. Vacuum thoroughly\n4. For stains, use a dedicated carpet cleaner\n\n💡 *Pro tip: Vacuum in multiple directions!*"
                elif mode == "cleaning":
                    response_text = "**General Cleaning Tips** 🧹\n\n1. Use **microfiber cloths** for dust\n2. Clean from **top to bottom**\n3. Let cleaners sit for 5-10 mins to work\n4. Open windows for ventilation\n\n💡 *Pro tip: A tidy home leads to a tidy mind!*"
                elif mode == "cooking":
                    response_text = "**Quick Cooking Tip** 🍳\n\n1. Prep all ingredients before starting (**Mise en place**)\n2. Keep your knives sharp for safety\n3. Season as you go, not just at the end\n4. Use a timer to avoid overcooking\n\n💡 *Pro tip: Fresh herbs make any dish better!*"
                elif mode == "service":
                    response_text = "**Recommended Services** 🛎\n\nBased on your home needs:\n• **Kitchen Deep Cleaning** — HIGH priority\n• **Chimney Cleaning** — MEDIUM priority\n• **Bathroom Scrub** — MEDIUM priority\n\n💡 *Tap Book Now to schedule any service!*"
                else:
                    response_text = "**Home Management Tip** 🏠\n\n1. Declutter one drawer a day\n2. Set a 15-minute timer for daily tidy-up\n3. Use vertical space for storage\n4. Label your storage boxes\n\n💡 *Pro tip: Less is more!*"

            return { 
                "response": response_text, 
                "mode": mode 
            } 

        except Exception as e: 
            print(f"Chat error: {e}")
            return { 
                "response": "Sorry, I couldn't process your request right now. Please try again.", 
                "mode": "general" 
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
