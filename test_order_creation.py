#!/usr/bin/env python3
"""
test_order_creation.py
Simple test script to create orders using the FINAL_ORDERS data.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))

# Import required modules
from step_1_authentication.token_service import get_bearer_token
from sheet_to_json import load_workbook_to_dict

# Configuration
ORDER_URL_TEMPLATE = "https://stageapi.glovoapp.com/v2/laas/quotes/{quote_id}/parcels"

# Get token
TOKEN = get_bearer_token()
if not TOKEN:
    print("❌ No authentication token available")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def create_order_payload(quote_data: Dict[str, Any], client_details: Dict[str, str]) -> Dict[str, Any]:
    """Create order payload for the Glovo API."""
    pickup_order_code = f"ORD{int(time.time())}{quote_data.get('index', 0)}"
    
    original_row = quote_data.get("original_row", {})
    
    payload = {
        "contact": {
            "name": client_details.get("name", "Default Client"),
            "phone": client_details.get("phone", "+1234567890"),
            "email": client_details.get("email", "client@example.com")
        },
        "pickupOrderCode": pickup_order_code,
        "packageDetails": {
            "contentType": "FOOD",
            "description": original_row.get("order_id", "Food delivery order"),
            "parcelValue": None,
            "weight": None,
            "products": []
        }
    }
    
    return payload

def send_order_with_quote_id(quote_id: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Send order creation request using quote ID."""
    url = ORDER_URL_TEMPLATE.format(quote_id=quote_id)
    
    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        
        if r.status_code >= 200 and r.status_code < 300:
            return True, r.json()
        
        try:
            return False, {"status": r.status_code, "error": r.json()}
        except Exception:
            return False, {"status": r.status_code, "error": r.text}
            
    except requests.RequestException as e:
        return False, {"error": str(e)}

def main():
    """Main function to test order creation."""
    print("🧪 Testing Order Creation with FINAL_ORDERS Data")
    print("="*60)
    
    # Load quote results from step 2
    try:
        with open("quote_results_final.json", "r", encoding="utf-8") as f:
            quote_data = json.load(f)
        
        successes = quote_data.get("successes", [])
        print(f"📊 Loaded {len(successes)} successful quotes from step 2")
        
    except FileNotFoundError:
        print("❌ Quote results file not found. Please run step 2 first.")
        return
    except Exception as e:
        print(f"❌ Error loading quote results: {e}")
        return
    
    if not successes:
        print("❌ No successful quotes found")
        return
    
    # Process each quote
    successful_orders = []
    failed_orders = []
    
    for i, success in enumerate(successes, start=1):
        quote_id = success.get("response", {}).get("quoteId")
        if not quote_id:
            print(f"⚠️  No quote ID found for success {i}")
            continue
        
        row = success.get("row", {})
        client_details = {
            "name": row.get("client_name", "Unknown Client"),
            "phone": row.get("client_phone", "Unknown Phone"),
            "email": row.get("client_email", "Unknown Email")
        }
        
        print(f"\n📦 Processing order {i}/{len(successes)}")
        print(f"   Client: {client_details['name']}")
        print(f"   Order: {row.get('order_id', 'Unknown')}")
        print(f"   Quote ID: {quote_id}")
        
        # Create order payload
        quote_data = {
            "quote_id": quote_id,
            "original_row": row,
            "index": i
        }
        
        payload = create_order_payload(quote_data, client_details)
        
        # Send order request
        print(f"   📤 Sending order request...")
        success_result, response = send_order_with_quote_id(quote_id, payload)
        
        if success_result:
            print(f"   ✅ Order created successfully!")
            print(f"   📋 Glovo Order ID: {response.get('id', 'N/A')}")
            print(f"   🏷️  Pickup Code: {payload['pickupOrderCode']}")
            
            successful_orders.append({
                "index": i,
                "quote_id": quote_id,
                "client_name": client_details['name'],
                "order_description": row.get('order_id', 'Unknown'),
                "glovo_order_id": response.get('id', 'N/A'),
                "pickup_order_code": payload['pickupOrderCode'],
                "response": response
            })
        else:
            print(f"   ❌ Order failed: {response}")
            failed_orders.append({
                "index": i,
                "quote_id": quote_id,
                "client_name": client_details['name'],
                "error": response
            })
        
        # Rate limiting
        if i < len(successes):
            time.sleep(0.5)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 ORDER CREATION TEST SUMMARY")
    print("="*60)
    print(f"📋 Total orders processed: {len(successes)}")
    print(f"✅ Successful orders: {len(successful_orders)}")
    print(f"❌ Failed orders: {len(failed_orders)}")
    print(f"📈 Success rate: {len(successful_orders) / len(successes) * 100:.1f}%")
    
    if successful_orders:
        print(f"\n🎉 SUCCESSFUL ORDERS:")
        for order in successful_orders:
            print(f"   • {order['client_name']} - {order['order_description']}")
            print(f"     Glovo Order ID: {order['glovo_order_id']}")
            print(f"     Pickup Code: {order['pickup_order_code']}")
    
    if failed_orders:
        print(f"\n⚠️  FAILED ORDERS:")
        for order in failed_orders:
            print(f"   • {order['client_name']} - {order['error']}")
    
    # Save results
    results = {
        "total_processed": len(successes),
        "successful_orders": successful_orders,
        "failed_orders": failed_orders,
        "success_rate": len(successful_orders) / len(successes) * 100 if successes else 0
    }
    
    with open("test_order_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Test results saved to: test_order_results.json")

if __name__ == "__main__":
    main()
