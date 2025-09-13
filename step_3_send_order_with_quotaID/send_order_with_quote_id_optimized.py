#!/usr/bin/env python3
"""
send_order_with_quote_id_optimized.py
Optimized order creation for single-sheet approach with up to 10 clients/month.
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Import order loggers
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from order_logger import OrderLogger
from google_sheets_logger import GoogleSheetsLogger

# Configuration
ORDER_URL_TEMPLATE = "https://stageapi.glovoapp.com/v2/laas/quotes/{quote_id}/parcels"

# Import token service from step 1
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'step_1_authentication'))
from token_service import get_bearer_token

# Get token from authentication module
TOKEN = get_bearer_token()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def extract_quote_ids_from_successes(successes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract quote IDs from successful quote creation responses.
    Optimized for single-sheet structure.
    """
    quote_data = []
    
    for success in successes:
        response = success.get("response", {})
        quote_id = response.get("quoteId")
        
        if quote_id:
            # Extract all information from the success response
            row = success.get("row", {})
            client_details = success.get("client_details", {})
            restaurant_details = success.get("restaurant_details", {})
            
            quote_data.append({
                "quote_id": quote_id,
                "original_row": row,
                "quote_response": response,
                "client_details": client_details,
                "restaurant_details": restaurant_details,
                "index": success.get("index")
            })
        else:
            print(f"⚠️  Warning: No quoteId found in success response at index {success.get('index')}")
    
    return quote_data

def create_order_payload(quote_data: Dict[str, Any], client_details: Dict[str, str]) -> Dict[str, Any]:
    """
    Create order payload for the Glovo API.
    Optimized for single-sheet structure with enhanced information.
    """
    # Generate pickup order code
    pickup_order_code = f"ORD{int(time.time())}{quote_data.get('index', 0)}"
    
    # Get additional information from original row
    original_row = quote_data.get("original_row", {})
    restaurant_details = quote_data.get("restaurant_details", {})
    
    payload = {
        "contact": {
            "name": client_details.get("name", "Default Client"),
            "phone": client_details.get("phone", "+1234567890"),
            "email": client_details.get("email", "client@example.com")
        },
        "pickupOrderCode": pickup_order_code,
        "packageDetails": {
            "contentType": "FOOD",  # Default to FOOD for restaurant orders
            "description": original_row.get("order_notes", "Food delivery order"),
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
        
        # Try to parse error response
        try:
            return False, {"status": r.status_code, "error": r.json()}
        except Exception:
            return False, {"status": r.status_code, "error": r.text}
            
    except requests.RequestException as e:
        return False, {"error": str(e)}

def process_orders_from_quotes_optimized(
        quote_data_list: List[Dict[str, Any]],
        rate_limit_per_sec: float = 2.0,
        log_orders: bool = True,
        excel_output_file: str = None,
        use_google_sheets: bool = True,
        google_sheets_url: str = None
    ) -> Dict[str, Any]:
    """
    Process multiple orders from quote data.
    Optimized for single-sheet approach with up to 10 clients/month.
    """
    delay = 1.0 / max(rate_limit_per_sec, 0.001)
    successful_orders = []
    failed_orders = []
    
    # Initialize order loggers if logging is enabled
    order_logger = None
    google_sheets_logger = None
    
    if log_orders:
        if use_google_sheets and google_sheets_url:
            try:
                google_sheets_logger = GoogleSheetsLogger(google_sheets_url, "Glovo-Orders-Summary")
                print("✅ Google Sheets logging enabled")
            except Exception as e:
                print(f"⚠️  Google Sheets logging failed: {e}")
                print("📝 Falling back to local Excel logging")
                order_logger = OrderLogger()
        else:
            order_logger = OrderLogger()
    
    print(f"🚀 Processing {len(quote_data_list)} orders with optimized approach...")
    print(f"📊 Rate limit: {rate_limit_per_sec} requests/second")
    
    for i, quote_data in enumerate(quote_data_list, start=1):
        quote_id = quote_data["quote_id"]
        original_row = quote_data.get("original_row", {})
        client_details = quote_data.get("client_details", {})
        restaurant_details = quote_data.get("restaurant_details", {})
        
        print(f"\n📦 Processing order {i}/{len(quote_data_list)}")
        print(f"   Client: {client_details.get('name', 'Unknown')}")
        print(f"   Restaurant: {restaurant_details.get('name', 'Unknown')}")
        print(f"   Quote ID: {quote_id}")
        
        # Create order payload
        payload = create_order_payload(quote_data, client_details)
        
        # Send order request
        print(f"   📤 Sending order request...")
        success, response = send_order_with_quote_id(quote_id, payload)
        
        if success:
            order_info = {
                "index": i,
                "quote_id": quote_id,
                "original_row": original_row,
                "order_response": response,
                "pickup_order_code": payload["pickupOrderCode"],
                "client_details": client_details,
                "restaurant_details": restaurant_details
            }
            successful_orders.append(order_info)
            print(f"   ✅ Order created successfully!")
            print(f"   📋 Order ID: {response.get('id', 'N/A')}")
            print(f"   🏷️  Pickup Code: {payload['pickupOrderCode']}")
            
            # Log the order if logging is enabled
            if google_sheets_logger:
                try:
                    google_sheets_logger.log_order(response, quote_data, client_details)
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not log order {quote_id} to Google Sheets: {e}")
            elif order_logger:
                try:
                    order_logger.log_order(response, quote_data, client_details)
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not log order {quote_id}: {e}")
        else:
            failed_orders.append({
                "index": i,
                "quote_id": quote_id,
                "original_row": original_row,
                "error": response
            })
            print(f"   ❌ Order failed: {response}")
        
        # Rate limiting
        if i < len(quote_data_list):
            time.sleep(delay)
    
    # Save orders to Google Sheets or Excel if logging is enabled
    excel_file = None
    google_sheets_success = False
    
    if google_sheets_logger and google_sheets_logger.order_log:
        try:
            google_sheets_success = google_sheets_logger.save_to_google_sheets()
            google_sheets_logger.print_summary()
        except Exception as e:
            print(f"⚠️  Warning: Could not save orders to Google Sheets: {e}")
    
    if order_logger and order_logger.order_log:
        try:
            if excel_output_file:
                excel_file = order_logger.append_to_existing_excel(excel_output_file)
            else:
                excel_file = order_logger.save_to_excel()
            
            # Print summary
            order_logger.print_summary()
        except Exception as e:
            print(f"⚠️  Warning: Could not save orders to Excel: {e}")
    
    return {
        "total_processed": len(quote_data_list),
        "successful_orders": successful_orders,
        "failed_orders": failed_orders,
        "success_rate": len(successful_orders) / len(quote_data_list) * 100 if quote_data_list else 0,
        "excel_file": excel_file,
        "google_sheets_success": google_sheets_success
    }

def print_detailed_summary(results: Dict[str, Any]):
    """Print a detailed summary of the order processing results."""
    print("\n" + "="*70)
    print("📊 ORDER CREATION SUMMARY")
    print("="*70)
    print(f"📋 Total orders processed: {results['total_processed']}")
    print(f"✅ Successful orders: {len(results['successful_orders'])}")
    print(f"❌ Failed orders: {len(results['failed_orders'])}")
    print(f"📈 Success rate: {results['success_rate']:.1f}%")
    
    if results['successful_orders']:
        print(f"\n🎉 SUCCESSFUL ORDERS:")
        for i, order in enumerate(results['successful_orders'][:5], 1):  # Show first 5
            client = order.get('client_details', {})
            restaurant = order.get('restaurant_details', {})
            response = order.get('order_response', {})
            
            print(f"   {i}. {client.get('name', 'Unknown')} → {restaurant.get('name', 'Unknown')}")
            print(f"      Order ID: {response.get('id', 'N/A')}")
            print(f"      Pickup Code: {order.get('pickup_order_code', 'N/A')}")
            print(f"      Quote ID: {order.get('quote_id', 'N/A')}")
    
    if results['failed_orders']:
        print(f"\n⚠️  FAILED ORDERS:")
        for i, failure in enumerate(results['failed_orders'][:3], 1):  # Show first 3
            original_row = failure.get('original_row', {})
            print(f"   {i}. {original_row.get('client_name', 'Unknown')} → {original_row.get('restaurant_name', 'Unknown')}")
            print(f"      Quote ID: {failure.get('quote_id', 'N/A')}")
            print(f"      Error: {failure.get('error', 'Unknown error')}")

def load_quote_successes_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load successful quote responses from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "successes" in data:
        return data["successes"]
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("Invalid JSON structure. Expected dict with 'successes' key or list of successes.")

def save_order_results(results: Dict[str, Any], output_file: str = "order_results_optimized.json"):
    """Save order processing results to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Order results saved to: {output_file}")

if __name__ == "__main__":
    # Example usage with optimized approach
    
    # Option 1: Load from file (if you saved step 2 results)
    try:
        quote_results_file = "quote_results_optimized.json"  # File from step 2
        successes = load_quote_successes_from_file(quote_results_file)
        print(f"📊 Loaded {len(successes)} successful quotes from {quote_results_file}")
    except FileNotFoundError:
        print("❌ Quote results file not found. Please run step 2 first or provide the file path.")
        exit(1)
    except Exception as e:
        print(f"❌ Error loading quote results: {e}")
        exit(1)
    
    # Extract quote IDs from successful responses
    quote_data_list = extract_quote_ids_from_successes(successes)
    print(f"📋 Extracted {len(quote_data_list)} quote IDs")
    
    if not quote_data_list:
        print("❌ No valid quote IDs found. Cannot proceed with order creation.")
        exit(1)
    
    # Process orders with Google Sheets logging
    print("\n🚀 Starting Optimized Order Creation")
    print("="*50)
    
    google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
    
    results = process_orders_from_quotes_optimized(
        quote_data_list=quote_data_list,
        rate_limit_per_sec=2.0,  # Conservative rate limiting
        log_orders=True,  # Enable order logging
        excel_output_file="order_results_optimized.xlsx",  # Fallback Excel file
        use_google_sheets=True,  # Use Google Sheets for logging
        google_sheets_url=google_sheets_url  # Your Google Sheets URL
    )
    
    # Print detailed summary
    print_detailed_summary(results)
    
    # Show logging information
    if results.get('google_sheets_success'):
        print(f"\n📊 Order results saved to Google Sheets!")
        print("   Sheet: 'Glovo-Orders-Summary'")
        print("   URL: https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit")
    elif results.get('excel_file'):
        print(f"\n📊 Order results saved to Excel: {results['excel_file']}")
    
    # Save results
    save_order_results(results, "order_results_optimized.json")
    
    print(f"\n🎉 Optimized order processing completed!")
    print(f"📈 Overall success rate: {results['success_rate']:.1f}%")
