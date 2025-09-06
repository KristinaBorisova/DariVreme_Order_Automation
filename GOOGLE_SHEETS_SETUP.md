# Google Sheets Integration Setup Guide

This guide will help you set up Google Sheets integration for automatic order logging to your existing spreadsheet.

## 🎯 **What This Does**

Instead of creating local Excel files, the system will now save order results directly to your Google Sheets document in the "Glovo-Orders-Summary" sheet.

## 📋 **Prerequisites**

1. **Google Account** with access to Google Sheets
2. **Google Cloud Project** (free)
3. **Google Sheets API** enabled
4. **Service Account** credentials

## 🔧 **Setup Steps**

### **Step 1: Create Google Cloud Project**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project ID

### **Step 2: Enable Google Sheets API**

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"

### **Step 3: Create Service Account**

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in:
   - **Name**: `glovo-order-logger`
   - **Description**: `Service account for Glovo order logging`
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

### **Step 4: Generate Credentials**

1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Choose "JSON" format
6. Download the JSON file
7. **Rename it to**: `google_sheets_credentials.json`
8. **Place it in your project root directory**

### **Step 5: Share Your Spreadsheet**

1. Open your Google Sheets document:
   [https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit](https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit)

2. Click "Share" button (top right)
3. Add the service account email (from the JSON file, field `client_email`)
4. Give it "Editor" permissions
5. Click "Send"

### **Step 6: Install Required Dependencies**

```bash
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
```

## 🧪 **Test the Setup**

### **Option 1: Test Google Sheets Logger**
```bash
python google_sheets_logger.py
```

### **Option 2: Test with Real Data**
```bash
python test_with_real_data.py
```

### **Option 3: Test Production Workflow**
```bash
python production_workflow.py
```

## 📊 **What Gets Logged**

The system will automatically log the following information to the "Glovo-Orders-Summary" sheet:

| Column | Description | Example |
|--------|-------------|---------|
| Timestamp | Order creation time | 2025-01-15 14:30:25 |
| Order ID | Glovo tracking number | 100010173030 |
| Quote ID | Quote identifier | aff76702-e284-43ab-8ae2-78d0d605d285 |
| Order State | Current status | CREATED |
| Client Name | Client name | Test Client |
| Client Phone | Client phone | +359888123456 |
| Client Email | Client email | test@darivreme.com |
| Pickup Address Book ID | Pickup location ID | dd560a2c-f1b5-43b7-81bc-2830595122f9 |
| Pickup Time | Scheduled pickup | 2025-01-15T15:30:00Z |
| Expected Delivery | Expected delivery time | 2025-01-15T16:00:00Z |
| Delivery Address | Full delivery address | g.k. Strelbishte, Nishava St 111р 1408, Bulgaria |
| Quote Price | Order cost | 8.06 |
| Currency | Price currency | BGN |
| Pickup Order Code | Your order code | ORD1705321234567 |
| Created At | API creation time | 2025-01-15T14:30:25Z |
| Delivery Latitude | Delivery latitude | 42.673758 |
| Delivery Longitude | Delivery longitude | 23.298064 |
| Partner ID | Glovo partner ID | 67915107 |
| City Code | City code | SOF |
| Cancellable | Can be cancelled | TRUE |

## 🔄 **Fallback Behavior**

If Google Sheets integration fails, the system will automatically fall back to creating local Excel files as before.

## 🚨 **Troubleshooting**

### **Error: "Could not connect to Google Sheets"**
- Check if `google_sheets_credentials.json` exists in project root
- Verify the service account email has access to the spreadsheet
- Ensure Google Sheets API is enabled

### **Error: "Worksheet not found"**
- The system will automatically create the "Glovo-Orders-Summary" sheet
- Make sure the service account has "Editor" permissions

### **Error: "Authentication failed"**
- Check if the JSON credentials file is valid
- Verify the service account is active
- Ensure the spreadsheet is shared with the service account email

## 📁 **File Structure**

After setup, your project should look like:
```
Glovo_DariVreme_Order_Automation/
├── google_sheets_credentials.json  # ← Your credentials file
├── google_sheets_logger.py         # ← Google Sheets logger
├── order_logger.py                 # ← Local Excel logger (fallback)
├── step_3_send_order_with_quotaID/
│   └── send_order_with_quote_id.py # ← Updated with Google Sheets support
└── production_workflow.py          # ← Updated with Google Sheets support
```

## 🎉 **Success Indicators**

When everything is working correctly, you'll see:

```
✅ Google Sheets logging enabled
📝 Order logged:
   Order ID: 100010173030
   Client: Test Client
   Status: CREATED
   Price: 8.06 BGN

✅ Successfully saved 1 orders to Google Sheets
📊 Sheet: Glovo-Orders-Summary
🔗 URL: https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit

📊 Order Summary:
   Total Orders: 1
   Total Value: 8.06 BGN
   Unique Clients: 1
   Unique Pickup Locations: 1
   Orders by Status:
     CREATED: 1
   Date Range: 2025-01-15 14:30:25 to 2025-01-15 14:30:25

📊 Order results saved to Google Sheets!
   Sheet: 'Glovo-Orders-Summary'
   URL: https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit
```

## 🔒 **Security Notes**

- Keep your `google_sheets_credentials.json` file secure
- Don't commit it to version control
- The service account has limited permissions (only to your specific spreadsheet)
- You can revoke access anytime from Google Cloud Console

## 💡 **Benefits**

- ✅ **Real-time logging**: Orders appear in your spreadsheet immediately
- ✅ **No local files**: No need to manage Excel files
- ✅ **Collaborative**: Multiple people can view the results
- ✅ **Automatic backup**: Google Sheets handles backup automatically
- ✅ **Easy access**: View results from anywhere with internet
- ✅ **Fallback support**: Still creates local files if Google Sheets fails
