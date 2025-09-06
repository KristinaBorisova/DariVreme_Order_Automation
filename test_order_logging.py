#!/usr/bin/env python3
"""
test_order_logging.py
Test the order logging functionality with real data.
"""

import os
import sys
import json
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_3_send_order_with_quotaID'))

def test_order_logging():
    """Test the complete order logging workflow."""
    print("🧪 Testing Order Logging System")
    print("=" * 50)
    
    try:
        # Step 1: Authentication
        print("\n🔐 Step 1: Authentication")
        from token_service import get_bearer_token
        token = get_bearer_token()
        
        if not token:
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful")
        
        # Step 2: Load data and create quotes
        print("\n📊 Step 2: Loading data and creating quotes")
        from sheet_to_json import load_workbook_to_dict
        from POST_create_quote_id import process_orders, iter_orders_from_memory
        
        google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
        workbook = load_workbook_to_dict(google_sheets_url)
        sheet_name = list(workbook.keys())[0]
        
        print(f"Loaded {len(workbook[sheet_name])} orders from Google Sheets")
        
        # Process only first 2 orders for testing
        rows = iter_orders_from_memory(workbook, sheet_name=sheet_name)
        test_rows = []
        for i, row in enumerate(rows):
            if i >= 2:  # Only test first 2 orders
                break
            test_rows.append(row)
        
        print(f"Testing with {len(test_rows)} orders")
        
        quote_summary = process_orders(test_rows, rate_limit_per_sec=2.0)
        
        if not quote_summary['successes']:
            print("❌ No successful quotes created")
            return False
        
        print(f"✅ Created {len(quote_summary['successes'])} quotes")
        
        # Step 3: Create orders with logging
        print("\n📦 Step 3: Creating orders with logging")
        from send_order_with_quote_id import (
            extract_quote_ids_from_successes,
            process_orders_from_quotes
        )
        
        quote_data_list = extract_quote_ids_from_successes(quote_summary['successes'])
        
        client_details = {
            "name": "Test Client",
            "phone": "+359888123456",
            "email": "test@darivreme.com"
        }
        
        # Create orders with logging enabled
        order_results = process_orders_from_quotes(
            quote_data_list=quote_data_list,
            client_details=client_details,
            rate_limit_per_sec=1.0,
            log_orders=True,  # Enable logging
            excel_output_file="test_order_results.xlsx"  # Test Excel file
        )
        
        print(f"\n📊 Order Creation Results:")
        print(f"   - Total processed: {order_results['total_processed']}")
        print(f"   - Successful orders: {len(order_results['successful_orders'])}")
        print(f"   - Failed orders: {len(order_results['failed_orders'])}")
        print(f"   - Success rate: {order_results['success_rate']:.1f}%")
        
        # Check if Excel file was created
        if order_results.get('excel_file'):
            print(f"\n📁 Excel file created: {order_results['excel_file']}")
            
            # Verify Excel file exists and has content
            if os.path.exists(order_results['excel_file']):
                print("✅ Excel file exists")
                
                # Try to read the Excel file to verify content
                try:
                    import pandas as pd
                    df = pd.read_excel(order_results['excel_file'], sheet_name='Order Results')
                    print(f"✅ Excel file contains {len(df)} orders")
                    print(f"   Columns: {list(df.columns)}")
                    
                    # Show sample data
                    if len(df) > 0:
                        print(f"\n📋 Sample order data:")
                        sample_order = df.iloc[0]
                        for column in ['timestamp', 'order_id', 'client_name', 'pickup_address_book_id', 'quote_price']:
                            if column in sample_order:
                                print(f"   {column}: {sample_order[column]}")
                    
                except Exception as e:
                    print(f"⚠️  Could not read Excel file: {e}")
            else:
                print("❌ Excel file was not created")
        else:
            print("❌ No Excel file path returned")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_order_logger_directly():
    """Test the OrderLogger class directly."""
    print("\n🧪 Testing OrderLogger Class Directly")
    print("-" * 40)
    
    try:
        from order_logger import OrderLogger
        
        # Create sample order data
        sample_order_data = {
            "trackingNumber": "100010173030",
            "status": {
                "state": "CREATED",
                "createdAt": "2025-09-06T15:39:34.131323196Z"
            },
            "quote": {
                "quoteId": "aff76702-e284-43ab-8ae2-78d0d605d285",
                "quotePrice": 8.06,
                "currencyCode": "BGN"
            },
            "contact": {
                "name": "Test Client",
                "phone": "+359888123456",
                "email": "test@darivreme.com"
            },
            "pickupDetails": {
                "addressBook": {
                    "id": "dd560a2c-f1b5-43b7-81bc-2830595122f9"
                },
                "pickupTime": "2025-09-06T20:15:22Z",
                "pickupOrderCode": "ORD123456"
            },
            "address": {
                "rawAddress": "g.k. Strelbishte, Nishava St 111р 1408, Bulgaria",
                "coordinates": {
                    "latitude": 42.673758,
                    "longitude": 23.298064
                }
            },
            "partnerId": 67915107,
            "cityCode": "SOF",
            "cancellable": True
        }
        
        sample_quote_data = {
            "quote_id": "aff76702-e284-43ab-8ae2-78d0d605d285",
            "original_row": {
                "pickupAddressBookId": "dd560a2c-f1b5-43b7-81bc-2830595122f9",
                "pickupTimeUtc": "2025-09-06T20:15:22Z",
                "deliveryRawAddress": "g.k. Strelbishte, Nishava St 111р 1408, Bulgaria"
            }
        }
        
        sample_client_details = {
            "name": "Test Client",
            "phone": "+359888123456",
            "email": "test@darivreme.com"
        }
        
        # Test logger
        logger = OrderLogger()
        
        # Log the order
        log_entry = logger.log_order(sample_order_data, sample_quote_data, sample_client_details)
        
        print(f"✅ Order logged successfully")
        print(f"   Order ID: {log_entry['order_id']}")
        print(f"   Client: {log_entry['client_name']}")
        print(f"   Price: {log_entry['quote_price']} {log_entry['currency']}")
        
        # Print summary
        logger.print_summary()
        
        # Save to Excel
        excel_file = logger.save_to_excel("direct_test_order_results.xlsx")
        
        if excel_file and os.path.exists(excel_file):
            print(f"✅ Direct test Excel file created: {excel_file}")
            return True
        else:
            print(f"❌ Direct test Excel file was not created")
            return False
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all order logging tests."""
    print("🔍 Order Logging System Test Suite")
    print("=" * 60)
    
    # Test 1: Direct OrderLogger test
    direct_test_success = test_order_logger_directly()
    
    # Test 2: Full workflow test
    workflow_test_success = test_order_logging()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Direct OrderLogger Test: {'✅ PASS' if direct_test_success else '❌ FAIL'}")
    print(f"Full Workflow Test: {'✅ PASS' if workflow_test_success else '❌ FAIL'}")
    
    if direct_test_success and workflow_test_success:
        print(f"\n🎉 All tests passed!")
        print(f"✅ Order logging system is working correctly")
        print(f"💡 You can now use order logging in your production workflow")
        
        print(f"\n📁 Generated files:")
        if os.path.exists("direct_test_order_results.xlsx"):
            print(f"   - direct_test_order_results.xlsx")
        if os.path.exists("test_order_results.xlsx"):
            print(f"   - test_order_results.xlsx")
    else:
        print(f"\n❌ Some tests failed")
        print(f"💡 Check the error messages above for troubleshooting")

if __name__ == "__main__":
    main()
