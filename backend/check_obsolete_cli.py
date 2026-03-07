import os

print("🔍 Checking for obsolete CLI files...")

# Check for potentially obsolete CLI files
obsolete_files = [
    "car_service/worker_admin_cli.py",
    "car_service/mechanic_cli.py", 
    "car_service/worker_cli.py"
]

found_obsolete = []
for file_path in obsolete_files:
    if os.path.exists(file_path):
        found_obsolete.append(file_path)
        print(f"🔍 Found: {file_path}")
    else:
        print(f"⚠️ Not found: {file_path}")

if found_obsolete:
    print(f"\n⚠️ Found {len(found_obsolete)} potentially obsolete CLI files:")
    for file in found_obsolete:
        print(f"  {file}")
    
    print(f"\n💡 Consider removing these if they're unused:")
    print("  1. Check if they're referenced in main CLI")
    print("  2. Verify no functionality is duplicated")
    print("  3. Ensure unified_mechanic_cli.py covers all needed functionality")
else:
    print("✅ No obvious obsolete CLI files found")

print("\n🔍 Check complete!")
