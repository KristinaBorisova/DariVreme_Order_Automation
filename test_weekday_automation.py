#!/usr/bin/env python3
"""
test_weekday_automation.py
Test the automation for different weekdays.
"""

import os
import sys
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from daily_delivery_automation import DailyDeliveryAutomation

def test_weekday(weekday_name, weekday_num):
    """Test automation for a specific weekday."""
    print(f"🧪 Testing {weekday_name} (weekday {weekday_num})")
    print("-" * 40)
    
    # Initialize automation
    automation = DailyDeliveryAutomation(
        "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004",
        "FINAL_ORDERS"
    )
    
    # Load data
    if not automation.load_data():
        print("❌ Failed to load data")
        return
    
    # Filter orders for this weekday
    filtered_orders = []
    for order in automation.orders:
        try:
            delivery_frequency = int(order.get('deliveryFrequency', 0))
            if automation.should_process_client(delivery_frequency, weekday_num):
                filtered_orders.append(order)
        except (ValueError, TypeError):
            continue
    
    print(f"📋 Orders scheduled for {weekday_name}: {len(filtered_orders)}")
    
    if filtered_orders:
        freq_3_count = sum(1 for order in filtered_orders if int(order.get('deliveryFrequency', 0)) == 3)
        freq_5_count = sum(1 for order in filtered_orders if int(order.get('deliveryFrequency', 0)) == 5)
        print(f"   Frequency 3: {freq_3_count}, Frequency 5: {freq_5_count}")
        
        for i, order in enumerate(filtered_orders[:5], 1):
            client_name = order.get('client_name', 'Unknown')
            delivery_freq = order.get('deliveryFrequency', 'Unknown')
            print(f"   {i}. {client_name} (freq={delivery_freq})")
        
        if len(filtered_orders) > 5:
            print(f"   ... and {len(filtered_orders) - 5} more")
    else:
        print("   No orders scheduled for this day")
    
    print()

def main():
    """Test all weekdays."""
    print("🧪 Testing Daily Automation for All Weekdays")
    print("="*60)
    
    weekdays = [
        ('Monday', 0),
        ('Tuesday', 1),
        ('Wednesday', 2),
        ('Thursday', 3),
        ('Friday', 4),
        ('Saturday', 5),
        ('Sunday', 6)
    ]
    
    for weekday_name, weekday_num in weekdays:
        test_weekday(weekday_name, weekday_num)
    
    print("✅ Weekday testing completed")

if __name__ == "__main__":
    main()
