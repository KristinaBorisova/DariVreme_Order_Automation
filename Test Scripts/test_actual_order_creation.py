#!/usr/bin/env python3
"""
test_actual_order_creation.py
Test the actual order creation process with real data to see where client details are lost.
"""

import os
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_3_send_order_with_quotaID'))

def test_actual_order_creation():
    """Test the actual order creation process with real data."""
    print("🧪 Testing Actual Order Creation Process")
    print("="*50)
    
    try:
        # Test 1: Load real data from Excel
        print("1️⃣ Loading real data from Excel...")
        from step_2_quota_Config.sheet_to_json import load_workbook_to_dict
        
        google_sheets_url = os.getenv('GOOGLE_SHEETS_URL', 'https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit')
        workbook = load_workbook_to_dict(google_sheets_url)
        orders = workbook['FINAL_ORDERS']
        
        print(f"✅ Loaded {len(orders)} orders from Excel")
        
        # Test 2: Simulate quote creation with real data
        print("\n2️⃣ Simulating quote creation with real data...")
        test_order = orders[0]
        
        print(f"   Excel data:")
        print(f"     client_id: {test_order.get('client_id', 'MISSING')}")
        print(f"     client_name: {test_order.get('client_name', 'MISSING')}")
        print(f"     client_phone: {test_order.get('client_phone', 'MISSING')}")
        print(f"     client_email: {test_order.get('client_email', 'MISSING')}")
        
        # Simulate what happens in quote creation
        mock_quote_success = {
            "index": 1,
            "row": test_order,
            "response": {"quoteId": "test-quote-123"},
            "client_details": {
                "client_id": test_order.get("client_id", ""),
                "name": test_order.get("client_name", ""),
                "phone": test_order.get("client_phone", ""),
                "email": test_order.get("client_email", "")
            },
            "restaurant_details": {
                "name": test_order.get("restaurant_name", ""),
                "pickup_address_book_id": test_order.get("pickupAddressBookId", "")
            },
            "order_details": {
                "order_description": test_order.get("order_id", ""),
                "delivery_frequency": test_order.get("deliveryFrequency", 0)
            }
        }
        
        print(f"   Quote success data:")
        print(f"     client_details: {mock_quote_success['client_details']}")
        
        # Test 3: Simulate daily automation data extraction
        print("\n3️⃣ Simulating daily automation data extraction...")
        quote_data = {
            "quote_id": mock_quote_success['response']['quoteId'],
            "original_row": mock_quote_success['row'],
            "quote_response": mock_quote_success['response'],
            "client_details": mock_quote_success.get('client_details', {}),
            "restaurant_details": mock_quote_success.get('restaurant_details', {}),
            "order_details": mock_quote_success.get('order_details', {}),
            "index": 0
        }
        
        print(f"   Quote data for order creation:")
        print(f"     client_details: {quote_data['client_details']}")
        
        # Test 4: Test order payload creation
        print("\n4️⃣ Testing order payload creation...")
        from send_order_with_quote_id_final import create_order_payload
        
        try:
            payload = create_order_payload(quote_data, quote_data['client_details'])
            print(f"   Order payload created:")
            print(f"     Contact Name: {payload['contact']['name']}")
            print(f"     Contact Phone: {payload['contact']['phone']}")
            print(f"     Contact Email: {payload['contact']['email']}")
            
            # Check if we got the right data
            expected_name = test_order.get('client_name', '')
            actual_name = payload['contact']['name']
            
            if actual_name == expected_name:
                print("✅ SUCCESS: Client name correctly extracted!")
            else:
                print(f"❌ FAIL: Expected '{expected_name}', got '{actual_name}'")
                return False
                
        except Exception as e:
            print(f"❌ Order payload creation failed: {e}")
            return False
        
        # Test 5: Check if there are any empty client details
        print("\n5️⃣ Checking for empty client details...")
        client_details = quote_data['client_details']
        
        if not client_details.get('name'):
            print("❌ Client name is empty!")
            return False
        if not client_details.get('phone'):
            print("❌ Client phone is empty!")
            return False
        if not client_details.get('email'):
            print("❌ Client email is empty!")
            return False
            
        print("✅ All client details are present")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🚀 Actual Order Creation Test")
    print("="*60)
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    success = test_actual_order_creation()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    if success:
        print("✅ Order creation process is working correctly!")
        print("   The issue might be in the actual API calls or token expiration.")
        return 0
    else:
        print("❌ Order creation process has issues!")
        print("   Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())
