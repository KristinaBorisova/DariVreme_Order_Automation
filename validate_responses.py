#!/usr/bin/env python3
"""
validate_responses.py
Validation script to check API responses and data formats.
"""

import json
import os
import sys
from typing import Dict, Any, List
from datetime import datetime

def validate_quote_response(response: Dict[str, Any]) -> List[str]:
    """
    Validate a quote response from the Glovo API.
    
    Args:
        response: Quote response dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Required fields
    required_fields = ["quoteId", "quotePrice", "currencyCode", "createdAt", "expiresAt"]
    for field in required_fields:
        if field not in response:
            errors.append(f"Missing required field: {field}")
    
    # Validate quote ID format (should be UUID-like)
    if "quoteId" in response:
        quote_id = response["quoteId"]
        if not isinstance(quote_id, str) or len(quote_id) < 10:
            errors.append(f"Invalid quoteId format: {quote_id}")
    
    # Validate timestamps
    for time_field in ["createdAt", "expiresAt"]:
        if time_field in response:
            try:
                datetime.fromisoformat(response[time_field].replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"Invalid timestamp format in {time_field}: {response[time_field]}")
    
    # Validate price
    if "quotePrice" in response:
        try:
            float(response["quotePrice"])
        except (ValueError, TypeError):
            errors.append(f"Invalid quotePrice: {response['quotePrice']}")
    
    return errors

def validate_order_response(response: Dict[str, Any]) -> List[str]:
    """
    Validate an order response from the Glovo API.
    
    Args:
        response: Order response dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check for common success indicators
    if "status" in response and response["status"] not in ["SUCCESS", "CREATED", "ACCEPTED"]:
        errors.append(f"Order status indicates failure: {response['status']}")
    
    # Check for error indicators
    if "error" in response:
        errors.append(f"Order creation error: {response['error']}")
    
    return errors

def validate_test_data(data: List[Dict[str, Any]]) -> List[str]:
    """
    Validate test data structure.
    
    Args:
        data: List of test order dictionaries
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not isinstance(data, list):
        errors.append("Data should be a list of orders")
        return errors
    
    if len(data) == 0:
        errors.append("No orders found in data")
        return errors
    
    # Required fields for each order
    required_fields = ["pickup_address_id", "pickup_time_utc", "dest_raw_address", "dest_lat", "dest_lng"]
    
    for i, order in enumerate(data):
        if not isinstance(order, dict):
            errors.append(f"Order {i} is not a dictionary")
            continue
        
        # Check required fields
        for field in required_fields:
            if field not in order:
                errors.append(f"Order {i}: Missing required field '{field}'")
            elif order[field] is None or order[field] == "":
                errors.append(f"Order {i}: Empty value for field '{field}'")
        
        # Validate coordinates
        if "dest_lat" in order and "dest_lng" in order:
            try:
                lat = float(order["dest_lat"])
                lng = float(order["dest_lng"])
                if not (-90 <= lat <= 90):
                    errors.append(f"Order {i}: Invalid latitude {lat}")
                if not (-180 <= lng <= 180):
                    errors.append(f"Order {i}: Invalid longitude {lng}")
            except (ValueError, TypeError):
                errors.append(f"Order {i}: Invalid coordinate format")
        
        # Validate pickup time
        if "pickup_time_utc" in order:
            try:
                pickup_time = datetime.fromisoformat(order["pickup_time_utc"].replace("Z", "+00:00"))
                if pickup_time <= datetime.now(pickup_time.tzinfo):
                    errors.append(f"Order {i}: Pickup time is in the past: {order['pickup_time_utc']}")
            except ValueError:
                errors.append(f"Order {i}: Invalid pickup time format: {order['pickup_time_utc']}")
    
    return errors

def validate_file_structure(file_path: str) -> List[str]:
    """
    Validate the structure of a JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not os.path.exists(file_path):
        errors.append(f"File does not exist: {file_path}")
        return errors
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON format: {e}")
        return errors
    except Exception as e:
        errors.append(f"Error reading file: {e}")
        return errors
    
    # Check if it's a workbook format or simple list
    if isinstance(data, dict):
        if "successes" in data:
            # Quote results format
            if not isinstance(data["successes"], list):
                errors.append("'successes' should be a list")
            else:
                for i, success in enumerate(data["successes"]):
                    if "response" not in success:
                        errors.append(f"Success {i}: Missing 'response' field")
                    else:
                        response_errors = validate_quote_response(success["response"])
                        errors.extend([f"Success {i}: {err}" for err in response_errors])
        
        elif "successful_orders" in data:
            # Order results format
            if not isinstance(data["successful_orders"], list):
                errors.append("'successful_orders' should be a list")
            else:
                for i, order in enumerate(data["successful_orders"]):
                    if "order_response" not in order:
                        errors.append(f"Order {i}: Missing 'order_response' field")
                    else:
                        response_errors = validate_order_response(order["order_response"])
                        errors.extend([f"Order {i}: {err}" for err in response_errors])
        
        else:
            # Workbook format
            for sheet_name, sheet_data in data.items():
                if not isinstance(sheet_data, list):
                    errors.append(f"Sheet '{sheet_name}': Should be a list of orders")
                else:
                    sheet_errors = validate_test_data(sheet_data)
                    errors.extend([f"Sheet '{sheet_name}': {err}" for err in sheet_errors])
    
    elif isinstance(data, list):
        # Simple list format
        errors.extend(validate_test_data(data))
    
    else:
        errors.append("Unsupported data format")
    
    return errors

def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("Usage: python validate_responses.py <file_path> [file_path2] ...")
        print("Example: python validate_responses.py test_orders.json quote_results.json")
        sys.exit(1)
    
    all_errors = []
    
    for file_path in sys.argv[1:]:
        print(f"\n🔍 Validating: {file_path}")
        errors = validate_file_structure(file_path)
        
        if errors:
            print(f"❌ Found {len(errors)} validation errors:")
            for error in errors:
                print(f"   - {error}")
            all_errors.extend(errors)
        else:
            print("✅ File is valid")
    
    print(f"\n📊 Summary:")
    print(f"   Files checked: {len(sys.argv) - 1}")
    print(f"   Total errors: {len(all_errors)}")
    
    if all_errors:
        print("\n💡 Common fixes:")
        print("   - Ensure all required fields are present")
        print("   - Check coordinate formats (should be numeric)")
        print("   - Verify timestamp formats (ISO8601 with Z)")
        print("   - Make sure pickup times are in the future")
        sys.exit(1)
    else:
        print("🎉 All files are valid!")

if __name__ == "__main__":
    main()
