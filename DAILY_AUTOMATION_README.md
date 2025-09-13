# 🤖 Daily Delivery Automation System

## Overview

This system automatically processes orders from your FINAL_ORDERS Google Sheet based on delivery frequency and current weekday. It runs every weekday (Monday-Friday) and creates orders only for clients whose delivery frequency matches the current day.

## 🎯 How It Works

### Delivery Frequency Logic

- **Frequency 3**: Orders are created on **Monday, Wednesday, Friday**
- **Frequency 5**: Orders are created **every weekday** (Monday-Friday)
- **Weekends**: No orders are processed on Saturday or Sunday

### Your Current Data

Based on your FINAL_ORDERS sheet:
- **Яна Димитрова** (frequency=3) → Monday, Wednesday, Friday
- **Панчо** (frequency=5) → Monday, Tuesday, Wednesday, Thursday, Friday  
- **Криси** (frequency=3) → Monday, Wednesday, Friday
- **Робърт** (frequency=3) → Monday, Wednesday, Friday

## 📁 Files Created

### Core Automation
- `daily_delivery_automation.py` - Main automation script
- `manual_scheduler.py` - Manual testing script
- `test_weekday_automation.py` - Test all weekdays

### Setup Files
- `daily_delivery_automation.cron` - Cron job configuration
- `daily-delivery-automation.service` - Systemd service file
- `setup_daily_automation.py` - Setup script

### Logs
- `logs/daily_delivery_YYYYMMDD.log` - Daily automation logs
- `daily_results/daily_automation_YYYYMMDD_HHMMSS.json` - Daily results

## 🚀 Quick Start

### 1. Test the System
```bash
# Test manual execution
python manual_scheduler.py

# Test all weekdays
python test_weekday_automation.py
```

### 2. Set Up Daily Automation

#### Option A: Cron Job (Recommended)
```bash
# Install the cron job
crontab daily_delivery_automation.cron

# Verify it was added
crontab -l

# Monitor logs
tail -f /tmp/daily_delivery_automation.log
```

#### Option B: Systemd Service
```bash
# Copy service file
sudo cp daily-delivery-automation.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable daily-delivery-automation.service

# Start service
sudo systemctl start daily-delivery-automation.service
```

## 📅 Daily Schedule

| Day | Frequency 3 Clients | Frequency 5 Clients | Total Orders |
|-----|---------------------|---------------------|--------------|
| Monday | Яна, Криси, Робърт | Панчо | 4 |
| Tuesday | - | Панчо | 1 |
| Wednesday | Яна, Криси, Робърт | Панчо | 4 |
| Thursday | - | Панчо | 1 |
| Friday | Яна, Криси, Робърт | Панчо | 4 |
| Saturday | - | - | 0 |
| Sunday | - | - | 0 |

## 🔧 Configuration

### Google Sheets URL
The system uses your FINAL_ORDERS sheet:
```
https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004
```

### Cron Schedule
- **Time**: 9:00 AM every weekday
- **Days**: Monday-Friday (1-5)
- **Command**: `0 9 * * 1-5`

### Rate Limiting
- **Quote Creation**: 2 requests/second
- **Order Creation**: 2 requests/second
- **Delay Between Orders**: 0.5 seconds

## 📊 Monitoring

### Log Files
- **Main Log**: `/tmp/daily_delivery_automation.log`
- **Detailed Logs**: `logs/daily_delivery_YYYYMMDD.log`
- **Results**: `daily_results/daily_automation_YYYYMMDD_HHMMSS.json`

### Log Levels
- **INFO**: Normal operations, successful orders
- **WARNING**: Non-critical issues, skipped clients
- **ERROR**: Critical failures, API errors

### Sample Log Output
```
2025-09-13 09:00:01 - INFO - 🤖 Starting Daily Delivery Automation
2025-09-13 09:00:01 - INFO - 📅 Today is Monday (weekday 0)
2025-09-13 09:00:01 - INFO - 📋 Filtered 4 orders for Monday
2025-09-13 09:00:01 - INFO - ✅ Client Яна Димитрова (frequency=3) scheduled for Monday
2025-09-13 09:00:01 - INFO - ✅ Client Панчо (frequency=5) scheduled for Monday
2025-09-13 09:00:01 - INFO - ✅ Client Криси (frequency=3) scheduled for Monday
2025-09-13 09:00:01 - INFO - ✅ Client Робърт (frequency=3) scheduled for Monday
2025-09-13 09:00:02 - INFO - 💰 Step 1: Creating quotes...
2025-09-13 09:00:05 - INFO - ✅ Created 4 successful quotes
2025-09-13 09:00:05 - INFO - 📦 Step 2: Creating orders...
2025-09-13 09:00:10 - INFO - ✅ Order created successfully!
2025-09-13 09:00:10 - INFO - 📋 Glovo Order ID: 100010173030
2025-09-13 09:00:10 - INFO - 🏷️ Pickup Code: ORD17577797161
```

## 🛠️ Troubleshooting

### Common Issues

1. **No orders scheduled for today**
   - Check if today is a weekend (Saturday/Sunday)
   - Verify client delivery frequencies in FINAL_ORDERS sheet

2. **Authentication errors**
   - Run `cd step_1_authentication && python token_service.py`
   - Check if credentials are valid

3. **Google Sheets access issues**
   - Verify the sheet URL is correct
   - Check if the sheet is publicly accessible
   - Ensure the sheet name is "FINAL_ORDERS"

4. **Cron job not running**
   - Check cron service: `sudo systemctl status cron`
   - Verify cron job: `crontab -l`
   - Check logs: `tail -f /tmp/daily_delivery_automation.log`

### Manual Testing

```bash
# Test current day
python manual_scheduler.py

# Test specific weekday (modify the script)
python test_weekday_automation.py

# Check quote creation only
python step_2_quota_Config/POST_create_quote_id_final.py

# Check order creation only
python test_order_creation.py
```

## 📈 Adding New Clients

To add new clients to the automation:

1. **Add to FINAL_ORDERS sheet** with these columns:
   - `client_id`: Unique identifier
   - `client_name`: Client name
   - `client_phone`: Phone number
   - `client_email`: Email address
   - `deliveryFrequency`: 3 or 5
   - `deliveryRawAddress`: Delivery address
   - `deliveryLattitude`: Latitude
   - `deliveryLongitude`: Longitude
   - `pickupAddressBookId`: Restaurant pickup ID
   - `pickup_time_utc`: Pickup time (ISO8601 UTC)
   - `restaurant_name`: Restaurant name
   - `order_id`: Order description

2. **Test the new client**:
   ```bash
   python test_weekday_automation.py
   ```

3. **The automation will automatically pick up new clients** on the next run

## 🔒 Security Notes

- **Credentials**: Store API credentials securely
- **Logs**: Logs may contain sensitive information
- **Access**: Ensure only authorized users can access the system
- **Monitoring**: Regularly check logs for errors

## 📞 Support

If you encounter issues:

1. Check the logs first
2. Test with manual scheduler
3. Verify your FINAL_ORDERS sheet data
4. Check authentication status

## 🎉 Success!

Your daily delivery automation system is now ready! The system will:

- ✅ Run automatically every weekday at 9:00 AM
- ✅ Process orders based on delivery frequency
- ✅ Create quotes and orders via Glovo API
- ✅ Log all activities and results
- ✅ Handle errors gracefully
- ✅ Scale with new clients

The automation is fully integrated with your FINAL_ORDERS sheet and will process orders according to each client's delivery frequency schedule.
