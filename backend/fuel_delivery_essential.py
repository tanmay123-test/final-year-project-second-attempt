#!/usr/bin/env python3
"""
Fuel Delivery Agent CLI - Essential Functions Only
"""

import requests
import time

API = "http://127.0.0.1:5000"

def view_active_delivery(agent_info):
    """View active fuel delivery"""
    print("\n" + "="*60)
    print("  ACTIVE FUEL DELIVERY")
    print("="*60)
    print("  No active delivery")
    input("\nPress Enter to continue...")

def view_delivery_history(agent_info):
    """View delivery history and earnings"""
    print("\n" + "="*60)
    print("  DELIVERY HISTORY & EARNINGS")
    print("="*60)
    print("  Total Earnings:  0.00")
    print("  Total Deliveries: 0")
    print("  Average Rating: 0.0/5.0")
    print("\n  No delivery history")
    input("\nPress Enter to continue...")

def view_performance(agent_info):
    """View performance and reputation"""
    print("\n" + "="*60)
    print("   PERFORMANCE & REPUTATION")
    print("="*60)
    print("  Performance Level: Bronze")
    print("  Rating: 0.0/5.0")
    print("  Total Deliveries: 0")
    print("  Completion Rate: 0.0%")
    print("  Recent Deliveries: 0 (last 30 days)")
    print("\n  No badges earned yet")
    print("\n   SAFETY COMPLIANCE:")
    print("     Verified: Yes")
    print("     Approved: Yes")
    input("\nPress Enter to continue...")
