#!/usr/bin/env python3
"""
fix_authentication.py
Fix authentication issues and test token validity.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))

def test_token_validity():
    """Test if the current token is valid."""
    print("🔍 Testing Token Validity")
    print("-" * 40)
    
    try:
        from token_service import get_bearer_token
        
        # Get current token
        token = get_bearer_token()
        
        if not token:
            print("❌ No token found")
            return False
        
        print(f"✅ Token retrieved: {token[:20]}...")
        
        # Test token with a simple API call
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Try a simple API endpoint to test token validity
        test_url = "https://stageapi.glovoapp.com/v2/laas/addresses"
        
        print(f"🧪 Testing token with API call...")
        response = requests.get(test_url, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token is valid!")
            return True
        elif response.status_code == 401:
            print("❌ Token is invalid or expired")
            print(f"   Error: {response.text}")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Token test failed: {e}")
        return False

def refresh_token():
    """Force refresh the authentication token."""
    print("\n🔄 Refreshing Authentication Token")
    print("-" * 40)
    
    try:
        from token_service import get_bearer_token
        
        # Force refresh by passing force_refresh=True
        print("🔄 Forcing token refresh...")
        token = get_bearer_token(force_refresh=True)
        
        if not token:
            print("❌ Failed to refresh token")
            return False
        
        print(f"✅ New token retrieved: {token[:20]}...")
        
        # Test the new token
        return test_token_validity()
        
    except Exception as e:
        print(f"❌ Token refresh failed: {e}")
        return False

def check_token_cache():
    """Check the token cache file."""
    print("\n📁 Checking Token Cache")
    print("-" * 40)
    
    try:
        import pathlib
        
        # Check cache file location
        cache_path = pathlib.Path("~/.cache/myapp/token.json").expanduser()
        
        if cache_path.exists():
            print(f"✅ Cache file exists: {cache_path}")
            
            # Read cache file
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            print(f"📋 Cache data:")
            print(f"   Access Token: {cache_data.get('accessToken', 'N/A')[:20]}...")
            print(f"   Expires At: {cache_data.get('expires_at', 'N/A')}")
            
            # Check if token is expired
            import time
            current_time = time.time()
            expires_at = cache_data.get('expires_at', 0)
            
            if expires_at > current_time:
                print(f"✅ Token is not expired (expires in {expires_at - current_time:.0f} seconds)")
            else:
                print(f"❌ Token is expired (expired {current_time - expires_at:.0f} seconds ago)")
            
            return cache_data
        else:
            print(f"❌ Cache file does not exist: {cache_path}")
            return None
            
    except Exception as e:
        print(f"❌ Cache check failed: {e}")
        return None

def clear_token_cache():
    """Clear the token cache to force fresh authentication."""
    print("\n🗑️  Clearing Token Cache")
    print("-" * 40)
    
    try:
        import pathlib
        
        cache_path = pathlib.Path("~/.cache/myapp/token.json").expanduser()
        
        if cache_path.exists():
            cache_path.unlink()
            print(f"✅ Cache file deleted: {cache_path}")
        else:
            print(f"ℹ️  Cache file does not exist: {cache_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache clear failed: {e}")
        return False

def test_authentication_flow():
    """Test the complete authentication flow."""
    print("\n🔐 Testing Complete Authentication Flow")
    print("-" * 40)
    
    try:
        # Test the authentication helper directly
        sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
        
        print("🧪 Testing 1_glovo_auth_helper.py...")
        from step_1_authentication import glovo_auth_helper
        
        # This will test the direct authentication
        print("✅ Authentication helper imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication flow test failed: {e}")
        return False

def fix_authentication():
    """Main function to fix authentication issues."""
    print("🔧 Glovo Authentication Fix")
    print("=" * 50)
    
    # Step 1: Check current token
    print("Step 1: Checking current token...")
    token_valid = test_token_validity()
    
    if token_valid:
        print("✅ Authentication is working correctly!")
        return True
    
    # Step 2: Check token cache
    print("\nStep 2: Checking token cache...")
    cache_data = check_token_cache()
    
    # Step 3: Clear cache if needed
    if cache_data:
        print("\nStep 3: Clearing expired token cache...")
        clear_token_cache()
    
    # Step 4: Refresh token
    print("\nStep 4: Refreshing authentication token...")
    token_refreshed = refresh_token()
    
    if token_refreshed:
        print("\n🎉 Authentication fixed successfully!")
        print("✅ You can now run your production workflow")
        return True
    else:
        print("\n❌ Authentication fix failed")
        print("💡 Manual steps to try:")
        print("   1. Check your API credentials in step_1_authentication/config.py")
        print("   2. Verify your Glovo API access")
        print("   3. Contact Glovo support if credentials are correct")
        return False

def main():
    """Run the authentication fix."""
    success = fix_authentication()
    
    if success:
        print("\n🚀 Next steps:")
        print("   1. Run: python test_with_real_data.py")
        print("   2. Run: python production_workflow.py")
    else:
        print("\n🔧 Troubleshooting steps:")
        print("   1. Check your API credentials")
        print("   2. Verify internet connection")
        print("   3. Check Glovo API status")

if __name__ == "__main__":
    main()
