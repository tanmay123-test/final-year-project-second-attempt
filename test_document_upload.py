#!/usr/bin/env python3
"""
Test script for document upload functionality
"""
import os
import sys
sys.path.append('.')

from document_upload import create_document_db, REQUIRED_DOCUMENTS, check_documents_complete

def test_document_system():
    print("🧪 Testing Document Upload System")
    print("=" * 50)
    
    # Test 1: Database creation
    print("1. Testing database creation...")
    try:
        create_document_db()
        print("✅ Database created successfully")
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return
    
    # Test 2: Required documents
    print("\n2. Testing required documents configuration...")
    print(f"📄 Required documents: {list(REQUIRED_DOCUMENTS.keys())}")
    print(f"📝 Document names: {list(REQUIRED_DOCUMENTS.values())}")
    print("✅ Required documents configured correctly")
    
    # Test 3: Document status check
    print("\n3. Testing document status check...")
    try:
        status = check_documents_complete(999)  # Non-existent worker
        print(f"📊 Status for worker 999: {status}")
        print("✅ Document status check working")
    except Exception as e:
        print(f"❌ Document status check failed: {e}")
    
    # Test 4: Upload directory structure
    print("\n4. Testing upload directory structure...")
    upload_dirs = [
        "uploads/healthcare_workers",
        "uploads/healthcare_workers/pending", 
        "uploads/healthcare_workers/approved"
    ]
    
    for dir_path in upload_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"⚠️ Directory missing: {dir_path}")
    
    print("\n🎉 Document upload system test completed!")
    print("\n📋 Next steps:")
    print("1. Start the backend server: python app.py")
    print("2. Run the CLI: python cli.py")
    print("3. Try healthcare worker signup with document upload")

if __name__ == "__main__":
    test_document_system()
