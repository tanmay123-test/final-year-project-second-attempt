#!/usr/bin/env python3
"""
Fix tow truck driver registration in CLI - Corrected version
"""

# Read the current CLI file
with open('cli.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with the issue and fix it
fixed_lines = []
for i, line in enumerate(lines):
    if i == 4383:  # Line with specialization assignment
        fixed_lines.append(line + '\n')
    elif i == 4384:  # Line that got corrupted
        fixed_lines.append('        years_exp = input("Years of Experience: ").strip()\n')
    else:
        fixed_lines.append(line)

# Write the fixed content back
with open('cli.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Fixed syntax error in CLI.py")
