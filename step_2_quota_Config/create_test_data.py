#!/usr/bin/env python3
"""
create_test_data.py
Create sample test data for testing the Glovo automation workflow.
"""

import json
import argparse
from datetime import datetime, timedelta
import uuid

def create_test_orders(count: int = 2) -> list:
    """
    Create sample test orders with valid data structure.
    
    Args:
        count: Number of test orders to create
        
    Returns:
        List of test order dictionaries
    """
    test_orders = []
    
    # Sample addresses in Barcelona
    addresses = [
        {
            "dest_raw_address": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
            "dest_lat": 41.39637,
            "dest_lng": 2.17939,
            "dest_details": "Floor 6 Door 3"
        },
        {
            "dest_raw_address": "Passeig de Gràcia, 1, L'Eixample, 08008 Barcelona",
            "dest_lat": 41.3851,
            "dest_lng": 2.1734,
            "dest_details": "Main entrance"
        },
        {
            "dest_raw_address": "Carrer de Mallorca, 401, L'Eixample, 08013 Barcelona",
            "dest_lat": 41.4036,
            "dest_lng": 2.1744,
            "dest_details": "Building A"
        },
        {
            "dest_raw_address": "Rambla de Catalunya, 1, L'Eixample, 08007 Barcelona",
            "dest_lat": 41.3879,
            "dest_lng": 2.1699,
            "dest_details": "Ground floor"
        },
        {
            "dest_raw_address": "Carrer de València, 200, L'Eixample, 08011 Barcelona",
            "dest_lat": 41.3888,
            "dest_lng": 2.1599,
            "dest_details": "Office building"
        }
    ]
    
    # Sample pickup address ID (you should replace this with a real one from your Glovo account)
    pickup_address_id = "497f6eca-6276-4993-bfeb-53cbbbba6f08"
    
    # Generate test orders
    for i in range(count):
        # Use different addresses cyclically
        address = addresses[i % len(addresses)]
        
        # Generate pickup time (current time + 30 minutes to 2 hours)
        pickup_time = datetime.utcnow() + timedelta(minutes=30 + (i * 30))
        pickup_time_utc = pickup_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        order = {
            "pickup_address_id": pickup_address_id,
            "pickup_time_utc": pickup_time_utc,
            "dest_raw_address": address["dest_raw_address"],
            "dest_lat": address["dest_lat"],
            "dest_lng": address["dest_lng"],
            "dest_details": address["dest_details"]
        }
        
        test_orders.append(order)
    
    return test_orders

def create_test_workbook(orders: list) -> dict:
    """
    Create a workbook structure with test orders.
    
    Args:
        orders: List of test orders
        
    Returns:
        Workbook dictionary structure
    """
    return {
        "Orders": orders,
        "TestSheet": orders[:1]  # Include a smaller test sheet
    }

def main():
    parser = argparse.ArgumentParser(description="Create test data for Glovo automation")
    parser.add_argument("--count", type=int, default=2, help="Number of test orders to create")
    parser.add_argument("--output", default="test_orders.json", help="Output file name")
    parser.add_argument("--workbook", action="store_true", help="Create workbook format instead of simple list")
    
    args = parser.parse_args()
    
    print(f"Creating {args.count} test orders...")
    
    # Create test orders
    orders = create_test_orders(args.count)
    
    # Choose output format
    if args.workbook:
        data = create_test_workbook(orders)
        print(f"Created workbook with {len(orders)} orders in 'Orders' sheet")
    else:
        data = orders
        print(f"Created {len(orders)} test orders")
    
    # Save to file
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Test data saved to: {args.output}")
    
    # Display sample order
    print("\nSample order structure:")
    print(json.dumps(orders[0], indent=2))
    
    # Validation
    print("\nValidation:")
    required_fields = ["pickup_address_id", "pickup_time_utc", "dest_raw_address", "dest_lat", "dest_lng"]
    for field in required_fields:
        if field in orders[0]:
            print(f"✅ {field}: {orders[0][field]}")
        else:
            print(f"❌ Missing field: {field}")
    
    print(f"\n📝 Note: Replace 'pickup_address_id' with a real address ID from your Glovo account")
    print(f"📝 Note: Adjust pickup times to be in the future (currently set to {orders[0]['pickup_time_utc']})")

if __name__ == "__main__":
    main()
