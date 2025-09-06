#!/usr/bin/env python3
"""
debug_api_response.py
Debug script to examine API responses and understand the correct payload structure.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))

def get_token():
    """Get authentication token."""
    from token_service import get_bearer_token
    return get_bearer_token()

def test_quote_creation():
    """Test quote creation and examine the response structure."""
    print("🔍 Testing Quote Creation")
    print("-" * 40)
    
    try:
        from sheet_to_json import load_workbook_to_dict
        from POST_create_quote_id import row_to_payload
        
        # Load data
        google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
        workbook = load_workbook_to_dict(google_sheets_url)
        sheet_name = list(workbook.keys())[0]
        
        # Get first order
        first_order = workbook[sheet_name][0]
        print(f"📋 First order data:")
        for key, value in first_order.items():
            print(f"   {key}: {value}")
        
        # Create quote payload
        quote_payload = row_to_payload(first_order)
        print(f"\n💰 Quote payload:")
        print(json.dumps(quote_payload, indent=2))
        
        # Send quote request
        token = get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        quote_url = "https://stageapi.glovoapp.com/v2/laas/quotes"
        print(f"\n🚀 Sending quote request to: {quote_url}")
        
        response = requests.post(quote_url, headers=headers, json=quote_payload, timeout=30)
        
        print(f"📊 Quote Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            quote_data = response.json()
            print(f"   Response Body:")
            print(json.dumps(quote_data, indent=2))
            
            quote_id = quote_data.get("quoteId")
            if quote_id:
                print(f"\n✅ Quote created successfully!")
                print(f"   Quote ID: {quote_id}")
                return quote_id, quote_data
            else:
                print(f"❌ No quoteId in response")
                return None, None
        else:
            print(f"   Error Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return None, None
            
    except Exception as e:
        print(f"❌ Quote creation error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_order_creation_with_different_payloads(quote_id):
    """Test order creation with different payload structures."""
    print(f"\n🔍 Testing Order Creation with Quote ID: {quote_id}")
    print("-" * 40)
    
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    order_url = f"https://stageapi.glovoapp.com/v2/laas/quotes/{quote_id}/parcels"
    
    # Test different payload structures
    test_payloads = [
        {
            "name": "finalClient structure",
            "payload": {
                "finalClient": {
                    "name": "Test Client",
                    "phone": "+359888123456",
                    "email": "test@darivreme.com"
                },
                "pickupOrderCode": "ORD123456"
            }
        },
        {
            "name": "contact structure",
            "payload": {
                "contact": {
                    "name": "Test Client",
                    "phone": "+359888123456",
                    "email": "test@darivreme.com"
                },
                "pickupOrderCode": "ORD123456"
            }
        },
        {
            "name": "client structure",
            "payload": {
                "client": {
                    "name": "Test Client",
                    "phone": "+359888123456",
                    "email": "test@darivreme.com"
                },
                "pickupOrderCode": "ORD123456"
            }
        },
        {
            "name": "customer structure",
            "payload": {
                "customer": {
                    "name": "Test Client",
                    "phone": "+359888123456",
                    "email": "test@darivreme.com"
                },
                "pickupOrderCode": "ORD123456"
            }
        },
        {
            "name": "minimal structure",
            "payload": {
                "pickupOrderCode": "ORD123456"
            }
        }
    ]
    
    for test in test_payloads:
        print(f"\n🧪 Testing: {test['name']}")
        print(f"   Payload: {json.dumps(test['payload'], indent=2)}")
        
        try:
            response = requests.post(order_url, headers=headers, json=test['payload'], timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
                return test['payload']  # Return the working payload structure
            else:
                print(f"   ❌ FAILED")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def examine_api_documentation():
    """Try to get API documentation or examples."""
    print(f"\n📚 API Documentation Analysis")
    print("-" * 40)
    
    # Common Glovo API patterns
    print("Common Glovo API parameter patterns:")
    print("1. 'contact' - Most likely correct")
    print("2. 'finalClient' - What we were using")
    print("3. 'client' - Alternative")
    print("4. 'customer' - Alternative")
    
    print(f"\n💡 Based on the error 'Missing parameter: contact',")
    print(f"   the correct parameter name is likely 'contact'")

def main():
    """Run the debug analysis."""
    print("🔍 Glovo API Debug Analysis")
    print("=" * 50)
    
    # Test quote creation first
    quote_id, quote_data = test_quote_creation()
    
    if quote_id:
        # Test different order payload structures
        working_payload = test_order_creation_with_different_payloads(quote_id)
        
        if working_payload:
            print(f"\n🎉 FOUND WORKING PAYLOAD STRUCTURE!")
            print(f"   Working payload: {json.dumps(working_payload, indent=2)}")
        else:
            print(f"\n❌ No working payload structure found")
            examine_api_documentation()
    else:
        print(f"\n❌ Could not create quote for testing")
        examine_api_documentation()

if __name__ == "__main__":
    main()
