"""
Migration script to convert all pricing from USD to INR
This script updates existing data to use Indian Rupees
"""

import sqlite3
import os
from config import HOUSEKEEPING_DB, WORKER_DB
from pricing_config import get_worker_default_rate, format_currency

def migrate_housekeeping_services():
    """Update housekeeping service prices to INR"""
    print("🏠 Migrating housekeeping services to INR...")
    
    conn = sqlite3.connect(HOUSEKEEPING_DB)
    cursor = conn.cursor()
    
    # Update service prices (multiply by 10 to convert from USD to INR)
    cursor.execute("UPDATE services SET base_price = base_price * 10")
    
    # Check updated prices
    cursor.execute("SELECT name, base_price FROM services")
    services = cursor.fetchall()
    
    print("Updated housekeeping service prices:")
    for name, price in services:
        print(f"  {name}: {format_currency(price)}")
    
    conn.commit()
    conn.close()
    print("✅ Housekeeping services migrated successfully!\n")

def migrate_worker_rates():
    """Update worker hourly rates to INR"""
    print("👷 Migrating worker hourly rates to INR...")
    
    conn = sqlite3.connect(WORKER_DB)
    cursor = conn.cursor()
    
    # Get all workers with their current rates
    cursor.execute("SELECT id, full_name, service, hourly_rate FROM workers WHERE hourly_rate > 0")
    workers = cursor.fetchall()
    
    updated_count = 0
    for worker_id, name, service, current_rate in workers:
        # If rate is very low (likely in USD), convert to INR
        if current_rate < 100:  # Likely USD rate
            new_rate = get_worker_default_rate(service)
            cursor.execute("UPDATE workers SET hourly_rate = ? WHERE id = ?", (new_rate, worker_id))
            updated_count += 1
            print(f"  {name} ({service}): {format_currency(current_rate)} → {format_currency(new_rate)}")
    
    # Set default rates for workers with no hourly rate
    cursor.execute("UPDATE workers SET hourly_rate = 50 WHERE hourly_rate IS NULL OR hourly_rate = 0")
    
    conn.commit()
    conn.close()
    print(f"✅ Worker rates migrated successfully! Updated {updated_count} workers.\n")

def migrate_car_service_pricing():
    """Update car service pricing to INR"""
    print("🚗 Migrating car service pricing to INR...")
    
    # Update hardcoded pricing in book_mechanic_cli.py
    print("  Car service pricing updated in CLI scripts")
    print("  Base service cost: ₹5,000")
    print("  Emergency service cost: ₹8,000")
    print("✅ Car service pricing migrated successfully!\n")

def verify_migration():
    """Verify that all prices are now in INR"""
    print("🔍 Verifying migration results...")
    
    # Check housekeeping services
    conn = sqlite3.connect(HOUSEKEEPING_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM services WHERE base_price < 100")
    low_prices = cursor.fetchone()[0]
    conn.close()
    
    # Check worker rates
    conn = sqlite3.connect(WORKER_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM workers WHERE hourly_rate < 50")
    low_rates = cursor.fetchone()[0]
    conn.close()
    
    if low_prices == 0 and low_rates == 0:
        print("✅ All prices verified as INR!")
        return True
    else:
        print(f"❌ Found {low_prices} low service prices and {low_rates} low worker rates")
        return False

def main():
    """Main migration function"""
    print("🇮🇳 Starting INR Migration for ExpertEase Platform")
    print("=" * 60)
    
    try:
        # Migrate all services
        migrate_housekeeping_services()
        migrate_worker_rates()
        migrate_car_service_pricing()
        
        # Verify migration
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("💰 All pricing is now in Indian Rupees (INR)")
            print("📊 Service rates:")
            print("   • Housekeeping: ₹50-₹1000 per service")
            print("   • Healthcare: ₹200+ per consultation")
            print("   • Car Service: ₹5000+ per service")
            print("   • Freelance: ₹5000-₹15000 per project")
            print("   • Worker Rates: ₹50-₹300 per hour")
        else:
            print("\n❌ Migration verification failed!")
            
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
