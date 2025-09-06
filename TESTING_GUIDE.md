# Testing Guide - Glovo DariVreme Order Automation

This guide will help you test the complete automation workflow step by step.

## Prerequisites

### 1. Environment Setup
```bash
# Set your Glovo API token
export GLOVO_TOKEN="your_actual_bearer_token_here"

# Verify token is set
echo $GLOVO_TOKEN
```

### 2. Required Dependencies
```bash
pip install requests pandas openpyxl
```

### 3. Test Data Preparation
You need either:
- A Google Sheets URL with order data, OR
- A local Excel file with order data

## Testing Steps

### Step 1: Test Authentication

#### Test 1.1: Basic Authentication
```bash
cd step_1_authentication
python 1_glovo_auth_helper.py
```

**Expected Output:**
```
Response <Response [200]>
Status Code 200
Response Data: {'accessToken': 'eyJ...', 'expires_in': 3600}
```

#### Test 1.2: Advanced Token Service
```bash
python token_service.py
```

**Expected Output:**
```
✅ Successfully got token: eyJhbGci...
Access Token in config: eyJhbGci...
```

### Step 2: Test Data Processing

#### Test 2.1: Convert Google Sheets to JSON
```bash
cd ../step_2_quota_Config

# Test with a public Google Sheet
python sheet_to_json.py "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing" -o test_json_export
```

**Expected Output:**
```
Done. JSON written to: test_json_export
```

#### Test 2.2: Verify JSON Structure
```bash
# Check the generated files
ls test_json_export/
cat test_json_export/workbook.json | head -20
```

**Expected Structure:**
```json
{
  "Sheet1": [
    {
      "pickup_address_id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "pickup_time_utc": "2024-01-15T14:15:22Z",
      "dest_raw_address": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
      "dest_lat": 41.39637,
      "dest_lng": 2.17939,
      "dest_details": "Floor 6 Door 3"
    }
  ]
}
```

### Step 3: Test Quote Creation

#### Test 3.1: Create Quotes (Dry Run)
```bash
# First, create a small test file with 1-2 orders
python create_test_data.py  # This will create test_orders.json

# Test quote creation with test data
python POST_create_quote_id.py
```

**Expected Output:**
```
=== Summary ===
Total: 2
Successes: 2
Failures: 0

Quote results saved to: quote_results.json
You can now run Step 3 to create orders with these quote IDs.
```

#### Test 3.2: Verify Quote Results
```bash
cat quote_results.json | jq '.successes[0].response.quoteId'
```

**Expected Output:**
```
"826e5192-f8c6-4e24-aab3-3910e46c52b7"
```

### Step 4: Test Order Creation

#### Test 4.1: Create Orders with Quote IDs
```bash
cd ../step_3_send_order_with_quotaID
python send_order_with_quote_id.py
```

**Expected Output:**
```
Loaded 2 successful quotes from quote_results.json
Extracted 2 quote IDs

=== Starting Order Creation ===
Processing 2 orders...
Processing order 1/2 - Quote ID: 826e5192-f8c6-4e24-aab3-3910e46c52b7
✅ Order created successfully for Quote ID: 826e5192-f8c6-4e24-aab3-3910e46c52b7
Processing order 2/2 - Quote ID: 826e5192-f8c6-4e24-aab3-3910e46c52b7
✅ Order created successfully for Quote ID: 826e5192-f8c6-4e24-aab3-3910e46c52b7

=== Order Creation Summary ===
Total processed: 2
Successful orders: 2
Failed orders: 0
Success rate: 100.0%
```

#### Test 4.2: Verify Order Results
```bash
cat order_results.json | jq '.successful_orders[0].order_response'
```

### Step 5: Test Complete Workflow

#### Test 5.1: Run Complete Workflow
```bash
python complete_workflow_example.py
```

**Expected Output:**
```
=== Glovo DariVreme Order Automation - Complete Workflow ===

Step 1: Checking authentication...
✅ Authentication token found

Step 2: Creating quotes...
✅ Quote creation completed:
   - Total processed: 2
   - Successful quotes: 2
   - Failed quotes: 0

Step 3: Creating orders with quote IDs...
✅ Extracted 2 quote IDs
✅ Order creation completed:
   - Total processed: 2
   - Successful orders: 2
   - Failed orders: 0
   - Success rate: 100.0%

Step 4: Saving results...
✅ Complete workflow results saved to: complete_workflow_results.json

=== Final Summary ===
Quotes created: 2
Orders placed: 2
Overall success rate: 100.0%

🎉 Complete workflow executed successfully!
```

## Test Data Creation

### Create Sample Test Data
```bash
cd step_2_quota_Config
python create_test_data.py
```

This creates `test_orders.json` with sample data:
```json
[
  {
    "pickup_address_id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "pickup_time_utc": "2024-01-15T14:15:22Z",
    "dest_raw_address": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
    "dest_lat": 41.39637,
    "dest_lng": 2.17939,
    "dest_details": "Floor 6 Door 3"
  },
  {
    "pickup_address_id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "pickup_time_utc": "2024-01-15T15:30:00Z",
    "dest_raw_address": "Passeig de Gràcia, 1, L'Eixample, 08008 Barcelona",
    "dest_lat": 41.3851,
    "dest_lng": 2.1734,
    "dest_details": "Main entrance"
  }
]
```

## Validation Scripts

### Validate API Responses
```bash
python validate_responses.py
```

### Check Data Format
```bash
python validate_data_format.py
```

## Common Issues and Solutions

### Issue 1: Authentication Failed
**Error:** `401 Unauthorized`
**Solution:**
```bash
# Check if token is set
echo $GLOVO_TOKEN

# Get new token
cd step_1_authentication
python token_service.py
```

### Issue 2: Invalid Data Format
**Error:** `Missing fields: pickup_address_id`
**Solution:**
- Check your Excel/Google Sheets column names
- Ensure all required fields are present
- Verify data types (lat/lng should be numeric)

### Issue 3: Quote Expired
**Error:** `Quote expired`
**Solution:**
- Quotes expire in 10 minutes
- Run order creation immediately after quote creation
- Check system time synchronization

### Issue 4: Rate Limiting
**Error:** `429 Too Many Requests`
**Solution:**
- Increase delay between requests
- Reduce `rate_limit_per_sec` parameter
- Wait and retry

## Performance Testing

### Test with Different Data Sizes
```bash
# Test with 5 orders
python create_test_data.py --count 5
python complete_workflow_example.py

# Test with 10 orders
python create_test_data.py --count 10
python complete_workflow_example.py
```

### Monitor API Usage
```bash
# Check response times
time python POST_create_quote_id.py

# Monitor memory usage
python -m memory_profiler complete_workflow_example.py
```

## Production Testing

### Pre-Production Checklist
- [ ] All tests pass
- [ ] Token is valid and not expired
- [ ] Data format is correct
- [ ] Rate limiting is appropriate
- [ ] Error handling works
- [ ] Results are saved properly

### Production Deployment
```bash
# Set production token
export GLOVO_TOKEN="production_token_here"

# Run with production data
python complete_workflow_example.py
```

## Debugging

### Enable Debug Mode
```bash
export DEBUG=1
python complete_workflow_example.py
```

### Check Logs
```bash
# View detailed logs
tail -f automation.log

# Check error logs
grep "ERROR" automation.log
```

### Test Individual Components
```bash
# Test only authentication
python step_1_authentication/token_service.py

# Test only data processing
python step_2_quota_Config/sheet_to_json.py "your_sheet_url"

# Test only quote creation
python step_2_quota_Config/POST_create_quote_id.py

# Test only order creation
python step_3_send_order_with_quotaID/send_order_with_quote_id.py
```

## Success Criteria

Your testing is successful when:
1. ✅ Authentication works without errors
2. ✅ Data processing converts Excel/Sheets to JSON correctly
3. ✅ Quote creation returns valid quote IDs
4. ✅ Order creation uses quote IDs successfully
5. ✅ Complete workflow runs end-to-end
6. ✅ All results are saved and accessible
7. ✅ Error handling works for invalid data
8. ✅ Rate limiting prevents API throttling

## Next Steps

After successful testing:
1. Prepare your production data
2. Set up monitoring and logging
3. Schedule regular runs if needed
4. Set up alerts for failures
5. Document any customizations made
