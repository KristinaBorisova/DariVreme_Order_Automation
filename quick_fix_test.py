#!/usr/bin/env python3
"""
quick_fix_test.py
Quick test to verify the fix for the 'contact' parameter issue.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))

def test_fixed_order_creation():
    """Test order creation with the corrected payload structure."""
    print("🔧 Testing Fixed Order Creation")
    print("=" * 40)
    
    try:
        # Get token
        from token_service import get_bearer_token
        token = get_bearer_token()
        
        if not token:
            print("❌ Could not get authentication token")
            return False
        
        print("✅ Authentication successful")
        
        # Create a test quote first
        from sheet_to_json import load_workbook_to_dict
        from POST_create_quote_id import row_to_payload
        
        # Load data
        google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
        workbook = load_workbook_to_dict(google_sheets_url)
        sheet_name = list(workbook.keys())[0]
        first_order = workbook[sheet_name][0]
        
        print(f"📋 Using order data:")
        print(f"   pickupAddressBookId: {first_order.get('pickupAddressBookId')}")
        print(f"   pickupTimeUtc: {first_order.get('pickupTimeUtc')}")
        print(f"   deliveryRawAddress: {first_order.get('deliveryRawAddress')}")
        
        # Create quote
        quote_payload = row_to_payload(first_order)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"\n💰 Creating quote...")
        quote_response = requests.post(
            "https://stageapi.glovoapp.com/v2/laas/quotes",
            headers=headers,
            json=quote_payload,
            timeout=30
        )
        
        if quote_response.status_code != 200:
            print(f"❌ Quote creation failed: {quote_response.status_code}")
            print(f"   Error: {quote_response.text}")
            return False
        
        quote_data = quote_response.json()
        quote_id = quote_data.get("quoteId")
        
        if not quote_id:
            print(f"❌ No quoteId in response")
            return False
        
        print(f"✅ Quote created successfully!")
        print(f"   Quote ID: {quote_id}")
        
        # Test order creation with FIXED payload structure
        print(f"\n📦 Testing order creation with FIXED payload...")
        
        # FIXED payload structure using 'contact' instead of 'finalClient'
        order_payload = {
            "contact": {
                "name": "Test Client",
                "phone": "+359888123456",
                "email": "test@darivreme.com"
            },
            "pickupOrderCode": f"ORD{int(datetime.now().timestamp())}"
        }
        
        print(f"   Payload: {json.dumps(order_payload, indent=2)}")
        
        order_url = f"https://stageapi.glovoapp.com/v2/laas/quotes/{quote_id}/parcels"
        order_response = requests.post(
            order_url,
            headers=headers,
            json=order_payload,
            timeout=30
        )
        
        print(f"   Status Code: {order_response.status_code}")
        
        if order_response.status_code == 200:
            order_data = order_response.json()
            print(f"   ✅ SUCCESS! Order created successfully!")
            print(f"   Response: {json.dumps(order_data, indent=2)}")
            return True
        else:
            print(f"   ❌ FAILED")
            try:
                error_data = order_response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error: {order_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the quick fix test."""
    print("🔧 Quick Fix Test - Contact Parameter Issue")
    print("=" * 50)
    
    print("🔍 Issue: API was expecting 'contact' parameter instead of 'finalClient'")
    print("🔧 Fix: Updated payload structure to use 'contact'")
    print("🧪 Testing: Verifying the fix works...")
    
    success = test_fixed_order_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 FIX CONFIRMED!")
        print("✅ The 'contact' parameter fix is working correctly")
        print("💡 You can now run your full test again:")
        print("   python test_with_real_data.py")
    else:
        print("❌ Fix needs more investigation")
        print("💡 Run the debug script for more details:")
        print("   python debug_api_response.py")

if __name__ == "__main__":
    main()
