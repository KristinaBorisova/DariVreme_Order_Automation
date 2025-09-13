#!/usr/bin/env python3
"""
manual_scheduler.py
Manual scheduler for testing daily delivery automation.
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from daily_delivery_automation import DailyDeliveryAutomation

def run_automation():
    """Run the daily automation."""
    print(f"🤖 Manual Scheduler - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Initialize automation
    automation = DailyDeliveryAutomation(
        "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004",
        "FINAL_ORDERS"
    )
    
    # Run automation
    results = automation.run_daily_automation()
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return False
    
    print("✅ Automation completed successfully")
    return True

if __name__ == "__main__":
    run_automation()
