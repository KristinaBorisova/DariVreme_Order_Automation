#!/usr/bin/env python3
"""
enhanced_send_order.py
Enhanced order creation with more complete payload information.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'step_1_authentication'))
from token_service import get_bearer_token

# Configuration
ORDER_URL_TEMPLATE = "https://stageapi.glovoapp.com/v2/laas/quotes/{quote_id}/parcels"
TOKEN = get_bearer_token()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def create_enhanced_order_payload(quote_data: Dict[str, Any], client_details: Dict[str, str]) -> Dict[str, Any]:
    """
    Create enhanced order payload with more complete information.
    
    Args:
        quote_data: Dictionary containing quote_id and original row data
        client_details: Client information (name, phone, email)
        
    Returns:
        Enhanced order payload for API request
    """
    # Generate pickup order code
    pickup_order_code = f"ORD{int(time.time())}{quote_data.get('index', 0)}"
    
    # Enhanced payload with more complete information
    payload = {
        "contact": {
            "name": client_details.get("name", "Default Client"),
            "phone": client_details.get("phone", "+1234567890"),
            "email": client_details.get("email", "client@example.com"),
            "rawPhone": client_details.get("phone", "+1234567890")  # Add raw phone for better handling
        },
        "pickupOrderCode": pickup_order_code,
        "packageDetails": {
            "contentType": "FOOD",  # Specify package type
            "description": "Food delivery order",
            "parcelValue": None,  # Can be set if known
            "weight": None,  # Can be set if known
            "products": []  # Can be populated with specific products
        }
    }
    
    return payload

def create_custom_order_payload(quote_data: Dict[str, Any], client_details: Dict[str, str], 
                               package_type: str = "FOOD", description: str = None) -> Dict[str, Any]:
    """
    Create custom order payload with specific package details.
    
    Args:
        quote_data: Dictionary containing quote_id and original row data
        client_details: Client information (name, phone, email)
        package_type: Type of package (FOOD, DOCUMENTS, OTHER)
        description: Custom description for the package
        
    Returns:
        Custom order payload for API request
    """
    pickup_order_code = f"ORD{int(time.time())}{quote_data.get('index', 0)}"
    
    payload = {
        "contact": {
            "name": client_details.get("name", "Default Client"),
            "phone": client_details.get("phone", "+1234567890"),
            "email": client_details.get("email", "client@example.com"),
            "rawPhone": client_details.get("phone", "+1234567890")
        },
        "pickupOrderCode": pickup_order_code,
        "packageDetails": {
            "contentType": package_type,
            "description": description or f"{package_type.lower()} delivery order",
            "parcelValue": None,
            "weight": None,
            "products": []
        }
    }
    
    return payload

def send_enhanced_order(quote_id: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Send enhanced order creation request.
    
    Args:
        quote_id: The quote ID obtained from step 2
        payload: Enhanced order payload with client details
        
    Returns:
        Tuple of (success, response_data)
    """
    url = ORDER_URL_TEMPLATE.format(quote_id=quote_id)
    
    try:
        print(f"🚀 Sending enhanced order to: {url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        r = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        
        print(f"📊 Response Status: {r.status_code}")
        
        if r.status_code >= 200 and r.status_code < 300:
            response_data = r.json()
            print(f"✅ Order created successfully!")
            print(f"📋 Response: {json.dumps(response_data, indent=2)}")
            return True, response_data
        
        # Try to parse error response
        try:
            error_data = r.json()
            print(f"❌ Order creation failed: {json.dumps(error_data, indent=2)}")
            return False, {"status": r.status_code, "error": error_data}
        except Exception:
            print(f"❌ Order creation failed: {r.text}")
            return False, {"status": r.status_code, "error": r.text}
            
    except requests.RequestException as e:
        print(f"❌ Request exception: {e}")
        return False, {"error": str(e)}

def test_enhanced_order_creation():
    """Test the enhanced order creation."""
    print("🧪 Testing Enhanced Order Creation")
    print("=" * 50)
    
    try:
        # Import required modules
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'step_2_quota_Config'))
        from sheet_to_json import load_workbook_to_dict
        from POST_create_quote_id import row_to_payload
        
        # Load data and create quote
        google_sheets_url = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
        workbook = load_workbook_to_dict(google_sheets_url)
        sheet_name = list(workbook.keys())[0]
        first_order = workbook[sheet_name][0]
        
        print("📋 Original Order Data:")
        for key, value in first_order.items():
            print(f"   {key}: {value}")
        
        # Create quote
        quote_payload = row_to_payload(first_order)
        quote_response = requests.post(
            "https://stageapi.glovoapp.com/v2/laas/quotes",
            headers=HEADERS,
            json=quote_payload,
            timeout=30
        )
        
        if quote_response.status_code != 200:
            print(f"❌ Quote creation failed: {quote_response.status_code}")
            return False
        
        quote_data = quote_response.json()
        quote_id = quote_data.get("quoteId")
        
        print(f"\n✅ Quote Created:")
        print(f"   Quote ID: {quote_id}")
        print(f"   Price: {quote_data.get('quotePrice')} {quote_data.get('currencyCode')}")
        
        # Test different payload variations
        client_details = {
            "name": "Enhanced Test Client",
            "phone": "+1234567890",
            "email": "client@example.com"
        }
        
        quote_data_for_order = {
            "quote_id": quote_id,
            "original_row": first_order,
            "index": 1
        }
        
        # Test 1: Enhanced payload
        print(f"\n🧪 Test 1: Enhanced Payload")
        enhanced_payload = create_enhanced_order_payload(quote_data_for_order, client_details)
        success, response = send_enhanced_order(quote_id, enhanced_payload)
        
        if success:
            print(f"✅ Enhanced payload works!")
            return True
        
        # Test 2: Custom payload with different package type
        print(f"\n🧪 Test 2: Custom Payload (DOCUMENTS)")
        custom_payload = create_custom_order_payload(
            quote_data_for_order, 
            client_details, 
            package_type="DOCUMENTS",
            description="Document delivery"
        )
        success, response = send_enhanced_order(quote_id, custom_payload)
        
        if success:
            print(f"✅ Custom payload works!")
            return True
        
        print(f"❌ All enhanced payload tests failed")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Enhanced Order Creation Test")
    print("=" * 50)
    
    success = test_enhanced_order_creation()
    
    if success:
        print(f"\n🎉 Enhanced order creation is working!")
        print(f"💡 You can now use the enhanced payload structure")
    else:
        print(f"\n❌ Enhanced order creation needs more investigation")
