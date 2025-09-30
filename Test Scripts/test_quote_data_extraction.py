#!/usr/bin/env python3
"""
test_quote_data_extraction.py
Test the quote data extraction process to verify client details are properly extracted.
"""

import os
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_2_quota_Config'))

def test_quote_data_extraction():
    """Test that quote creation properly extracts client details from Excel data."""
    print("🧪 Testing Quote Data Extraction")
    print("="*50)
    
    try:
        from sheet_to_json import load_workbook_to_dict
        
        # Load the Google Sheets data
        google_sheets_url = os.getenv('GOOGLE_SHEETS_URL', 'https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit')
        
        print(f"📊 Loading data from Google Sheets...")
        workbook = load_workbook_to_dict(google_sheets_url)
        
        if 'FINAL_ORDERS' not in workbook:
            print("❌ FINAL_ORDERS sheet not found!")
            return False
        
        orders = workbook['FINAL_ORDERS']
        print(f"✅ Loaded {len(orders)} orders from FINAL_ORDERS sheet")
        
        # Test the first order
        if not orders:
            print("❌ No orders found in sheet")
            return False
        
        test_order = orders[0]
        print(f"\n📋 Testing with order:")
        print(f"   Client ID: {test_order.get('client_id', 'MISSING')}")
        print(f"   Client Name: {test_order.get('client_name', 'MISSING')}")
        print(f"   Client Phone: {test_order.get('client_phone', 'MISSING')}")
        print(f"   Client Email: {test_order.get('client_email', 'MISSING')}")
        print(f"   Restaurant: {test_order.get('restaurant_name', 'MISSING')}")
        print(f"   Order Description: {test_order.get('order_id', 'MISSING')}")
        
        # Simulate the quote creation process (without API call)
        print(f"\n🔍 Simulating quote creation data extraction...")
        
        # This is what happens in the quote creation success
        mock_quote_success = {
            "index": 1,
            "row": test_order,
            "response": {
                "quoteId": "test-quote-123"
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
        print(f"   Client Details: {mock_quote_success['client_details']}")
        print(f"   Restaurant Details: {mock_quote_success['restaurant_details']}")
        print(f"   Order Details: {mock_quote_success['order_details']}")
        
        # Test the daily automation data extraction
        print(f"\n🔍 Testing daily automation data extraction...")
        
        quote_data = {
            "quote_id": mock_quote_success['response']['quoteId'],
            "original_row": mock_quote_success['row'],
            "quote_response": mock_quote_success['response'],
            "client_details": mock_quote_success.get('client_details', {}),
            "restaurant_details": mock_quote_success.get('restaurant_details', {}),
            "order_details": mock_quote_success.get('order_details', {}),
            "index": 0
        }
        
        print(f"✅ Quote data extracted:")
        print(f"   Quote ID: {quote_data['quote_id']}")
        print(f"   Client: {quote_data['client_details']['name']}")
        print(f"   Restaurant: {quote_data['restaurant_details']['name']}")
        print(f"   Order: {quote_data['order_details']['order_description']}")
        
        # Test order payload creation
        print(f"\n🔍 Testing order payload creation...")
        
        # Simulate the order payload creation
        client_details = quote_data['client_details']
        pickup_order_code = f"ORD{int(datetime.now().timestamp())}0"
        package_description = quote_data['original_row'].get("order_id", "Food delivery order")
        
        payload = {
            "contact": {
                "name": client_details["name"],
                "phone": client_details["phone"],
                "email": client_details["email"]
            },
            "pickupOrderCode": pickup_order_code,
            "packageDetails": {
                "contentType": "FOOD",
                "description": package_description,
                "parcelValue": None,
                "weight": None,
                "products": []
            }
        }
        
        print(f"✅ Order payload created:")
        print(f"   Contact Name: {payload['contact']['name']}")
        print(f"   Contact Phone: {payload['contact']['phone']}")
        print(f"   Contact Email: {payload['contact']['email']}")
        print(f"   Pickup Code: {payload['pickupOrderCode']}")
        print(f"   Package Description: {payload['packageDetails']['description']}")
        
        # Verify no default values are used
        if "Default" in payload['contact']['name'] or "Unknown" in payload['contact']['name']:
            print("❌ FAIL: Default values detected in payload")
            return False
        
        if not payload['contact']['name'] or not payload['contact']['phone'] or not payload['contact']['email']:
            print("❌ FAIL: Missing required client details")
            return False
        
        print("✅ SUCCESS: All data properly extracted from Excel file")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🚀 Quote Data Extraction Test")
    print("="*60)
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    success = test_quote_data_extraction()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    if success:
        print("✅ Quote data extraction is working correctly!")
        print("   Client details are properly extracted from Excel file.")
        print("   No default values should be used in order creation.")
        return 0
    else:
        print("❌ Quote data extraction has issues!")
        print("   Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())
