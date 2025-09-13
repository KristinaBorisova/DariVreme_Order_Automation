#!/usr/bin/env python3
"""
test_with_real_data.py
Test the system with your actual Google Sheets data.
"""

import os
import sys
import json
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))

def test_authentication():
    """Test authentication with your credentials."""
    print("🔐 Testing Authentication")
    print("-" * 30)
    
    try:
        from token_service import get_bearer_token
        token = get_bearer_token()
        
        if token and len(token) > 10:
            print("✅ Authentication successful")
            print(f"   Token: {token[:20]}...")
            return True
        else:
            print("❌ Authentication failed - invalid token")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def test_data_loading():
    """Test loading data from your Google Sheets."""
    print("\n📊 Testing Data Loading")
    print("-" * 30)
    
    try:
        from sheet_to_json import load_workbook_to_dict
        
        # Your actual Google Sheets URL
        google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
        
        print(f"Loading from: {google_sheets_url}")
        workbook = load_workbook_to_dict(google_sheets_url)
        
        # Find the sheet with order data
        sheet_names = list(workbook.keys())
        print(f"Available sheets: {sheet_names}")
        
        # Use the first sheet that contains data
        sheet_name = sheet_names[0] if sheet_names else "Sheet1"
        print(f"Using sheet: {sheet_name}")
        
        if workbook[sheet_name]:
            print(f"✅ Found {len(workbook[sheet_name])} orders")
            
            # Display the first few orders
            print("\n📋 Sample orders:")
            for i, order in enumerate(workbook[sheet_name][:3], 1):
                print(f"\n   Order {i}:")
                for key, value in order.items():
                    print(f"     {key}: {value}")
            
            # Validate data structure
            print("\n🔍 Data validation:")
            required_fields = ["pickupAddressBookId", "pickupTimeUtc", "deliveryRawAddress", "deliveryLatitude", "deliveryLongitude"]
            
            sample_order = workbook[sheet_name][0]
            for field in required_fields:
                if field in sample_order and sample_order[field] is not None:
                    print(f"   ✅ {field}: {sample_order[field]}")
                else:
                    print(f"   ❌ Missing: {field}")
            
            return True, workbook, sheet_name
        else:
            print("❌ No data found in the sheet")
            return False, None, None
            
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def test_quote_creation(workbook, sheet_name):
    """Test quote creation with real data."""
    print("\n💰 Testing Quote Creation")
    print("-" * 30)
    
    try:
        from POST_create_quote_id import process_orders, iter_orders_from_memory
        
        # Process only the first 2 orders for testing
        rows = iter_orders_from_memory(workbook, sheet_name=sheet_name)
        test_rows = []
        for i, row in enumerate(rows):
            if i >= 2:  # Only test first 2 orders
                break
            test_rows.append(row)
        
        print(f"Testing with {len(test_rows)} orders...")
        
        # Process the test orders
        summary = process_orders(test_rows, rate_limit_per_sec=2.0)
        
        print(f"Quote creation results:")
        print(f"   - Total processed: {summary['total']}")
        print(f"   - Successful quotes: {len(summary['successes'])}")
        print(f"   - Failed quotes: {len(summary['failures'])}")
        
        if summary['successes']:
            print("✅ Quote creation successful")
            
            # Show sample success
            success = summary['successes'][0]
            print(f"\n📋 Sample successful quote:")
            print(f"   Quote ID: {success['response'].get('quoteId', 'N/A')}")
            print(f"   Price: {success['response'].get('quotePrice', 'N/A')}")
            print(f"   Currency: {success['response'].get('currencyCode', 'N/A')}")
            print(f"   Expires: {success['response'].get('expiresAt', 'N/A')}")
            
            return True, summary
        else:
            print("❌ Quote creation failed")
            if summary['failures']:
                print("Sample failure:")
                failure = summary['failures'][0]
                print(f"   Error: {failure.get('reason', 'Unknown error')}")
            return False, summary
            
    except Exception as e:
        print(f"❌ Quote creation error: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_order_creation(quote_summary):
    """Test order creation with quote IDs."""
    print("\n📦 Testing Order Creation")
    print("-" * 30)
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'step_3_send_order_with_quotaID'))
        from send_order_with_quote_id import (
            extract_quote_ids_from_successes,
            process_orders_from_quotes
        )
        
        # Extract quote IDs from successful responses
        quote_data_list = extract_quote_ids_from_successes(quote_summary['successes'])
        print(f"Extracted {len(quote_data_list)} quote IDs")
        
        if not quote_data_list:
            print("❌ No valid quote IDs found")
            return False
        
        # Client details for testing
        client_details = {
            "name": "Test Client",
            "phone": "+359888123456",
            "email": "test@darivreme.com"
        }
        
        print(f"Creating orders with client details:")
        print(f"   Name: {client_details['name']}")
        print(f"   Phone: {client_details['phone']}")
        print(f"   Email: {client_details['email']}")
        
        # Create orders (only test with first quote)
        test_quote_data = quote_data_list[:1]  # Only test first order
        
        results = process_orders_from_quotes(
            quote_data_list=test_quote_data,
            client_details=client_details,
            rate_limit_per_sec=1.0
        )
        
        print(f"Order creation results:")
        print(f"   - Total processed: {results['total_processed']}")
        print(f"   - Successful orders: {len(results['successful_orders'])}")
        print(f"   - Failed orders: {len(results['failed_orders'])}")
        print(f"   - Success rate: {results['success_rate']:.1f}%")
        
        if results['successful_orders']:
            print("✅ Order creation successful")
            
            # Show sample success
            order = results['successful_orders'][0]
            print(f"\n📋 Sample successful order:")
            print(f"   Quote ID: {order['quote_id']}")
            print(f"   Pickup Code: {order['pickup_order_code']}")
            if 'order_response' in order and 'id' in order['order_response']:
                print(f"   Order ID: {order['order_response']['id']}")
            
            return True
        else:
            print("❌ Order creation failed")
            if results['failed_orders']:
                print("Sample failure:")
                failure = results['failed_orders'][0]
                print(f"   Error: {failure.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Order creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the complete test with real data."""
    print("🧪 Glovo DariVreme - Test with Real Data")
    print("=" * 50)
    
    # Test 1: Authentication
    if not test_authentication():
        print("\n❌ Authentication test failed. Cannot proceed.")
        return False
    
    # Test 2: Data loading
    success, workbook, sheet_name = test_data_loading()
    if not success:
        print("\n❌ Data loading test failed. Cannot proceed.")
        return False
    
    # Test 3: Quote creation
    success, quote_summary = test_quote_creation(workbook, sheet_name)
    if not success:
        print("\n❌ Quote creation test failed. Cannot proceed.")
        return False
    
    # Test 4: Order creation
    success = test_order_creation(quote_summary)
    if not success:
        print("\n❌ Order creation test failed.")
        return False
    
    # All tests passed
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 50)
    print("✅ Authentication: Working")
    print("✅ Data loading: Working")
    print("✅ Quote creation: Working")
    print("✅ Order creation: Working")
    
    print("\n💡 Your system is ready for production!")
    print("   Run: python production_workflow.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
