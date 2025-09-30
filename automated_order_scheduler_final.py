#!/usr/bin/env python3
"""
automated_order_scheduler_final.py
Automated order scheduling for FINAL_ORDERS sheet with exact column names.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Tuple, Optional

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_3_send_order_with_quotaID'))

try:
    from sheet_to_json import load_workbook_to_dict
    from POST_create_quote_id_final import process_orders_final
    from send_order_with_quote_id_final import process_orders_from_quotes_final
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("   Please ensure all required files are in the correct locations")
    load_workbook_to_dict = None
    process_orders_final = None
    process_orders_from_quotes_final = None

class FinalOrderScheduler:
    """Automated order scheduling system for FINAL_ORDERS sheet."""
    
    def __init__(self, google_sheets_url: str):
        self.google_sheets_url = google_sheets_url
        self.workbook = None
        self.orders = []
        
    def load_data(self):
        """Load orders from FINAL_ORDERS sheet."""
        if not load_workbook_to_dict:
            print("❌ Cannot load data - required modules not available")
            return
            
        print("📊 Loading orders from FINAL_ORDERS sheet...")
        self.workbook = load_workbook_to_dict(self.google_sheets_url)
        
        # Load orders from FINAL_ORDERS sheet
        orders_data = self.workbook.get("FINAL_ORDERS", [])
        self.orders = orders_data
        print(f"✅ Loaded {len(self.orders)} existing orders from FINAL_ORDERS sheet")
        
        # Display sample order structure
        if self.orders:
            print(f"\n📋 Sample order structure (FINAL_ORDERS columns):")
            sample_order = self.orders[0]
            for key, value in sample_order.items():
                print(f"   {key}: {value}")
    
    def process_existing_orders(self, process_immediately: bool = True) -> Dict[str, Any]:
        """Process all existing orders from FINAL_ORDERS sheet."""
        if not self.orders:
            print("📭 No orders found in FINAL_ORDERS sheet")
            return {"total_processed": 0, "successful_orders": [], "failed_orders": []}
        
        print(f"\n🚀 Processing {len(self.orders)} existing orders from FINAL_ORDERS sheet...")
        
        if not process_immediately:
            print("⏸️  Orders loaded but not processed (process_immediately=False)")
            return {
                "total_processed": 0,
                "successful_orders": [],
                "failed_orders": [],
                "pending_orders": self.orders
            }
        
        # Step 1: Create quotes
        if not process_orders_final:
            print("❌ Cannot process orders - required modules not available")
            return {"total_processed": 0, "successful_orders": [], "failed_orders": []}
            
        print("\n💰 Step 1: Creating quotes...")
        quote_summary = process_orders_final(self.orders, rate_limit_per_sec=2.0)
        
        if not quote_summary['successes']:
            print("❌ No successful quotes created. Cannot proceed to order creation.")
            return {
                "total_processed": len(self.orders),
                "successful_orders": [],
                "failed_orders": quote_summary['failures'],
                "quote_summary": quote_summary
            }
        
        # Step 2: Create orders
        if not process_orders_from_quotes_final:
            print("❌ Cannot create orders - required modules not available")
            return {
                "total_processed": len(self.orders),
                "successful_orders": [],
                "failed_orders": quote_summary['failures'],
                "quote_summary": quote_summary
            }
            
        print("\n📦 Step 2: Creating orders...")
        from send_order_with_quote_id_final import extract_quote_ids_from_successes, process_orders_from_quotes_final
        
        quote_data_list = extract_quote_ids_from_successes(quote_summary['successes'])
        
        order_results = process_orders_from_quotes_final(
            quote_data_list=quote_data_list,
            rate_limit_per_sec=1.5,
            log_orders=True,
            excel_output_file="final_automated_order_results.xlsx",
            use_google_sheets=True,
            google_sheets_url=self.google_sheets_url
        )
        
        return {
            "total_processed": len(self.orders),
            "successful_orders": order_results['successful_orders'],
            "failed_orders": order_results['failed_orders'],
            "quote_summary": quote_summary,
            "order_results": order_results
        }
    
    def print_summary(self, results: Dict[str, Any]):
        """Print comprehensive summary of the automation run."""
        print("\n" + "="*70)
        print("🤖 AUTOMATED ORDER SCHEDULING SUMMARY (FINAL_ORDERS Sheet)")
        print("="*70)
        print(f"📊 Total orders processed: {results.get('total_processed', 0)}")
        print(f"✅ Successful orders: {len(results.get('successful_orders', []))}")
        print(f"❌ Failed orders: {len(results.get('failed_orders', []))}")
        
        if results.get('successful_orders'):
            success_rate = len(results['successful_orders']) / results['total_processed'] * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
            
            print(f"\n🎉 SUCCESSFUL ORDERS:")
            for i, order in enumerate(results['successful_orders'][:5], 1):
                original_row = order.get('original_row', {})
                client_name = original_row.get('client_name', 'Unknown')
                client_id = original_row.get('client_id', 'N/A')
                restaurant_name = original_row.get('restaurant_name', 'Unknown')
                order_description = original_row.get('order_id', 'N/A')
                print(f"   {i}. {client_name} ({client_id}) → {restaurant_name}")
                print(f"      Order: {order_description}")
        
        if results.get('failed_orders'):
            print(f"\n⚠️  FAILED ORDERS:")
            for i, failure in enumerate(results['failed_orders'][:3], 1):
                original_row = failure.get('original_row', {})
                client_name = original_row.get('client_name', 'Unknown')
                client_id = original_row.get('client_id', 'N/A')
                restaurant_name = original_row.get('restaurant_name', 'Unknown')
                order_description = original_row.get('order_id', 'N/A')
                error = failure.get('error', 'Unknown error')
                print(f"   {i}. {client_name} ({client_id}) → {restaurant_name}")
                print(f"      Order: {order_description}")
                print(f"      Error: {error}")

def main():
    """Main automation function for FINAL_ORDERS sheet."""
    print("🤖 Glovo Final Order Scheduler (FINAL_ORDERS Sheet)")
    print("="*60)
    
    # Configuration
    GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
    
    # Initialize scheduler
    scheduler = FinalOrderScheduler(GOOGLE_SHEETS_URL)
    
    try:
        # Load data
        scheduler.load_data()
        
        if not scheduler.orders:
            print("📭 No orders found in FINAL_ORDERS sheet")
            return
        
        # Process all existing orders
        results = scheduler.process_existing_orders(process_immediately=True)
        
        # Print summary
        scheduler.print_summary(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"final_automated_results_{timestamp}.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
