#!/usr/bin/env python3
"""
test_github_actions.py
Test script to verify GitHub Actions setup and environment variables.
"""

import os
import sys
from datetime import datetime

def test_environment_variables():
    """Test if all required environment variables are set."""
    print("🧪 Testing GitHub Actions Environment Variables")
    print("="*60)
    
    required_vars = [
        'TOKEN_URL',
        'API_KEY', 
        'API_SECRET',
        'GOOGLE_SHEETS_URL'
    ]
    
    missing_vars = []
    present_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            present_vars.append(var)
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
    
    print(f"\n📊 Summary:")
    print(f"   Present: {len(present_vars)}/{len(required_vars)}")
    print(f"   Missing: {len(missing_vars)}")
    
    if missing_vars:
        print(f"\n⚠️  Missing variables: {', '.join(missing_vars)}")
        print("   Please set these as GitHub Secrets:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    else:
        print(f"\n✅ All environment variables are set!")
        return True

def test_imports():
    """Test if all required modules can be imported."""
    print("\n🧪 Testing Module Imports")
    print("="*60)
    
    modules_to_test = [
        'requests',
        'pandas', 
        'openpyxl',
        'gspread',
        'google.auth',
        'json',
        'datetime',
        'os',
        'sys'
    ]
    
    failed_imports = []
    successful_imports = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            successful_imports.append(module)
            print(f"✅ {module}")
        except ImportError as e:
            failed_imports.append(module)
            print(f"❌ {module}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Successful: {len(successful_imports)}/{len(modules_to_test)}")
    print(f"   Failed: {len(failed_imports)}")
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        print("   Please install missing packages:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print(f"\n✅ All modules imported successfully!")
        return True

def test_automation_script():
    """Test if the automation script can be imported and run."""
    print("\n🧪 Testing Automation Script")
    print("="*60)
    
    try:
        # Test import
        from daily_delivery_automation import DailyDeliveryAutomation
        print("✅ DailyDeliveryAutomation imported successfully")
        
        # Test initialization
        automation = DailyDeliveryAutomation(
            "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004",
            "FINAL_ORDERS"
        )
        print("✅ DailyDeliveryAutomation initialized successfully")
        
        # Test data loading
        if automation.load_data():
            print("✅ Data loading successful")
        else:
            print("❌ Data loading failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing automation script: {e}")
        return False

def test_authentication():
    """Test authentication with Glovo API."""
    print("\n🧪 Testing Authentication")
    print("="*60)
    
    try:
        from step_1_authentication.token_service import get_bearer_token
        
        token = get_bearer_token()
        if token:
            print("✅ Authentication successful")
            print(f"   Token: {token[:20]}...")
            return True
        else:
            print("❌ Authentication failed - no token received")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 GitHub Actions Setup Test")
    print("="*60)
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Module Imports", test_imports),
        ("Automation Script", test_automation_script),
        ("Authentication", test_authentication)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! GitHub Actions setup is ready!")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    exit(main())
