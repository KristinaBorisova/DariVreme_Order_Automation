#!/usr/bin/env python3
"""
quick_auth_fix.py
Quick fix for authentication issues.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))

def quick_fix():
    """Quick fix for authentication issues."""
    print("🔧 Quick Authentication Fix")
    print("=" * 40)
    
    try:
        # Step 1: Clear any cached tokens
        print("🗑️  Clearing cached tokens...")
        import pathlib
        cache_path = pathlib.Path("~/.cache/myapp/token.json").expanduser()
        if cache_path.exists():
            cache_path.unlink()
            print("✅ Cache cleared")
        
        # Step 2: Test direct authentication
        print("\n🔐 Testing direct authentication...")
        
        # Use the same credentials from your config
        payload = {
            "grantType": "client_credentials",
            "clientId": "175482686405285",
            "clientSecret": "dc190e6d0e4f4fc79e4021e4b981e596"
        }
        
        headers = {"Content-Type": "application/json"}
        url = "https://stageapi.glovoapp.com/oauth/token"
        
        print(f"🚀 Sending authentication request...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("accessToken")
            
            if token:
                print(f"✅ Authentication successful!")
                print(f"   Token: {token[:20]}...")
                print(f"   Expires in: {data.get('expires_in', 'N/A')} seconds")
                
                # Test the token with a simple API call
                print(f"\n🧪 Testing token with API call...")
                test_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Try to get addresses to test token
                test_response = requests.get(
                    "https://stageapi.glovoapp.com/v2/laas/addresses",
                    headers=test_headers,
                    timeout=30
                )
                
                print(f"📊 Test API Response: {test_response.status_code}")
                
                if test_response.status_code == 200:
                    print("✅ Token is working correctly!")
                    return True
                else:
                    print(f"❌ Token test failed: {test_response.status_code}")
                    print(f"   Error: {test_response.text}")
                    return False
            else:
                print("❌ No access token in response")
                return False
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Quick fix failed: {e}")
        return False

def test_quote_creation_with_fresh_token():
    """Test quote creation with a fresh token."""
    print("\n🧪 Testing Quote Creation with Fresh Token")
    print("-" * 40)
    
    try:
        # Get fresh token
        payload = {
            "grantType": "client_credentials",
            "clientId": "175482686405285",
            "clientSecret": "dc190e6d0e4f4fc79e4021e4b981e596"
        }
        
        headers = {"Content-Type": "application/json"}
        url = "https://stageapi.glovoapp.com/oauth/token"
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
        
        data = response.json()
        token = data.get("accessToken")
        
        if not token:
            print("❌ No token received")
            return False
        
        print(f"✅ Fresh token obtained: {token[:20]}...")
        
        # Test quote creation
        quote_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Create a test quote payload
        test_quote_payload = {
            "pickupDetails": {
                "addressBook": {
                    "id": "dd560a2c-f1b5-43b7-81bc-2830595122f9"
                },
                "pickupTime": "2025-12-20T15:30:00Z"
            },
            "deliveryAddress": {
                "rawAddress": "g.k. Strelbishte, Nishava St 111р 1408, Bulgaria",
                "coordinates": {
                    "latitude": 42.673758,
                    "longitude": 23.298064
                },
                "details": "Test delivery"
            }
        }
        
        print(f"🚀 Testing quote creation...")
        quote_response = requests.post(
            "https://stageapi.glovoapp.com/v2/laas/quotes",
            headers=quote_headers,
            json=test_quote_payload,
            timeout=30
        )
        
        print(f"📊 Quote Response: {quote_response.status_code}")
        
        if quote_response.status_code == 200:
            quote_data = quote_response.json()
            print(f"✅ Quote creation successful!")
            print(f"   Quote ID: {quote_data.get('quoteId', 'N/A')}")
            print(f"   Price: {quote_data.get('quotePrice', 'N/A')} {quote_data.get('currencyCode', 'N/A')}")
            return True
        else:
            print(f"❌ Quote creation failed: {quote_response.status_code}")
            print(f"   Error: {quote_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Quote test failed: {e}")
        return False

def main():
    """Run the quick authentication fix."""
    print("🚀 Quick Authentication Fix for Glovo API")
    print("=" * 50)
    
    # Step 1: Quick fix
    auth_success = quick_fix()
    
    if auth_success:
        # Step 2: Test quote creation
        quote_success = test_quote_creation_with_fresh_token()
        
        if quote_success:
            print("\n🎉 Authentication is working correctly!")
            print("✅ You can now run your production workflow")
            print("\n💡 Next steps:")
            print("   1. Run: python test_with_real_data.py")
            print("   2. Run: python production_workflow.py")
        else:
            print("\n⚠️  Authentication works but quote creation failed")
            print("💡 This might be a data or API endpoint issue")
    else:
        print("\n❌ Authentication fix failed")
        print("💡 Possible issues:")
        print("   1. API credentials are incorrect")
        print("   2. API endpoint is down")
        print("   3. Network connectivity issues")
        print("   4. Glovo API access has been revoked")

if __name__ == "__main__":
    main()
