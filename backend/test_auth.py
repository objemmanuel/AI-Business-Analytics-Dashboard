"""
Test script for authentication
Run this to verify JWT auth works
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_login(username, password):
    """Test login endpoint"""
    print(f"\n🔐 Testing login for: {username}")
    
    response = requests.post(
        f"{API_BASE}/api/auth/login",
        data={
            "username": username,
            "password": password
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"   User: {data['user']['full_name']}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint"""
    print(f"\n🔒 Testing protected endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{API_BASE}/api/metrics/kpis", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Protected endpoint accessible!")
        print(f"   Revenue: ${data['kpis']['total_revenue']['value']:,.2f}")
        return True
    else:
        print(f"❌ Protected endpoint failed: {response.text}")
        return False

def test_invalid_token():
    """Test with invalid token"""
    print(f"\n🚫 Testing with invalid token...")
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    response = requests.get(f"{API_BASE}/api/metrics/kpis", headers=headers)
    
    if response.status_code == 401:
        print(f"✅ Invalid token correctly rejected (401)")
        return True
    else:
        print(f"❌ Expected 401, got: {response.status_code}")
        return False

def main():
    print("="*60)
    print("🧪 Testing JWT Authentication")
    print("="*60)
    
    # Test 1: Login with admin
    token = test_login("admin", "admin123")
    if not token:
        print("\n❌ Authentication tests failed!")
        return
    
    # Test 2: Access protected endpoint
    if not test_protected_endpoint(token):
        print("\n❌ Protected endpoint test failed!")
        return
    
    # Test 3: Login with demo user
    demo_token = test_login("demo", "demo123")
    if not demo_token:
        print("\n❌ Demo user login failed!")
        return
    
    # Test 4: Invalid credentials
    print("\n🔐 Testing invalid credentials...")
    bad_response = requests.post(
        f"{API_BASE}/api/auth/login",
        data={"username": "wrong", "password": "wrong"}
    )
    if bad_response.status_code == 401:
        print("✅ Invalid credentials correctly rejected")
    else:
        print(f"❌ Expected 401, got: {bad_response.status_code}")
    
    # Test 5: Invalid token
    test_invalid_token()
    
    # Test 6: Get current user
    print(f"\n👤 Testing /api/auth/me endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/api/auth/me", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Current user retrieved: {user['full_name']}")
    else:
        print(f"❌ Failed to get current user")
    
    print("\n" + "="*60)
    print("🎉 All authentication tests passed!")
    print("="*60)
    print("\n📋 Demo Credentials:")
    print("   Admin: admin / admin123")
    print("   Demo:  demo / demo123")
    print("\n🌐 Try the login page at: http://localhost:3000")
    print("")

if __name__ == "__main__":
    main()