# GitHub Actions Setup Guide

This guide will help you set up automatic Glovo order processing every 5 minutes using GitHub Actions.

## 🎯 **What This Does**

- ✅ **Automatic triggering** every 5 minutes
- ✅ **Reads orders** from your Google Sheets
- ✅ **Creates quotes** and orders automatically
- ✅ **Logs results** back to Google Sheets
- ✅ **Sends notifications** on success/failure
- ✅ **Secure credential management**

## 🚀 **Setup Steps**

### **Step 1: Upload to GitHub**

1. **Create a new repository** on GitHub
2. **Upload your project** to the repository
3. **Make sure** all files are committed

### **Step 2: Set up GitHub Secrets**

Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:

#### **Glovo API Secrets**
```
GLOVO_CLIENT_ID = 175482686405285
GLOVO_CLIENT_SECRET = dc190e6d0e4f4fc79e4021e4b981e596
GLOVO_API_URL = https://stageapi.glovoapp.com
```

#### **Google Sheets Secret**
```
GOOGLE_SHEETS_URL = https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
```

### **Step 3: Enable GitHub Actions**

1. Go to your repository → **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow will start running automatically

### **Step 4: Test the Setup**

1. **Manual trigger**: Go to Actions → Glovo Order Automation → Run workflow
2. **Check logs**: Click on the workflow run to see detailed logs
3. **Verify results**: Check your Google Sheets for new orders

## ⚙️ **Configuration Options**

### **Change Schedule**
Edit `.github/workflows/glovo-automation.yml`:

```yaml
schedule:
  # Every 5 minutes
  - cron: '*/5 * * * *'
  
  # Every hour
  - cron: '0 * * * *'
  
  # Every day at 9 AM
  - cron: '0 9 * * *'
  
  # Every weekday at 9 AM
  - cron: '0 9 * * 1-5'
```

### **Limit Orders Per Run**
Set environment variables in the workflow:

```yaml
env:
  MAX_ORDERS_PER_RUN: 10  # Process max 10 orders per run
  RATE_LIMIT_PER_SEC: 1.0  # Slower rate limiting
```

## 📊 **Monitoring and Logs**

### **View Workflow Runs**
1. Go to **Actions** tab in your repository
2. Click on **"Glovo Order Automation"**
3. View individual runs and their logs

### **Download Logs**
- Each run creates downloadable artifacts
- Logs are kept for 30 days
- Includes detailed error information

### **Success Notifications**
- ✅ **Console output** shows success messages
- ✅ **Logs** contain detailed information
- ✅ **Google Sheets** updated with new orders

### **Failure Notifications**
- ❌ **GitHub Issues** created automatically on failure
- ❌ **Detailed error logs** in artifacts
- ❌ **Email notifications** (if configured)

## 🔒 **Security Features**

### **Credential Protection**
- ✅ **Secrets** are encrypted and never visible in logs
- ✅ **Credentials** are only available during workflow execution
- ✅ **No sensitive data** in repository

### **Access Control**
- ✅ **Repository permissions** control who can trigger workflows
- ✅ **Branch protection** prevents unauthorized changes
- ✅ **Audit trail** of all workflow runs

## 🚨 **Troubleshooting**

### **Common Issues**

#### **"Authentication failed"**
- Check if `GLOVO_CLIENT_ID` and `GLOVO_CLIENT_SECRET` are correct
- Verify the Glovo API is accessible

#### **"Google Sheets access denied"**
- Ensure `GOOGLE_SHEETS_CREDENTIALS` is valid JSON
- Check if service account has access to the spreadsheet
- Verify the spreadsheet URL is correct

#### **"No orders found"**
- Check if your Google Sheets has data
- Verify the sheet name and structure
- Ensure pickup times are in the future

#### **"Rate limit exceeded"**
- Increase `RATE_LIMIT_PER_SEC` in workflow
- Reduce `MAX_ORDERS_PER_RUN`
- Check Glovo API rate limits

### **Debug Mode**
Enable debug logging by adding to workflow:

```yaml
env:
  LOG_LEVEL: DEBUG
```

## 📈 **Performance Optimization**

### **Recommended Settings**
```yaml
env:
  RATE_LIMIT_PER_SEC: 2.0      # 2 requests per second
  MAX_ORDERS_PER_RUN: 20       # Max 20 orders per run
  LOG_LEVEL: INFO              # Info level logging
```

### **Scaling Considerations**
- **High volume**: Increase `MAX_ORDERS_PER_RUN`
- **API limits**: Decrease `RATE_LIMIT_PER_SEC`
- **Frequent runs**: Adjust cron schedule

## 🎉 **Expected Results**

### **Successful Run Output**
```
🚀 Starting Glovo Order Automation
📅 Run started at: 2025-01-15T14:30:00Z
🔐 Step 1: Authentication
✅ Authentication successful
📊 Step 2: Loading data from Google Sheets
📋 Loaded 5 orders from Google Sheets
💰 Step 3: Creating quotes
Quote creation completed:
   - Total processed: 5
   - Successful quotes: 5
   - Failed quotes: 0
📦 Step 4: Creating orders with Google Sheets logging
✅ Google Sheets logging enabled
Processing 5 orders...
Processing order 1/5 - Quote ID: abc123...
✅ Order created successfully for Quote ID: abc123...
📝 Order logged:
   Order ID: 100010000000
   Client: Automated Client
   Status: CREATED
   Price: 8.06 BGN
...
Order creation completed:
   - Total processed: 5
   - Successful orders: 5
   - Failed orders: 0
   - Success rate: 100.0%
📊 Orders saved to Google Sheets: 'Glovo-Orders-Summary'
💾 Step 5: Saving results
✅ Results saved to: automation_results_20250115_143045.json
🎉 Automation completed successfully!
📊 Summary: Automation completed successfully. 5 orders created.
```

## 🔄 **Workflow Triggers**

The automation runs on:

1. **Schedule**: Every 5 minutes (configurable)
2. **Manual**: Click "Run workflow" button
3. **Code changes**: When you push changes to main branch
4. **File changes**: When order-related files are modified

## 📱 **Mobile Access**

- **GitHub Mobile App**: Monitor workflow runs on your phone
- **Email notifications**: Get notified of successes/failures
- **Google Sheets Mobile**: View order results on mobile

## 🛠️ **Maintenance**

### **Regular Checks**
- ✅ **Monitor workflow runs** weekly
- ✅ **Check error logs** for issues
- ✅ **Verify Google Sheets** access
- ✅ **Update credentials** if needed

### **Updates**
- ✅ **Dependencies**: Update `requirements.txt` as needed
- ✅ **Workflow**: Modify `.github/workflows/glovo-automation.yml`
- ✅ **Configuration**: Adjust environment variables

## 🎯 **Next Steps**

1. **Set up the repository** and secrets
2. **Test with manual trigger**
3. **Monitor the first few automatic runs**
4. **Adjust settings** based on your needs
5. **Set up notifications** for failures

Your Glovo order automation will now run every 5 minutes automatically! 🚀
