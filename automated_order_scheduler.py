#!/usr/bin/env python3
"""
automated_order_scheduler.py
Automated order scheduling system for 3 weekly orders per client with scalability to 300 clients.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_3_send_order_with_quotaID'))

from sheet_to_json import load_workbook_to_dict
from POST_create_quote_id_optimized import process_orders_optimized
from send_order_with_quote_id_optimized import process_orders_from_quotes_optimized

class AutomatedOrderScheduler:
    """Automated order scheduling system for scalable client management."""
    
    def __init__(self, google_sheets_url: str):
        self.google_sheets_url = google_sheets_url
        self.workbook = None
        self.clients = {}
        self.restaurants = {}
        self.orders = []
        
    def load_data(self):
        """Load all data from Google Sheets."""
        print("📊 Loading data from Google Sheets...")
        self.workbook = load_workbook_to_dict(self.google_sheets_url)
        
        # Load clients
        clients_data = self.workbook.get("Clients", [])
        self.clients = {row["client_id"]: row for row in clients_data if row.get("is_active", True)}
        print(f"✅ Loaded {len(self.clients)} active clients")
        
        # Load restaurants
        restaurants_data = self.workbook.get("Restaurants", [])
        self.restaurants = {row["restaurant_id"]: row for row in restaurants_data if row.get("is_active", True)}
        print(f"✅ Loaded {len(self.restaurants)} active restaurants")
        
        # Load existing orders
        orders_data = self.workbook.get("Orders", [])
        self.orders = orders_data
        print(f"✅ Loaded {len(self.orders)} existing orders")
    
    def get_next_order_dates(self, client_id: str, days_ahead: int = 7) -> List[date]:
        """Get next order dates for a client based on their schedule."""
        client = self.clients.get(client_id)
        if not client:
            return []
        
        order_days = client.get("order_days", "").split(",")
        order_days = [day.strip().lower() for day in order_days]
        
        # Map day names to numbers
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_days = [day_mapping.get(day, -1) for day in order_days]
        target_days = [d for d in target_days if d != -1]
        
        if not target_days:
            return []
        
        # Start from today
        start_date = date.today()
        next_dates = []
        
        for i in range(days_ahead * 2):  # Look ahead enough days
            check_date = start_date + timedelta(days=i)
            if check_date.weekday() in target_days:
                next_dates.append(check_date)
                if len(next_dates) >= 3:  # Get next 3 orders
                    break
        
        return next_dates
    
    def generate_orders_for_client(self, client_id: str, order_dates: List[date]) -> List[Dict[str, Any]]:
        """Generate order records for a client for given dates."""
        client = self.clients.get(client_id)
        if not client:
            return []
        
        restaurant_id = client.get("restaurant_id")
        restaurant = self.restaurants.get(restaurant_id)
        if not restaurant:
            print(f"⚠️  Warning: Restaurant {restaurant_id} not found for client {client_id}")
            return []
        
        orders = []
        for order_date in order_dates:
            # Check if order already exists for this date
            existing_order = any(
                order.get("client_id") == client_id and 
                order.get("order_date") == order_date.isoformat() and
                order.get("order_status") in ["PENDING", "CONFIRMED", "IN_PROGRESS"]
                for order in self.orders
            )
            
            if existing_order:
                print(f"   ⏭️  Order already exists for {client_id} on {order_date}")
                continue
            
            # Generate pickup time
            order_time = client.get("order_time", "17:45")
            pickup_datetime = datetime.combine(order_date, datetime.strptime(order_time, "%H:%M").time())
            pickup_time_utc = pickup_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Generate order ID
            order_id = f"ORD_{order_date.strftime('%Y%m%d')}_{client_id}"
            
            order = {
                "order_id": order_id,
                "client_id": client_id,
                "restaurant_id": restaurant_id,
                "order_date": order_date.isoformat(),
                "pickup_time_utc": pickup_time_utc,
                "order_status": "PENDING",
                "quote_id": None,
                "glovo_order_id": None,
                "pickup_order_code": None,
                "order_notes": client.get("delivery_details", ""),
                "created_at": datetime.now().isoformat(),
                "is_automated": True,
                # Include all data needed for API calls
                "client_name": client.get("client_name"),
                "client_phone": client.get("client_phone"),
                "client_email": client.get("client_email"),
                "delivery_address": client.get("delivery_address"),
                "delivery_latitude": client.get("delivery_latitude"),
                "delivery_longitude": client.get("delivery_longitude"),
                "delivery_details": client.get("delivery_details", ""),
                "restaurant_name": restaurant.get("restaurant_name"),
                "pickup_address_book_id": restaurant.get("pickup_address_book_id")
            }
            
            orders.append(order)
        
        return orders
    
    def schedule_orders(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Schedule orders for all active clients."""
        print(f"📅 Scheduling orders for next {days_ahead} days...")
        
        all_new_orders = []
        
        for client_id, client in self.clients.items():
            if not client.get("is_active", True):
                continue
            
            print(f"\n👤 Processing client: {client.get('client_name', client_id)}")
            
            # Get next order dates for this client
            order_dates = self.get_next_order_dates(client_id, days_ahead)
            
            if not order_dates:
                print(f"   ⚠️  No order dates found for client {client_id}")
                continue
            
            print(f"   📅 Next order dates: {[d.isoformat() for d in order_dates]}")
            
            # Generate orders for this client
            client_orders = self.generate_orders_for_client(client_id, order_dates)
            all_new_orders.extend(client_orders)
            
            print(f"   ✅ Generated {len(client_orders)} new orders")
        
        print(f"\n📊 Total new orders generated: {len(all_new_orders)}")
        return all_new_orders
    
    def process_scheduled_orders(self, new_orders: List[Dict[str, Any]], 
                               process_immediately: bool = True) -> Dict[str, Any]:
        """Process scheduled orders through the Glovo API."""
        if not new_orders:
            print("📭 No orders to process")
            return {"total_processed": 0, "successful_orders": [], "failed_orders": []}
        
        print(f"\n🚀 Processing {len(new_orders)} scheduled orders...")
        
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
        quote_summary = process_orders_optimized(new_orders, rate_limit_per_sec=2.0)
        
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
        from send_order_with_quote_id_optimized import extract_quote_ids_from_successes, process_orders_from_quotes_optimized
        
        quote_data_list = extract_quote_ids_from_successes(quote_summary['successes'])
        
        order_results = process_orders_from_quotes_optimized(
            quote_data_list=quote_data_list,
            rate_limit_per_sec=1.5,
            log_orders=True,
            excel_output_file="automated_order_results.xlsx",
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
    
    def update_client_schedules(self, results: Dict[str, Any]):
        """Update client next order dates based on processing results."""
        print("\n📅 Updating client schedules...")
        
        # Update last order dates for successful orders
        for order in results.get('successful_orders', []):
            client_id = order.get('original_row', {}).get('client_id')
            if client_id and client_id in self.clients:
                order_date = order.get('original_row', {}).get('order_date')
                if order_date:
                    self.clients[client_id]['last_order_date'] = order_date
                    # Calculate next order date
                    next_dates = self.get_next_order_dates(client_id, 14)  # Look 2 weeks ahead
                    if next_dates:
                        self.clients[client_id]['next_order_date'] = next_dates[0].isoformat()
        
        print("✅ Client schedules updated")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print comprehensive summary of the automation run."""
        print("\n" + "="*70)
        print("🤖 AUTOMATED ORDER SCHEDULING SUMMARY")
        print("="*70)
        print(f"📊 Total orders processed: {results.get('total_processed', 0)}")
        print(f"✅ Successful orders: {len(results.get('successful_orders', []))}")
        print(f"❌ Failed orders: {len(results.get('failed_orders', []))}")
        
        if results.get('successful_orders'):
            success_rate = len(results['successful_orders']) / results['total_processed'] * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
            
            print(f"\n🎉 SUCCESSFUL ORDERS:")
            for i, order in enumerate(results['successful_orders'][:5], 1):
                client_name = order.get('client_details', {}).get('name', 'Unknown')
                restaurant_name = order.get('restaurant_details', {}).get('name', 'Unknown')
                order_id = order.get('original_row', {}).get('order_id', 'N/A')
                print(f"   {i}. {client_name} → {restaurant_name} (Order: {order_id})")
        
        if results.get('failed_orders'):
            print(f"\n⚠️  FAILED ORDERS:")
            for i, failure in enumerate(results['failed_orders'][:3], 1):
                client_name = failure.get('original_row', {}).get('client_name', 'Unknown')
                error = failure.get('error', 'Unknown error')
                print(f"   {i}. {client_name} - {error}")

def main():
    """Main automation function."""
    print("🤖 Glovo Automated Order Scheduler")
    print("="*50)
    
    # Configuration
    GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
    
    # Initialize scheduler
    scheduler = AutomatedOrderScheduler(GOOGLE_SHEETS_URL)
    
    try:
        # Load data
        scheduler.load_data()
        
        # Schedule orders for next 7 days
        new_orders = scheduler.schedule_orders(days_ahead=7)
        
        if not new_orders:
            print("📭 No new orders to schedule")
            return
        
        # Process orders immediately (set to False for testing)
        results = scheduler.process_scheduled_orders(new_orders, process_immediately=True)
        
        # Update client schedules
        scheduler.update_client_schedules(results)
        
        # Print summary
        scheduler.print_summary(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"automated_results_{timestamp}.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
