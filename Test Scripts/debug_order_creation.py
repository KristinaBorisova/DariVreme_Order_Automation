#!/usr/bin/env python3
"""
debug_order_creation.py
Debug the order creation process to see why client details are showing as Unknown.
"""

import os
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def debug_order_creation_flow():
    """Debug the order creation flow to find where client details are lost."""
    print("🔍 Debugging Order Creation Flow")
    print("="*50)
    
    try:
        from step_2_quota_Config.sheet_to_json import load_workbook_to_dict
        
        # Load the Google Sheets data
        google_sheets_url = os.getenv('GOOGLE_SHEETS_URL', 'https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit')
        
        print(f"📊 Loading data from Google Sheets...")
        workbook = load_workbook_to_dict(google_sheets_url)
        
        if 'FINAL_ORDERS' not in workbook:
            print("❌ FINAL_ORDERS sheet not found!")
            return False
        
        orders = workbook['FINAL_ORDERS']
        print(f"✅ Loaded {len(orders)} orders from FINAL_ORDERS sheet")
        
        # Test with the first order
        test_order = orders[0]
        print(f"\n📋 Test order from Excel:")
        print(f"   Client ID: {test_order.get('client_id', 'MISSING')}")
        print(f"   Client Name: {test_order.get('client_name', 'MISSING')}")
        print(f"   Client Phone: {test_order.get('client_phone', 'MISSING')}")
        print(f"   Client Email: {test_order.get('client_email', 'MISSING')}")
        
        # Simulate successful quote creation (as it would happen in real scenario)
        print(f"\n🔍 Simulating successful quote creation...")
        
        # This is what the quote creation process creates
        mock_quote_success = {
            "index": 1,
            "row": test_order,
            "response": {
                "quoteId": "99da5a06-90f5-499c-a1b1-02254337d905"  # Real quote ID from your output
            },
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
                "delivery_frequency": test_order.get("deliveryFrequency", 0),
                "pickup_code": test_order.get("pickup_code", ""),
                "city": test_order.get("ADDRESS_CITY_NAME", ""),
                "country": test_order.get("ADDRESS_COUNTRY", ""),
                "postal_code": test_order.get("Address_postal_code", "")
            }
        }
        
        print(f"✅ Mock quote success created:")
        print(f"   Quote ID: {mock_quote_success['response']['quoteId']}")
        print(f"   Client Details: {mock_quote_success['client_details']}")
        print(f"   Restaurant Details: {mock_quote_success['restaurant_details']}")
        print(f"   Order Details: {mock_quote_success['order_details']}")
        
        # Test the daily automation data extraction (this is where the issue might be)
        print(f"\n🔍 Testing daily automation data extraction...")
        
        # This is what daily_delivery_automation.py does
        quote_data = {
            "quote_id": mock_quote_success['response']['quoteId'],
            "original_row": mock_quote_success['row'],
            "quote_response": mock_quote_success['response'],
            "client_details": mock_quote_success.get('client_details', {}),
            "restaurant_details": mock_quote_success.get('restaurant_details', {}),
            "order_details": mock_quote_success.get('order_details', {}),
            "index": 0
        }
        
        print(f"✅ Quote data extracted by daily automation:")
        print(f"   Quote ID: {quote_data['quote_id']}")
        print(f"   Client Details: {quote_data['client_details']}")
        print(f"   Restaurant Details: {quote_data['restaurant_details']}")
        print(f"   Order Details: {quote_data['order_details']}")
        
        # Test the order creation process
        print(f"\n🔍 Testing order creation process...")
        
        # This is what process_orders_from_quotes_final does
        client_details = quote_data.get("client_details", {})
        restaurant_details = quote_data.get("restaurant_details", {})
        order_details = quote_data.get("order_details", {})
        
        print(f"   Extracted client_details: {client_details}")
        print(f"   Extracted restaurant_details: {restaurant_details}")
        print(f"   Extracted order_details: {order_details}")
        
        # Test the order payload creation
        print(f"\n🔍 Testing order payload creation...")
        
        from send_order_with_quote_id_final import create_order_payload
        
        try:
            payload = create_order_payload(quote_data, client_details)
            print(f"✅ Order payload created successfully:")
            print(f"   Contact Name: {payload['contact']['name']}")
            print(f"   Contact Phone: {payload['contact']['phone']}")
            print(f"   Contact Email: {payload['contact']['email']}")
            print(f"   Pickup Code: {payload['pickupOrderCode']}")
            print(f"   Package Description: {payload['packageDetails']['description']}")
            
            # Check if we have the right data
            if payload['contact']['name'] == test_order.get('client_name'):
                print("✅ SUCCESS: Client name correctly extracted from Excel!")
            else:
                print(f"❌ FAIL: Expected '{test_order.get('client_name')}', got '{payload['contact']['name']}'")
                return False
                
        except Exception as e:
            print(f"❌ Order payload creation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function."""
    print("🚀 Order Creation Debug")
    print("="*60)
    print(f"📅 Debug run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    success = debug_order_creation_flow()
    
    print("\n" + "="*60)
    print("📊 DEBUG SUMMARY")
    print("="*60)
    
    if success:
        print("✅ Order creation flow is working correctly!")
        print("   The issue might be in the actual API calls or token expiration.")
        return 0
    else:
        print("❌ Order creation flow has issues!")
        print("   Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())
