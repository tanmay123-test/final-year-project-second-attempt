#!/usr/bin/env python3
"""
Test script to verify the automobile expert CLI fix
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the CLI module
try:
    from car_service.automobile_expert_cli import automobile_expert_signup
    print("✅ Successfully imported automobile_expert_cli")
    
    # Check if the file has been updated by looking at the source
    import inspect
    source = inspect.getsource(automobile_expert_signup)
    
    if "press Enter to skip" in source:
        print("✅ CLI has been updated with skip option")
    else:
        print("❌ CLI still has old code")
        
    if "⚠️ Certificate file not found" in source:
        print("✅ CLI has user-friendly warning message")
    else:
        print("❌ CLI still has old error message")
        
    if "📝 Continuing without certificate file" in source:
        print("✅ CLI has continuation message")
    else:
        print("❌ CLI missing continuation message")
        
    print("\n🎉 CLI fix verification completed!")
    
except ImportError as e:
    print(f"❌ Failed to import CLI: {e}")
except Exception as e:
    print(f"❌ Error during testing: {e}")
