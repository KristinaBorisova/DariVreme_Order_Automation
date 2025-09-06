# Glovo DariVreme Order Automation

A Python-based automation system for processing orders through the Glovo API. This project automates the workflow from authentication to order processing using Excel/Google Sheets data.

## Project Overview

This automation system consists of three main steps:
1. **Authentication** - Obtain and manage Glovo API access tokens
2. **Quota Configuration** - Process Excel/Google Sheets data and create quote requests
3. **Order Sending** - Send orders with quote IDs to the Glovo API

## Project Structure

```
Glovo_DariVreme_Order_Automation/
├── step_1_authentication/          # Authentication module
│   ├── config.py                   # Configuration settings
│   ├── token_service.py            # Token management service
│   └── 1_glovo_auth_helper.py      # Authentication helper script
├── step_2_quota_Config/            # Data processing and quote creation
│   ├── get_excel_data_to_json_main.py  # Main data processing script
│   ├── POST_create_quote_id.py     # Quote creation API calls
│   └── sheet_to_json.py            # Excel/Google Sheets to JSON converter
├── step_3_send_order_with_quotaID/ # Order sending module
│   ├── send_order_with_quote_id.py     # Main order creation script
│   └── complete_workflow_example.py    # Complete workflow demonstration
└── README.md                       # This documentation
```

---

## Step 1: Authentication Module

### `config.py`
**Purpose**: Central configuration file containing API settings and credentials.

**Structure**:
```python
API_URL = "https://stageapi.glovoapp.com/oauth/token"  # Glovo OAuth endpoint
API_KEY = "your_api_key"                               # API key placeholder
API_SECRET = "your_api_secret"                         # API secret placeholder
Access_Token = []                                      # List to store access tokens
```

**Variables**:
- `API_URL`: The Glovo OAuth token endpoint URL
- `API_KEY`: Placeholder for API key (currently unused)
- `API_SECRET`: Placeholder for API secret (currently unused)
- `Access_Token`: List to store retrieved access tokens

### `token_service.py`
**Purpose**: Advanced token management service with caching, automatic refresh, and error handling.

**Key Features**:
- Token caching to disk (`~/.cache/myapp/token.json`)
- Automatic token refresh when expired
- Environment variable support
- Error handling and validation

**Structure**:
```python
# Configuration
TOKEN_URL = os.getenv("TOKEN_URL", config.API_URL)
CACHE_PATH = pathlib.Path(os.getenv("TOKEN_CACHE_FILE", "~/.cache/myapp/token.json")).expanduser()

# Core Functions
def _read_cache() -> Optional[dict]           # Read cached token
def _write_cache(token: str, expires_in: int) # Write token to cache
def _fetch_new_token() -> str                 # Fetch new token from API
def get_bearer_token(force_refresh: bool = False) -> str  # Main token getter
```

**Variables**:
- `TOKEN_URL`: OAuth endpoint URL (configurable via environment)
- `CACHE_PATH`: Path to token cache file
- `payload`: Authentication payload with client credentials
- `headers`: HTTP headers for API requests

**Authentication Payload**:
```python
{
    "grantType": "client_credentials",
    "clientId": "175482686405285",
    "clientSecret": "dc190e6d0e4f4fc79e4021e4b981e596"
}
```

### `1_glovo_auth_helper.py`
**Purpose**: Simple authentication helper script for basic token retrieval.

**Structure**:
```python
# Direct authentication request
payload = {
    "grantType": "client_credentials",
    "clientId": "175482686405285",
    "clientSecret": "dc190e6d0e4f4fc79e4021e4b981e596"
}
```

**Variables**:
- `payload`: Authentication credentials
- `glovoUrl`: API endpoint from config
- `headers`: Content-Type headers
- `response`: HTTP response object

---

## Step 2: Quota Configuration Module

### `sheet_to_json.py`
**Purpose**: Comprehensive utility for converting Google Sheets or Excel files to JSON format.

**Key Features**:
- Support for Google Sheets URLs and local Excel files
- Multiple output formats (individual sheets + combined workbook)
- Data normalization and sanitization
- Command-line interface

**Structure**:
```python
# Core Functions
def is_google_sheet(url_or_path: str) -> bool                    # Detect Google Sheets
def extract_spreadsheet_id(url: str) -> str                      # Extract sheet ID
def fetch_xlsx_bytes_from_gsheets(url: str) -> bytes             # Download from Google
def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]   # Clean data
def dataframe_to_records(df: pd.DataFrame) -> List[Dict[str, Any]] # Convert to records
def export_workbook_to_json(xlsx_bytes: bytes, outdir: str)      # Export to files
def convert_sheet_to_json(input_source: str, outdir: str)        # Main converter
def load_workbook_to_dict(input_source: str)                     # Load to memory
```

**Variables**:
- `GOOGLE_EXPORT_TPL`: Google Sheets export URL template
- `input_source`: URL or file path to process
- `outdir`: Output directory for JSON files
- `xlsx_bytes`: Raw Excel file data
- `combined`: Dictionary containing all sheet data

**Output Structure**:
```json
{
  "Sheet1": [
    {"column1": "value1", "column2": "value2"},
    {"column1": "value3", "column2": "value4"}
  ],
  "Sheet2": [...]
}
```

### `get_excel_data_to_json_main.py`
**Purpose**: Main script demonstrating how to load and process Excel/Google Sheets data.

**Structure**:
```python
# Example usage
url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing"
data = load_workbook_to_dict(url)
```

**Variables**:
- `url`: Google Sheets URL
- `data`: Dictionary containing all sheet data

### `POST_create_quote_id.py`
**Purpose**: Comprehensive script for creating quote requests from processed data and sending them to the Glovo API.

**Key Features**:
- Data validation for required fields
- Rate limiting for API requests
- Error handling and retry logic
- Support for both in-memory and file-based data sources
- Detailed success/failure reporting

**Structure**:
```python
# Configuration
URL = "https://stageapi.glovoapp.com/v2/laas/quotes"
TOKEN = os.getenv("GLOVO_TOKEN", "YOUR_BEARER_TOKEN_HERE")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Core Functions
def row_to_payload(row: Dict[str, Any]) -> Dict[str, Any]        # Convert row to API payload
def validate_row(row: Dict[str, Any]) -> Optional[str]           # Validate row data
def send_quote(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]  # Send API request
def iter_orders_from_memory(workbook, sheet_name)               # Iterate in-memory data
def iter_orders_from_file(path, sheet_name)                     # Iterate file data
def process_orders(rows, rate_limit_per_sec)                    # Main processing function
```

**Required Data Fields**:
```python
{
    "pickup_address_id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",  # UUID
    "pickup_time_utc": "2024-07-24T14:15:22Z",                    # ISO8601 UTC
    "dest_raw_address": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",  # Full address
    "dest_lat": 41.39637,                                          # Latitude
    "dest_lng": 2.17939,                                           # Longitude
    "dest_details": "Floor 6 Door 3"                               # Optional details
}
```

**API Payload Structure**:
```python
{
    "pickupDetails": {
        "addressBook": {"id": "pickup_address_id"},
        "pickupTime": "2024-07-24T14:15:22Z"
    },
    "deliveryAddress": {
        "rawAddress": "Full delivery address",
        "coordinates": {
            "latitude": 41.39637,
            "longitude": 2.17939
        },
        "details": "Additional delivery details"
    }
}
```

**Variables**:
- `URL`: Glovo quotes API endpoint
- `TOKEN`: Bearer token for authentication
- `HEADERS`: HTTP headers for API requests
- `rate_limit_per_sec`: Rate limiting parameter (default: 5.0)
- `delay`: Calculated delay between requests
- `successes`: List of successful requests
- `failures`: List of failed requests

---

## Step 3: Order Sending Module

### `send_order_with_quote_id.py`
**Purpose**: Complete order creation system that filters quote responses from Step 2 and creates orders using the Glovo API.

**Key Features**:
- Extracts quote IDs from successful quote responses
- Creates orders using the `/v2/laas/quotes/{quoteId}/parcels` endpoint
- Handles client details and pickup order codes
- Rate limiting and error handling
- Comprehensive result tracking and reporting

**Structure**:
```python
# Configuration
ORDER_URL_TEMPLATE = "https://stageapi.glovoapp.com/v2/laas/quotes/{quote_id}/parcels"
TOKEN = os.getenv("GLOVO_TOKEN", "YOUR_BEARER_TOKEN_HERE")

# Core Functions
def extract_quote_ids_from_successes(successes) -> List[Dict[str, Any]]  # Extract quote IDs
def create_order_payload(quote_data, client_details) -> Dict[str, Any]   # Create order payload
def send_order_with_quote_id(quote_id, payload) -> Tuple[bool, Dict]     # Send order request
def process_orders_from_quotes(quote_data_list, client_details)          # Process multiple orders
def load_quote_successes_from_file(file_path) -> List[Dict[str, Any]]    # Load quote results
def save_order_results(results, output_file)                             # Save results
```

**Quote Response Structure** (from Step 2):
```json
{
  "quoteId": "826e5192-f8c6-4e24-aab3-3910e46c52b7",
  "quotePrice": 0,
  "currencyCode": "EUR",
  "distanceInMeters": 1500,
  "createdAt": "2024-01-15T14:15:22Z",
  "expiresAt": "2024-01-15T14:25:22Z",
  "pickupDetails": {
    "addressBook": {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "formattedAddress": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
      "coordinates": {
        "latitude": 41.39637,
        "longitude": 2.17939
      }
    },
    "pickupTime": "2024-01-15T14:15:22Z"
  },
  "deliveryAddress": {
    "rawAddress": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
    "formattedAddress": "Carrer de Casp, 111, L'Eixample, 08013 Barcelona",
    "coordinates": {
      "latitude": 41.39637,
      "longitude": 2.17939
    },
    "details": "Floor 6 Door 3"
  },
  "estimatedTimeOfDelivery": {
    "lowerBound": "PT15M",
    "upperBound": "PT30M"
  }
}
```

**Order Payload Structure**:
```json
{
  "contact": {
    "name": "DariVreme Client",
    "phone": "+1234567890",
    "email": "client@darivreme.com"
  },
  "pickupOrderCode": "ORD1705321234567"
}
```

**Variables**:
- `ORDER_URL_TEMPLATE`: Glovo order creation endpoint template
- `TOKEN`: Bearer token for authentication
- `quote_id`: Extracted from quote response
- `client_details`: Client information dictionary
- `pickup_order_code`: Generated unique order code
- `rate_limit_per_sec`: Rate limiting parameter (default: 2.0)

### `complete_workflow_example.py`
**Purpose**: Comprehensive example demonstrating the complete workflow from quote creation to order placement.

**Key Features**:
- Demonstrates quote response filtering
- Shows complete workflow execution
- Interactive example with user prompts
- Error handling and validation
- Result saving and reporting

**Structure**:
```python
def run_complete_workflow() -> bool                    # Execute complete workflow
def demonstrate_quote_response_filtering()             # Show filtering examples
```

**Workflow Steps**:
1. Authentication validation
2. Quote creation (Step 2)
3. Quote ID extraction and filtering
4. Order creation (Step 3)
5. Result saving and reporting

---

## Usage Workflow

### 1. Authentication
```bash
# Option A: Use the advanced token service
python step_1_authentication/token_service.py

# Option B: Use the simple helper
python step_1_authentication/1_glovo_auth_helper.py
```

### 2. Data Processing
```bash
# Convert Google Sheets to JSON
python step_2_quota_Config/sheet_to_json.py "https://docs.google.com/spreadsheets/d/XXX/edit?usp=sharing" -o json_export

# Process data and create quotes
python step_2_quota_Config/POST_create_quote_id.py
```

### 3. Order Creation
```bash
# Create orders using quote IDs from Step 2
python step_3_send_order_with_quotaID/send_order_with_quote_id.py

# Run complete workflow (all steps)
python step_3_send_order_with_quotaID/complete_workflow_example.py
```

### 4. Environment Variables
```bash
export GLOVO_TOKEN="your_bearer_token_here"
export TOKEN_URL="https://stageapi.glovoapp.com/oauth/token"
export TOKEN_CACHE_FILE="~/.cache/myapp/token.json"
```

## Dependencies

- `requests`: HTTP client for API calls
- `pandas`: Data manipulation and Excel processing
- `pathlib`: File path handling
- `json`: JSON data processing
- `time`: Rate limiting and timing
- `os`: Environment variable access
- `typing`: Type hints for better code documentation

## Data Flow

1. **Authentication**: Obtain bearer token from Glovo OAuth endpoint
2. **Data Source**: Load order data from Excel/Google Sheets
3. **Data Processing**: Convert to JSON format and validate required fields
4. **Quote Creation**: Send validated data to Glovo quotes API
5. **Response Filtering**: Extract quote IDs from successful quote responses
6. **Order Creation**: Use quote IDs to create final orders via `/v2/laas/quotes/{quoteId}/parcels`

## Error Handling

- Token expiration and automatic refresh
- Data validation with detailed error messages
- API rate limiting to prevent throttling
- Comprehensive error logging and reporting
- Graceful handling of network timeouts

## Security Notes

- API credentials are currently hardcoded (should be moved to environment variables)
- Token caching includes expiration handling
- Rate limiting prevents API abuse
- Input validation prevents malformed requests

## Quote Response Filtering Process

Based on the [Glovo API documentation](https://logistics-docs.glovoapp.com/laas-partners/index.html#operation/getToken), here's how to filter responses and create orders:

### 1. Quote Response Structure
When Step 2 creates quotes successfully, each response contains:
```json
{
  "quoteId": "826e5192-f8c6-4e24-aab3-3910e46c52b7",
  "quotePrice": 0,
  "currencyCode": "EUR",
  "expiresAt": "2024-01-15T14:25:22Z",
  // ... other fields
}
```

### 2. Filtering Process
```python
# Extract quote IDs from successful responses
def extract_quote_ids_from_successes(successes):
    quote_data = []
    for success in successes:
        response = success.get("response", {})
        quote_id = response.get("quoteId")
        if quote_id:
            quote_data.append({
                "quote_id": quote_id,
                "original_row": success.get("row", {}),
                "quote_response": response
            })
    return quote_data
```

### 3. Order Creation
```python
# Create order using quote ID
order_payload = {
    "contact": {
        "name": "Client Name",
        "phone": "+1234567890",
        "email": "client@example.com"
    },
    "pickupOrderCode": "ORD123456"
}

# POST to /v2/laas/quotes/{quoteId}/parcels
response = requests.post(
    f"https://stageapi.glovoapp.com/v2/laas/quotes/{quote_id}/parcels",
    headers={"Authorization": f"Bearer {token}"},
    json=order_payload
)
```

## Future Enhancements

- Add comprehensive logging system
- Implement retry logic for failed requests
- Add configuration file support
- Create unit tests for all modules
- Add order status tracking
- Implement webhook handling for order updates