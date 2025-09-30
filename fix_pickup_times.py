#!/usr/bin/env python3
"""
fix_pickup_times.py
Utility to fix pickup times in the Google Sheets to ensure they're in the future.
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))

def get_future_pickup_time(hours_ahead: int = 2) -> str:
    """
    Generate a pickup time that's in the future.
    
    Args:
        hours_ahead: Number of hours ahead of current time (default: 2)
        
    Returns:
        ISO8601 UTC string for pickup time
    """
    # Get current time in UTC
    now_utc = datetime.now(pytz.UTC)
    
    # Add the specified hours
    future_time = now_utc + timedelta(hours=hours_ahead)
    
    # Format as ISO8601 UTC string
    return future_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def get_tomorrow_pickup_time(hour: int = 9) -> str:
    """
    Generate a pickup time for tomorrow at a specific hour.
    
    Args:
        hour: Hour of the day (0-23, default: 9 for 9 AM)
        
    Returns:
        ISO8601 UTC string for pickup time
    """
    # Get current time in UTC
    now_utc = datetime.now(pytz.UTC)
    
    # Get tomorrow at the specified hour
    tomorrow = now_utc + timedelta(days=1)
    tomorrow_pickup = tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)
    
    # Format as ISO8601 UTC string
    return tomorrow_pickup.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def validate_pickup_time(pickup_time_str: str) -> bool:
    """
    Validate if a pickup time is in the future.
    
    Args:
        pickup_time_str: ISO8601 UTC string
        
    Returns:
        True if pickup time is in the future, False otherwise
    """
    try:
        # Parse the pickup time
        pickup_time = datetime.fromisoformat(pickup_time_str.replace('Z', '+00:00'))
        
        # Get current time in UTC
        now_utc = datetime.now(pytz.UTC)
        
        # Check if pickup time is at least 1 hour in the future
        return pickup_time > (now_utc + timedelta(hours=1))
        
    except Exception as e:
        print(f"❌ Error validating pickup time '{pickup_time_str}': {e}")
        return False

def main():
    """Main function to demonstrate pickup time utilities."""
    print("🕐 Pickup Time Utilities")
    print("="*50)
    
    # Show current time
    now_utc = datetime.now(pytz.UTC)
    print(f"🕐 Current UTC time: {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Generate future pickup times
    print(f"\n⏰ Future pickup times:")
    print(f"   • 2 hours ahead: {get_future_pickup_time(2)}")
    print(f"   • 4 hours ahead: {get_future_pickup_time(4)}")
    print(f"   • Tomorrow 9 AM: {get_tomorrow_pickup_time(9)}")
    print(f"   • Tomorrow 2 PM: {get_tomorrow_pickup_time(14)}")
    
    # Test validation
    print(f"\n✅ Validation tests:")
    test_times = [
        get_future_pickup_time(2),
        get_tomorrow_pickup_time(9),
        "2023-01-01T10:00:00.000Z",  # Past time
        "2024-01-01T10:00:00.000Z"   # Future time
    ]
    
    for time_str in test_times:
        is_valid = validate_pickup_time(time_str)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"   • {time_str}: {status}")

if __name__ == "__main__":
    main()