# 🚀 EXPERTISE SUBSCRIPTION SYSTEM IMPLEMENTATION PROMPT

## 📋 CURRENT STATE ANALYSIS

### ✅ What's Already Implemented (CLI Side):
- Complete subscription menu interface in `cli.py`
- Subscription plan viewing (`view_subscription_plans()`)
- Subscription purchasing (`subscribe_to_plan()`)
- Usage statistics (`view_subscription_stats()`)
- Subscription cancellation (`cancel_subscription()`)
- Payment integration with Razorpay

### ✅ What's Already Implemented (Payment Folder):
- Basic payment database structure (`payment_db.py`)
- Razorpay service integration (`razor_service.py`)
- Webhook handler (`webhook_handler.py`)
- Payment routes (`payment_route.py`)
- Database schema (`create_db.py`)

### ❌ What's Missing (Backend API):
- **No subscription API endpoints in main `app.py`**
- **No subscription database tables**
- **No subscription plan management**
- **No usage tracking system**
- **No subscription payment processing**

## 🎯 IMPLEMENTATION PLAN

### Phase 1: Database Schema & Models

#### 1.1 Create Subscription Database Tables
```sql
-- Subscription Plans Table
CREATE TABLE subscription_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    duration_days INTEGER NOT NULL,
    max_appointments_per_day INTEGER NOT NULL,
    features TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Worker Subscriptions Table
CREATE TABLE worker_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    status TEXT DEFAULT 'active',
    razorpay_subscription_id TEXT,
    auto_renew BOOLEAN DEFAULT 1,
    payment_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(id),
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
);

-- Usage Tracking Table
CREATE TABLE subscription_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    date DATE NOT NULL,
    appointments_count INTEGER DEFAULT 0,
    plan_limit INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (worker_id) REFERENCES workers(id)
);
```

#### 1.2 Update Workers Table (if needed)
```sql
-- Add subscription reference to workers table
ALTER TABLE workers ADD COLUMN current_subscription_id INTEGER;
ALTER TABLE workers ADD COLUMN subscription_status TEXT DEFAULT 'none';
```

### Phase 2: Backend API Implementation

#### 2.1 Subscription Management Endpoints
```python
# In app.py - Add these routes:

@app.route("/api/subscription/plans", methods=["GET"])
def get_subscription_plans():
    """Get all available subscription plans"""
    plans = subscription_db.get_all_plans()
    return jsonify({"plans": plans}), 200

@app.route("/api/subscription/current/<int:worker_id>", methods=["GET"])
def get_current_subscription(worker_id):
    """Get worker's current subscription"""
    subscription = subscription_db.get_worker_subscription(worker_id)
    return jsonify({"subscription": subscription}), 200

@app.route("/api/subscription/subscribe", methods=["POST"])
def create_subscription():
    """Create new subscription for worker"""
    data = request.json
    worker_id = data["worker_id"]
    plan_id = data["plan_id"]
    
    # Create Razorpay subscription order
    order = subscription_service.create_subscription_order(worker_id, plan_id)
    
    # Save subscription
    subscription_id = subscription_db.create_subscription(worker_id, plan_id, order["id"])
    
    return jsonify({
        "subscription_id": subscription_id,
        "order_id": order["id"],
        "amount": order["amount"]
    }), 201

@app.route("/api/subscription/cancel/<int:worker_id>", methods=["POST"])
def cancel_subscription(worker_id):
    """Cancel worker's subscription"""
    success = subscription_db.cancel_subscription(worker_id)
    return jsonify({"message": "Subscription cancelled"}), 200

@app.route("/api/subscription/stats/<int:worker_id>", methods=["GET"])
def get_subscription_stats(worker_id):
    """Get subscription usage statistics"""
    stats = subscription_db.get_usage_stats(worker_id)
    return jsonify({"stats": stats}), 200
```

#### 2.2 Subscription Service Class
```python
# Create subscription_service.py
class SubscriptionService:
    def __init__(self):
        self.client = razorpay.Client(auth=(
            RAZORPAY_KEY_ID,
            RAZORPAY_KEY_SECRET
        ))
    
    def create_subscription_order(self, worker_id, plan_id):
        """Create Razorpay subscription order"""
        plan = subscription_db.get_plan(plan_id)
        
        order = self.client.subscription.create({
            "plan_id": plan["razorpay_plan_id"],
            "customer_notify": "1",
            "notify_email": "worker@example.com",
            "quantity": "1",
            "total_count": "12",  # 12 months
            "start_at": int(time.time()) + 3600,  # Start in 1 hour
            "expire_by": "2026-12-31",
            "notes": {
                "worker_id": str(worker_id),
                "plan_name": plan["name"]
            }
        })
        
        return order
    
    def process_webhook(self, payload):
        """Process subscription webhook events"""
        event = payload.get("event")
        
        if event == "subscription.charged":
            # Activate subscription
            subscription_id = payload["payload"]["subscription"]["entity"]["id"]
            subscription_db.activate_subscription(subscription_id)
            
        elif event == "subscription.cancelled":
            # Cancel subscription
            subscription_id = payload["payload"]["subscription"]["entity"]["id"]
            subscription_db.cancel_subscription_by_id(subscription_id)
```

### Phase 3: Database Service Layer

#### 3.1 Create subscription_db.py
```python
class SubscriptionDB:
    def __init__(self):
        self.conn = sqlite3.connect("data/expertease.db")
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def get_all_plans(self):
        """Get all active subscription plans"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM subscription_plans WHERE is_active = 1")
        return cursor.fetchall()
    
    def get_worker_subscription(self, worker_id):
        """Get worker's current subscription"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ws.*, sp.name as plan_name, sp.max_appointments_per_day 
            FROM worker_subscriptions ws 
            JOIN subscription_plans sp ON ws.plan_id = sp.id 
            WHERE ws.worker_id = ? AND ws.status = 'active'
        """, (worker_id,))
        return cursor.fetchone()
    
    def create_subscription(self, worker_id, plan_id, razorpay_order_id):
        """Create new subscription"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO worker_subscriptions 
            (worker_id, plan_id, razorpay_subscription_id, start_date, status)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'active')
        """, (worker_id, plan_id, razorpay_order_id))
        
        # Update worker's current subscription
        cursor.execute("""
            UPDATE workers 
            SET current_subscription_id = last_insert_rowid(), subscription_status = 'active'
            WHERE id = ?
        """, (worker_id,))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def cancel_subscription(self, worker_id):
        """Cancel worker's subscription"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE worker_subscriptions 
            SET status = 'cancelled', end_date = CURRENT_TIMESTAMP
            WHERE worker_id = ? AND status = 'active'
        """, (worker_id,))
        
        # Update worker status
        cursor.execute("""
            UPDATE workers 
            SET subscription_status = 'cancelled'
            WHERE id = ?
        """, (worker_id,))
        
        self.conn.commit()
        return True
```

### Phase 4: Integration with Existing System

#### 4.1 Update CLI to Use New APIs
- Change CLI subscription functions to call new backend APIs
- Update API endpoints to match new backend structure
- Add proper error handling and validation

#### 4.2 Update Appointment System
```python
# Check subscription limits before accepting appointments
def check_subscription_limits(worker_id, appointment_date):
    """Check if worker can accept more appointments"""
    subscription = subscription_db.get_worker_subscription(worker_id)
    
    if not subscription:
        return False, "No active subscription"
    
    # Check daily usage
    today_usage = subscription_db.get_today_usage(worker_id)
    daily_limit = subscription["max_appointments_per_day"]
    
    if today_usage >= daily_limit:
        return False, f"Daily limit reached ({today_usage}/{daily_limit})"
    
    # Check subscription validity
    if subscription["end_date"] and subscription["end_date"] < datetime.now():
        return False, "Subscription expired"
    
    return True, "Subscription valid"
```

### Phase 5: Business Logic Implementation

#### 5.1 Subscription Tiers
```python
# Default subscription plans
DEFAULT_PLANS = [
    {
        "id": 1,
        "name": "Basic",
        "price": 499.0,
        "duration_days": 30,
        "max_appointments_per_day": 5,
        "features": "Basic appointment scheduling, Profile management",
        "razorpay_plan_id": "plan_BASIC_001"
    },
    {
        "id": 2,
        "name": "Professional",
        "price": 999.0,
        "duration_days": 30,
        "max_appointments_per_day": 15,
        "features": "Advanced scheduling, Analytics, Priority support",
        "razorpay_plan_id": "plan_PRO_002"
    },
    {
        "id": 3,
        "name": "Enterprise",
        "price": 1999.0,
        "duration_days": 30,
        "max_appointments_per_day": 50,
        "features": "Unlimited appointments, Advanced analytics, Dedicated support",
        "razorpay_plan_id": "plan_ENT_003"
    }
]
```

#### 5.2 Usage Tracking
```python
def track_appointment_usage(worker_id):
    """Track appointment usage for subscription limits"""
    subscription = subscription_db.get_worker_subscription(worker_id)
    
    if subscription and subscription["status"] == "active":
        # Increment daily usage
        subscription_db.increment_usage(worker_id)
        
        # Check if approaching limits
        today_usage = subscription_db.get_today_usage(worker_id)
        daily_limit = subscription["max_appointments_per_day"]
        
        if today_usage >= daily_limit * 0.8:  # 80% warning
            # Send notification to worker
            notification_service.send_usage_warning(worker_id, today_usage, daily_limit)
```

## 🔧 IMPLEMENTATION STEPS

### Step 1: Database Setup
1. Create `subscription_db.py` with all database methods
2. Add subscription tables to existing database migration
3. Insert default subscription plans

### Step 2: Backend API
1. Add subscription service class
2. Implement all subscription endpoints in `app.py`
3. Add subscription validation to appointment acceptance
4. Integrate with existing authentication system

### Step 3: Frontend Integration
1. Update CLI to use new backend APIs
2. Add subscription status to worker dashboard
3. Implement subscription purchase flow
4. Add usage tracking display

### Step 4: Testing & Validation
1. Test subscription creation and cancellation
2. Test usage limits and warnings
3. Test webhook processing
4. Test integration with appointment system

## 🎯 KEY FEATURES TO IMPLEMENT

### ✅ Core Features:
- [ ] Subscription plan management
- [ ] Recurring payment processing
- [ ] Usage tracking and limits
- [ ] Subscription lifecycle management
- [ ] Webhook integration for automatic updates
- [ ] Integration with appointment limits

### ✅ Advanced Features:
- [ ] Tiered subscription plans
- [ ] Usage analytics and reporting
- [ ] Automatic subscription renewals
- [ ] Grace period handling
- [ ] Subscription upgrade/downgrade
- [ ] Promotional codes and discounts

## 🔗 INTEGRATION POINTS

### With Existing Payment System:
- Use existing Razorpay integration
- Extend current payment database schema
- Leverage existing webhook infrastructure
- Integrate with current authentication system

### With Existing Appointment System:
- Add subscription checks before appointment acceptance
- Track usage per appointment
- Limit features based on subscription tier
- Provide upgrade prompts when limits reached

## 📋 BUSINESS RULES

### Subscription Model:
- **Monthly recurring payments**
- **Tiered feature access**
- **Usage-based limitations**
- **Automatic renewals**
- **Grace periods for failed payments**

### Integration Rules:
- **Free tier**: 5 appointments/day maximum
- **Basic tier**: 15 appointments/day, analytics
- **Professional tier**: 50 appointments/day, priority support
- **Enterprise tier**: Unlimited appointments, dedicated support

## 🚀 DEPLOYMENT CHECKLIST

### Pre-deployment:
- [ ] Database migrations tested
- [ ] All API endpoints implemented
- [ ] Subscription plans configured
- [ ] Webhook endpoints secured
- [ ] Error handling complete
- [ ] CLI integration updated

### Post-deployment:
- [ ] Test subscription purchase flow
- [ ] Test usage limit enforcement
- [ ] Test subscription cancellation
- [ ] Test webhook processing
- [ ] Load testing for subscription APIs

---

## 🎯 NEXT STEPS

1. **Implement database layer** (`subscription_db.py`)
2. **Create subscription service** (`subscription_service.py`)
3. **Add API endpoints** to `app.py`
4. **Update CLI integration** with new APIs
5. **Test complete flow** end-to-end
6. **Deploy and monitor** subscription system

This comprehensive plan will give ExpertEase a complete subscription system that integrates seamlessly with the existing payment and appointment management systems!
