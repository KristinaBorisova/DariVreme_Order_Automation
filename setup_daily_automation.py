#!/usr/bin/env python3
"""
setup_daily_automation.py
Setup script for daily delivery automation.
Creates cron job and provides scheduling options.
"""

import os
import sys
import subprocess
from pathlib import Path

def get_script_path():
    """Get the absolute path to the daily automation script."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'daily_delivery_automation.py'))

def get_python_path():
    """Get the Python executable path."""
    return sys.executable

def create_cron_job():
    """Create a cron job for daily automation."""
    script_path = get_script_path()
    python_path = get_python_path()
    
    # Cron job runs every weekday at 9:00 AM
    cron_entry = f"0 9 * * 1-5 {python_path} {script_path} >> /tmp/daily_delivery_automation.log 2>&1"
    
    print("🤖 Daily Delivery Automation Setup")
    print("="*50)
    print(f"📁 Script path: {script_path}")
    print(f"🐍 Python path: {python_path}")
    print()
    print("📅 Cron job entry (runs Monday-Friday at 9:00 AM):")
    print(f"   {cron_entry}")
    print()
    
    # Instructions for manual setup
    print("📋 Manual Setup Instructions:")
    print("1. Open your crontab:")
    print("   crontab -e")
    print()
    print("2. Add this line to run every weekday at 9:00 AM:")
    print(f"   {cron_entry}")
    print()
    print("3. Save and exit the editor")
    print()
    print("4. Verify the cron job was added:")
    print("   crontab -l")
    print()
    
    # Alternative: Create a cron file
    cron_file = "daily_delivery_automation.cron"
    with open(cron_file, 'w') as f:
        f.write(f"# Daily Delivery Automation - Runs Monday-Friday at 9:00 AM\n")
        f.write(f"{cron_entry}\n")
    
    print(f"💾 Cron file created: {cron_file}")
    print(f"   To install: crontab {cron_file}")
    print()
    
    return cron_entry

def create_systemd_service():
    """Create a systemd service for the automation."""
    script_path = get_script_path()
    python_path = get_python_path()
    user = os.getenv('USER', 'root')
    
    service_content = f"""[Unit]
Description=Daily Delivery Automation
After=network.target

[Service]
Type=oneshot
User={user}
WorkingDirectory={os.path.dirname(script_path)}
ExecStart={python_path} {script_path}
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "daily-delivery-automation.service"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print("🔧 Systemd Service Setup:")
    print(f"📁 Service file created: {service_file}")
    print()
    print("📋 Installation instructions:")
    print(f"1. Copy service file: sudo cp {service_file} /etc/systemd/system/")
    print("2. Reload systemd: sudo systemctl daemon-reload")
    print("3. Enable service: sudo systemctl enable daily-delivery-automation.service")
    print("4. Start service: sudo systemctl start daily-delivery-automation.service")
    print()
    print("📅 To run daily at 9:00 AM, create a timer:")
    print("   sudo systemctl edit daily-delivery-automation.timer")
    print()
    
    return service_file

def create_manual_scheduler():
    """Create a manual scheduler script."""
    scheduler_content = '''#!/usr/bin/env python3
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
        "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit",
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
'''
    
    scheduler_file = "manual_scheduler.py"
    with open(scheduler_file, 'w') as f:
        f.write(scheduler_content)
    
    # Make it executable
    os.chmod(scheduler_file, 0o755)
    
    print("📝 Manual Scheduler:")
    print(f"📁 Created: {scheduler_file}")
    print(f"🚀 Run with: python {scheduler_file}")
    print()
    
    return scheduler_file

def create_test_script():
    """Create a test script for different weekdays."""
    test_content = '''#!/usr/bin/env python3
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
        "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit",
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
'''
    
    test_file = "test_weekday_automation.py"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Make it executable
    os.chmod(test_file, 0o755)
    
    print("🧪 Test Script:")
    print(f"📁 Created: {test_file}")
    print(f"🚀 Run with: python {test_file}")
    print()
    
    return test_file

def main():
    """Main setup function."""
    print("🚀 Daily Delivery Automation Setup")
    print("="*50)
    print()
    
    # Create cron job
    cron_entry = create_cron_job()
    
    # Create systemd service
    service_file = create_systemd_service()
    
    # Create manual scheduler
    scheduler_file = create_manual_scheduler()
    
    # Create test script
    test_file = create_test_script()
    
    print("📋 Summary of created files:")
    print(f"   • daily_delivery_automation.cron - Cron job configuration")
    print(f"   • {service_file} - Systemd service file")
    print(f"   • {scheduler_file} - Manual scheduler")
    print(f"   • {test_file} - Weekday testing script")
    print()
    
    print("🎯 Next Steps:")
    print("1. Test the automation: python manual_scheduler.py")
    print("2. Test different weekdays: python test_weekday_automation.py")
    print("3. Set up cron job: crontab daily_delivery_automation.cron")
    print("4. Monitor logs: tail -f /tmp/daily_delivery_automation.log")
    print()
    
    print("✅ Setup completed!")

if __name__ == "__main__":
    main()
