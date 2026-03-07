#!/usr/bin/env python3
"""
Remove all unused, test, debug, and temporary files from the project
"""

import os
import glob
import shutil

print("🧹 CLEANING UP UNUSED CODE...")

# Define patterns for files to remove
remove_patterns = [
    "test_*.py",
    "debug_*.py", 
    "check_*.py",
    "*_verification.py",
    "*_fix.py",
    "*_demo.py",
    "simple_active_job_fix.py",
    "minimal_active_job_fix.py",
    "working_active_job_fix.py",
    "final_active_job_fix.py",
    "apply_active_job_fix.py"
]

# Define files to keep (important ones)
keep_files = {
    "cli.py",
    "app.py", 
    "setup_smart_search.py",
    "CODE_ANALYSIS.md",
    "ACTIVE_JOBS_COMPLETE_SOLUTION.md"
}

removed_count = 0
kept_count = 0

# Get all Python files
all_py_files = glob.glob("*.py")
car_service_files = glob.glob("car_service/*.py")

print(f"📁 Found {len(all_py_files)} Python files in root")
print(f"📁 Found {len(car_service_files)} Python files in car_service/")

# Remove files matching patterns
for pattern in remove_patterns:
    # Root directory
    files_to_remove = glob.glob(pattern)
    for file in files_to_remove:
        if os.path.exists(file):
            print(f"🗑️ Removing: {file}")
            os.remove(file)
            removed_count += 1
        else:
            print(f"⚠️ File not found: {file}")
    
    # Car service directory
    car_pattern = pattern.replace("*", "car_service/")
    files_to_remove = glob.glob(car_pattern)
    for file in files_to_remove:
        if os.path.exists(file):
            print(f"🗑️ Removing: {file}")
            os.remove(file)
            removed_count += 1
        else:
            print(f"⚠️ File not found: {file}")

# Count remaining important files
for file in all_py_files + car_service_files:
    if os.path.exists(file):
        filename = os.path.basename(file)
        if filename in keep_files:
            kept_count += 1
        else:
            # Check if it matches remove patterns but wasn't caught
            for pattern in remove_patterns:
                if pattern.replace("*", "").replace("car_service/", "") in filename:
                    print(f"🗑️ Removing missed file: {file}")
                    os.remove(file)
                    removed_count += 1
                    break

print(f"\n📊 CLEANUP SUMMARY:")
print(f"  Files removed: {removed_count}")
print(f"  Files kept: {kept_count}")
print(f"  Net reduction: {removed_count - len(keep_files)}")

print(f"\n✅ Cleanup completed!")
print(f"💡 Project is now cleaner and more maintainable")
