# 🧹 Housekeeping Reminder Notification System

## 📋 Overview
This system provides automated email notifications for housekeeping cleaning reminders. Users can set reminders via the AI Chat interface and receive email notifications when reminders are due.

## 🚀 Features

### ✅ Implemented Features
- **Immediate Confirmation Emails**: When users set reminders, they receive confirmation emails
- **Automated Daily Processing**: System checks and sends due reminders daily
- **Repeating Reminders**: Supports recurring reminders (15, 30, 60 days)
- **Custom Date Reminders**: One-time reminders for specific dates
- **Email Templates**: Professional email notifications with cleaning tips
- **API Integration**: RESTful endpoints for manual processing
- **Error Handling**: Robust error handling and logging

### 📧 Email Notifications
- **Confirmation Email**: Sent immediately when reminder is set
- **Reminder Email**: Sent on the due date
- **Professional Template**: Includes reminder details and booking links
- **Branding**: ExpertEase Housekeeping branding

## 🛠️ Setup Instructions

### 1. Prerequisites
- Backend server running on `localhost:5000`
- Email service configured (`email_service.py`)
- Database with users table containing email addresses
- Python 3.7+ with required packages

### 2. Configuration

#### Email Service Setup
Ensure `email_service.py` is properly configured with SMTP settings:

```python
# Example email_service.py configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USERNAME = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
```

#### Database Check
Verify the `users` table has an `email` column:
```sql
SELECT id, name, email FROM users LIMIT 5;
```

### 3. Manual Testing
Run the test script to verify everything works:

```bash
cd backend
python test_reminder_notifications.py
```

### 4. Automated Daily Processing

#### Option A: Manual Script
```bash
cd backend
python scripts/process_daily_reminders.py
```

#### Option B: Cron Job (Linux/Mac)
Add to crontab (`crontab -e`):
```bash
# Run daily at 9:00 AM
0 9 * * * cd /path/to/backend && python scripts/process_daily_reminders.py
```

#### Option C: Windows Task Scheduler
- Create a new task to run daily at 9:00 AM
- Action: `python scripts/process_daily_reminders.py`
- Start in: `backend` directory

## 📡 API Endpoints

### Set Reminder
```
POST /api/ai/set-reminder
Content-Type: application/json

{
  "user_id": 1,
  "reminder_type": "Deep Cleaning",
  "frequency_type": "30_days",
  "custom_date": "2024-01-15",
  "repeat": true
}
```

### Get User Reminders
```
GET /api/ai/get-reminders?user_id=1
```

### Process Due Reminders (Manual)
```
POST /api/ai/process-reminders
```

### Delete Reminder
```
POST /api/ai/delete-reminder
Content-Type: application/json

{
  "reminder_id": 123
}
```

## 🗂️ File Structure

```
backend/
├── services/housekeeping/arrival/backend/
│   ├── services/
│   │   └── ai_advisor_service.py     # Core reminder logic
│   └── controllers/
│       └── ai_advisor_controller.py  # API endpoints
├── scripts/
│   └── process_daily_reminders.py    # Daily scheduler script
├── test_reminder_notifications.py    # Test script
├── notification_service.py           # Email notification service
└── email_service.py                 # SMTP configuration
```

## 🔄 How It Works

### 1. User Sets Reminder
- User creates reminder via AI Chat
- System saves reminder to `cleaning_reminders` table
- **Immediate confirmation email** is sent to user

### 2. Daily Processing
- Scheduler runs `process_daily_reminders.py`
- Script calls `/api/ai/process-reminders` endpoint
- System finds all due reminders (`next_reminder_date <= today`)

### 3. Email Sending
- For each due reminder:
  - Gets user email from `users` table
  - Sends professional reminder email
  - Updates next reminder date (if repeating)
  - Deactivates non-repeating reminders

### 4. Repeat Logic
- **15_days**: Adds 15 days to next reminder date
- **30_days**: Adds 30 days to next reminder date  
- **60_days**: Adds 60 days to next reminder date
- **custom**: One-time reminder (deactivated after sending)

## 📊 Database Schema

### cleaning_reminders Table
```sql
CREATE TABLE cleaning_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reminder_type TEXT NOT NULL,
    frequency_type TEXT NOT NULL,
    next_reminder_date TEXT NOT NULL,
    repeat INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1
);
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Emails Not Sending
- Check `email_service.py` configuration
- Verify SMTP credentials and network connectivity
- Check notification logs in `notification.log`

#### 2. No User Email Found
- Verify `users` table has email addresses
- Check `get_user_email()` function in `ai_advisor_service.py`

#### 3. Reminders Not Processing
- Ensure backend server is running
- Check API endpoint: `POST /api/ai/process-reminders`
- Verify database connectivity

#### 4. Cron Job Not Working
- Check cron service status: `sudo service cron status`
- Verify script path and permissions
- Check cron logs: `grep CRON /var/log/syslog`

### Debug Mode
Enable debug logging by modifying the script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Monitoring

### Check System Status
```bash
# Test API endpoints
curl -X POST http://localhost:5000/api/ai/process-reminders

# Check recent reminders
sqlite3 data/housekeeping.db "SELECT * FROM cleaning_reminders WHERE is_active = 1 ORDER BY next_reminder_date DESC LIMIT 10;"
```

### Email Delivery Logs
```bash
# Check notification log
tail -f notification.log

# Look for recent email attempts
grep "Email" notification.log | tail -10
```

## 🔧 Customization

### Email Templates
Modify email content in `ai_advisor_service.py`:
- `set_reminder()` - Confirmation email template
- `process_due_reminders()` - Reminder email template

### Processing Schedule
Change the daily processing time in your cron job or task scheduler.

### Reminder Frequencies
Add new frequency types in `process_due_reminders()` function.

## 🚀 Deployment Checklist

- [ ] Email service configured and tested
- [ ] Database has user email addresses
- [ ] Test script runs successfully
- [ ] Daily scheduler script created
- [ ] Cron job/task scheduler set up
- [ ] Monitoring and logging in place
- [ ] Error handling tested
- [ ] Documentation updated

## 📞 Support

For issues with the notification system:
1. Check the troubleshooting section above
2. Review logs in `notification.log`
3. Run the test script to diagnose problems
4. Verify email service configuration

---

**ExpertEase Housekeeping** - Keeping spaces clean and healthy! 🌟
