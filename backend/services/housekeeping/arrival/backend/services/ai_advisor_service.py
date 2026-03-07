import sqlite3
from datetime import datetime, timedelta
from services.housekeeping.models.database import housekeeping_db

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
        1️⃣ GET /api/ai/cleaning-status
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
        5️⃣ GET /api/ai/seasonal-tip
        """
        month = datetime.now().month
        
        if month in [10, 11]: # Oct, Nov
            return "Festival season is approaching. Consider Deep Cleaning for best hygiene results."
        elif month in [6, 7, 8]: # June-Aug (Monsoon)
            return "Monsoon brings humidity. Anti-fungal cleaning prevents mold growth."
        else:
            return "Regular dusting prevents respiratory allergies. Keep windows open for ventilation."

    def set_reminder(self, user_id, reminder_type, frequency_type, custom_date=None, repeat=False):
        """
        3️⃣ POST /api/ai/set-reminder
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
        4️⃣ GET /api/ai/upgrade-suggestion
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
                "message": "You’ve booked Basic Cleaning 3 times. Deep Cleaning is recommended for better hygiene."
            }
        
        return {"show_upgrade": False}
