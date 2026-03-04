#!/usr/bin/env python3
"""
Fix tow truck driver registration in CLI
"""

import re

# Read the current CLI file
with open('cli.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the pattern and replace it
pattern = r'(\s+years_exp = input\("Years of Experience: "\)\.strip\(\)\s+if years_exp and years_exp\.isdigit\(\):\s+documents\[\'years_experience\'\] = int\(years_exp\)\s+\n\s+\# Step 4: Submit application)'

replacement = r'''    years_exp = input("Years of Experience: ").strip()
        if years_exp and years_exp.isdigit():
            documents['years_experience'] = int(years_exp)
    
    # Step 4: Collect truck-specific information for TOW_TRUCK
    if worker_type == 'TOW_TRUCK':
        print(f"\\n🚚 TRUCK INFORMATION")
        print("="*30)
        
        truck_type = input("Truck Type (FLATBED/WHEEL_LIFT/HEAVY_DUTY): ").strip().upper()
        truck_registration = input("Truck Registration Number: ").strip()
        truck_model = input("Truck Model: ").strip()
        truck_capacity = input("Truck Capacity (SMALL_CAR/SUV/HEAVY_VEHICLE): ").strip().upper()
        insurance_expiry = input("Insurance Expiry Date (YYYY-MM-DD): ").strip()
        fitness_expiry = input("Fitness Certificate Expiry Date (YYYY-MM-DD): ").strip()
        
        # Add truck info to documents
        documents['truck_type'] = truck_type
        documents['truck_registration_number'] = truck_registration
        documents['truck_model'] = truck_model
        documents['truck_capacity'] = truck_capacity
        documents['insurance_expiry_date'] = insurance_expiry
        documents['fitness_expiry_date'] = fitness_expiry
    
    # Step 5: Submit application'''

# Apply the fix
new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

# Write the fixed content back
with open('cli.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Fixed tow truck driver registration in CLI.py")
