#!/usr/bin/env python3

import os
import sys

print("🔍 COMPREHENSIVE ERROR ANALYSIS")
print("="*60)

print("📋 ISSUE 1: MISSING RAZORPAY ENVIRONMENT VARIABLES")
print("-" * 50)

# Check main .env
main_env = "c:\\Users\\Admin\\Desktop\\Project\\final-year-project-\\.env"
payment_env = "c:\\Users\\Admin\\Desktop\\Project\\final-year-project-\\payment\\.env"

print(f"Main .env exists: {os.path.exists(main_env)}")
print(f"Payment .env exists: {os.path.exists(payment_env)}")

if os.path.exists(payment_env):
    with open(payment_env, 'r') as f:
        print(f"Payment .env content:")
        for line in f:
            print(f"  {line.strip()}")

print("\n📋 ISSUE 2: DATABASE PATH MISMATCH")
print("-" * 50)
print("Payment system uses: database.db")
print("Subscription system uses: data/expertease.db")
print("This causes confusion and potential conflicts")

print("\n📋 ISSUE 3: SQL SYNTAX ERRORS")
print("-" * 50)
print("payment_db.py has SQL syntax errors:")
print("Line 7: Missing closing quote in status value")
print("Line 15: Missing opening quote in status value")

print("\n📋 ISSUE 4: IMPORT PATH ISSUES")
print("-" * 50)
print("razor_service.py calls create_order(amount, receipt)")
print("payment_route.py calls create_order(amount, booking_id)")
print("Parameter mismatch causing errors")

print("\n🎯 ROOT CAUSE ANALYSIS")
print("="*60)
print("The recurring error is caused by:")
print("1. ❌ Missing .env file in main directory")
print("2. ❌ SQL syntax errors in payment_db.py")
print("3. ❌ Database path confusion")
print("4. ❌ Function parameter mismatches")
print("5. ❌ Environment variable loading issues")

print("\n🔧 IMMEDIATE FIXES NEEDED")
print("="*60)

if __name__ == "__main__":
    pass
