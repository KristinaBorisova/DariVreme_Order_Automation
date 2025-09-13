# 🚀 GitHub Actions Setup for Daily Delivery Automation

## Overview

This guide will help you set up GitHub Actions to automatically run your daily delivery automation every weekday at 9:00 AM UTC.

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **GitHub Secrets**: You'll need to configure some secrets
3. **Python Dependencies**: All required packages should be in `requirements.txt`

## 🔧 Setup Steps

### 1. Create GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `TOKEN_URL` | Glovo API token URL | `https://stageapi.glovoapp.com/v2/laas/oauth/token` |
| `API_KEY` | Your Glovo API key | `175482686405285` |
| `API_SECRET` | Your Glovo API secret | `dc190e6d0e4f4fc79e4021e4b981e596` |
| `GOOGLE_SHEETS_URL` | Your Google Sheets URL | `https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004` |

### 2. Update requirements.txt

Make sure your `requirements.txt` includes all necessary packages:

```txt
requests>=2.31.0
pandas>=2.0.0
openpyxl>=3.1.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.100.0
```

### 3. Verify Workflow File

The workflow file is already created at:
```
.github/workflows/daily-delivery-automation.yml
```

### 4. Test the Workflow

#### Manual Test (Recommended First)
1. Go to your repository → Actions tab
2. Click on "Daily Delivery Automation"
3. Click "Run workflow"
4. Select "Run in test mode (dry run)" to test without creating actual orders
5. Click "Run workflow"

#### Schedule Test
The workflow will automatically run every weekday at 9:00 AM UTC. You can check the Actions tab to see the runs.

## ⏰ Timezone Configuration

The workflow is set to run at 9:00 AM UTC. To change the timezone:

1. **Option 1: Change the cron schedule**
   ```yaml
   schedule:
     - cron: '0 11 * * 1-5'  # 11:00 AM UTC = 1:00 PM CET
   ```

2. **Option 2: Use a different timezone**
   ```yaml
   schedule:
     - cron: '0 9 * * 1-5'
   timezone: 'Europe/Sofia'  # Adjust to your timezone
   ```

## 📊 Monitoring

### View Workflow Runs
1. Go to your repository → Actions tab
2. Click on "Daily Delivery Automation"
3. Click on any run to see detailed logs

### Download Logs and Results
Each run creates artifacts with:
- **Logs**: Detailed execution logs
- **Results**: JSON files with order results

### Check Run Status
- ✅ **Green**: Automation completed successfully
- ❌ **Red**: Automation failed (check logs for details)
- 🟡 **Yellow**: Automation is running

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check if API credentials are correct in secrets
   - Verify TOKEN_URL is correct
   - Check if API key/secret are valid

2. **Google Sheets Access Error**
   - Verify GOOGLE_SHEETS_URL is correct
   - Ensure the sheet is publicly accessible
   - Check if sheet name is "FINAL_ORDERS"

3. **Python Dependencies Missing**
   - Update requirements.txt with all needed packages
   - Check if all imports are available

4. **Workflow Not Running**
   - Check if the workflow file is in the correct location
   - Verify the cron schedule syntax
   - Check if the repository has Actions enabled

### Debug Steps

1. **Check Workflow Logs**
   ```bash
   # View the latest run logs
   # Go to Actions → Daily Delivery Automation → Latest run
   ```

2. **Test Locally First**
   ```bash
   # Test the automation locally
   python daily_delivery_automation.py
   
   # Test in dry run mode
   python test_weekday_automation.py
   ```

3. **Verify Secrets**
   - Go to Settings → Secrets and variables → Actions
   - Ensure all required secrets are present
   - Check if secret values are correct

## 📈 Advanced Configuration

### Custom Schedule
```yaml
schedule:
  - cron: '0 8 * * 1-5'   # 8:00 AM UTC
  - cron: '0 14 * * 1-5'  # 2:00 PM UTC (twice daily)
```

### Different Python Version
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Change version
```

### Environment-Specific Configuration
```yaml
- name: Set up environment variables
  run: |
    if [ "${{ github.ref }}" = "refs/heads/main" ]; then
      echo "ENVIRONMENT=production" >> $GITHUB_ENV
    else
      echo "ENVIRONMENT=staging" >> $GITHUB_ENV
    fi
```

## 🚨 Notifications

### Email Notifications
Add this step to get email notifications on failure:
```yaml
- name: Notify on failure
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: 'Daily Delivery Automation Failed'
    to: your-email@example.com
    from: GitHub Actions
    body: 'The daily delivery automation failed. Check the logs for details.'
```

### Slack Notifications
```yaml
- name: Notify Slack on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    channel: '#delivery-automation'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Discord Notifications
```yaml
- name: Notify Discord on failure
  if: failure()
  uses: Ilshidur/action-discord@master
  with:
    args: 'Daily delivery automation failed. Check the logs for details.'
  env:
    DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
```

## ✅ Verification Checklist

- [ ] GitHub repository created
- [ ] All secrets configured
- [ ] requirements.txt updated
- [ ] Workflow file in place
- [ ] Manual test run successful
- [ ] Schedule test run successful
- [ ] Logs and results accessible
- [ ] Notifications working (optional)

## 🎉 Success!

Once everything is set up, your daily delivery automation will:

- ✅ Run automatically every weekday at 9:00 AM UTC
- ✅ Process orders based on delivery frequency
- ✅ Create quotes and orders via Glovo API
- ✅ Log all activities and results
- ✅ Handle errors gracefully
- ✅ Provide detailed logs and artifacts

The system is now fully automated and will run in the cloud without any local intervention!
