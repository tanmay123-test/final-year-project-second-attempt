"""
Pricing Configuration for ExpertEase Platform
All prices are in Indian Rupees (INR) for the Indian market
"""

# Default pricing for different services (in INR)
DEFAULT_PRICING = {
    # Housekeeping Services
    "housekeeping": {
        "services": {
            "General Cleaning": 500.0,
            "Deep Cleaning": 1000.0,
            "Bathroom Cleaning": 400.0,
            "Kitchen Cleaning": 600.0,
        },
        "worker_hourly_rate": 50.0,  # Default hourly rate for workers
        "base_price_range": {
            "min": 300.0,
            "max": 2000.0
        }
    },
    
    # Healthcare Services
    "healthcare": {
        "consultation_fee": 500.0,  # Base consultation fee
        "video_consultation": 800.0,
        "emergency_fee": 1500.0,
        "worker_hourly_rate": 200.0,  # Default for doctors
        "specialization_premium": {
            "Cardiology": 1000.0,
            "Neurology": 1200.0,
            "Orthopedics": 800.0,
            "Pediatrics": 600.0,
            "General": 500.0
        }
    },
    
    # Car Services
    "car_service": {
        "base_service": 5000.0,  # Default car service cost
        "emergency_service": 8000.0,
        "inspection_fee": 1500.0,
        "worker_hourly_rate": 150.0,  # Default for mechanics
        "service_types": {
            "Oil Change": 2000.0,
            "Brake Service": 3500.0,
            "Engine Repair": 8000.0,
            "AC Service": 2500.0,
            "General Maintenance": 3000.0
        }
    },
    
    # Freelance Marketplace
    "freelance": {
        "minimum_project_budget": 5000.0,
        "recommended_budget_range": {
            "min": 5000.0,
            "max": 15000.0
        },
        "worker_hourly_rate": {
            "Entry Level": 200.0,
            "Mid Level": 500.0,
            "Expert": 1000.0
        },
        "platform_commission": 0.20,  # 20% platform commission
        "categories": {
            "Web Development": {"min": 8000.0, "max": 25000.0},
            "Mobile Development": {"min": 10000.0, "max": 30000.0},
            "Design": {"min": 5000.0, "max": 20000.0},
            "Content Writing": {"min": 3000.0, "max": 15000.0},
            "Digital Marketing": {"min": 6000.0, "max": 20000.0}
        }
    },
    
    # Money Management (Finny)
    "money_management": {
        "subscription_tiers": {
            "Free": 0.0,
            "Basic": 199.0,  # Monthly
            "Premium": 499.0,  # Monthly
            "Professional": 999.0  # Monthly
        },
        "transaction_limits": {
            "Free": 50,
            "Basic": 500,
            "Premium": 2000,
            "Professional": "Unlimited"
        }
    }
}

# Currency configuration
CURRENCY_CONFIG = {
    "currency": "INR",
    "symbol": "₹",
    "decimal_places": 2,
    "thousand_separator": ",",
    "decimal_separator": "."
}

# Platform commission rates
PLATFORM_COMMISSION = {
    "housekeeping": 0.15,  # 15%
    "healthcare": 0.20,    # 20%
    "car_service": 0.15,  # 15%
    "freelance": 0.20,    # 20%
    "money_management": 0.0  # No commission on money management
}

# Worker default rates by service
WORKER_DEFAULT_RATES = {
    "housekeeping": 50.0,    # ₹50/hour
    "healthcare": 200.0,      # ₹200/hour for doctors
    "car_service": 150.0,    # ₹150/hour for mechanics
    "freelance": 300.0,      # ₹300/hour average for freelancers
}

def get_default_pricing(service_type):
    """Get default pricing for a service type"""
    return DEFAULT_PRICING.get(service_type, {})

def get_worker_default_rate(service_type):
    """Get default hourly rate for a worker in a service"""
    return WORKER_DEFAULT_RATES.get(service_type, 50.0)

def format_currency(amount):
    """Format amount as INR currency"""
    if amount is None:
        return f"{CURRENCY_CONFIG['symbol']}0.00"
    
    formatted = f"{amount:,.2f}"
    return f"{CURRENCY_CONFIG['symbol']}{formatted}"

def calculate_platform_fee(service_type, amount):
    """Calculate platform commission fee"""
    commission_rate = PLATFORM_COMMISSION.get(service_type, 0.15)
    return amount * commission_rate

def validate_pricing(service_type, price):
    """Validate if price is within acceptable range for service type"""
    pricing = get_default_pricing(service_type)
    
    if "base_price_range" in pricing:
        min_price = pricing["base_price_range"]["min"]
        max_price = pricing["base_price_range"]["max"]
        return min_price <= price <= max_price
    
    return True  # No validation if no range defined

# Indian market specific configurations
INDIAN_MARKET_CONFIG = {
    "working_hours": {
        "start": "09:00",
        "end": "21:00"
    },
    "weekend_surcharge": 0.25,  # 25% extra for weekend services
    "emergency_surcharge": 0.50,  # 50% extra for emergency services
    "gst_rate": 0.18,  # 18% GST
    "payment_methods": [
        "UPI",
        "Credit Card",
        "Debit Card", 
        "Net Banking",
        "Cash on Service"
    ]
}

def calculate_total_amount(service_type, base_amount, is_emergency=False, is_weekend=False):
    """Calculate total amount including GST and surcharges"""
    total = base_amount
    
    # Add emergency surcharge
    if is_emergency:
        total += total * INDIAN_MARKET_CONFIG["emergency_surcharge"]
    
    # Add weekend surcharge
    if is_weekend:
        total += total * INDIAN_MARKET_CONFIG["weekend_surcharge"]
    
    # Add GST
    total += total * INDIAN_MARKET_CONFIG["gst_rate"]
    
    # Add platform commission
    platform_fee = calculate_platform_fee(service_type, base_amount)
    total += platform_fee
    
    return round(total, 2)

if __name__ == "__main__":
    # Test pricing functions
    print("=== ExpertEase Pricing Configuration ===")
    print(f"Currency: {CURRENCY_CONFIG['currency']} ({CURRENCY_CONFIG['symbol']})")
    print(f"Default Housekeeping Rate: {format_currency(get_worker_default_rate('housekeeping'))}/hour")
    print(f"Default Healthcare Rate: {format_currency(get_worker_default_rate('healthcare'))}/hour")
    print(f"Car Service Base Price: {format_currency(DEFAULT_PRICING['car_service']['base_service'])}")
    print(f"Freelance Recommended Budget: {format_currency(DEFAULT_PRICING['freelance']['recommended_budget_range']['min'])} - {format_currency(DEFAULT_PRICING['freelance']['recommended_budget_range']['max'])}")
    
    # Test total calculation
    base_price = DEFAULT_PRICING['housekeeping']['services']['General Cleaning']
    total = calculate_total_amount('housekeeping', base_price, is_weekend=True)
    print(f"General Cleaning (Weekend): {format_currency(base_price)} → {format_currency(total)}")
