#!/usr/bin/env python3
"""
send_order_with_quote_id.py
Step 3: Send orders using Quote IDs obtained from Step 2

This module:
1. Filters successful quote responses from Step 2
2. Extracts quote IDs from the responses
3. Creates orders using the Glovo API /v2/laas/quotes/{quoteId}/parcels endpoint
4. Handles order creation with client details and pickup codes
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
    
    Args:
        successes: List of successful responses from step 2
        
    Returns:
        List of dictionaries containing quote_id and original row data
    """
    quote_data = []
    
    for success in successes:
        response = success.get("response", {})
        quote_id = response.get("quoteId")
        
        if quote_id:
            quote_data.append({
                "quote_id": quote_id,
                "original_row": success.get("row", {}),
                "quote_response": response,
                "index": success.get("index")
            })
        else:
            print(f"Warning: No quoteId found in success response at index {success.get('index')}")
    
    return quote_data

def create_order_payload(quote_data: Dict[str, Any], client_details: Dict[str, str]) -> Dict[str, Any]:
    """
    Create order payload for the Glovo API.
    
    Args:
        quote_data: Dictionary containing quote_id and original row data
        client_details: Client information (name, phone, email)
        
    Returns:
        Order payload for API request
    """
    # Generate pickup order code (you can customize this logic)
    pickup_order_code = f"ORD{int(time.time())}{quote_data.get('index', 0)}"
    
    payload = {
        "contact": {
            "name": client_details.get("name", "Default Client"),
            "phone": client_details.get("phone", "+1234567890"),
            "email": client_details.get("email", "client@example.com")
        },
        "pickupOrderCode": pickup_order_code
    }
    
    return payload

def send_order_with_quote_id(quote_id: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Send order creation request using quote ID.
    
    Args:
        quote_id: The quote ID obtained from step 2
        payload: Order payload with client details
        
    Returns:
        Tuple of (success, response_data)
    """
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

def process_orders_from_quotes(quote_data_list: List[Dict[str, Any]], 
                              client_details: Dict[str, str],
                              rate_limit_per_sec: float = 2.0,
                              log_orders: bool = True,
                              excel_output_file: str = None,
                              use_google_sheets: bool = True,
                              google_sheets_url: str = None) -> Dict[str, Any]:
    """
    Process multiple orders from quote data.
    
    Args:
        quote_data_list: List of quote data with quote IDs
        client_details: Client information for all orders
        rate_limit_per_sec: Rate limiting for API requests
        log_orders: Whether to log orders
        excel_output_file: Path to Excel file for logging (fallback)
        use_google_sheets: Whether to use Google Sheets for logging
        google_sheets_url: URL of Google Sheets document
        
    Returns:
        Summary of order processing results
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
    
    print(f"Processing {len(quote_data_list)} orders...")
    
    for i, quote_data in enumerate(quote_data_list, start=1):
        quote_id = quote_data["quote_id"]
        print(f"Processing order {i}/{len(quote_data_list)} - Quote ID: {quote_id}")
        
        # Create order payload
        payload = create_order_payload(quote_data, client_details)
        
        # Send order request
        success, response = send_order_with_quote_id(quote_id, payload)
        
        if success:
            order_info = {
                "index": i,
                "quote_id": quote_id,
                "original_row": quote_data["original_row"],
                "order_response": response,
                "pickup_order_code": payload["pickupOrderCode"]
            }
            successful_orders.append(order_info)
            print(f"✅ Order created successfully for Quote ID: {quote_id}")
            
            # Log the order if logging is enabled
            if google_sheets_logger:
                try:
                    google_sheets_logger.log_order(response, quote_data, client_details)
                except Exception as e:
                    print(f"⚠️  Warning: Could not log order {quote_id} to Google Sheets: {e}")
            elif order_logger:
                try:
                    order_logger.log_order(response, quote_data, client_details)
                except Exception as e:
                    print(f"⚠️  Warning: Could not log order {quote_id}: {e}")
        else:
            failed_orders.append({
                "index": i,
                "quote_id": quote_id,
                "original_row": quote_data["original_row"],
                "error": response
            })
            print(f"❌ Order failed for Quote ID: {quote_id} - {response}")
        
        # Rate limiting
        if i < len(quote_data_list):  # Don't sleep after the last request
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

def load_quote_successes_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Load successful quote responses from a JSON file.
    
    Args:
        file_path: Path to JSON file containing quote results
        
    Returns:
        List of successful quote responses
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "successes" in data:
        return data["successes"]
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("Invalid JSON structure. Expected dict with 'successes' key or list of successes.")

def save_order_results(results: Dict[str, Any], output_file: str = "order_results.json"):
    """
    Save order processing results to a JSON file.
    
    Args:
        results: Order processing results
        output_file: Output file path
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Order results saved to: {output_file}")

if __name__ == "__main__":
    # Example usage
    
    # Option 1: Load from file (if you saved step 2 results)
    try:
        quote_results_file = "quote_results.json"  # File from step 2
        successes = load_quote_successes_from_file(quote_results_file)
        print(f"Loaded {len(successes)} successful quotes from {quote_results_file}")
    except FileNotFoundError:
        print("Quote results file not found. Please run step 2 first or provide the file path.")
        exit(1)
    except Exception as e:
        print(f"Error loading quote results: {e}")
        exit(1)
    
    # Extract quote IDs from successful responses
    quote_data_list = extract_quote_ids_from_successes(successes)
    print(f"Extracted {len(quote_data_list)} quote IDs")
    
    if not quote_data_list:
        print("No valid quote IDs found. Cannot proceed with order creation.")
        exit(1)
    
    # Client details for orders (customize as needed)
    client_details = {
        "name": "DariVreme Client",
        "phone": "+1234567890",
        "email": "client@darivreme.com"
    }
    
    # Process orders with Google Sheets logging
    print("\n=== Starting Order Creation ===")
    google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
    
    results = process_orders_from_quotes(
        quote_data_list=quote_data_list,
        client_details=client_details,
        rate_limit_per_sec=2.0,  # Conservative rate limiting
        log_orders=True,  # Enable order logging
        excel_output_file="order_results.xlsx",  # Fallback Excel file
        use_google_sheets=True,  # Use Google Sheets for logging
        google_sheets_url=google_sheets_url  # Your Google Sheets URL
    )
    
    # Print summary
    print("\n=== Order Creation Summary ===")
    print(f"Total processed: {results['total_processed']}")
    print(f"Successful orders: {len(results['successful_orders'])}")
    print(f"Failed orders: {len(results['failed_orders'])}")
    print(f"Success rate: {results['success_rate']:.1f}%")
    
    # Show logging information
    if results.get('google_sheets_success'):
        print(f"\n📊 Order results saved to Google Sheets!")
        print("   Sheet: 'Glovo-Orders-Summary'")
        print("   URL: https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit")
        print("   Columns: timestamp, order_id, client_name, pickup_address_book_id, etc.")
    elif results.get('excel_file'):
        print(f"\n📊 Order results saved to Excel: {results['excel_file']}")
        print("   Sheet: 'Order Results'")
        print("   Columns: timestamp, order_id, client_name, pickup_address_book_id, etc.")
    
    # Save results
    save_order_results(results, "order_results.json")
    
    # Show sample successful orders
    if results["successful_orders"]:
        print("\n=== Sample Successful Orders ===")
        for order in results["successful_orders"][:3]:
            print(f"Quote ID: {order['quote_id']}")
            print(f"Pickup Code: {order['pickup_order_code']}")
            print(f"Order Response: {json.dumps(order['order_response'], indent=2)}")
            print("-" * 50)
    
    # Show sample failures
    if results["failed_orders"]:
        print("\n=== Sample Failed Orders ===")
        for failure in results["failed_orders"][:3]:
            print(f"Quote ID: {failure['quote_id']}")
            print(f"Error: {json.dumps(failure['error'], indent=2)}")
            print("-" * 50)
