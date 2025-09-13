#!/usr/bin/env python3
"""
automated_order_scheduler_simple.py
Automated order scheduling for simple A-L structure (columns A-L, each row = one complete order).
Perfect for 3 weekly orders per client with scalability to 300 clients.
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

from sheet_to_json import load_workbook_to_dict
from POST_create_quote_id_simple import process_orders_simple
from send_order_with_quote_id_simple import process_orders_from_quotes_simple

class SimpleOrderScheduler:
    """Simple automated order scheduling system for A-L structure."""
    
    def __init__(self, google_sheets_url: str):
        self.google_sheets_url = google_sheets_url
        self.workbook = None
        self.orders = []
        
    def load_data(self):
        """Load orders from Google Sheets with A-L structure."""
        print("📊 Loading orders from Google Sheets (A-L structure)...")
        self.workbook = load_workbook_to_dict(self.google_sheets_url)
        
        # Load orders (each row contains complete order information)
        orders_data = self.workbook.get("Orders", [])
        self.orders = orders_data
        print(f"✅ Loaded {len(self.orders)} existing orders")
        
        # Display sample order structure
        if self.orders:
            print(f"\n📋 Sample order structure (A-L columns):")
            sample_order = self.orders[0]
            for key, value in sample_order.items():
                print(f"   {key}: {value}")
    
    def generate_weekly_orders(self, client_name: str, client_phone: str, client_email: str,
                             delivery_address: str, delivery_latitude: float, delivery_longitude: float,
                             delivery_details: str, pickup_address_book_id: str, 
                             order_days: List[str] = ["Monday", "Wednesday", "Friday"],
                             order_time: str = "17:45", order_notes: str = "") -> List[Dict[str, Any]]:
        """
        Generate 3 weekly orders for a client.
        Returns list of order dictionaries ready for processing.
        """
        print(f"📅 Generating weekly orders for {client_name}...")
        
        # Map day names to numbers
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_days = [day_mapping.get(day.lower(), -1) for day in order_days]
        target_days = [d for d in target_days if d != -1]
        
        if not target_days:
            print(f"❌ No valid order days specified: {order_days}")
            return []
        
        # Generate orders for next 7 days
        start_date = date.today()
        new_orders = []
        
        for i in range(14):  # Look ahead 2 weeks to find 3 orders
            check_date = start_date + timedelta(days=i)
            if check_date.weekday() in target_days:
                # Check if order already exists for this date
                existing_order = any(
                    order.get("client_name") == client_name and 
                    order.get("order_date") == check_date.isoformat() and
                    order.get("order_status") in ["PENDING", "CONFIRMED", "IN_PROGRESS"]
                    for order in self.orders
                )
                
                if existing_order:
                    print(f"   ⏭️  Order already exists for {client_name} on {check_date}")
                    continue
                
                # Generate pickup time
                pickup_datetime = datetime.combine(check_date, datetime.strptime(order_time, "%H:%M").time())
                pickup_time_utc = pickup_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                # Generate order ID
                order_id = f"ORD_{check_date.strftime('%Y%m%d')}_{client_name.replace(' ', '_')}"
                
                order = {
                    "order_id": order_id,
                    "client_name": client_name,
                    "client_phone": client_phone,
                    "client_email": client_email,
                    "delivery_address": delivery_address,
                    "delivery_latitude": delivery_latitude,
                    "delivery_longitude": delivery_longitude,
                    "delivery_details": delivery_details,
                    "pickup_address_book_id": pickup_address_book_id,
                    "pickup_time_utc": pickup_time_utc,
                    "order_notes": order_notes,
                    "order_status": "PENDING"
                }
                
                new_orders.append(order)
                print(f"   ✅ Generated order for {check_date}: {order_id}")
                
                if len(new_orders) >= 3:  # Generate exactly 3 orders
                    break
        
        print(f"📊 Generated {len(new_orders)} new orders for {client_name}")
        return new_orders
    
    def process_orders(self, new_orders: List[Dict[str, Any]], 
                      process_immediately: bool = True) -> Dict[str, Any]:
        """Process new orders through the Glovo API."""
        if not new_orders:
            print("📭 No orders to process")
            return {"total_processed": 0, "successful_orders": [], "failed_orders": []}
        
        print(f"\n🚀 Processing {len(new_orders)} new orders...")
        
        if not process_immediately:
            print("⏸️  Orders generated but not processed (process_immediately=False)")
            return {
                "total_processed": 0,
                "successful_orders": [],
                "failed_orders": [],
                "pending_orders": new_orders
            }
        
        # Step 1: Create quotes
        print("\n💰 Step 1: Creating quotes...")
        quote_summary = process_orders_simple(new_orders, rate_limit_per_sec=2.0)
        
        if not quote_summary['successes']:
            print("❌ No successful quotes created. Cannot proceed to order creation.")
            return {
                "total_processed": len(new_orders),
                "successful_orders": [],
                "failed_orders": quote_summary['failures'],
                "quote_summary": quote_summary
            }
        
        # Step 2: Create orders
        print("\n📦 Step 2: Creating orders...")
        from send_order_with_quote_id_simple import extract_quote_ids_from_successes, process_orders_from_quotes_simple
        
        quote_data_list = extract_quote_ids_from_successes(quote_summary['successes'])
        
        order_results = process_orders_from_quotes_simple(
            quote_data_list=quote_data_list,
            rate_limit_per_sec=1.5,
            log_orders=True,
            excel_output_file="automated_order_results_simple.xlsx",
            use_google_sheets=True,
            google_sheets_url=self.google_sheets_url
        )
        
        return {
            "total_processed": len(new_orders),
            "successful_orders": order_results['successful_orders'],
            "failed_orders": order_results['failed_orders'],
            "quote_summary": quote_summary,
            "order_results": order_results
        }
    
    def print_summary(self, results: Dict[str, Any]):
        """Print comprehensive summary of the automation run."""
        print("\n" + "="*70)
        print("🤖 AUTOMATED ORDER SCHEDULING SUMMARY (A-L Structure)")
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
                order_id = original_row.get('order_id', 'N/A')
                print(f"   {i}. {client_name} - Order {order_id}")
        
        if results.get('failed_orders'):
            print(f"\n⚠️  FAILED ORDERS:")
            for i, failure in enumerate(results['failed_orders'][:3], 1):
                original_row = failure.get('original_row', {})
                client_name = original_row.get('client_name', 'Unknown')
                order_id = original_row.get('order_id', 'N/A')
                error = failure.get('error', 'Unknown error')
                print(f"   {i}. {client_name} - Order {order_id} - {error}")

def main():
    """Main automation function for A-L structure."""
    print("🤖 Glovo Simple Order Scheduler (A-L Structure)")
    print("="*60)
    
    # Configuration
    GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
    
    # Initialize scheduler
    scheduler = SimpleOrderScheduler(GOOGLE_SHEETS_URL)
    
    try:
        # Load data
        scheduler.load_data()
        
        # Example: Generate weekly orders for one client
        # You can modify these parameters for your client
        client_orders = scheduler.generate_weekly_orders(
            client_name="Яна Димитрова",
            client_phone="894387703",
            client_email="yanatest@gmail.com",
            delivery_address="g.k. Strelbishte, Nishava St 1р 1408, Bulgaria",
            delivery_latitude=42.673758,
            delivery_longitude=23.298064,
            delivery_details="Етаж 2 ап. 1",
            pickup_address_book_id="dd560a2c-f1b5-43b7-81bc-2830595122f9",
            order_days=["Monday", "Wednesday", "Friday"],
            order_time="17:45",
            order_notes="Regular weekly order"
        )
        
        if not client_orders:
            print("📭 No new orders to generate")
            return
        
        # Process orders immediately
        results = scheduler.process_orders(client_orders, process_immediately=True)
        
        # Print summary
        scheduler.print_summary(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"simple_automated_results_{timestamp}.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
