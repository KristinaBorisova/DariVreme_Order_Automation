# 🔒 Security Guide for Public Repository

## ⚠️ **CRITICAL: Before Making Public**

### 1. **Remove All Sensitive Data**
```bash
# Search and remove these patterns:
grep -r "API_KEY=" . --exclude-dir=.git
grep -r "API_SECRET = os.getenv("API_SECRET", "your_api_secret_here")google.com/spreadsheets" . --exclude-dir=.git
grep -r "glovoapp.com" . --exclude-dir=.git
```

### 2. **Replace with Placeholders**
```python
# BEFORE (DANGEROUS):
API_KEY = "17548268-1234-5678-9abc-def012345678"

# AFTER (SAFE):
API_KEY = os.getenv('API_KEY', 'your_api_key_here')
```

### 3. **Use Environment Variables**
```python
# Secure way to handle credentials:
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
GOOGLE_SHEETS_URL = os.getenv('GOOGLE_SHEETS_URL')
```

## 🚫 **What to NEVER Include in Public Code:**

### API Credentials
- `API_KEY`
- `API_SECRET` 
- `TOKEN_URL`
- Any hardcoded authentication tokens

### Business Data
- Real client names, phones, emails
- Actual delivery addresses
- Restaurant names and locations
- Pickup address book IDs
- Google Sheets URLs with real IDs

### Internal URLs
- Production API endpoints
- Internal service URLs
- Database connection strings

## ✅ **Safe to Include:**

### Code Structure
- Python scripts and logic
- Configuration templates
- Documentation
- Test data (with fake information)

### Example Data
```python
# Safe example data:
SAMPLE_ORDER = {
    "client_id": "CLIENT_001",
    "client_name": "Sample Client",
    "client_phone": "+1234567890",
    "client_email": "client@example.com",
    "deliveryRawAddress": "123 Sample Street, Sample City",
    "pickupAddressBookId": "sample-uuid-here"
}
```

## 🔧 **Implementation Steps:**

### 1. Create Environment File
```bash
# Create .env file (add to .gitignore)
touch .env
echo "API_KEY=your_real_key" >> .env
echo "API_SECRET=your_real_secret" >> .env
echo "GOOGLE_SHEETS_URL=your_real_url" >> .env
```

### 2. Update .gitignore
```gitignore
# Add to .gitignore
.env
*.env
google_sheets_credentials.json
daily_results/
logs/
__pycache__/
*.pyc
```

### 3. Create Example Files
```bash
# Create example files for public use
cp .env .env.example
# Edit .env.example to have placeholder values
```

### 4. Sanitize Existing Code
```python
# Replace hardcoded values:
# OLD:
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"

# NEW:
GOOGLE_SHEETS_URL = os.getenv('GOOGLE_SHEETS_URL', 'https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit')
```

## 📋 **Pre-Public Checklist:**

- [ ] Remove all API keys and secrets
- [ ] Replace real URLs with placeholders
- [ ] Anonymize all client data
- [ ] Remove business-specific information
- [ ] Add .env to .gitignore
- [ ] Create .env.example with placeholders
- [ ] Update README with setup instructions
- [ ] Test with example data only

## 🚨 **Additional Security Measures:**

### Rate Limiting
```python
# Implement rate limiting to prevent API abuse
import time
time.sleep(1)  # 1 second between requests
```

### Input Validation
```python
# Validate all inputs to prevent injection attacks
def validate_client_data(data):
    if not isinstance(data.get('client_name'), str):
        raise ValueError("Invalid client name")
    # Add more validations...
```

### Error Handling
```python
# Don't expose internal errors
try:
    # API call
except Exception as e:
    logger.error("API call failed")
    # Don't log sensitive error details
```

## 📖 **Documentation for Public Users:**

### Setup Instructions
1. Clone the repository
2. Copy `.env.example` to `.env`
3. Fill in your own API credentials
4. Update Google Sheets URL
5. Run the automation

### Required Permissions
- Glovo API access
- Google Sheets API access
- Service account credentials

## ⚡ **Quick Security Script:**

```bash
#!/bin/bash
# security_check.sh - Run before making public

echo "🔍 Checking for sensitive data..."

# Check for API keys
if grep -r "API_KEY=" . --exclude-dir=.git | grep -v "your_api_key_here"; then
    echo "❌ Found hardcoded API keys!"
    exit 1
fi

# Check for real URLs
if grep -r "docs.google.com/spreadsheets/d/" . --exclude-dir=.git | grep -v "YOUR_SPREADSHEET_ID"; then
    echo "❌ Found real Google Sheets URLs!"
    exit 1
fi

# Check for real client data
if grep -r "@gmail.com\|@yahoo.com\|@outlook.com" . --exclude-dir=.git; then
    echo "❌ Found real email addresses!"
    exit 1
fi

echo "✅ Security check passed!"
```

Remember: **When in doubt, don't include it!** It's better to be overly cautious than to accidentally expose sensitive business data.
