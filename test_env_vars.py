#!/usr/bin/env python3
"""
test_env_vars.py
Test script to verify environment variables are set correctly.
"""

import os

def test_environment_variables():
    """Test if all required environment variables are set."""
    print("🧪 Testing Environment Variables")
    print("="*50)
    
    required_vars = [
        'TOKEN_URL',
        'API_KEY', 
        'API_SECRET',
        'GOOGLE_SHEETS_URL'
    ]
    
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                masked_value = value[:8] + '*' * (len(value) - 12) + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    print(f"\n📊 Summary: {'✅ All variables set' if all_set else '❌ Some variables missing'}")
    return all_set

def test_token_url():
    """Test if TOKEN_URL is accessible."""
    import requests
    
    token_url = os.getenv('TOKEN_URL')
    if not token_url:
        print("❌ TOKEN_URL not set")
        return False
    
    print(f"\n🌐 Testing TOKEN_URL: {token_url}")
    
    try:
        # Test if URL is reachable
        response = requests.get(token_url, timeout=10)
        print(f"✅ URL is reachable: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ URL not reachable: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Environment Variables Test")
    print("="*50)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test token URL if available
    if env_ok:
        test_token_url()
    
    if env_ok:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
