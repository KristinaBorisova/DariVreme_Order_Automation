#!/usr/bin/env python3
"""
POST_create_quote_id_optimized.py
Optimized version for single-sheet approach with up to 10 clients/month.
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
    Convert a single row to Glovo API payload.
    Optimized for single-sheet structure.
    """
    return {
        "pickupDetails": {
            "addressBook": {
                "id": row["pickup_address_book_id"],
            },
            "pickupTime": row["pickup_time_utc"],
        },
        "deliveryAddress": {
            "rawAddress": row["delivery_address"],
            "coordinates": {
                "latitude": float(row["delivery_latitude"]),
                "longitude": float(row["delivery_longitude"]),
            },
            "details": row.get("delivery_details", ""),
        },
    }

def validate_row(row: Dict[str, Any]) -> Optional[str]:
    """
    Validate a single row for all required fields.
    Optimized for single-sheet structure.
    """
    # Required fields for quote creation
    required_fields = [
        "client_name", "client_phone", "client_email",
        "pickup_address_book_id", "pickup_time_utc", 
        "delivery_address", "delivery_latitude", "delivery_longitude"
    ]
    
    missing = [k for k in required_fields if k not in row or row[k] in (None, "")]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    
    # Validate coordinates
    try:
        float(row["delivery_latitude"])
        float(row["delivery_longitude"])
    except (ValueError, TypeError):
        return "delivery_latitude/delivery_longitude must be numeric"
    
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

def process_orders_optimized(rows: Iterable[Dict[str, Any]], 
                           rate_limit_per_sec: float = 3.0) -> Dict[str, Any]:
    """
    Process orders with optimized validation and error handling.
    Perfect for 10 clients/month scale.
    """
    delay = 1.0 / max(rate_limit_per_sec, 0.001)
    successes = []
    failures = []
    
    print(f"🚀 Processing orders with optimized single-sheet approach...")
    print(f"📊 Rate limit: {rate_limit_per_sec} requests/second")
    
    for i, row in enumerate(rows, start=1):
        print(f"\n📋 Processing order {i}...")
        print(f"   Client: {row.get('client_name', 'Unknown')}")
        print(f"   Restaurant: {row.get('restaurant_name', 'Unknown')}")
        print(f"   Delivery: {row.get('delivery_address', 'Unknown')[:50]}...")
        
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
            
            # Preserve all client and order information
            successes.append({
                "index": i,
                "row": row,
                "response": response,
                "client_details": {
                    "name": row.get("client_name", "Unknown Client"),
                    "phone": row.get("client_phone", "Unknown Phone"),
                    "email": row.get("client_email", "Unknown Email")
                },
                "restaurant_details": {
                    "name": row.get("restaurant_name", "Unknown Restaurant"),
                    "pickup_address_book_id": row.get("pickup_address_book_id")
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
    print("\n" + "="*60)
    print("📊 QUOTE CREATION SUMMARY")
    print("="*60)
    print(f"📋 Total orders processed: {summary['total']}")
    print(f"✅ Successful quotes: {len(summary['successes'])}")
    print(f"❌ Failed quotes: {len(summary['failures'])}")
    print(f"📈 Success rate: {summary['success_rate']:.1f}%")
    
    if summary['successes']:
        print(f"\n🎉 SUCCESSFUL QUOTES:")
        for i, success in enumerate(summary['successes'][:5], 1):  # Show first 5
            row = success['row']
            response = success['response']
            print(f"   {i}. {row.get('client_name', 'Unknown')} → {row.get('restaurant_name', 'Unknown')}")
            print(f"      Quote ID: {response.get('quoteId', 'N/A')}")
            print(f"      Delivery: {row.get('delivery_address', 'Unknown')[:40]}...")
    
    if summary['failures']:
        print(f"\n⚠️  FAILED QUOTES:")
        for i, failure in enumerate(summary['failures'][:3], 1):  # Show first 3
            row = failure['row']
            print(f"   {i}. {row.get('client_name', 'Unknown')} → {row.get('restaurant_name', 'Unknown')}")
            print(f"      Error: {failure['reason']}")

if __name__ == "__main__":
    # Load data from Google Sheets
    from sheet_to_json import load_workbook_to_dict
    
    # Your Google Sheets URL
    google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
    
    print("📊 Loading data from Google Sheets...")
    workbook = load_workbook_to_dict(google_sheets_url)
    
    # Use the first sheet
    sheet_names = list(workbook.keys())
    sheet_name = sheet_names[0] if sheet_names else "Sheet1"
    print(f"📋 Using sheet: {sheet_name}")
    
    rows = workbook[sheet_name]
    print(f"📊 Found {len(rows)} orders to process")
    
    # Process orders
    summary = process_orders_optimized(rows, rate_limit_per_sec=2.0)
    
    # Print summary
    print_summary(summary)
    
    # Save results for Step 3
    results_file = "quote_results_optimized.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Quote results saved to: {results_file}")
    print("🚀 Ready for Step 3: Order creation!")
