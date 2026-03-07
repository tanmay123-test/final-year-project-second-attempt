#!/usr/bin/env python3
"""
Fix CLI syntax errors
"""

import re

# Read the current CLI file
with open('cli.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the indentation issues
content = re.sub(
    r'years_exp = input\("Years of Experience: "\)\.strip\(\)\s+if years_exp and years_exp\.isdigit\(\):\s+documents\[\'years_experience\'\] = int\(years_exp\)\s+',
    '        years_exp = input("Years of Experience: ").strip()\n        if years_exp and years_exp.isdigit():\n            documents[\'years_experience\'] = int(years_exp)\n    ',
    content,
    flags=re.MULTILINE
)

# Write the fixed content back
with open('cli.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed CLI syntax errors")
