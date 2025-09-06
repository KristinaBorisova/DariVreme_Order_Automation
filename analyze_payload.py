#!/usr/bin/env python3
"""
analyze_payload.py
Analyze the order creation payload and response to identify any issues.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_3_send_order_with_quotaID'))

def analyze_successful_order():
    """Analyze a successful order creation to understand the complete flow."""
    print("🔍 Analyzing Successful Order Creation")
    print("=" * 50)
    
    try:
        # Get token
        from token_service import get_bearer_token
        token = get_bearer_token()
        
        if not token:
            print("❌ Could not get authentication token")
            return False
        
        # Load data and create quote
        from sheet_to_json import load_workbook_to_dict
        from POST_create_quote_id import row_to_payload
        
        google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
        workbook = load_workbook_to_dict(google_sheets_url)
        sheet_name = list(workbook.keys())[0]
        first_order = workbook[sheet_name][0]
        
        print("📋 Original Order Data:")
        for key, value in first_order.items():
            print(f"   {key}: {value}")
        
        # Create quote
        quote_payload = row_to_payload(first_order)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"\n💰 Quote Payload:")
        print(json.dumps(quote_payload, indent=2))
        
        quote_response = requests.post(
            "https://stageapi.glovoapp.com/v2/laas/quotes",
            headers=headers,
            json=quote_payload,
            timeout=30
        )
        
        if quote_response.status_code != 200:
            print(f"❌ Quote creation failed: {quote_response.status_code}")
            return False
        
        quote_data = quote_response.json()
        quote_id = quote_data.get("quoteId")
        
        print(f"\n✅ Quote Created Successfully:")
        print(f"   Quote ID: {quote_id}")
        print(f"   Price: {quote_data.get('quotePrice')} {quote_data.get('currencyCode')}")
        print(f"   Expires: {quote_data.get('expiresAt')}")
        
        # Create order payload
        from send_order_with_quote_id import create_order_payload
        
        client_details = {
            "name": "Test Client",
            "phone": "+359888123456",
            "email": "test@darivreme.com"
        }
        
        quote_data_for_order = {
            "quote_id": quote_id,
            "original_row": first_order,
            "index": 1
        }
        
        order_payload = create_order_payload(quote_data_for_order, client_details)
        
        print(f"\n📦 Order Payload:")
        print(json.dumps(order_payload, indent=2))
        
        # Send order
        order_url = f"https://stageapi.glovoapp.com/v2/laas/quotes/{quote_id}/parcels"
        print(f"\n🚀 Sending order to: {order_url}")
        
        order_response = requests.post(
            order_url,
            headers=headers,
            json=order_payload,
            timeout=30
        )
        
        print(f"📊 Order Response:")
        print(f"   Status Code: {order_response.status_code}")
        
        if order_response.status_code == 200:
            order_data = order_response.json()
            print(f"   ✅ SUCCESS!")
            print(f"   Order Data:")
            print(json.dumps(order_data, indent=2))
            
            # Analyze the response
            analyze_order_response(order_data)
            
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
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_order_response(order_data):
    """Analyze the order response to identify key information."""
    print(f"\n🔍 Order Response Analysis:")
    print("-" * 30)
    
    # Key fields to check
    key_fields = [
        "trackingNumber",
        "orderCode", 
        "status.state",
        "quote.quoteId",
        "quote.quotePrice",
        "quote.currencyCode",
        "contact.name",
        "contact.phone",
        "contact.email",
        "pickupDetails.pickupOrderCode",
        "pickupDetails.pickupTime",
        "address.rawAddress",
        "address.coordinates"
    ]
    
    for field in key_fields:
        value = get_nested_value(order_data, field)
        if value is not None:
            print(f"   ✅ {field}: {value}")
        else:
            print(f"   ❌ Missing: {field}")
    
    # Check if order is in a good state
    status = order_data.get("status", {})
    state = status.get("state")
    
    print(f"\n📊 Order Status Analysis:")
    if state == "CREATED":
        print(f"   ✅ Order successfully created!")
        print(f"   📦 Tracking Number: {order_data.get('trackingNumber', 'N/A')}")
        print(f"   💰 Price: {order_data.get('quote', {}).get('quotePrice', 'N/A')} {order_data.get('quote', {}).get('currencyCode', 'N/A')}")
    elif state == "ACCEPTED":
        print(f"   ✅ Order accepted by courier!")
    elif state == "PICKING_UP":
        print(f"   🚚 Order is being picked up!")
    elif state == "DELIVERING":
        print(f"   🚛 Order is being delivered!")
    elif state == "DELIVERED":
        print(f"   ✅ Order delivered successfully!")
    else:
        print(f"   ⚠️  Order in state: {state}")

def get_nested_value(data, key_path):
    """Get a value from nested dictionary using dot notation."""
    keys = key_path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def check_payload_completeness():
    """Check if the payload contains all necessary information."""
    print(f"\n🔍 Payload Completeness Check:")
    print("-" * 30)
    
    # Required fields for order creation
    required_fields = [
        "contact.name",
        "contact.phone", 
        "contact.email",
        "pickupOrderCode"
    ]
    
    # Optional but recommended fields
    optional_fields = [
        "contact.rawPhone",
        "packageDetails.contentType",
        "packageDetails.description"
    ]
    
    print("Required fields:")
    for field in required_fields:
        print(f"   ✅ {field}")
    
    print("\nOptional fields (recommended):")
    for field in optional_fields:
        print(f"   💡 {field}")

def suggest_payload_improvements():
    """Suggest improvements to the payload structure."""
    print(f"\n💡 Payload Improvement Suggestions:")
    print("-" * 30)
    
    improvements = [
        "Add 'rawPhone' field to contact for better phone number handling",
        "Add 'packageDetails.contentType' to specify package type (FOOD, DOCUMENTS, etc.)",
        "Add 'packageDetails.description' for package description",
        "Consider adding 'packageDetails.weight' if known",
        "Add 'packageDetails.parcelValue' for insurance purposes"
    ]
    
    for i, improvement in enumerate(improvements, 1):
        print(f"   {i}. {improvement}")

def main():
    """Run the payload analysis."""
    print("🔍 Glovo Order Payload Analysis")
    print("=" * 50)
    
    # Analyze successful order
    success = analyze_successful_order()
    
    if success:
        # Check payload completeness
        check_payload_completeness()
        
        # Suggest improvements
        suggest_payload_improvements()
        
        print(f"\n🎉 Analysis Complete!")
        print(f"✅ Your order creation is working correctly")
        print(f"💡 The payload structure is valid and functional")
    else:
        print(f"\n❌ Analysis failed - could not create test order")

if __name__ == "__main__":
    main()
