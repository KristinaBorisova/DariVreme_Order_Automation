#!/usr/bin/env python3
"""
test_delivery_frequency.py
Test script to verify delivery frequency logic.
"""

import os
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))

try:
    from daily_delivery_automation import DailyDeliveryAutomation
    from sheet_to_json import load_workbook_to_dict
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    exit(1)

def test_delivery_frequency_logic():
    """Test the delivery frequency logic for different weekdays."""
    print("🧪 Testing Delivery Frequency Logic")
    print("="*50)
    
    # Initialize automation system
    automation = DailyDeliveryAutomation(
        "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004",
        "FINAL_ORDERS"
    )
    
    # Load data
    if not automation.load_data():
        print("❌ Failed to load data")
        return
    
    # Test different weekdays
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    print(f"📅 Current day: {weekdays[datetime.now().weekday()]}")
    print()
    
    for weekday_num in range(7):
        weekday_name = weekdays[weekday_num]
        
        print(f"📅 Testing {weekday_name} (weekday {weekday_num}):")
        
        # Test frequency 3 (Monday, Wednesday, Friday)
        should_process_3 = automation.should_process_client(3, weekday_num)
        print(f"   Frequency 3 (Mon, Wed, Fri): {'✅ YES' if should_process_3 else '❌ NO'}")
        
        # Test frequency 5 (Monday-Friday)
        should_process_5 = automation.should_process_client(5, weekday_num)
        print(f"   Frequency 5 (Mon-Fri): {'✅ YES' if should_process_5 else '❌ NO'}")
        
        print()
    
    # Test with actual data
    print("📊 Testing with actual FINAL_ORDERS data:")
    print("-" * 40)
    
    current_weekday = datetime.now().weekday()
    current_weekday_name = weekdays[current_weekday]
    
    print(f"📅 Today is {current_weekday_name}")
    
    # Filter orders for today
    today_orders = automation.filter_orders_for_today()
    
    print(f"📋 Orders scheduled for today: {len(today_orders)}")
    
    if today_orders:
        print("\n📦 Orders to be processed today:")
        for i, order in enumerate(today_orders, 1):
            client_name = order.get('client_name', 'Unknown')
            delivery_freq = order.get('deliveryFrequency', 'Unknown')
            order_desc = order.get('order_id', 'Unknown')
            print(f"   {i}. {client_name} (frequency={delivery_freq}) - {order_desc}")
    else:
        print("ℹ️  No orders scheduled for today")
    
    # Show delivery frequency summary
    freq_summary = automation.get_delivery_frequency_summary(today_orders)
    print(f"\n📊 Delivery Frequency Summary:")
    print(f"   Frequency 3 orders: {freq_summary['frequency_3_orders']}")
    print(f"   Frequency 5 orders: {freq_summary['frequency_5_orders']}")
    print(f"   Total orders: {freq_summary['total_orders']}")

def test_weekday_simulation():
    """Test what would happen on different weekdays."""
    print("\n" + "="*50)
    print("🎭 Simulating Different Weekdays")
    print("="*50)
    
    # Initialize automation system
    automation = DailyDeliveryAutomation(
        "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004",
        "FINAL_ORDERS"
    )
    
    # Load data
    if not automation.load_data():
        print("❌ Failed to load data")
        return
    
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for weekday_num in range(7):
        weekday_name = weekdays[weekday_num]
        
        print(f"\n📅 {weekday_name}:")
        
        # Simulate filtering for this weekday
        filtered_orders = []
        for order in automation.orders:
            try:
                delivery_frequency = int(order.get('deliveryFrequency', 0))
                if automation.should_process_client(delivery_frequency, weekday_num):
                    filtered_orders.append(order)
            except (ValueError, TypeError):
                continue
        
        print(f"   Orders scheduled: {len(filtered_orders)}")
        
        if filtered_orders:
            freq_3_count = sum(1 for order in filtered_orders if int(order.get('deliveryFrequency', 0)) == 3)
            freq_5_count = sum(1 for order in filtered_orders if int(order.get('deliveryFrequency', 0)) == 5)
            print(f"   Frequency 3: {freq_3_count}, Frequency 5: {freq_5_count}")
            
            # Show first few orders
            for i, order in enumerate(filtered_orders[:3], 1):
                client_name = order.get('client_name', 'Unknown')
                delivery_freq = order.get('deliveryFrequency', 'Unknown')
                print(f"     {i}. {client_name} (freq={delivery_freq})")
            
            if len(filtered_orders) > 3:
                print(f"     ... and {len(filtered_orders) - 3} more")

if __name__ == "__main__":
    test_delivery_frequency_logic()
    test_weekday_simulation()
