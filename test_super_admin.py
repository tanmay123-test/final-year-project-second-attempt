#!/usr/bin/env python3
"""
Test script for Super Admin Backend System
"""
import os
import sys
import requests
import json

sys.path.append('.')

from admin_db import admin_db
from admin_auth import generate_admin_token, verify_admin_token

API_BASE = "http://127.0.0.1:5001/api"

def test_admin_database():
    """Test admin database functionality"""
    print("🔐 Testing Admin Database")
    print("=" * 40)
    
    # Test 1: Check default admin
    admin = admin_db.get_admin_by_username('superadmin')
    if admin:
        print(f"✅ Default admin found: {admin['username']}")
        print(f"   Role: {admin['role']}")
        print(f"   Created: {admin['created_at']}")
    else:
        print("❌ Default admin not found")
        return False
    
    # Test 2: Password verification
    if admin_db.verify_password('admin123', admin['password_hash']):
        print("✅ Password verification working")
    else:
        print("❌ Password verification failed")
        return False
    
    return True

def test_admin_authentication():
    """Test admin authentication system"""
    print("\n🔑 Testing Admin Authentication")
    print("=" * 40)
    
    # Test 1: Generate token
    try:
        token = generate_admin_token('superadmin')
        print(f"✅ Token generated successfully")
        print(f"   Token length: {len(token)} characters")
    except Exception as e:
        print(f"❌ Token generation failed: {e}")
        return False
    
    # Test 2: Verify token
    try:
        admin, error = verify_admin_token(token)
        if admin:
            print(f"✅ Token verification successful")
            print(f"   Admin: {admin['username']} ({admin['role']})")
        else:
            print(f"❌ Token verification failed: {error}")
            return False
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return False
    
    return True

def test_admin_api_endpoints():
    """Test admin API endpoints"""
    print("\n🌐 Testing Admin API Endpoints")
    print("=" * 40)
    
    # Test 1: Admin login
    print("\n1. Testing admin login...")
    try:
        response = requests.post(f"{API_BASE}/admin/login", json={
            "username": "superadmin",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data.get('token')
                print(f"✅ Admin login successful")
                print(f"   Token received: {len(token)} chars")
                
                # Test 2: Verify token endpoint
                print("\n2. Testing token verification...")
                verify_response = requests.post(f"{API_BASE}/admin/verify-token", json={
                    "token": token
                })
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    if verify_data.get('success'):
                        print("✅ Token verification successful")
                        
                        # Test 3: Dashboard stats (protected route)
                        print("\n3. Testing dashboard statistics...")
                        headers = {"Authorization": f"Bearer {token}"}
                        stats_response = requests.get(f"{API_BASE}/admin/dashboard/stats", headers=headers)
                        
                        if stats_response.status_code == 200:
                            stats = stats_response.json()
                            if stats.get('success'):
                                print("✅ Dashboard stats retrieved")
                                stats_data = stats.get('stats', {})
                                print(f"   Users: {stats_data.get('users', {}).get('total', 0)}")
                                print(f"   Workers: {stats_data.get('workers', {}).get('total', 0)}")
                                print(f"   Pending Workers: {stats_data.get('workers', {}).get('pending', 0)}")
                            else:
                                print(f"❌ Dashboard stats error: {stats.get('error')}")
                        else:
                            print(f"❌ Dashboard stats failed: {stats_response.status_code}")
                    else:
                        print(f"❌ Token verification failed: {verify_data.get('error')}")
                else:
                    print(f"❌ Token verification error: {verify_response.status_code}")
            else:
                print(f"❌ Login failed: {data.get('error')}")
        else:
            print(f"❌ Login HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Cannot connect to API server")
        print("   Make sure the backend is running: python app.py")
        return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False
    
    return True

def test_platform_commission():
    """Test platform commission endpoint"""
    print("\n💰 Testing Platform Commission")
    print("=" * 40)
    
    try:
        # Get commission (public endpoint)
        response = requests.get(f"{API_BASE}/admin/platform/commission")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                commission = data.get('commission', {})
                print(f"✅ Platform commission: {commission.get('percentage', 0)}%")
                print(f"   Decimal: {commission.get('decimal', 0)}")
                return True
            else:
                print(f"❌ Commission error: {data.get('error')}")
        else:
            print(f"❌ Commission HTTP error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Cannot connect to API server")
        return False
    except Exception as e:
        print(f"❌ Commission test error: {e}")
        return False
    
    return False

def main():
    """Run all tests"""
    print("🚀 SUPER ADMIN BACKEND TEST SUITE")
    print("=" * 60)
    
    # Test database
    if not test_admin_database():
        print("\n❌ Database tests failed")
        return
    
    # Test authentication
    if not test_admin_authentication():
        print("\n❌ Authentication tests failed")
        return
    
    # Test API endpoints
    if not test_admin_api_endpoints():
        print("\n❌ API endpoint tests failed")
        return
    
    # Test platform commission
    if not test_platform_commission():
        print("\n❌ Platform commission tests failed")
        return
    
    print("\n🎉 ALL TESTS PASSED!")
    print("\n📋 Super Admin Backend is ready!")
    print("\n🔐 Default Login Credentials:")
    print("   Username: superadmin")
    print("   Password: admin123")
    print("\n🌐 Available Endpoints:")
    print("   POST /api/admin/login - Admin login")
    print("   POST /api/admin/verify-token - Verify token")
    print("   GET  /api/admin/dashboard/stats - Dashboard statistics")
    print("   GET  /api/admin/platform/commission - Commission settings")
    print("   GET  /api/admin/workers - Worker management")
    print("   GET  /api/admin/users - User management")
    print("\n🚀 Next Steps:")
    print("1. Start backend: python app.py")
    print("2. Test login: POST /api/admin/login")
    print("3. Use JWT token for protected routes")
    print("4. Build frontend dashboard")

if __name__ == "__main__":
    main()
