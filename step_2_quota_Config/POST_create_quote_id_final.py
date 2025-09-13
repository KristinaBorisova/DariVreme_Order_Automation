#!/usr/bin/env python3
"""
POST_create_quote_id_final.py
Quote creation for FINAL_ORDERS sheet with exact column names.
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Iterable, Tuple, Optional

URL = "https://stageapi.glovoapp.com/v2/laas/quotes"

# Import token service from step 1
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_1_authentication'))
from token_service import get_bearer_token

# Get token from authentication module
TOKEN = get_bearer_token()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def row_to_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a single row from FINAL_ORDERS sheet to Glovo API payload.
    Uses exact column names from your sheet.
    """
    return {
        "pickupDetails": {
            "addressBook": {
                "id": row["pickupAddressBookId"],
            },
            "pickupTime": row["pickup_time_utc"],
        },
        "deliveryAddress": {
            "rawAddress": row["deliveryRawAddress"],
            "coordinates": {
                "latitude": float(row["deliveryLattitude"]),
                "longitude": float(row["deliveryLongitude"]),
            },
            "details": row.get("deliveryDetails", ""),
        },
    }

def validate_row(row: Dict[str, Any]) -> Optional[str]:
    """
    Validate a single row from FINAL_ORDERS sheet for all required fields.
    Uses exact column names from your sheet.
    """
    # Required fields for quote creation using your exact column names
    required_fields = [
        "client_id", "client_name", "client_phone", "client_email",
        "deliveryRawAddress", "deliveryLattitude", "deliveryLongitude",
        "pickupAddressBookId", "pickup_time_utc", "restaurant_name"
    ]
    
    missing = [k for k in required_fields if k not in row or row[k] in (None, "")]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    
    # Validate coordinates
    try:
        float(row["deliveryLattitude"])
        float(row["deliveryLongitude"])
    except (ValueError, TypeError):
        return "deliveryLattitude/deliveryLongitude must be numeric"
    
    # Validate pickup time format
    pickup_time = row["pickup_time_utc"]
    if not isinstance(pickup_time, str) or not pickup_time.endswith("Z"):
        return "pickup_time_utc must be ISO8601 UTC string ending with 'Z'"
    
    # Validate email format (basic check)
    email = row.get("client_email", "")
    if "@" not in email or "." not in email.split("@")[-1]:
        return "client_email must be a valid email format"
    
    # Validate phone (basic check)
    phone = str(row.get("client_phone", ""))
    if len(phone) < 8:
        return "client_phone must be at least 8 characters"
    
    # Validate pickup address book ID format (UUID)
    pickup_id = row.get("pickupAddressBookId", "")
    if len(pickup_id) < 30:  # Basic UUID length check
        return "pickupAddressBookId must be a valid UUID format"
    
    return None

def send_quote(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Send quote request to Glovo API."""
    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
        if r.status_code >= 200 and r.status_code < 300:
            return True, r.json()
        try:
            return False, {"status": r.status_code, "error": r.json()}
        except Exception:
            return False, {"status": r.status_code, "error": r.text}
    except requests.RequestException as e:
        return False, {"error": str(e)}

def process_orders_final(rows: Iterable[Dict[str, Any]], 
                        rate_limit_per_sec: float = 3.0) -> Dict[str, Any]:
    """
    Process orders from FINAL_ORDERS sheet with exact column names.
    """
    delay = 1.0 / max(rate_limit_per_sec, 0.001)
    successes = []
    failures = []
    
    print(f"🚀 Processing orders from FINAL_ORDERS sheet...")
    print(f"📊 Rate limit: {rate_limit_per_sec} requests/second")
    
    for i, row in enumerate(rows, start=1):
        print(f"\n📋 Processing order {i}...")
        print(f"   Client ID: {row.get('client_id', 'Unknown')}")
        print(f"   Client: {row.get('client_name', 'Unknown')}")
        print(f"   Restaurant: {row.get('restaurant_name', 'Unknown')}")
        print(f"   Delivery: {row.get('deliveryRawAddress', 'Unknown')[:50]}...")
        print(f"   Order Description: {row.get('order_id', 'Unknown')}")
        
        # Validate row
        validation_error = validate_row(row)
        if validation_error:
            print(f"   ❌ Validation failed: {validation_error}")
            failures.append({
                "index": i, 
                "row": row, 
                "reason": f"Validation error: {validation_error}"
            })
            continue
        
        # Create payload
        payload = row_to_payload(row)
        
        # Send quote request
        print(f"   📤 Sending quote request...")
        success, response = send_quote(payload)
        
        if success:
            print(f"   ✅ Quote created successfully!")
            print(f"   📋 Quote ID: {response.get('quoteId', 'N/A')}")
            
            # Preserve all information from the row using your exact column names
            successes.append({
                "index": i,
                "row": row,  # Complete row with all data
                "response": response,
                "client_details": {
                    "client_id": row.get("client_id", "Unknown"),
                    "name": row.get("client_name", "Unknown Client"),
                    "phone": row.get("client_phone", "Unknown Phone"),
                    "email": row.get("client_email", "Unknown Email")
                },
                "restaurant_details": {
                    "name": row.get("restaurant_name", "Unknown Restaurant"),
                    "pickup_address_book_id": row.get("pickupAddressBookId", "Unknown")
                },
                "order_details": {
                    "order_description": row.get("order_id", "Unknown"),  # Your descriptive order_id
                    "delivery_frequency": row.get("deliveryFrequency", 0),
                    "pickup_code": row.get("pickup_code", "Unknown"),
                    "city": row.get("ADDRESS_CITY_NAME", "Unknown"),
                    "country": row.get("ADDRESS_COUNTRY", "Unknown"),
                    "postal_code": row.get("Address_postal_code", "Unknown")
                }
            })
        else:
            print(f"   ❌ Quote creation failed: {response}")
            failures.append({
                "index": i, 
                "row": row, 
                "reason": response
            })
        
        # Rate limiting
        if i < len(list(rows)) if hasattr(rows, '__len__') else True:
            time.sleep(delay)
    
    return {
        "total": len(successes) + len(failures),
        "successes": successes,
        "failures": failures,
        "success_rate": len(successes) / (len(successes) + len(failures)) * 100 if (len(successes) + len(failures)) > 0 else 0
    }

def print_summary(summary: Dict[str, Any]):
    """Print a detailed summary of the processing results."""
    print("\n" + "="*70)
    print("📊 QUOTE CREATION SUMMARY (FINAL_ORDERS Sheet)")
    print("="*70)
    print(f"📋 Total orders processed: {summary['total']}")
    print(f"✅ Successful quotes: {len(summary['successes'])}")
    print(f"❌ Failed quotes: {len(summary['failures'])}")
    print(f"📈 Success rate: {summary['success_rate']:.1f}%")
    
    if summary['successes']:
        print(f"\n🎉 SUCCESSFUL QUOTES:")
        for i, success in enumerate(summary['successes'][:5], 1):  # Show first 5
            row = success['row']
            response = success['response']
            print(f"   {i}. {row.get('client_name', 'Unknown')} ({row.get('client_id', 'N/A')})")
            print(f"      Restaurant: {row.get('restaurant_name', 'Unknown')}")
            print(f"      Order: {row.get('order_id', 'Unknown')}")
            print(f"      Quote ID: {response.get('quoteId', 'N/A')}")
            print(f"      Delivery: {row.get('deliveryRawAddress', 'Unknown')[:40]}...")
    
    if summary['failures']:
        print(f"\n⚠️  FAILED QUOTES:")
        for i, failure in enumerate(summary['failures'][:3], 1):  # Show first 3
            row = failure['row']
            print(f"   {i}. {row.get('client_name', 'Unknown')} ({row.get('client_id', 'N/A')})")
            print(f"      Restaurant: {row.get('restaurant_name', 'Unknown')}")
            print(f"      Order: {row.get('order_id', 'Unknown')}")
            print(f"      Error: {failure['reason']}")

def load_orders_from_final_sheet(google_sheets_url: str, sheet_name: str = "FINAL_ORDERS") -> List[Dict[str, Any]]:
    """
    Load orders from FINAL_ORDERS sheet with exact column names.
    """
    try:
        from sheet_to_json import load_workbook_to_dict
    except ImportError as e:
        print(f"❌ Error importing sheet_to_json: {e}")
        return []
    
    print(f"📊 Loading orders from FINAL_ORDERS sheet...")
    workbook = load_workbook_to_dict(google_sheets_url)
    
    if sheet_name not in workbook:
        print(f"❌ Sheet '{sheet_name}' not found. Available sheets: {list(workbook.keys())}")
        return []
    
    orders = workbook[sheet_name]
    print(f"✅ Loaded {len(orders)} orders from '{sheet_name}' sheet")
    
    # Display sample order structure
    if orders:
        print(f"\n📋 Sample order structure (FINAL_ORDERS columns):")
        sample_order = orders[0]
        for key, value in sample_order.items():
            print(f"   {key}: {value}")
    
    return orders

if __name__ == "__main__":
    # Load orders from FINAL_ORDERS sheet
    google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
    
    print("📊 Loading orders from FINAL_ORDERS sheet...")
    orders = load_orders_from_final_sheet(google_sheets_url, "FINAL_ORDERS")
    
    if not orders:
        print("❌ No orders found. Please check your FINAL_ORDERS sheet structure.")
        print("Expected columns: client_id, client_name, client_phone, client_email, deliveryRawAddress, deliveryLattitude, deliveryLongitude, pickupAddressBookId, pickup_time, restaurant_name")
        exit(1)
    
    # Process orders
    print(f"\n🚀 Processing {len(orders)} orders from FINAL_ORDERS...")
    summary = process_orders_final(orders, rate_limit_per_sec=2.0)
    
    # Print summary
    print_summary(summary)
    
    # Save results for Step 3
    results_file = "quote_results_final.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Quote results saved to: {results_file}")
    print("🚀 Ready for Step 3: Order creation!")
