#!/usr/bin/env python3
"""
complete_workflow_example.py
Complete workflow example showing how to:
1. Create quotes (Step 2)
2. Filter responses and extract quote IDs
3. Create orders with quote IDs (Step 3)

This demonstrates the complete process from quote creation to order placement.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List

# Add parent directories to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_1_authentication'))

from POST_create_quote_id import process_orders, iter_orders_from_file
from send_order_with_quote_id import extract_quote_ids_from_successes, process_orders_from_quotes

def run_complete_workflow():
    """
    Run the complete workflow from quote creation to order placement.
    """
    print("=== Glovo DariVreme Order Automation - Complete Workflow ===\n")
    
    # Step 1: Check authentication
    print("Step 1: Checking authentication...")
    token = os.getenv("GLOVO_TOKEN")
    if not token or token == "YOUR_BEARER_TOKEN_HERE":
        print("❌ Please set GLOVO_TOKEN environment variable")
        print("   export GLOVO_TOKEN='your_actual_token_here'")
        return False
    print("✅ Authentication token found")
    
    # Step 2: Create quotes
    print("\nStep 2: Creating quotes...")
    try:
        # Load order data (adjust path as needed)
        path_to_json = "../step_2_quota_Config/workbook.json"
        sheet_name = "Orders"
        
        if not os.path.exists(path_to_json):
            print(f"❌ Data file not found: {path_to_json}")
            print("   Please run the data processing step first")
            return False
        
        rows = iter_orders_from_file(path_to_json, sheet_name=sheet_name)
        quote_summary = process_orders(rows, rate_limit_per_sec=3.0)
        
        print(f"✅ Quote creation completed:")
        print(f"   - Total processed: {quote_summary['total']}")
        print(f"   - Successful quotes: {len(quote_summary['successes'])}")
        print(f"   - Failed quotes: {len(quote_summary['failures'])}")
        
        if not quote_summary['successes']:
            print("❌ No successful quotes created. Cannot proceed to order creation.")
            return False
            
    except Exception as e:
        print(f"❌ Error in quote creation: {e}")
        return False
    
    # Step 3: Extract quote IDs and create orders
    print("\nStep 3: Creating orders with quote IDs...")
    try:
        # Extract quote IDs from successful responses
        quote_data_list = extract_quote_ids_from_successes(quote_summary['successes'])
        print(f"✅ Extracted {len(quote_data_list)} quote IDs")
        
        if not quote_data_list:
            print("❌ No valid quote IDs found")
            return False
        
        # Client details (customize as needed)
        client_details = {
            "name": "DariVreme Client",
            "phone": "+1234567890",
            "email": "client@darivreme.com"
        }
        
        # Create orders
        order_results = process_orders_from_quotes(
            quote_data_list=quote_data_list,
            client_details=client_details,
            rate_limit_per_sec=2.0
        )
        
        print(f"✅ Order creation completed:")
        print(f"   - Total processed: {order_results['total_processed']}")
        print(f"   - Successful orders: {len(order_results['successful_orders'])}")
        print(f"   - Failed orders: {len(order_results['failed_orders'])}")
        print(f"   - Success rate: {order_results['success_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Error in order creation: {e}")
        return False
    
    # Save final results
    print("\nStep 4: Saving results...")
    final_results = {
        "workflow_completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "quote_summary": quote_summary,
        "order_results": order_results
    }
    
    with open("complete_workflow_results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print("✅ Complete workflow results saved to: complete_workflow_results.json")
    
    # Final summary
    print("\n=== Final Summary ===")
    print(f"Quotes created: {len(quote_summary['successes'])}")
    print(f"Orders placed: {len(order_results['successful_orders'])}")
    print(f"Overall success rate: {order_results['success_rate']:.1f}%")
    
    return True

def demonstrate_quote_response_filtering():
    """
    Demonstrate how to filter quote responses and extract quote IDs.
    """
    print("\n=== Quote Response Filtering Example ===")
    
    # Example quote response structure (as returned by Glovo API)
    example_quote_response = {
        "quoteId": "826e5192-f8c6-4e24-aab3-3910e46c52b7",
        "quotePrice": 0,
        "currencyCode": "EUR",
        "distanceInMeters": 1500,
        "createdAt": "2024-01-15T14:15:22Z",
        "expiresAt": "2024-01-15T14:25:22Z",
        "pickupDetails": {
            "addressBook": {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "formattedAddress": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
                "coordinates": {
                    "latitude": 41.39637,
                    "longitude": 2.17939
                }
            },
            "pickupTime": "2024-01-15T14:15:22Z"
        },
        "deliveryAddress": {
            "rawAddress": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
            "formattedAddress": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
            "coordinates": {
                "latitude": 41.39637,
                "longitude": 2.17939
            },
            "details": "Floor 6 Door 3"
        },
        "estimatedTimeOfDelivery": {
            "lowerBound": "PT15M",
            "upperBound": "PT30M"
        }
    }
    
    # Example success entry from step 2
    example_success = {
        "index": 1,
        "row": {
            "pickup_address_id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "pickup_time_utc": "2024-01-15T14:15:22Z",
            "dest_raw_address": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
            "dest_lat": 41.39637,
            "dest_lng": 2.17939,
            "dest_details": "Floor 6 Door 3"
        },
        "response": example_quote_response
    }
    
    print("Example quote response structure:")
    print(json.dumps(example_quote_response, indent=2))
    
    print("\nExtracting quote ID:")
    quote_id = example_quote_response.get("quoteId")
    print(f"Quote ID: {quote_id}")
    
    print("\nQuote data for order creation:")
    quote_data = {
        "quote_id": quote_id,
        "original_row": example_success["row"],
        "quote_response": example_quote_response,
        "index": example_success["index"]
    }
    print(json.dumps(quote_data, indent=2))
    
    print("\nOrder payload that would be sent:")
    order_payload = {
        "finalClient": {
            "name": "DariVreme Client",
            "phone": "+1234567890",
            "email": "client@darivreme.com"
        },
        "pickupOrderCode": f"ORD{int(time.time())}{example_success['index']}"
    }
    print(json.dumps(order_payload, indent=2))

if __name__ == "__main__":
    # Run demonstration
    demonstrate_quote_response_filtering()
    
    # Ask user if they want to run the complete workflow
    print("\n" + "="*60)
    response = input("Do you want to run the complete workflow? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        success = run_complete_workflow()
        if success:
            print("\n🎉 Complete workflow executed successfully!")
        else:
            print("\n❌ Workflow failed. Please check the errors above.")
    else:
        print("Workflow demonstration completed.")
