# 🚀 Glovo Order Automation System

## 📋 Overview
Automated food delivery order processing system that integrates with Glovo's API and Google Sheets to manage client orders based on delivery frequencies.

**Key Features:**
- ✅ Automated daily processing (Monday-Friday, 9:00 AM UTC)
- ✅ Smart delivery frequency logic (3x/week or 5x/week)
- ✅ Google Sheets integration for data management
- ✅ GitHub Actions cloud deployment
- ✅ Comprehensive logging and monitoring

---

## 🌐 Access & Deployment

### GitHub Repository
**URL:** `https://github.com/KristinaBorisova/Glovo_DariVreme_Order_Automation`

### Google Sheets
**URL:** `https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"Daily Delivery Automation"**
3. Click **"Run workflow"**
4. Select **"Run in test mode"** (optional)
5. Click **"Run workflow"**

### Local Testing
```bash
# Test complete automation
python daily_delivery_automation.py

# Test quote creation only
python step_2_quota_Config/POST_create_quote_id_final.py

# Test order creation only
python test_order_creation.py
```

---

## 🔄 Main Steps & Logic

### Step 1: Authentication
- **File:** `step_1_authentication/token_service.py`
- **Purpose:** Get valid bearer token from Glovo API
- **Logic:** OAuth 2.0 Client Credentials flow with token caching

### Step 2: Data Loading
- **File:** `daily_delivery_automation.py`
- **Purpose:** Load orders from Google Sheets
- **Logic:** Connect to FINAL_ORDERS sheet and validate data

### Step 3: Delivery Frequency Filtering
- **File:** `daily_delivery_automation.py`
- **Purpose:** Determine which clients to process today
- **Logic:**
  - **Frequency 3:** Monday, Wednesday, Friday
  - **Frequency 5:** Monday-Friday
  - **Weekends:** No processing

### Step 4: Quote Creation
- **File:** `step_2_quota_Config/POST_create_quote_id_final.py`
- **Purpose:** Create quotes for valid orders
- **Logic:**
  1. Validate order data
  2. Create Glovo API payload
  3. Send quote request
  4. Extract client details

### Step 5: Order Creation
- **File:** `step_3_send_order_with_quotaID/send_order_with_quote_id_final.py`
- **Purpose:** Create actual orders from quotes
- **Logic:**
  1. Extract quote IDs
  2. Create order payload with client info
  3. Send order request
  4. Log results

### Step 6: Logging & Results
- **Files:** `google_sheets_logger.py`, `order_logger.py`
- **Purpose:** Track all activities and results
- **Logic:** Save to Google Sheets and Excel files

---

## ⚙️ Configuration

### GitHub Secrets Required
| Secret Name | Value | Description |
|-------------|-------|-------------|
| `API_KEY` | `175482686405285` | Glovo API client ID |
| `API_SECRET` | `dc190e6d0e4f4fc79e4021e4b981e596` | Glovo API client secret |
| `GOOGLE_SHEETS_URL` | `https://docs.google.com/spreadsheets/d/...` | FINAL_ORDERS sheet URL |

### Google Sheets Structure
**Required Columns in FINAL_ORDERS sheet:**
- `client_id` - Unique client identifier
- `client_name` - Client full name
- `client_phone` - Client phone number
- `client_email` - Client email address
- `deliveryFrequency` - 3 or 5 (deliveries per week)
- `pickup_time_utc` - ISO8601 UTC timestamp (future date)
- `pickupAddressBookId` - Restaurant pickup location ID
- `deliveryRawAddress` - Delivery address
- `deliveryLattitude` - Delivery latitude
- `deliveryLongitude` - Delivery longitude
- `restaurant_name` - Restaurant name
- `order_id` - Order description

---

## 📊 Monitoring

### GitHub Actions
- **Location:** Repository → Actions → "Daily Delivery Automation"
- **Status:** Green = success, Red = failure, Yellow = running
- **Logs:** Click any run to see detailed logs

### Log Files
- **Google Sheets:** `Glovo-Orders-Summary` sheet
- **Excel Files:** `order_results_YYYYMMDD_HHMMSS.xlsx`
- **Daily Logs:** `logs/daily_delivery_YYYYMMDD.log`

### Common Issues & Solutions

#### "Secret not set" errors
**Solution:** Verify GitHub Secrets are configured correctly

#### "PICKUP_TIME_MUST_BE_GREATER_THAN_CURRENT_TIME"
**Solution:** Update pickup times to future dates
```bash
python "Test Scripts/fix_pickup_times.py"
```

#### "Default Client" in orders
**Solution:** Fixed in latest version - client details now properly extracted

---

## 🔌 API Integration

### Glovo API Endpoints
1. **Authentication:** `POST /oauth/token`
2. **Quote Creation:** `POST /v2/laas/quotes`
3. **Order Creation:** `POST /v2/laas/quotes/{quoteId}/parcels`

### Rate Limiting
- **Quote Creation:** 2 requests/second
- **Order Creation:** 2 requests/second
- **Delay Between Requests:** 0.5 seconds

---

## 🔧 Maintenance

### Regular Tasks
1. **Monitor pickup times** - Ensure they're in the future
2. **Check API credentials** - Verify monthly
3. **Review logs** - Check daily for errors
4. **Update client data** - Add/update clients in sheet

### Adding New Clients
1. Open FINAL_ORDERS Google Sheet
2. Add new row with required columns
3. Set delivery frequency (3 or 5)
4. Set future pickup time
5. Save sheet - automation picks up automatically

### Debug Commands
```bash
# Test environment variables
python "Test Scripts/test_env_vars.py"

# Test all components
python "Test Scripts/test_automation.py"

# Test weekday logic (now included in test_automation.py)
python "Test Scripts/test_automation.py"
```

---

## 📈 Success Metrics

### Key Performance Indicators
- **Automation Success Rate:** Target 95%+
- **Order Creation Success:** Target 90%+
- **Data Accuracy:** 100% (no "Default Client" issues)
- **Uptime:** 99%+ (GitHub Actions reliability)

### Current Status
- ✅ **Authentication:** Working
- ✅ **Quote Creation:** Working
- ✅ **Order Creation:** Working
- ✅ **Client Details:** Fixed
- ✅ **GitHub Actions:** Deployed
- ✅ **Logging:** Comprehensive

---

## 📞 Support

### Key Files
- **Main Automation:** `daily_delivery_automation.py`
- **GitHub Workflow:** `.github/workflows/daily-delivery-automation.yml`
- **Configuration:** `requirements.txt`

### Documentation
- **Setup Guide:** `GITHUB_ACTIONS_SETUP.md`
- **Troubleshooting:** `GITHUB_ACTIONS_TROUBLESHOOTING.md`
- **Client Details Fix:** `CLIENT_DETAILS_FIX.md`

---

**🎉 The Glovo Order Automation System is production-ready and fully automated for daily order processing based on client delivery frequencies.**

