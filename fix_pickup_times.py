#!/usr/bin/env python3
"""
fix_pickup_times.py
Fix pickup times in FINAL_ORDERS sheet to be in the future.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))

try:
    from sheet_to_json import load_workbook_to_dict
except ImportError as e:
    print(f"❌ Error importing sheet_to_json: {e}")
    exit(1)

def get_future_pickup_times(days_ahead: int = 1, hour: int = 16) -> List[str]:
    """
    Generate future pickup times for the next few days.
    
    Args:
        days_ahead: Number of days ahead to generate times for
        hour: Hour of day (24-hour format)
        
    Returns:
        List of ISO8601 UTC timestamps
    """
    now = datetime.utcnow()
    pickup_times = []
    
    for i in range(days_ahead):
        future_date = now + timedelta(days=i+1)
        future_date = future_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        pickup_times.append(future_date.isoformat() + 'Z')
    
    return pickup_times

def update_pickup_times_in_sheet(google_sheets_url: str, sheet_name: str = "FINAL_ORDERS"):
    """
    Update pickup times in the FINAL_ORDERS sheet.
    Note: This is a read-only operation - you'll need to manually update the sheet.
    """
    print("🔧 Fixing Pickup Times in FINAL_ORDERS Sheet")
    print("="*60)
    
    # Load data from Google Sheets
    print(f"📊 Loading data from Google Sheets...")
    workbook = load_workbook_to_dict(google_sheets_url)
    
    if sheet_name not in workbook:
        print(f"❌ Sheet '{sheet_name}' not found in workbook")
        return
    
    orders = workbook[sheet_name]
    print(f"✅ Loaded {len(orders)} orders from '{sheet_name}' sheet")
    
    # Generate future pickup times
    future_times = get_future_pickup_times(days_ahead=len(orders), hour=16)
    
    print(f"\n📅 Current time: {datetime.utcnow().isoformat()}Z")
    print(f"📅 Generated future pickup times:")
    for i, time in enumerate(future_times, 1):
        print(f"   {i}. {time}")
    
    print(f"\n🔍 Current pickup times in sheet:")
    for i, order in enumerate(orders, 1):
        current_time = order.get('pickup_time_utc', 'Not set')
        print(f"   {i}. {order.get('client_name', 'Unknown')}: {current_time}")
    
    print(f"\n📝 RECOMMENDED UPDATES:")
    print(f"Please update your FINAL_ORDERS sheet with these pickup times:")
    print(f"="*60)
    
    for i, order in enumerate(orders, 1):
        client_name = order.get('client_name', 'Unknown')
        new_time = future_times[i-1] if i <= len(future_times) else future_times[-1]
        print(f"Row {i+1}: {client_name}")
        print(f"  Current: {order.get('pickup_time_utc', 'Not set')}")
        print(f"  Update to: {new_time}")
        print()
    
    print(f"📋 INSTRUCTIONS:")
    print(f"1. Open your FINAL_ORDERS Google Sheet")
    print(f"2. Update the 'pickup_time_utc' column with the times above")
    print(f"3. Save the sheet")
    print(f"4. Run the automation again")
    
    return future_times

def create_test_data_with_future_times():
    """Create test data with future pickup times for testing."""
    print(f"\n🧪 Creating test data with future pickup times...")
    
    future_times = get_future_pickup_times(days_ahead=4, hour=16)
    
    test_orders = [
        {
            "client_id": "CLIENT_001",
            "client_name": "Яна Димитрова",
            "client_phone": "886612261",
            "client_email": "yana@gmail.com",
            "deliveryRawAddress": "g.k. Strelbishte, Nishava St 1р 1408, Bulgaria",
            "deliveryLattitude": 42.673758,
            "deliveryLongitude": 23.298064,
            "ADDRESS_CITY_NAME": "София",
            "ADDRESS_COUNTRY": "България",
            "Address_postal_code": 1000,
            "deliveryDetails": "Етаж 1 ап. 1",
            "deliveryFrequency": 3,
            "order_id": "1 супа и 1 основно",
            "restaurant_name": "Тест-Ресторант-2",
            "pickupAddressBookId": "cc97d6fb-bbf3-45b1-af21-29dfd29b68fc",
            "pickup_time_utc": future_times[0],
            "pickup_code": 1,
            "created_at": datetime.utcnow().isoformat() + 'Z'
        },
        {
            "client_id": "CLIENT_002",
            "client_name": "Панчо",
            "client_phone": "886612262",
            "client_email": "pancho@gmail.com",
            "deliveryRawAddress": "g.k. Strelbishte, Nishava St 2р 1409, Bulgaria",
            "deliveryLattitude": 42.673758,
            "deliveryLongitude": 23.298064,
            "ADDRESS_CITY_NAME": "София",
            "ADDRESS_COUNTRY": "България",
            "Address_postal_code": 1000,
            "deliveryDetails": "Етаж 2 ап. 2",
            "deliveryFrequency": 5,
            "order_id": "2 супи и 2 основни",
            "restaurant_name": "Тест-Ресторант-2",
            "pickupAddressBookId": "cc97d6fb-bbf3-45b1-af21-29dfd29b68fc",
            "pickup_time_utc": future_times[1],
            "pickup_code": 2,
            "created_at": datetime.utcnow().isoformat() + 'Z'
        },
        {
            "client_id": "CLIENT_003",
            "client_name": "Криси",
            "client_phone": "886612263",
            "client_email": "krisi@gmail.com",
            "deliveryRawAddress": "g.k. Strelbishte, Nishava St 3р 1410, Bulgaria",
            "deliveryLattitude": 42.673758,
            "deliveryLongitude": 23.298064,
            "ADDRESS_CITY_NAME": "София",
            "ADDRESS_COUNTRY": "България",
            "Address_postal_code": 1000,
            "deliveryDetails": "Етаж 3 ап. 3",
            "deliveryFrequency": 3,
            "order_id": "3 супи и 3 основни",
            "restaurant_name": "Тест-Ресторант-2",
            "pickupAddressBookId": "cc97d6fb-bbf3-45b1-af21-29dfd29b68fc",
            "pickup_time_utc": future_times[2],
            "pickup_code": 3,
            "created_at": datetime.utcnow().isoformat() + 'Z'
        },
        {
            "client_id": "CLIENT_004",
            "client_name": "Робърт",
            "client_phone": "886612264",
            "client_email": "robert@gmail.com",
            "deliveryRawAddress": "g.k. Strelbishte, Nishava St 4р 1411, Bulgaria",
            "deliveryLattitude": 42.673758,
            "deliveryLongitude": 23.298064,
            "ADDRESS_CITY_NAME": "София",
            "ADDRESS_COUNTRY": "България",
            "Address_postal_code": 1000,
            "deliveryDetails": "Етаж 4 ап. 4",
            "deliveryFrequency": 3,
            "order_id": "4 супи и 4 основни",
            "restaurant_name": "Тест-Ресторант-2",
            "pickupAddressBookId": "cc97d6fb-bbf3-45b1-af21-29dfd29b68fc",
            "pickup_time_utc": future_times[3],
            "pickup_code": 4,
            "created_at": datetime.utcnow().isoformat() + 'Z'
        }
    ]
    
    # Save test data
    import json
    with open("test_orders_future_times.json", "w", encoding="utf-8") as f:
        json.dump(test_orders, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Test data saved to: test_orders_future_times.json")
    print(f"📋 Test orders with future pickup times:")
    for i, order in enumerate(test_orders, 1):
        print(f"   {i}. {order['client_name']}: {order['pickup_time_utc']}")
    
    return test_orders

def main():
    """Main function to fix pickup times."""
    print("🔧 Pickup Time Fixer")
    print("="*50)
    
    google_sheets_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004"
    
    # Update pickup times in sheet
    future_times = update_pickup_times_in_sheet(google_sheets_url)
    
    # Create test data
    test_orders = create_test_data_with_future_times()
    
    print(f"\n🎯 SUMMARY:")
    print(f"1. Update your FINAL_ORDERS sheet with the recommended pickup times above")
    print(f"2. Or use the test data in 'test_orders_future_times.json' for testing")
    print(f"3. Run the automation again after updating pickup times")
    
    return 0

if __name__ == "__main__":
    exit(main())
