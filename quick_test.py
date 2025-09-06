#!/usr/bin/env python3
"""
quick_test.py
Quick test script to verify the complete workflow with minimal setup.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 Checking environment...")
    
    # Check if token is set
    token = os.getenv("GLOVO_TOKEN")
    if not token or token == "YOUR_BEARER_TOKEN_HERE":
        print("❌ GLOVO_TOKEN not set. Please run:")
        print("   export GLOVO_TOKEN='your_actual_token_here'")
        return False
    print("✅ GLOVO_TOKEN is set")
    
    # Check Python dependencies
    try:
        import requests
        import pandas
        print("✅ Required dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install requests pandas openpyxl")
        return False
    
    return True

def create_test_data():
    """Create test data for the workflow."""
    print("\n📝 Creating test data...")
    
    # Create test orders
    test_orders = [
        {
            "pickup_address_id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "pickup_time_utc": "2024-12-20T15:30:00Z",  # Future time
            "dest_raw_address": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
            "dest_lat": 41.39637,
            "dest_lng": 2.17939,
            "dest_details": "Floor 6 Door 3"
        },
        {
            "pickup_address_id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "pickup_time_utc": "2024-12-20T16:00:00Z",  # Future time
            "dest_raw_address": "Passeig de Gràcia, 1, L'Eixample, 08008 Barcelona",
            "dest_lat": 41.3851,
            "dest_lng": 2.1734,
            "dest_details": "Main entrance"
        }
    ]
    
    # Save as workbook format
    workbook = {"Orders": test_orders}
    
    with open("test_workbook.json", "w", encoding="utf-8") as f:
        json.dump(workbook, f, ensure_ascii=False, indent=2)
    
    print("✅ Test data created: test_workbook.json")
    return True

def test_authentication():
    """Test authentication."""
    print("\n🔐 Testing authentication...")
    
    try:
        # Import and test token service
        sys.path.append("step_1_authentication")
        from token_service import get_bearer_token
        
        token = get_bearer_token()
        if token and len(token) > 10:
            print("✅ Authentication successful")
            return True
        else:
            print("❌ Authentication failed - invalid token")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def test_quote_creation():
    """Test quote creation."""
    print("\n💰 Testing quote creation...")
    
    try:
        # Modify the POST script to use our test data
        import sys
        sys.path.append("step_2_quota_Config")
        
        # Import the necessary functions
        from POST_create_quote_id import process_orders, iter_orders_from_file
        
        # Process test data
        rows = iter_orders_from_file("test_workbook.json", sheet_name="Orders")
        summary = process_orders(rows, rate_limit_per_sec=2.0)
        
        if summary["successes"]:
            print(f"✅ Quote creation successful: {len(summary['successes'])} quotes created")
            return True
        else:
            print(f"❌ Quote creation failed: {len(summary['failures'])} failures")
            if summary["failures"]:
                print("   Sample error:", summary["failures"][0].get("reason", "Unknown error"))
            return False
    except Exception as e:
        print(f"❌ Quote creation error: {e}")
        return False

def test_order_creation():
    """Test order creation."""
    print("\n📦 Testing order creation...")
    
    try:
        # Check if quote results exist
        if not os.path.exists("quote_results.json"):
            print("❌ Quote results not found. Run quote creation first.")
            return False
        
        # Import order creation functions
        sys.path.append("step_3_send_order_with_quotaID")
        from send_order_with_quote_id import (
            load_quote_successes_from_file,
            extract_quote_ids_from_successes,
            process_orders_from_quotes
        )
        
        # Load and process quotes
        successes = load_quote_successes_from_file("quote_results.json")
        quote_data_list = extract_quote_ids_from_successes(successes)
        
        if not quote_data_list:
            print("❌ No valid quote IDs found")
            return False
        
        # Create orders
        client_details = {
            "name": "Test Client",
            "phone": "+1234567890",
            "email": "test@example.com"
        }
        
        results = process_orders_from_quotes(
            quote_data_list=quote_data_list,
            client_details=client_details,
            rate_limit_per_sec=1.0  # Slower for testing
        )
        
        if results["successful_orders"]:
            print(f"✅ Order creation successful: {len(results['successful_orders'])} orders created")
            return True
        else:
            print(f"❌ Order creation failed: {len(results['failed_orders'])} failures")
            if results["failed_orders"]:
                print("   Sample error:", results["failed_orders"][0].get("error", "Unknown error"))
            return False
    except Exception as e:
        print(f"❌ Order creation error: {e}")
        return False

def cleanup():
    """Clean up test files."""
    print("\n🧹 Cleaning up test files...")
    
    test_files = [
        "test_workbook.json",
        "quote_results.json",
        "order_results.json",
        "complete_workflow_results.json"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed: {file}")
    
    print("✅ Cleanup completed")

def main():
    """Run the quick test."""
    print("🚀 Glovo Automation - Quick Test")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return False
    
    # Create test data
    if not create_test_data():
        print("\n❌ Test data creation failed.")
        return False
    
    # Test each step
    steps = [
        ("Authentication", test_authentication),
        ("Quote Creation", test_quote_creation),
        ("Order Creation", test_order_creation)
    ]
    
    results = {}
    for step_name, test_func in steps:
        try:
            results[step_name] = test_func()
        except Exception as e:
            print(f"❌ {step_name} test crashed: {e}")
            results[step_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for step_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {step_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your automation is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Prepare your real data (Excel/Google Sheets)")
        print("   2. Update pickup_address_id with real values")
        print("   3. Run the complete workflow with production data")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("\n💡 Troubleshooting:")
        print("   1. Verify your GLOVO_TOKEN is valid")
        print("   2. Check your internet connection")
        print("   3. Ensure pickup_address_id is valid")
        print("   4. Make sure pickup times are in the future")
    
    # Ask about cleanup
    try:
        cleanup_choice = input("\n🧹 Clean up test files? (y/n): ").lower().strip()
        if cleanup_choice in ['y', 'yes']:
            cleanup()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
