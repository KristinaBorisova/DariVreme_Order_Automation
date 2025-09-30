#!/usr/bin/env python3
"""
test_automation.py
Test script for the daily delivery automation system.
Tests environment variables, authentication, and basic functionality.
"""

import os
import sys
from datetime import datetime

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
                print(f"✅ {var}: {masked_value} (length: {len(value)})")
            else:
                print(f"✅ {var}: {value} (length: {len(value)})")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    print(f"\n📊 Environment Variables: {'✅ All set' if all_set else '❌ Some missing'}")
    return all_set

def test_authentication():
    """Test authentication with Glovo API."""
    print("\n🔐 Testing Authentication")
    print("="*50)
    
    try:
        # Add path for imports
        sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
        from token_service import get_bearer_token
        
        print("📤 Requesting bearer token...")
        token = get_bearer_token()
        
        if token and len(token) > 10:  # Basic token validation
            print(f"✅ Authentication successful!")
            print(f"🔑 Token length: {len(token)} characters")
            print(f"🔑 Token preview: {token[:20]}...{token[-10:]}")
            return True
        else:
            print("❌ Authentication failed: Invalid token received")
            return False
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_pickup_time_generation():
    """Test pickup time generation utilities."""
    print("\n⏰ Testing Pickup Time Generation")
    print("="*50)
    
    try:
        from fix_pickup_times import get_future_pickup_time, validate_pickup_time
        
        # Test future pickup time generation
        pickup_time = get_future_pickup_time(hours_ahead=2)
        print(f"✅ Generated pickup time: {pickup_time}")
        
        # Test validation
        is_valid = validate_pickup_time(pickup_time)
        print(f"✅ Pickup time validation: {'Valid' if is_valid else 'Invalid'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pickup time generation failed: {e}")
        return False

def test_google_sheets_connection():
    """Test Google Sheets connection."""
    print("\n📊 Testing Google Sheets Connection")
    print("="*50)
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))
        from sheet_to_json import load_workbook_to_dict
        
        google_sheets_url = os.getenv('GOOGLE_SHEETS_URL')
        if not google_sheets_url:
            print("❌ GOOGLE_SHEETS_URL not set")
            return False
        
        print(f"📤 Connecting to Google Sheets...")
        print(f"🔗 URL: {google_sheets_url[:50]}...")
        
        workbook = load_workbook_to_dict(google_sheets_url)
        
        if 'FINAL_ORDERS' in workbook:
            orders = workbook['FINAL_ORDERS']
            print(f"✅ Successfully connected to Google Sheets")
            print(f"📋 Found {len(orders)} orders in FINAL_ORDERS sheet")
            return True
        else:
            print(f"❌ FINAL_ORDERS sheet not found")
            print(f"📋 Available sheets: {list(workbook.keys())}")
            return False
            
    except Exception as e:
        print(f"❌ Google Sheets connection failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Daily Delivery Automation - Test Suite")
    print("="*60)
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run all tests
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Authentication", test_authentication),
        ("Pickup Time Generation", test_pickup_time_generation),
        ("Google Sheets Connection", test_google_sheets_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for automation.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    exit(main())
