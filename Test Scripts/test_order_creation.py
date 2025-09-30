#!/usr/bin/env python3
"""
test_order_creation.py
Test script to verify order creation is working properly.
"""

import os
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_3_send_order_with_quotaID'))

def test_order_creation_flow():
    """Test the complete order creation flow."""
    print("🧪 Testing Order Creation Flow")
    print("="*50)
    
    try:
        # Test 1: Authentication
        print("1️⃣ Testing Authentication...")
        from token_service import get_bearer_token
        token = get_bearer_token()
        if not token:
            print("❌ Authentication failed")
            return False
        print("✅ Authentication successful")
        
        # Test 2: Quote Creation
        print("\n2️⃣ Testing Quote Creation...")
        from POST_create_quote_id_final import process_orders_final
        
        # Create a test order
        test_order = {
            "client_id": "TEST001",
            "client_name": "Test Client",
            "client_phone": "+1234567890",
            "client_email": "test@example.com",
            "deliveryRawAddress": "123 Test Street, Test City",
            "deliveryLattitude": "40.7128",
            "deliveryLongitude": "-74.0060",
            "pickupAddressBookId": "12345678-1234-1234-1234-123456789012",
            "restaurant_name": "Test Restaurant",
            "order_id": "Test Order Description",
            "deliveryFrequency": 3
        }
        
        print(f"   📋 Test order: {test_order['client_name']} - {test_order['order_id']}")
        
        # Create quote
        quote_results = process_orders_final([test_order], rate_limit_per_sec=1.0)
        
        if not quote_results['successes']:
            print("❌ Quote creation failed")
            print(f"   Errors: {quote_results['failures']}")
            return False
        
        print(f"✅ Quote created successfully: {quote_results['successes'][0]['response']['quoteId']}")
        
        # Test 3: Order Creation
        print("\n3️⃣ Testing Order Creation...")
        from send_order_with_quote_id_final import process_orders_from_quotes_final
        
        # Extract quote data (simulating daily automation)
        success = quote_results['successes'][0]
        quote_data = {
            "quote_id": success['response']['quoteId'],
            "original_row": success['row'],
            "quote_response": success['response'],
            "client_details": success.get('client_details', {}),
            "restaurant_details": success.get('restaurant_details', {}),
            "order_details": success.get('order_details', {}),
            "index": 0
        }
        
        print(f"   📋 Quote data structure:")
        print(f"      Client details: {quote_data['client_details']}")
        print(f"      Restaurant details: {quote_data['restaurant_details']}")
        print(f"      Order details: {quote_data['order_details']}")
        
        # Create order
        order_results = process_orders_from_quotes_final(
            quote_data_list=[quote_data],
            rate_limit_per_sec=1.0,
            log_orders=False  # Disable logging for test
        )
        
        if order_results['successful_orders']:
            order = order_results['successful_orders'][0]
            client_details = order.get('client_details', {})
            order_response = order.get('order_response', {})
            
            print("✅ Order creation successful!")
            print(f"   Client: {client_details.get('name', 'Unknown')}")
            print(f"   Glovo Order ID: {order_response.get('id', 'N/A')}")
            print(f"   Pickup Code: {order.get('pickup_order_code', 'N/A')}")
            return True
        else:
            print("❌ Order creation failed")
            print(f"   Errors: {order_results['failed_orders']}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🚀 Order Creation Test Suite")
    print("="*60)
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    success = test_order_creation_flow()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    if success:
        print("✅ All tests passed! Order creation is working properly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())
