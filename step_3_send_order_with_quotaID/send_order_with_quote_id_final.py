#!/usr/bin/env python3
"""
send_order_with_quote_id_final.py
Order creation for FINAL_ORDERS sheet with exact column names.
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
try:
    from order_logger import OrderLogger
    from google_sheets_logger import GoogleSheetsLogger
except ImportError as e:
    print(f"⚠️  Warning: Could not import logging modules: {e}")
    print("   Order logging will be disabled")
    OrderLogger = None
    GoogleSheetsLogger = None

# Configuration
ORDER_URL_TEMPLATE = "https://stageapi.glovoapp.com/v2/laas/quotes/{quote_id}/parcels"

# Import token service from step 1
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    from step_1_authentication.token_service import get_bearer_token
except ImportError:
    try:
        from token_service import get_bearer_token
    except ImportError as e:
        print(f"❌ Error importing token_service: {e}")
        print("   Please ensure the authentication module is properly set up")
        def get_bearer_token():
            return None

# Get token from authentication module
TOKEN = get_bearer_token()

if not TOKEN:
    print("❌ No authentication token available. Please check your authentication setup.")
    print("   Run the authentication module first or check your credentials.")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def extract_quote_ids_from_successes(successes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract quote IDs from successful quote creation responses.
    Optimized for FINAL_ORDERS sheet structure.
    """
    quote_data = []
    
    for success in successes:
        response = success.get("response", {})
        quote_id = response.get("quoteId")
        
        if quote_id:
            # Extract all the structured data that was created in quote creation
            row = success.get("row", {})
            client_details = success.get("client_details", {})
            restaurant_details = success.get("restaurant_details", {})
            order_details = success.get("order_details", {})
            
            # Debug: Print what we're extracting (can be removed in production)
            # print(f"🔍 Extracting data for quote {quote_id}:")
            # print(f"   Client: {client_details.get('name', 'Unknown')}")
            # print(f"   Restaurant: {restaurant_details.get('name', 'Unknown')}")
            # print(f"   Order: {order_details.get('order_description', 'Unknown')}")
            
            quote_data.append({
                "quote_id": quote_id,
                "original_row": row,  # Complete row with all data
                "quote_response": response,
                "client_details": client_details,
                "restaurant_details": restaurant_details,
                "order_details": order_details,
                "index": success.get("index")
            })
        else:
            print(f"⚠️  Warning: No quoteId found in success response at index {success.get('index')}")
    
    return quote_data

def create_order_payload(quote_data: Dict[str, Any], client_details: Dict[str, str]) -> Dict[str, Any]:
    """
    Create order payload for the Glovo API.
    Optimized for FINAL_ORDERS sheet structure.
    """
    # Debug: Print client details being used (can be removed in production)
    # print(f"🔍 Creating order payload with client details:")
    # print(f"   Client details: {client_details}")
    # print(f"   Name: {client_details.get('name', 'NOT_FOUND')}")
    # print(f"   Phone: {client_details.get('phone', 'NOT_FOUND')}")
    # print(f"   Email: {client_details.get('email', 'NOT_FOUND')}")
    
    # Generate pickup order code
    pickup_order_code = f"ORD{int(time.time())}{quote_data.get('index', 0)}"
    
    # Get additional information from original row
    original_row = quote_data.get("original_row", {})
    order_details = quote_data.get("order_details", {})
    
    # Use the descriptive order_id as package description
    package_description = original_row.get("order_id", "Food delivery order")
    
    # Validate that we have all required client details
    if not client_details.get("name") or not client_details.get("phone") or not client_details.get("email"):
        raise ValueError(f"Missing required client details: {client_details}")
    
    payload = {
        "contact": {
            "name": client_details["name"],
            "phone": client_details["phone"],
            "email": client_details["email"]
        },
        "pickupOrderCode": pickup_order_code,
        "packageDetails": {
            "contentType": "FOOD",  # Default to FOOD for restaurant orders
            "description": package_description,  # Use your descriptive order_id
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

def process_orders_from_quotes_final(
        quote_data_list: List[Dict[str, Any]],
        rate_limit_per_sec: float = 2.0,
        log_orders: bool = True,
        excel_output_file: str = None,
        use_google_sheets: bool = True,
        google_sheets_url: str = None
    ) -> Dict[str, Any]:
    """
    Process multiple orders from quote data.
    Optimized for FINAL_ORDERS sheet structure.
    """
    delay = 1.0 / max(rate_limit_per_sec, 0.001)
    successful_orders = []
    failed_orders = []
    
    # Initialize order loggers if logging is enabled
    order_logger = None
    google_sheets_logger = None
    
    if log_orders:
        if use_google_sheets and google_sheets_url and GoogleSheetsLogger:
            try:
                google_sheets_logger = GoogleSheetsLogger(google_sheets_url, "Glovo-Orders-Summary")
                print("✅ Google Sheets logging enabled")
            except Exception as e:
                print(f"⚠️  Google Sheets logging failed: {e}")
                print("📝 Falling back to local Excel logging")
                if OrderLogger:
                    order_logger = OrderLogger()
                else:
                    print("⚠️  Order logging disabled - modules not available")
        elif OrderLogger:
            order_logger = OrderLogger()
        else:
            print("⚠️  Order logging disabled - modules not available")
    
    print(f"🚀 Processing {len(quote_data_list)} orders from FINAL_ORDERS...")
    print(f"📊 Rate limit: {rate_limit_per_sec} requests/second")
    
    for i, quote_data in enumerate(quote_data_list, start=1):
        quote_id = quote_data["quote_id"]
        original_row = quote_data.get("original_row", {})
        client_details = quote_data.get("client_details", {})
        restaurant_details = quote_data.get("restaurant_details", {})
        order_details = quote_data.get("order_details", {})
        
        print(f"\n📦 Processing order {i}/{len(quote_data_list)}")
        # Show actual data or indicate missing data
        client_id = client_details.get('client_id', '')
        client_name = client_details.get('name', '')
        restaurant_name = restaurant_details.get('name', '')
        order_desc = order_details.get('order_description', '')
        
        print(f"   Client ID: {client_id if client_id else '❌ MISSING'}")
        print(f"   Client: {client_name if client_name else '❌ MISSING'}")
        print(f"   Restaurant: {restaurant_name if restaurant_name else '❌ MISSING'}")
        print(f"   Order: {order_desc if order_desc else '❌ MISSING'}")
        print(f"   Quote ID: {quote_id}")
        
        # Create order payload
        payload = create_order_payload(quote_data, client_details)
        
        # Send order request
        print(f"   📤 Sending order request...")
        print(f"   🔗 URL: {ORDER_URL_TEMPLATE.format(quote_id=quote_id)}")
        print(f"   📋 Payload: {json.dumps(payload, indent=2)}")
        success, response = send_order_with_quote_id(quote_id, payload)
        
        if success:
            order_info = {
                "index": i,
                "quote_id": quote_id,
                "original_row": original_row,
                "order_response": response,
                "pickup_order_code": payload["pickupOrderCode"],
                "client_details": client_details,
                "restaurant_details": restaurant_details,
                "order_details": order_details
            }
            successful_orders.append(order_info)
            print(f"   ✅ Order created successfully!")
            print(f"   📋 Glovo Order ID: {response.get('id', 'N/A')}")
            print(f"   🏷️  Pickup Code: {payload['pickupOrderCode']}")
            print(f"   📄 Full Response: {json.dumps(response, indent=2)}")
            
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
            print(f"   📄 Full Error Response: {json.dumps(response, indent=2)}")
        
        # Rate limiting
        if i < len(quote_data_list):
            time.sleep(delay)
    
    # Save orders to Google Sheets or Excel if logging is enabled
    excel_file = None
    google_sheets_success = False
    
    if google_sheets_logger and hasattr(google_sheets_logger, 'order_log') and google_sheets_logger.order_log:
        try:
            google_sheets_success = google_sheets_logger.save_to_google_sheets()
            google_sheets_logger.print_summary()
        except Exception as e:
            print(f"⚠️  Warning: Could not save orders to Google Sheets: {e}")
    
    if order_logger and hasattr(order_logger, 'order_log') and order_logger.order_log:
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
    print("📊 ORDER CREATION SUMMARY (FINAL_ORDERS Sheet)")
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
            order_details = order.get('order_details', {})
            response = order.get('order_response', {})
            
            print(f"   {i}. {client.get('name', 'Unknown')} ({client.get('client_id', 'N/A')})")
            print(f"      Restaurant: {restaurant.get('name', 'Unknown')}")
            print(f"      Order: {order_details.get('order_description', 'N/A')}")
            print(f"      Glovo Order ID: {response.get('id', 'N/A')}")
            print(f"      Pickup Code: {order.get('pickup_order_code', 'N/A')}")
            print(f"      Quote ID: {order.get('quote_id', 'N/A')}")
    
    if results['failed_orders']:
        print(f"\n⚠️  FAILED ORDERS:")
        for i, failure in enumerate(results['failed_orders'][:3], 1):  # Show first 3
            original_row = failure.get('original_row', {})
            print(f"   {i}. {original_row.get('client_name', 'Unknown')} ({original_row.get('client_id', 'N/A')})")
            print(f"      Restaurant: {original_row.get('restaurant_name', 'Unknown')}")
            print(f"      Order: {original_row.get('order_id', 'N/A')}")
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

def save_order_results(results: Dict[str, Any], output_file: str = "order_results_final.json"):
    """Save order processing results to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Order results saved to: {output_file}")

if __name__ == "__main__":
    # Example usage with FINAL_ORDERS sheet structure
    
    # Option 1: Load from file (if you saved step 2 results)
    try:
        quote_results_file = "quote_results_final.json"  # File from step 2
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
    print("\n🚀 Starting Order Creation (FINAL_ORDERS Sheet)")
    print("="*60)
    
    google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
    
    results = process_orders_from_quotes_final(
        quote_data_list=quote_data_list,
        rate_limit_per_sec=2.0,  # Conservative rate limiting
        log_orders=True,  # Enable order logging
        excel_output_file="order_results_final.xlsx",  # Fallback Excel file
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
    save_order_results(results, "order_results_final.json")
    
    print(f"\n🎉 Order processing completed (FINAL_ORDERS Sheet)!")
    print(f"📈 Overall success rate: {results['success_rate']:.1f}%")
