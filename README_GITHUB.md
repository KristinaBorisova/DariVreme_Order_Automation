# Glovo DariVreme Order Automation - GitHub Actions

🤖 **Automated Glovo order processing every 5 minutes using GitHub Actions**

## 🚀 **Quick Start**

1. **Upload this project to GitHub**
2. **Set up secrets** (see [GITHUB_SETUP.md](GITHUB_SETUP.md))
3. **Enable GitHub Actions**
4. **Watch your orders process automatically!**

## 📋 **What It Does**

- ✅ **Reads orders** from your Google Sheets every 5 minutes
- ✅ **Creates Glovo quotes** automatically
- ✅ **Places orders** with quote IDs
- ✅ **Logs results** back to Google Sheets
- ✅ **Sends notifications** on success/failure
- ✅ **Handles errors** gracefully with detailed logging

## 🔧 **Setup Required**

### **GitHub Secrets**
Add these to your repository secrets:

```
GLOVO_CLIENT_ID = your_glovo_client_id
GLOVO_CLIENT_SECRET = your_glovo_client_secret
GLOVO_API_URL = https://stageapi.glovoapp.com
GOOGLE_SHEETS_URL = your_google_sheets_url
GOOGLE_SHEETS_CREDENTIALS = your_service_account_json
```

### **Google Sheets Setup**
1. Create Google Cloud Project
2. Enable Google Sheets API
3. Create Service Account
4. Share your spreadsheet with service account email

## 📊 **Data Flow**

```
Google Sheets (Orders) 
    ↓ (Every 5 minutes)
GitHub Actions
    ↓
Glovo API (Quotes)
    ↓
Glovo API (Orders)
    ↓
Google Sheets (Results)
```

## 🎯 **Features**

- **🔄 Automatic**: Runs every 5 minutes
- **📊 Logging**: Detailed logs and results
- **🔒 Secure**: Credentials stored as GitHub secrets
- **📱 Monitoring**: GitHub Actions dashboard
- **🚨 Alerts**: Automatic issue creation on failures
- **📈 Scalable**: Configurable rate limits and batch sizes

## 📁 **Project Structure**

```
├── .github/workflows/
│   └── glovo-automation.yml    # GitHub Actions workflow
├── step_1_authentication/      # Glovo API authentication
├── step_2_quota_Config/        # Quote creation
├── step_3_send_order_with_quotaID/  # Order creation
├── google_sheets_logger.py     # Google Sheets integration
├── github_automation.py        # Main automation script
├── requirements.txt            # Python dependencies
└── GITHUB_SETUP.md            # Detailed setup guide
```

## 🛠️ **Configuration**

### **Schedule**
Edit `.github/workflows/glovo-automation.yml`:
```yaml
schedule:
  - cron: '*/5 * * * *'  # Every 5 minutes
```

### **Rate Limiting**
```yaml
env:
  RATE_LIMIT_PER_SEC: 2.0      # 2 requests per second
  MAX_ORDERS_PER_RUN: 20       # Max 20 orders per run
```

## 📈 **Monitoring**

- **GitHub Actions**: View workflow runs and logs
- **Google Sheets**: See order results in real-time
- **Notifications**: Get alerts on failures
- **Artifacts**: Download detailed logs

## 🔒 **Security**

- ✅ **No credentials in code**
- ✅ **Encrypted secrets**
- ✅ **Service account permissions**
- ✅ **Audit trail**

## 🚨 **Troubleshooting**

### **Common Issues**
- **Authentication failed**: Check Glovo API credentials
- **Google Sheets access denied**: Verify service account permissions
- **No orders found**: Check Google Sheets data and structure
- **Rate limit exceeded**: Adjust rate limiting settings

### **Debug Mode**
Enable debug logging:
```yaml
env:
  LOG_LEVEL: DEBUG
```

## 📚 **Documentation**

- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Complete setup guide
- [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) - Google Sheets integration
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing instructions
- [README.md](README.md) - Original project documentation

## 🎉 **Success Indicators**

When working correctly, you'll see:

```
✅ Authentication successful
📋 Loaded 5 orders from Google Sheets
✅ Created 5 quotes
✅ Created 5 orders
📊 Orders saved to Google Sheets: 'Glovo-Orders-Summary'
🎉 Automation completed successfully!
```

## 🔄 **Workflow Triggers**

- **⏰ Schedule**: Every 5 minutes
- **👆 Manual**: Run workflow button
- **📝 Code changes**: Push to main branch
- **📁 File changes**: Modify order-related files

## 📱 **Mobile Access**

- **GitHub Mobile**: Monitor runs on your phone
- **Google Sheets Mobile**: View results anywhere
- **Email notifications**: Get alerts instantly

## 🛠️ **Maintenance**

- **Weekly**: Check workflow runs and logs
- **Monthly**: Review and update credentials
- **As needed**: Adjust rate limits and batch sizes

---

**Ready to automate your Glovo orders?** 

👉 **Start with [GITHUB_SETUP.md](GITHUB_SETUP.md) for complete setup instructions!**
