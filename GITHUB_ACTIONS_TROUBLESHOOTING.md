# 🔧 GitHub Actions Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Issue 1: Environment Variables Not Set

**Problem**: `GOOGLE_SHEETS_URL` or other environment variables are empty.

**Solution**:
1. **Check GitHub Secrets**:
   - Go to Repository → Settings → Secrets and variables → Actions
   - Verify all secrets are set:
     - `TOKEN_URL`: `https://stageapi.glovoapp.com/v2/laas/oauth/token`
     - `API_KEY`: `175482686405285`
     - `API_SECRET`: `dc190e6d0e4f4fc79e4021e4b981e596`
     - `GOOGLE_SHEETS_URL`: `https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004`

2. **Test Environment Variables**:
   ```bash
   # Run locally to test
   python test_env_vars.py
   ```

### Issue 2: 404 Error When Fetching Token

**Problem**: `requests.exceptions.HTTPError: 404 Client Error: Not Found`

**Causes**:
- Wrong `TOKEN_URL` in secrets
- API endpoint changed
- Network issues

**Solution**:
1. **Verify TOKEN_URL**:
   - Should be: `https://stageapi.glovoapp.com/v2/laas/oauth/token`
   - Check if it's accessible: `curl https://stageapi.glovoapp.com/v2/laas/oauth/token`

2. **Test Authentication Locally**:
   ```bash
   cd step_1_authentication
   python token_service.py
   ```

3. **Check API Documentation**:
   - Verify the endpoint URL is correct
   - Check if there are any API changes

### Issue 3: Import Errors

**Problem**: `ModuleNotFoundError` or import failures.

**Solution**:
1. **Check requirements.txt**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test imports locally**:
   ```bash
   python test_github_actions.py
   ```

### Issue 4: Google Sheets Access Error

**Problem**: Cannot access Google Sheets.

**Solution**:
1. **Verify Sheet URL**:
   - Check if the URL is correct
   - Ensure the sheet is publicly accessible
   - Verify the sheet name is "FINAL_ORDERS"

2. **Test Sheet Access**:
   ```bash
   python test_weekday_automation.py
   ```

## 🔍 Debugging Steps

### Step 1: Check Workflow Logs
1. Go to Repository → Actions
2. Click on the failed workflow run
3. Click on the failed step
4. Check the logs for error details

### Step 2: Test Locally
```bash
# Test environment variables
python test_env_vars.py

# Test authentication
cd step_1_authentication
python token_service.py

# Test automation
python daily_delivery_automation.py

# Test weekday automation
python test_weekday_automation.py
```

### Step 3: Verify Secrets
```bash
# Check if secrets are set (in GitHub Actions)
echo "TOKEN_URL: $TOKEN_URL"
echo "API_KEY: $API_KEY"
echo "API_SECRET: $API_SECRET"
echo "GOOGLE_SHEETS_URL: $GOOGLE_SHEETS_URL"
```

## 🛠️ Quick Fixes

### Fix 1: Update Secrets
1. Go to Repository → Settings → Secrets and variables → Actions
2. Delete and recreate the problematic secret
3. Ensure the value is exactly correct (no extra spaces)

### Fix 2: Test with Manual Trigger
1. Go to Actions → Daily Delivery Automation
2. Click "Run workflow"
3. Select "Run in test mode (dry run)"
4. Click "Run workflow"

### Fix 3: Check Workflow File
Ensure `.github/workflows/daily-delivery-automation.yml` is correct:
```yaml
- name: Set up environment variables
  run: |
    echo "TOKEN_URL=${{ secrets.TOKEN_URL }}" >> $GITHUB_ENV
    echo "API_KEY=${{ secrets.API_KEY }}" >> $GITHUB_ENV
    echo "API_SECRET=${{ secrets.API_SECRET }}" >> $GITHUB_ENV
    echo "GOOGLE_SHEETS_URL=${{ secrets.GOOGLE_SHEETS_URL }}" >> $GITHUB_ENV
```

## 📊 Status Check Commands

### Check Environment Variables
```bash
python test_env_vars.py
```

### Check Authentication
```bash
cd step_1_authentication
python token_service.py
```

### Check All Modules
```bash
python test_github_actions.py
```

### Check Weekday Logic
```bash
python test_weekday_automation.py
```

## 🚨 Emergency Fixes

### If All Else Fails

1. **Reset Everything**:
   ```bash
   # Update all files
   git add .
   git commit -m "Fix GitHub Actions issues"
   git push origin main
   ```

2. **Check GitHub Status**:
   - Go to https://www.githubstatus.com/
   - Check if GitHub Actions is having issues

3. **Use Manual Trigger**:
   - Run the workflow manually instead of on schedule
   - This can help isolate the issue

## 📞 Getting Help

### Before Asking for Help

1. **Check the logs** in the Actions tab
2. **Test locally** with the same commands
3. **Verify secrets** are set correctly
4. **Check this troubleshooting guide**

### When Reporting Issues

Include:
- The exact error message
- Which step failed
- The workflow run URL
- What you've already tried

## ✅ Success Checklist

- [ ] All secrets are set in GitHub
- [ ] Environment variables test passes
- [ ] Authentication test passes
- [ ] All modules import successfully
- [ ] Google Sheets access works
- [ ] Workflow runs without errors

---

**🎯 Most issues are related to missing or incorrect secrets. Double-check your GitHub Secrets configuration!**
