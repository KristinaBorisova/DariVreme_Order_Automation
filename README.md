# Glovo DariVreme Order Automation

A Python-based automation system for processing food delivery orders through the Glovo API. This system automates the complete workflow from authentication to order processing using Google Sheets data, with intelligent daily scheduling based on delivery frequencies.

## 🎯 Project Overview

This automation system processes orders from a Google Sheets document (`FINAL_ORDERS` sheet) and automatically:
- Authenticates with the Glovo API
- Creates quotes for valid orders
- Places orders based on delivery frequency schedules
- Logs results back to Google Sheets

### Key Features

- ✅ **Automated Daily Processing**: Runs Monday-Friday at 9:00 AM UTC via GitHub Actions
- ✅ **Smart Delivery Frequency Logic**: 
  - Frequency 3: Monday, Wednesday, Friday
  - Frequency 5: Every weekday (Monday-Friday)
- ✅ **Google Sheets Integration**: Reads orders and logs results
- ✅ **Cloud Deployment**: GitHub Actions for automated execution
- ✅ **Comprehensive Logging**: Detailed logs and result tracking
- ✅ **Error Handling**: Robust error handling and retry logic

## 📁 Project Structure

```
Glovo_DariVreme_Order_Automation/
├── step_1_authentication/          # Authentication module
│   ├── config.py                   # Configuration settings
│   ├── token_service.py            # Token management service (with caching)
│   └── 1_glovo_auth_helper.py      # Simple authentication helper
├── step_2_quota_Config/            # Data processing and quote creation
│   ├── sheet_to_json.py            # Google Sheets/Excel to JSON converter
│   ├── POST_create_quote_id_final.py  # Quote creation API calls
│   └── get_excel_data_to_json_main.py # Data processing example
├── step_3_send_order_with_quotaID/ # Order sending module
│   ├── send_order_with_quote_id_final.py  # Main order creation script
│   └── enhanced_send_order.py      # Enhanced order creation
├── daily_delivery_automation.py    # Main daily automation script ⭐
├── production_workflow.py          # Alternative production workflow
├── setup_daily_automation.py       # Setup script for cron/systemd
├── manual_scheduler.py             # Manual testing script
├── order_logger.py                 # Order logging utilities
├── google_sheets_logger.py         # Google Sheets logging
├── Test Scripts/                   # Testing utilities
├── .github/workflows/               # GitHub Actions workflows
│   └── daily-delivery-automation.yml
├── requirements.txt                 # Python dependencies
├── env.example                      # Environment variables template
└── README.md                        # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Glovo_DariVreme_Order_Automation

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file or set environment variables:

```bash
# Copy the example file
cp env.example .env 
#TODO QUESTION - env.example or .env.example ? Which is latest?

# Edit .env with your credentials
```

Required environment variables:
```bash
TOKEN_URL=https://stageapi.glovoapp.com/oauth/token #TODO let's rename to GLOVO_OAUTH_TOKEN_URL
API_KEY=your_api_key_here #TODO rename to #GLOVO_API_KEY
API_SECRET=your_api_secret_here #TODO rename to #GLOVO_API_SECRET
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
```

### 3. Google Sheets Setup

1. **Create a Google Cloud Project** and enable Google Sheets API
2. **Create a Service Account** and download credentials JSON
3. **Share your Google Sheet** with the service account email
4. **Place credentials** as `google_sheets_credentials.json` in project root

See detailed setup in the [Google Sheets Integration](#google-sheets-integration) section below.

### 4. Test the System

```bash
# Test authentication
python step_1_authentication/token_service.py

# Test manual execution
python manual_scheduler.py

# Run full daily automation
python daily_delivery_automation.py
```

## 💻 Running Locally

This section provides detailed instructions for running the project on your local machine.

### Prerequisites

Before running locally, ensure you have:

- **Python 3.8+** installed
- **pip** package manager
- **Git** (if cloning from repository)
- **Google Cloud Project** with Sheets API enabled
- **Glovo API credentials** (API key and secret)
- **Google Sheets** with `FINAL_ORDERS` sheet set up

### Step-by-Step Local Setup

#### 1. Clone and Navigate to Project

```bash
# Clone the repository
git clone <repository-url>
cd Glovo_DariVreme_Order_Automation

# Verify you're in the correct directory
ls -la
```

#### 2. Create Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
```

#### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp env.example .env

# Edit .env file with your credentials
# On macOS/Linux:
nano .env
# or
vim .env

# On Windows:
notepad .env
```

**Required variables in `.env`:**
```bash
# Glovo API Configuration
TOKEN_URL=https://stageapi.glovoapp.com/oauth/token
API_KEY=your_actual_api_key_here
API_SECRET=your_actual_api_secret_here

# Google Sheets Configuration
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit

# Optional: Token cache location
TOKEN_CACHE_FILE=~/.cache/myapp/token.json
```

**Alternative: Set environment variables directly:**
```bash
# macOS/Linux
export TOKEN_URL="https://stageapi.glovoapp.com/oauth/token"
export API_KEY="your_api_key"
export API_SECRET="your_api_secret"
export GOOGLE_SHEETS_URL="https://docs.google.com/spreadsheets/d/YOUR_ID/edit"

# Windows (PowerShell)
$env:TOKEN_URL="https://stageapi.glovoapp.com/oauth/token"
$env:API_KEY="your_api_key"
$env:API_SECRET="your_api_secret"
$env:GOOGLE_SHEETS_URL="https://docs.google.com/spreadsheets/d/YOUR_ID/edit"
```

#### 5. Set Up Google Sheets Credentials

1. **Download service account credentials** from Google Cloud Console
2. **Rename the file** to `google_sheets_credentials.json`
3. **Place it in the project root directory**:
   ```bash
   # Verify file is in the right place
   ls -la google_sheets_credentials.json
   ```
4. **Share your Google Sheet** with the service account email (found in the JSON file)

#### 6. Verify Setup

```bash
# Test environment variables are loaded
python Test Scripts/test_env_vars.py

# Test authentication
python step_1_authentication/token_service.py

# Expected output: ✅ Successfully got token: eyJ...
```

### Running Different Scripts Locally

#### Run Daily Automation (Main Script)

```bash
# Run the complete daily automation
python daily_delivery_automation.py

# This will:
# 1. Load orders from FINAL_ORDERS sheet
# 2. Filter by current weekday and delivery frequency
# 3. Create quotes for valid orders
# 4. Place orders using quote IDs
# 5. Log results to Google Sheets and local files
```

#### Run Production Workflow

```bash
# Run the production workflow (interactive)
python production_workflow.py

# This will prompt for confirmation before processing real orders
```

#### Run Manual Scheduler (Testing)

```bash
# Run manual scheduler for testing
python manual_scheduler.py

# Useful for testing without waiting for scheduled time
```

#### Run Individual Steps

```bash
# Step 1: Test Authentication Only
cd step_1_authentication
python token_service.py
cd ..

# Step 2: Test Quote Creation Only
python step_2_quota_Config/POST_create_quote_id_final.py

# Step 3: Test Order Creation Only
python step_3_send_order_with_quotaID/send_order_with_quote_id_final.py
```

#### Run Test Scripts

```bash
# Test complete automation
python Test Scripts/test_automation.py

# Test order creation
python Test Scripts/test_order_creation.py

# Validate Excel/Sheets data
python Test Scripts/validate_excel_data.py

# Test data flow
python Test Scripts/test_data_flow.py
```

### Local Development Workflow

#### 1. Make Changes to Code

```bash
# Edit files as needed
# Example: Modify daily_delivery_automation.py
nano daily_delivery_automation.py
```

#### 2. Test Your Changes

```bash
# Run tests to verify changes
python Test Scripts/test_automation.py

# Or run the main script
python daily_delivery_automation.py
```

#### 3. Check Logs

```bash
# View daily logs
tail -f logs/daily_delivery_*.log

# View results
cat daily_results/daily_automation_*.json | jq .
```

### Running with Different Configurations

#### Use Different Google Sheet

```python
# Create a test script
from daily_delivery_automation import DailyDeliveryAutomation

automation = DailyDeliveryAutomation(
    google_sheets_url="https://docs.google.com/spreadsheets/d/TEST_SHEET_ID/edit",
    sheet_name="FINAL_ORDERS"
)
results = automation.run_daily_automation()
```

#### Adjust Rate Limiting

```python
# In your script
from daily_delivery_automation import DailyDeliveryAutomation

automation = DailyDeliveryAutomation(
    google_sheets_url="YOUR_SHEET_URL",
    sheet_name="FINAL_ORDERS"
)
# Use slower rate limit (1 request per second)
results = automation.run_daily_automation(rate_limit_per_sec=1.0)
```

### Common Local Setup Issues

#### Issue: ModuleNotFoundError

```bash
# Solution: Ensure you're in the project directory and virtual environment is activated
cd /path/to/Glovo_DariVreme_Order_Automation
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Issue: Authentication Fails

```bash
# Check environment variables are set
echo $API_KEY
echo $API_SECRET

# Or check .env file exists and has correct values
cat .env

# Test authentication directly
python step_1_authentication/token_service.py
```

#### Issue: Google Sheets Access Denied

```bash
# Verify credentials file exists
ls -la google_sheets_credentials.json

# Check service account email has access to sheet
# (Open Google Sheet → Share → Verify service account email is listed)

# Test Google Sheets access
python Test Scripts/validate_excel_data.py
```

#### Issue: Python Version Mismatch

```bash
# Check Python version
python --version  # Should be 3.8+

# If wrong version, specify Python 3 explicitly
python3 daily_delivery_automation.py
```

#### Issue: Permission Denied

```bash
# Make scripts executable (macOS/Linux)
chmod +x daily_delivery_automation.py
chmod +x manual_scheduler.py

# Or run with Python explicitly
python daily_delivery_automation.py
```

### Local Logging and Output

When running locally, you'll see:

- **Console output**: Real-time progress and results
- **Log files**: `logs/daily_delivery_YYYYMMDD.log`
- **Result files**: `daily_results/daily_automation_YYYYMMDD_HHMMSS.json`
- **Google Sheets**: Results logged to `Glovo-Orders-Summary` sheet

### Stopping Local Execution

```bash
# If script is running, stop with:
Ctrl + C

# For background processes:
ps aux | grep python
kill <process_id>
```

### Next Steps After Local Setup

Once running locally:

1. ✅ Verify all tests pass
2. ✅ Test with sample data
3. ✅ Review logs for any issues
4. ✅ Set up scheduled execution (cron/systemd) if needed
5. ✅ Deploy to GitHub Actions for cloud execution

## 📋 How It Works

### Three-Step Process

#### Step 1: Authentication
- Obtains bearer token from Glovo OAuth endpoint
- Uses token caching to avoid unnecessary API calls
- Automatically refreshes expired tokens

**Files:**
- `step_1_authentication/token_service.py` - Advanced token service with caching
- `step_1_authentication/1_glovo_auth_helper.py` - Simple helper script

#### Step 2: Quote Creation
- Loads order data from Google Sheets (`FINAL_ORDERS` sheet)
- Validates required fields (addresses, coordinates, pickup times)
- Creates quotes via Glovo API (`/v2/laas/quotes`)
- Filters orders based on delivery frequency and current weekday

**Files:**
- `step_2_quota_Config/sheet_to_json.py` - Data loading utility
- `step_2_quota_Config/POST_create_quote_id_final.py` - Quote creation

#### Step 3: Order Placement
- Extracts quote IDs from successful quote responses
- Creates orders using quote IDs (`/v2/laas/quotes/{quoteId}/parcels`)
- Logs results to Google Sheets (`Glovo-Orders-Summary` sheet)

**Files:**
- `step_3_send_order_with_quotaID/send_order_with_quote_id_final.py` - Order creation

### Daily Automation Logic

The `daily_delivery_automation.py` script automatically:

1. **Loads orders** from `FINAL_ORDERS` Google Sheet
2. **Filters by weekday**:
   - **Frequency 3**: Processes on Monday, Wednesday, Friday
   - **Frequency 5**: Processes every weekday (Monday-Friday)
   - **Weekends**: No processing
3. **Creates quotes** for filtered orders
4. **Places orders** using successful quote IDs
5. **Logs results** to Google Sheets and local files

## 🔧 Configuration

### Google Sheets Structure

Your `FINAL_ORDERS` sheet should contain these columns:

| Column | Description | Required |
|--------|-------------|----------|
| `client_id` | Unique client identifier | Yes |
| `client_name` | Client name | Yes |
| `client_phone` | Phone number | Yes |
| `client_email` | Email address | Yes |
| `deliveryFrequency` | 3 or 5 (deliveries per week) | Yes |
| `deliveryRawAddress` | Full delivery address | Yes |
| `deliveryLattitude` | Delivery latitude | Yes |
| `deliveryLongitude` | Delivery longitude | Yes |
| `pickupAddressBookId` | Restaurant pickup address ID (UUID) | Yes |
| `pickup_time_utc` | Pickup time in ISO8601 UTC format | Yes |
| `restaurant_name` | Restaurant name | No |
| `order_id` | Order description | No |

### Delivery Frequency Schedule

| Day | Frequency 3 Clients | Frequency 5 Clients |
|-----|---------------------|---------------------|
| Monday | ✅ | ✅ |
| Tuesday | ❌ | ✅ |
| Wednesday | ✅ | ✅ |
| Thursday | ❌ | ✅ |
| Friday | ✅ | ✅ |
| Saturday | ❌ | ❌ |
| Sunday | ❌ | ❌ |

## 🌐 Deployment

### GitHub Actions (Recommended)

The project includes GitHub Actions workflows for automated execution:

**Workflow:** `.github/workflows/daily-delivery-automation.yml`

- **Schedule**: Runs Monday-Friday at 9:00 AM UTC
- **Manual Trigger**: Available via GitHub Actions UI

**Setup:**

1. **Add GitHub Secrets** (Repository → Settings → Secrets):
   ```
   API_KEY=your_api_key
   API_SECRET=your_api_secret
   GOOGLE_SHEETS_URL=your_sheets_url
   GOOGLE_SHEETS_CREDENTIALS=your_service_account_json
   ```

2. **Enable GitHub Actions** in repository settings

3. **Test the workflow**:
   - Go to Actions tab
   - Select "Daily Delivery Automation"
   - Click "Run workflow"

### Local Deployment (Cron/Systemd)

```bash
# Run setup script
python setup_daily_automation.py

# Option A: Install cron job
crontab daily_delivery_automation.cron

# Option B: Install systemd service
sudo cp daily-delivery-automation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable daily-delivery-automation.service
```

## 🧪 Testing

### Test Authentication
```bash
cd step_1_authentication
python token_service.py
```

### Test Quote Creation
```bash
python step_2_quota_Config/POST_create_quote_id_final.py
```

### Test Order Creation
```bash
python step_3_send_order_with_quotaID/send_order_with_quote_id_final.py
```

### Test Complete Workflow
```bash
# Manual test
python manual_scheduler.py

# Production workflow
python production_workflow.py
```

### Test Scripts
The `Test Scripts/` directory contains additional testing utilities:
- `test_automation.py` - Complete automation test
- `test_order_creation.py` - Order creation test
- `test_env_vars.py` - Environment variable validation
- `validate_excel_data.py` - Data validation

## 📊 Google Sheets Integration

### Setup Steps

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project

2. **Enable Google Sheets API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it

3. **Create Service Account**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Name: `glovo-order-logger`
   - Skip role assignment

4. **Generate Credentials**
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key" > "JSON"
   - Download and rename to `google_sheets_credentials.json`
   - Place in project root

5. **Share Google Sheet**
   - Open your Google Sheet
   - Click "Share" button
   - Add the service account email (from credentials JSON)
   - Give "Editor" permissions

### Sheets Used

- **FINAL_ORDERS**: Source sheet with order data
- **Glovo-Orders-Summary**: Destination sheet for order results

## 🔒 Security

### Best Practices

1. **Never commit credentials**:
   - Use `.env` file (add to `.gitignore`)
   - Use GitHub Secrets for CI/CD
   - Use environment variables in production

2. **Secure credential storage**:
   ```python
   # ✅ Good: Use environment variables
   API_KEY = os.getenv('API_KEY')
   
   # ❌ Bad: Hardcode credentials
   API_KEY = "17548268-1234-5678-9abc"
   ```

3. **Sanitize logs**:
   - Logs may contain sensitive information
   - Review logs before sharing
   - Use log rotation

4. **Access control**:
   - Limit access to Google Sheets
   - Use service accounts with minimal permissions
   - Rotate credentials regularly

### Environment Variables

Always use environment variables for sensitive data:
```bash
export API_KEY="your_key"
export API_SECRET="your_secret"
export GOOGLE_SHEETS_URL="your_url"
```

## 📝 Usage Examples

### Run Daily Automation Manually
```bash
python daily_delivery_automation.py
```

### Run Production Workflow
```bash
python production_workflow.py
```

### Process Specific Sheet
```python
from daily_delivery_automation import DailyDeliveryAutomation

automation = DailyDeliveryAutomation(
    google_sheets_url="https://docs.google.com/spreadsheets/d/YOUR_ID/edit",
    sheet_name="FINAL_ORDERS"
)
results = automation.run_daily_automation()
```

## 🐛 Troubleshooting

### Common Issues

1. **Authentication fails**
   - Check API credentials in environment variables
   - Verify `TOKEN_URL` is correct
   - Check token cache permissions

2. **Google Sheets access denied**
   - Verify service account email has access to sheet
   - Check credentials JSON file exists and is valid
   - Ensure Google Sheets API is enabled

3. **No orders processed**
   - Check current weekday matches delivery frequency
   - Verify `FINAL_ORDERS` sheet exists and has data
   - Check column names match expected format

4. **Quote creation fails**
   - Validate required fields (addresses, coordinates, pickup times)
   - Check pickup address IDs are valid UUIDs
   - Verify pickup times are in future (UTC)

5. **Order creation fails**
   - Ensure quotes were created successfully
   - Check quote IDs are valid
   - Verify client details are complete

### Logs

- **Daily logs**: `logs/daily_delivery_YYYYMMDD.log`
- **Results**: `daily_results/daily_automation_YYYYMMDD_HHMMSS.json`
- **Cron logs**: `/tmp/daily_delivery_automation.log` (if using cron)

## 📦 Dependencies

See `requirements.txt` for complete list. Main dependencies:

- `requests` - HTTP client for API calls
- `pandas` - Data manipulation
- `openpyxl` - Excel file handling
- `gspread` - Google Sheets API client
- `google-auth` - Google authentication
- `python-dotenv` - Environment variable management

## 🔄 Data Flow

1. **Authentication** → Get bearer token from Glovo OAuth
2. **Data Loading** → Load orders from Google Sheets
3. **Filtering** → Filter by delivery frequency and weekday
4. **Quote Creation** → Create quotes via Glovo API
5. **Order Placement** → Create orders using quote IDs
6. **Logging** → Save results to Google Sheets and local files

## 📚 Additional Resources

- **Glovo API Documentation**: [Logistics API Docs](https://logistics-docs.glovoapp.com/laas-partners/)
- **Google Sheets API**: [Google Sheets API Docs](https://developers.google.com/sheets/api)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Verify environment setup
4. Test individual components

---

**Last Updated**: 2024
