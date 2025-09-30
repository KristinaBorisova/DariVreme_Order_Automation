#!/usr/bin/env python3
"""
production_workflow.py
Production workflow using real Google Sheets data and authentication module.
"""

import os
import sys
import json
import time
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_3_send_order_with_quotaID'))


def main():
    """Run the complete production workflow."""
    print("🚀 Glovo DariVreme Order Automation - Production Workflow")
    print("=" * 60)

    # Configuration
    GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"

    try:
        # Step 1: Authentication
        print("\n🔐 Step 1: Authentication")
        print("-" * 30)

        from token_service import get_bearer_token
        token = get_bearer_token()

        if not token or len(token) < 10:
            print("❌ Authentication failed - invalid token")
            return False

        print("✅ Authentication successful")
        print(f"   Token: {token[:20]}...")

        # Step 2: Load and process data
        print("\n📊 Step 2: Loading data from Google Sheets")
        print("-" * 30)

        from sheet_to_json import load_workbook_to_dict
        from POST_create_quote_id import process_orders, iter_orders_from_memory

        print(f"Loading from: {GOOGLE_SHEETS_URL}")
        workbook = load_workbook_to_dict(GOOGLE_SHEETS_URL)

        # Find the sheet with order data
        sheet_names = list(workbook.keys())
        print(f"Available sheets: {sheet_names}")

        # Use the first sheet that contains data
        sheet_name = sheet_names[0] if sheet_names else "Sheet1"
        print(f"Using sheet: {sheet_name}")

        # Display sample data
        if workbook[sheet_name]:
            print(f"Found {len(workbook[sheet_name])} orders")
            print("Sample order structure:")

            sample_order = workbook[sheet_name][0]
            for key, value in sample_order.items():
                print(f"   {key}: {value}")

            #>> Correct Client information here
            client_keys = ["client_name", "client_phone", "client_email"]
            client_info = {k: sample_order.get(k, "N/A") for k in client_keys}
            print("\nExtracted client information (from first order row):")
            for k, v in client_info.items():
                print(f"Client Information: {k}: {v}")
        else:
            print("❌ No data found in the sheet")
            return False

        # Step 3: Create quotes
        print("\n💰 Step 3: Creating quotes")
        print("-" * 30)

        rows = iter_orders_from_memory(workbook, sheet_name=sheet_name)
        quote_summary = process_orders(rows, rate_limit_per_sec=2.0)  # Conservative rate

        print(f"Quote creation completed:")
        print(f"   - Total processed: {quote_summary['total']}")
        print(f"   - Successful quotes: {len(quote_summary['successes'])}")
        print(f"   - Failed quotes: {len(quote_summary['failures'])}")

        if not quote_summary['successes']:
            print("❌ No successful quotes created. Cannot proceed to order creation.")
            if quote_summary['failures']:
                print("Sample failure:")
                print(json.dumps(quote_summary['failures'][0], indent=2))
            return False

        # Step 4: Create orders
        print("\n📦 Step 4: Creating orders with quote IDs")
        print("-" * 30)

        from send_order_with_quote_id import (
            extract_quote_ids_from_successes,
            process_orders_from_quotes
        )

        # Extract quote IDs + preserve client info for each row
        quote_data_list = []
        for success in quote_summary['successes']:
            order_row = success.get("row", {})  # Use "row" instead of "order_row"
            # Try different keys for quote_id
            quote_id = success.get("response", {}).get("quoteId") or success.get("quote_id") or success.get("id")
            if not quote_id:
                print(f"⚠️ Skipping success entry, no quote_id found: {success}")
                continue

            client_details = {
                "name": order_row.get("client_name", "Unknown Client"),
                "phone": order_row.get("client_phone", "Unknown Phone"),
                "email": order_row.get("client_email", "Unknown Email")
            }

            quote_data_list.append({
                "quote_id": quote_id,
                "original_row": order_row,
                "client_details": client_details,
                "quote_response": success.get("response", {})
            })


        print(f"Prepared {len(quote_data_list)} quote IDs with client details")

        # Create orders with Google Sheets logging
        google_sheets_url = GOOGLE_SHEETS_URL

        order_results = process_orders_from_quotes(
            quote_data_list=quote_data_list,
            rate_limit_per_sec=1.5,
            log_orders=True,
            excel_output_file="production_order_results.xlsx",
            use_google_sheets=True,
            google_sheets_url=google_sheets_url
        )

        print(f"Order creation completed:")
        print(f"   - Total processed: {order_results['total_processed']}")
        print(f"   - Successful orders: {len(order_results['successful_orders'])}")
        print(f"   - Failed orders: {len(order_results['failed_orders'])}")
        print(f"   - Success rate: {order_results['success_rate']:.1f}%")

        # Show logging information
        if order_results.get('google_sheets_success'):
            print(f"   - Google Sheets: ✅ Saved to 'Glovo-Orders-Summary' sheet")
        elif order_results.get('excel_file'):
            print(f"   - Excel file: {order_results['excel_file']}")

        # Step 5: Save results
        print("\n💾 Step 5: Saving results")
        print("-" * 30)

        final_results = {
            "workflow_completed_at": datetime.now().isoformat(),
            "google_sheets_url": GOOGLE_SHEETS_URL,
            "sheet_name": sheet_name,
            "total_orders_processed": len(workbook[sheet_name]),
            "quote_summary": quote_summary,
            "order_results": order_results
        }

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"production_results_{timestamp}.json"

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2)

        print(f"✅ Results saved to: {results_file}")

        # Final summary
        print("\n" + "=" * 60)
        print("📊 PRODUCTION WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Data source: Google Sheets ({sheet_name})")
        print(f"📋 Total orders in sheet: {len(workbook[sheet_name])}")
        print(f"💰 Quotes created: {len(quote_summary['successes'])}")
        print(f"📦 Orders placed: {len(order_results['successful_orders'])}")
        print(f"✅ Overall success rate: {order_results['success_rate']:.1f}%")

        if order_results['successful_orders']:
            print(f"\n🎉 SUCCESS: {len(order_results['successful_orders'])} orders successfully placed!")

            # Show sample successful orders
            print("\n📋 Sample successful orders:")
            for i, order in enumerate(order_results['successful_orders'][:3], 1):
                print(f"   {i}. Quote ID: {order['quote_id']}")
                print(f"      Pickup Code: {order['pickup_order_code']}")
                if 'order_response' in order and 'id' in order['order_response']:
                    print(f"      Order ID: {order['order_response']['id']}")

        if order_results['failed_orders']:
            print(f"\n⚠️  WARNING: {len(order_results['failed_orders'])} orders failed")
            print("Sample failures:")
            for i, failure in enumerate(order_results['failed_orders'][:2], 1):
                print(f"   {i}. Quote ID: {failure['quote_id']}")
                print(f"      Error: {failure.get('error', 'Unknown error')}")

        print(f"\n📁 Detailed results saved in: {results_file}")

        return True

    except Exception as e:
        print(f"\n❌ Workflow failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_environment():
    """Validate that the environment is ready for production."""
    print("🔍 Validating environment...")

    # Check required dependencies
    try:
        import requests
        import pandas
        print("✅ Required dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install requests pandas openpyxl")
        return False

    # Check if authentication module exists
    auth_path = os.path.join(os.path.dirname(__file__), 'step_1_authentication', 'token_service.py')
    if not os.path.exists(auth_path):
        print(f"❌ Authentication module not found: {auth_path}")
        return False
    print("✅ Authentication module found")

    # Check if Google Sheets is accessible
    try:
        import requests
        test_url = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
        response = requests.head(test_url, timeout=10)
        if response.status_code == 200:
            print("✅ Google Sheets is accessible")
        else:
            print(f"⚠️  Google Sheets returned status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not verify Google Sheets access: {e}")

    return True


if __name__ == "__main__":
    print("🚀 Starting Glovo DariVreme Production Workflow")

    # Validate environment first
    if not validate_environment():
        print("\n❌ Environment validation failed. Please fix the issues above.")
        sys.exit(1)

    # Ask for confirmation
    print("\n⚠️  This will process REAL orders from your Google Sheets!")
    print("   Make sure you have:")
    print("   - Valid Glovo API credentials")
    print("   - Correct pickup address IDs")
    print("   - Future pickup times")

    try:
        confirm = input("\n🤔 Do you want to proceed? (yes/no): ").lower().strip()
        if confirm not in ['yes', 'y']:
            print("👋 Workflow cancelled by user")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n👋 Workflow cancelled by user")
        sys.exit(0)

    # Run the workflow
    success = main()

    if success:
        print("\n🎉 Production workflow completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Production workflow failed!")
        sys.exit(1)
