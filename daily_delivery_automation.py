#!/usr/bin/env python3
"""
daily_delivery_automation.py
Automated daily delivery system for FINAL_ORDERS sheet.
Processes orders based on deliveryFrequency (3 or 5) and current weekday.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_3_send_order_with_quotaID'))

# Import required modules
try:
    from step_1_authentication.token_service import get_bearer_token
    from sheet_to_json import load_workbook_to_dict
    from POST_create_quote_id_final import process_orders_final
    from send_order_with_quote_id_final import process_orders_from_quotes_final
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("   Please ensure all required files are in the correct locations")
    exit(1)

# Configuration
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004"
SHEET_NAME = "FINAL_ORDERS"

# Delivery frequency mapping
DELIVERY_FREQUENCY_3_DAYS = [0, 2, 4]  # Monday, Wednesday, Friday (0-based)
DELIVERY_FREQUENCY_5_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday (0-based)

# Weekday names for logging
WEEKDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class DailyDeliveryAutomation:
    """Automated daily delivery system for FINAL_ORDERS sheet."""
    
    def __init__(self, google_sheets_url: str, sheet_name: str = "FINAL_ORDERS"):
        self.google_sheets_url = google_sheets_url
        self.sheet_name = sheet_name
        self.workbook = None
        self.orders = []
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the automation system."""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"daily_delivery_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def load_data(self):
        """Load orders from FINAL_ORDERS sheet."""
        try:
            self.logger.info("📊 Loading orders from FINAL_ORDERS sheet...")
            self.workbook = load_workbook_to_dict(self.google_sheets_url)
            
            if self.sheet_name not in self.workbook:
                self.logger.error(f"❌ Sheet '{self.sheet_name}' not found in workbook")
                return False
                
            self.orders = self.workbook[self.sheet_name]
            self.logger.info(f"✅ Loaded {len(self.orders)} orders from '{self.sheet_name}' sheet")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error loading data: {e}")
            return False
    
    def get_current_weekday(self) -> int:
        """Get current weekday (0=Monday, 6=Sunday)."""
        return datetime.now().weekday()
    
    def should_process_client(self, delivery_frequency: int, current_weekday: int) -> bool:
        """
        Determine if a client should be processed today based on delivery frequency.
        
        Args:
            delivery_frequency: 3 or 5 (delivery frequency per week)
            current_weekday: Current weekday (0=Monday, 6=Sunday)
            
        Returns:
            True if client should be processed today
        """
        # Only process Monday-Friday (0-4)
        if current_weekday > 4:  # Saturday or Sunday
            return False
            
        if delivery_frequency == 3:
            return current_weekday in DELIVERY_FREQUENCY_3_DAYS
        elif delivery_frequency == 5:
            return current_weekday in DELIVERY_FREQUENCY_5_DAYS
        else:
            self.logger.warning(f"⚠️  Unknown delivery frequency: {delivery_frequency}")
            return False
    
    def filter_orders_for_today(self) -> List[Dict[str, Any]]:
        """Filter orders that should be processed today based on delivery frequency."""
        current_weekday = self.get_current_weekday()
        current_weekday_name = WEEKDAY_NAMES[current_weekday]
        
        self.logger.info(f"📅 Today is {current_weekday_name} (weekday {current_weekday})")
        
        filtered_orders = []
        
        for order in self.orders:
            try:
                delivery_frequency = int(order.get('deliveryFrequency', 0))
                
                if self.should_process_client(delivery_frequency, current_weekday):
                    filtered_orders.append(order)
                    self.logger.info(f"✅ Client {order.get('client_name', 'Unknown')} (frequency={delivery_frequency}) scheduled for {current_weekday_name}")
                else:
                    self.logger.debug(f"⏭️  Client {order.get('client_name', 'Unknown')} (frequency={delivery_frequency}) not scheduled for {current_weekday_name}")
                    
            except (ValueError, TypeError) as e:
                self.logger.warning(f"⚠️  Invalid delivery frequency for client {order.get('client_name', 'Unknown')}: {e}")
                continue
        
        self.logger.info(f"📋 Filtered {len(filtered_orders)} orders for {current_weekday_name}")
        return filtered_orders
    
    def process_daily_orders(self, rate_limit_per_sec: float = 2.0) -> Dict[str, Any]:
        """
        Process daily orders based on delivery frequency.
        
        Args:
            rate_limit_per_sec: Rate limit for API requests
            
        Returns:
            Dictionary with processing results
        """
        current_weekday = self.get_current_weekday()
        current_weekday_name = WEEKDAY_NAMES[current_weekday]
        
        self.logger.info(f"🚀 Starting daily delivery automation for {current_weekday_name}")
        self.logger.info("="*60)
        
        # Filter orders for today
        today_orders = self.filter_orders_for_today()
        
        if not today_orders:
            self.logger.info("ℹ️  No orders scheduled for today")
            return {
                "total_processed": 0,
                "successful_orders": [],
                "failed_orders": [],
                "weekday": current_weekday_name,
                "message": "No orders scheduled for today"
            }
        
        self.logger.info(f"📦 Processing {len(today_orders)} orders for {current_weekday_name}")
        
        # Step 1: Create quotes
        self.logger.info("💰 Step 1: Creating quotes...")
        quote_summary = process_orders_final(today_orders, rate_limit_per_sec=rate_limit_per_sec)
        
        if not quote_summary['successes']:
            self.logger.error("❌ No successful quotes created. Cannot proceed to order creation.")
            return {
                "total_processed": len(today_orders),
                "successful_orders": [],
                "failed_orders": quote_summary['failures'],
                "quote_summary": quote_summary,
                "weekday": current_weekday_name,
                "message": "Quote creation failed"
            }
        
        self.logger.info(f"✅ Created {len(quote_summary['successes'])} successful quotes")
        
        # Step 2: Create orders
        self.logger.info("📦 Step 2: Creating orders...")
        
        # Extract quote data for order creation
        quote_data_list = []
        for i, success in enumerate(quote_summary['successes'], 1):
            # Debug: Print what we're extracting from quote creation
            self.logger.info(f"🔍 DEBUG - Extracting quote data {i}:")
            self.logger.info(f"   success keys: {list(success.keys())}")
            self.logger.info(f"   client_details: {success.get('client_details', {})}")
            self.logger.info(f"   restaurant_details: {success.get('restaurant_details', {})}")
            self.logger.info(f"   order_details: {success.get('order_details', {})}")
            
            quote_data = {
                "quote_id": success['response']['quoteId'],
                "original_row": success['row'],
                "quote_response": success['response'],
                "client_details": success.get('client_details', {}),
                "restaurant_details": success.get('restaurant_details', {}),
                "order_details": success.get('order_details', {}),
                "index": len(quote_data_list)
            }
            quote_data_list.append(quote_data)
        
        # Create orders
        order_results = process_orders_from_quotes_final(
            quote_data_list=quote_data_list,
            rate_limit_per_sec=rate_limit_per_sec,
            log_orders=True,
            use_google_sheets=True,
            google_sheets_url=self.google_sheets_url
        )
        
        # Log results
        self.logger.info("="*60)
        self.logger.info("📊 DAILY DELIVERY AUTOMATION SUMMARY")
        self.logger.info("="*60)
        self.logger.info(f"📅 Day: {current_weekday_name}")
        self.logger.info(f"📋 Total orders processed: {order_results['total_processed']}")
        self.logger.info(f"✅ Successful orders: {len(order_results['successful_orders'])}")
        self.logger.info(f"❌ Failed orders: {len(order_results['failed_orders'])}")
        
        if order_results['successful_orders']:
            self.logger.info("🎉 SUCCESSFUL ORDERS:")
            for order in order_results['successful_orders']:
                client_details = order.get('client_details', {})
                order_details = order.get('order_details', {})
                order_response = order.get('order_response', {})
                
                client_name = client_details.get('name', '')
                order_description = order_details.get('order_description', '')
                glovo_order_id = order_response.get('id', '')
                pickup_code = order.get('pickup_order_code', '')
                
                # Show actual data or indicate missing data
                if not client_name:
                    client_name = '❌ MISSING CLIENT NAME'
                if not order_description:
                    order_description = '❌ MISSING ORDER DESCRIPTION'
                if not glovo_order_id:
                    glovo_order_id = '❌ ORDER NOT CREATED'
                if not pickup_code:
                    pickup_code = '❌ MISSING PICKUP CODE'
                
                self.logger.info(f"   • {client_name} - {order_description}")
                self.logger.info(f"     Glovo Order ID: {glovo_order_id}")
                self.logger.info(f"     Pickup Code: {pickup_code}")
        
        if order_results['failed_orders']:
            self.logger.warning("⚠️  FAILED ORDERS:")
            for order in order_results['failed_orders']:
                original_row = order.get('original_row', {})
                client_name = original_row.get('client_name', 'Unknown')
                error = order.get('error', 'Unknown error')
                self.logger.warning(f"   • {client_name} - {error}")
        
        # Add weekday information to results
        order_results['weekday'] = current_weekday_name
        order_results['delivery_frequency_summary'] = self.get_delivery_frequency_summary(today_orders)
        
        return order_results
    
    def get_delivery_frequency_summary(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of delivery frequencies for processed orders."""
        freq_3_count = sum(1 for order in orders if int(order.get('deliveryFrequency', 0)) == 3)
        freq_5_count = sum(1 for order in orders if int(order.get('deliveryFrequency', 0)) == 5)
        
        return {
            "frequency_3_orders": freq_3_count,
            "frequency_5_orders": freq_5_count,
            "total_orders": len(orders)
        }
    
    def run_daily_automation(self, rate_limit_per_sec: float = 2.0) -> Dict[str, Any]:
        """Run the complete daily automation process."""
        self.logger.info("🤖 Starting Daily Delivery Automation")
        self.logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*60)
        
        # Load data
        if not self.load_data():
            return {"error": "Failed to load data"}
        
        # Process orders
        results = self.process_daily_orders(rate_limit_per_sec)
        
        # Save results
        self.save_daily_results(results)
        
        return results
    
    def save_daily_results(self, results: Dict[str, Any]):
        """Save daily automation results to file."""
        try:
            results_dir = "daily_results"
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"daily_automation_{timestamp}.json"
            filepath = os.path.join(results_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 Daily results saved to: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving daily results: {e}")

def main():
    """Main function to run daily delivery automation."""
    print("🤖 Daily Delivery Automation System")
    print("="*50)
    
    # Initialize automation system
    automation = DailyDeliveryAutomation(GOOGLE_SHEETS_URL, SHEET_NAME)
    
    # Run daily automation
    results = automation.run_daily_automation(rate_limit_per_sec=2.0)
    
    if "error" in results:
        print(f"❌ Automation failed: {results['error']}")
        return 1
    
    # Print final summary
    print("\n" + "="*50)
    print("🎯 AUTOMATION COMPLETED")
    print("="*50)
    print(f"📅 Day: {results.get('weekday', 'Unknown')}")
    print(f"📋 Total processed: {results.get('total_processed', 0)}")
    print(f"✅ Successful: {len(results.get('successful_orders', []))}")
    print(f"❌ Failed: {len(results.get('failed_orders', []))}")
    
    if results.get('delivery_frequency_summary'):
        summary = results['delivery_frequency_summary']
        print(f"📊 Frequency 3 orders: {summary.get('frequency_3_orders', 0)}")
        print(f"📊 Frequency 5 orders: {summary.get('frequency_5_orders', 0)}")
    
    return 0

if __name__ == "__main__":
    exit(main())
