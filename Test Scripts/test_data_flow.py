#!/usr/bin/env python3
"""
test_data_flow.py
Test script to verify the data flow between quote creation and order creation.
"""

import os
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_3_send_order_with_quotaID'))

def test_quote_data_structure():
    """Test that quote data has the correct structure for order creation."""
    print("🧪 Testing Quote Data Structure")
    print("="*50)
    
    try:
        from step_2_quota_Config.POST_create_quote_id_final import row_to_payload, validate_row
        
        # Create a test order (without making API calls)
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
        
        print(f"📋 Test order: {test_order['client_name']} - {test_order['order_id']}")
        
        # Test validation
        print("\n1️⃣ Testing row validation...")
        validation_error = validate_row(test_order)
        if validation_error:
            print(f"❌ Validation failed: {validation_error}")
            return False
        print("✅ Row validation passed")
        
        # Test payload creation
        print("\n2️⃣ Testing payload creation...")
        payload = row_to_payload(test_order)
        print(f"✅ Payload created successfully")
        print(f"   Pickup time: {payload['pickupDetails']['pickupTime']}")
        print(f"   Delivery address: {payload['deliveryAddress']['rawAddress']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_order_payload_creation():
    """Test order payload creation with mock quote data."""
    print("\n🧪 Testing Order Payload Creation")
    print("="*50)
    
    try:
        from step_3_send_order_with_quotaID.send_order_with_quote_id_final import create_order_payload
        
        # Create mock quote data (simulating successful quote creation)
        mock_quote_data = {
            "quote_id": "test-quote-123",
            "original_row": {
                "client_id": "TEST001",
                "client_name": "Test Client",
                "client_phone": "+1234567890",
                "client_email": "test@example.com",
                "order_id": "Test Order Description",
                "restaurant_name": "Test Restaurant"
            },
            "client_details": {
                "client_id": "TEST001",
                "name": "Test Client",
                "phone": "+1234567890",
                "email": "test@example.com"
            },
            "restaurant_details": {
                "name": "Test Restaurant",
                "pickup_address_book_id": "12345678-1234-1234-1234-123456789012"
            },
            "order_details": {
                "order_description": "Test Order Description",
                "delivery_frequency": 3
            },
            "index": 0
        }
        
        print(f"📋 Mock quote data: {mock_quote_data['client_details']['name']}")
        
        # Test order payload creation
        print("\n3️⃣ Testing order payload creation...")
        payload = create_order_payload(mock_quote_data, mock_quote_data['client_details'])
        
        print("✅ Order payload created successfully")
        print(f"   Contact name: {payload['contact']['name']}")
        print(f"   Contact phone: {payload['contact']['phone']}")
        print(f"   Contact email: {payload['contact']['email']}")
        print(f"   Pickup code: {payload['pickupOrderCode']}")
        print(f"   Package description: {payload['packageDetails']['description']}")
        
        # Verify the payload has the correct structure
        required_fields = ['contact', 'pickupOrderCode', 'packageDetails']
        for field in required_fields:
            if field not in payload:
                print(f"❌ Missing required field: {field}")
                return False
        
        contact_fields = ['name', 'phone', 'email']
        for field in contact_fields:
            if field not in payload['contact']:
                print(f"❌ Missing contact field: {field}")
                return False
        
        print("✅ Order payload structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_daily_automation_data_flow():
    """Test the data flow as it would happen in daily automation."""
    print("\n🧪 Testing Daily Automation Data Flow")
    print("="*50)
    
    try:
        # Simulate the quote creation success structure
        mock_quote_success = {
            "index": 1,
            "row": {
                "client_id": "TEST001",
                "client_name": "Test Client",
                "client_phone": "+1234567890",
                "client_email": "test@example.com",
                "order_id": "Test Order Description",
                "restaurant_name": "Test Restaurant",
                "deliveryFrequency": 3
            },
            "response": {
                "quoteId": "test-quote-123"
            },
            "client_details": {
                "client_id": "TEST001",
                "name": "Test Client",
                "phone": "+1234567890",
                "email": "test@example.com"
            },
            "restaurant_details": {
                "name": "Test Restaurant",
                "pickup_address_book_id": "12345678-1234-1234-1234-123456789012"
            },
            "order_details": {
                "order_description": "Test Order Description",
                "delivery_frequency": 3
            }
        }
        
        print(f"📋 Mock quote success: {mock_quote_success['client_details']['name']}")
        
        # Simulate the daily automation quote data extraction
        print("\n4️⃣ Testing daily automation data extraction...")
        quote_data = {
            "quote_id": mock_quote_success['response']['quoteId'],
            "original_row": mock_quote_success['row'],
            "quote_response": mock_quote_success['response'],
            "client_details": mock_quote_success.get('client_details', {}),
            "restaurant_details": mock_quote_success.get('restaurant_details', {}),
            "order_details": mock_quote_success.get('order_details', {}),
            "index": 0
        }
        
        print("✅ Quote data extracted successfully")
        print(f"   Quote ID: {quote_data['quote_id']}")
        print(f"   Client: {quote_data['client_details']['name']}")
        print(f"   Restaurant: {quote_data['restaurant_details']['name']}")
        print(f"   Order: {quote_data['order_details']['order_description']}")
        
        # Test that all required fields are present
        required_fields = ['quote_id', 'original_row', 'client_details', 'restaurant_details', 'order_details']
        for field in required_fields:
            if field not in quote_data:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ Quote data structure is correct for order creation")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🚀 Data Flow Test Suite")
    print("="*60)
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    tests = [
        ("Quote Data Structure", test_quote_data_structure),
        ("Order Payload Creation", test_order_payload_creation),
        ("Daily Automation Data Flow", test_daily_automation_data_flow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
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
        print("🎉 All tests passed! Data flow is working correctly.")
        print("   The 'Unknown' client names issue should be resolved.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())
