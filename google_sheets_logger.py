#!/usr/bin/env python3
"""
google_sheets_logger.py
Order logging system that saves results directly to Google Sheets.
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
import gspread
from google.oauth2.service_account import Credentials

class GoogleSheetsLogger:
    """Class to handle order logging directly to Google Sheets."""
    
    def __init__(self, spreadsheet_url: str, sheet_name: str = "Glovo-Orders-Summary"):
        """
        Initialize the Google Sheets logger.
        
        Args:
            spreadsheet_url: URL of the Google Sheets document
            sheet_name: Name of the sheet to log orders to
        """
        self.spreadsheet_url = spreadsheet_url
        self.sheet_name = sheet_name
        self.order_log = []
        self.spreadsheet_id = self._extract_spreadsheet_id(spreadsheet_url)
        
    def _extract_spreadsheet_id(self, url: str) -> str:
        """Extract spreadsheet ID from Google Sheets URL."""
        import re
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if not match:
            raise ValueError("Could not extract spreadsheet ID from URL")
        return match.group(1)
    
    def _setup_google_sheets_connection(self):
        """Setup connection to Google Sheets using service account."""
        try:
            # Check if service account credentials exist
            credentials_file = "google_sheets_credentials.json"
            
            if not os.path.exists(credentials_file):
                print("⚠️  Google Sheets credentials not found.")
                print("💡 To use Google Sheets logging, you need to:")
                print("   1. Create a Google Cloud Project")
                print("   2. Enable Google Sheets API")
                print("   3. Create a service account")
                print("   4. Download credentials as 'google_sheets_credentials.json'")
                print("   5. Share your spreadsheet with the service account email")
                return None
            
            # Define the scope
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials
            creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
            
            # Authorize and create client
            client = gspread.authorize(creds)
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            
            return spreadsheet
            
        except Exception as e:
            print(f"❌ Google Sheets connection failed: {e}")
            return None
    
    def log_order(self, order_data: Dict[str, Any], quote_data: Dict[str, Any], 
                  client_details: Dict[str, str]) -> Dict[str, Any]:
        """
        Log a single order with all relevant information.
        
        Args:
            order_data: Order response data from Glovo API
            quote_data: Original quote data
            client_details: Client information used for the order
            
        Returns:
            Logged order information
        """
        # Extract information from order response
        order_id = order_data.get('trackingNumber') or order_data.get('orderCode') or 'N/A'
        status = order_data.get('status', {})
        order_state = status.get('state', 'UNKNOWN')
        created_at = status.get('createdAt', datetime.now().isoformat())
        
        # Extract quote information
        quote_info = order_data.get('quote', {})
        quote_id = quote_info.get('quoteId', 'N/A')
        quote_price = quote_info.get('quotePrice', 0)
        currency = quote_info.get('currencyCode', 'N/A')
        
        # Extract delivery information
        delivery_info = order_data.get('address', {})
        delivery_address = delivery_info.get('rawAddress', 'N/A')
        delivery_coordinates = delivery_info.get('coordinates', {})
        delivery_lat = delivery_coordinates.get('latitude', 0)
        delivery_lng = delivery_coordinates.get('longitude', 0)
        
        # Extract pickup information
        pickup_info = order_data.get('pickupDetails', {})
        pickup_address_book_id = pickup_info.get('addressBook', {}).get('id', 'N/A')
        pickup_time = pickup_info.get('pickupTime', 'N/A')
        pickup_order_code = pickup_info.get('pickupOrderCode', 'N/A')
        
        # Extract contact information - prioritize client_details over order_data
        contact_info = order_data.get('contact', {})
        contact_name = client_details.get('name', contact_info.get('name', 'N/A'))
        contact_phone = client_details.get('phone', contact_info.get('phone', 'N/A'))
        contact_email = client_details.get('email', contact_info.get('email', 'N/A'))
        
        # Calculate expected delivery time (if available)
        estimated_delivery = order_data.get('estimatedTimeOfArrival', 'N/A')
        
        # Create log entry
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'order_id': order_id,
            'quote_id': quote_id,
            'order_state': order_state,
            'created_at': created_at,
            'expected_delivery': estimated_delivery,
            'client_name': contact_name,
            'client_phone': contact_phone,
            'client_email': contact_email,
            'pickup_address_book_id': pickup_address_book_id,
            'pickup_time': pickup_time,
            'pickup_order_code': pickup_order_code,
            'delivery_address': delivery_address,
            'delivery_latitude': delivery_lat,
            'delivery_longitude': delivery_lng,
            'quote_price': quote_price,
            'currency': currency,
            'partner_id': order_data.get('partnerId', 'N/A'),
            'city_code': order_data.get('cityCode', 'N/A'),
            'cancellable': order_data.get('cancellable', False)
        }
        
        # Add to log
        self.order_log.append(log_entry)
        
        print(f"📝 Order logged:")
        print(f"   Order ID: {order_id}")
        print(f"   Client: {contact_name}")
        print(f"   Status: {order_state}")
        print(f"   Price: {quote_price} {currency}")
        
        return log_entry
    
    def save_to_google_sheets(self) -> bool:
        """
        Save order log to Google Sheets.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.order_log:
            print("⚠️  No orders to save")
            return False
        
        try:
            # Setup Google Sheets connection
            spreadsheet = self._setup_google_sheets_connection()
            
            if not spreadsheet:
                print("❌ Could not connect to Google Sheets")
                return False
            
            # Get or create the worksheet
            try:
                worksheet = spreadsheet.worksheet(self.sheet_name)
                print(f"✅ Found existing sheet: {self.sheet_name}")
            except gspread.WorksheetNotFound:
                print(f"📝 Creating new sheet: {self.sheet_name}")
                worksheet = spreadsheet.add_worksheet(title=self.sheet_name, rows=1000, cols=20)
            
            # Prepare data for Google Sheets
            if not worksheet.get_all_values():
                # If sheet is empty, add headers
                headers = [
                    'Timestamp', 'Order ID', 'Quote ID', 'Order State', 'Client Name',
                    'Client Phone', 'Client Email', 'Pickup Address Book ID', 'Pickup Time',
                    'Expected Delivery', 'Delivery Address', 'Quote Price', 'Currency',
                    'Pickup Order Code', 'Created At', 'Delivery Latitude', 'Delivery Longitude',
                    'Partner ID', 'City Code', 'Cancellable'
                ]
                worksheet.append_row(headers)
                print(f"✅ Added headers to sheet")
            
            # Add order data
            for order in self.order_log:
                row_data = [
                    order['timestamp'],
                    order['order_id'],
                    order['quote_id'],
                    order['order_state'],
                    order['client_name'],
                    order['client_phone'],
                    order['client_email'],
                    order['pickup_address_book_id'],
                    order['pickup_time'],
                    order['expected_delivery'],
                    order['delivery_address'],
                    order['quote_price'],
                    order['currency'],
                    order['pickup_order_code'],
                    order['created_at'],
                    order['delivery_latitude'],
                    order['delivery_longitude'],
                    order['partner_id'],
                    order['city_code'],
                    order['cancellable']
                ]
                worksheet.append_row(row_data)
            
            print(f"✅ Successfully saved {len(self.order_log)} orders to Google Sheets")
            print(f"📊 Sheet: {self.sheet_name}")
            print(f"🔗 URL: {self.spreadsheet_url}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save to Google Sheets: {e}")
            return False
    
    def get_order_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of logged orders.
        
        Returns:
            Summary statistics
        """
        if not self.order_log:
            return {"total_orders": 0}
        
        df = pd.DataFrame(self.order_log)
        
        summary = {
            "total_orders": len(df),
            "orders_by_status": df['order_state'].value_counts().to_dict(),
            "total_value": df['quote_price'].sum(),
            "currency": df['currency'].iloc[0] if len(df) > 0 else 'N/A',
            "date_range": {
                "earliest": df['timestamp'].min(),
                "latest": df['timestamp'].max()
            },
            "unique_clients": df['client_name'].nunique(),
            "unique_pickup_locations": df['pickup_address_book_id'].nunique()
        }
        
        return summary
    
    def print_summary(self):
        """Print order summary statistics."""
        summary = self.get_order_summary()
        
        print(f"\n📊 Order Summary:")
        print(f"   Total Orders: {summary['total_orders']}")
        print(f"   Total Value: {summary['total_value']} {summary['currency']}")
        print(f"   Unique Clients: {summary['unique_clients']}")
        print(f"   Unique Pickup Locations: {summary['unique_pickup_locations']}")
        
        if summary['orders_by_status']:
            print(f"   Orders by Status:")
            for status, count in summary['orders_by_status'].items():
                print(f"     {status}: {count}")
        
        if summary['date_range']['earliest']:
            print(f"   Date Range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")

def test_google_sheets_logger():
    """Test the Google Sheets logger with sample data."""
    print("🧪 Testing Google Sheets Logger")
    print("=" * 50)
    
    # Your Google Sheets URL
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing&ouid=100766369247091180171&rtpof=true&sd=true"
    
    # Create sample order data
    sample_order_data = {
        "trackingNumber": "100010173030",
        "status": {
            "state": "CREATED",
            "createdAt": "2025-09-06T15:39:34.131323196Z"
        },
        "quote": {
            "quoteId": "aff76702-e284-43ab-8ae2-78d0d605d285",
            "quotePrice": 8.06,
            "currencyCode": "BGN"
        },
        "contact": {
            "name": "Test Client",
            "phone": "+359888123456",
            "email": "test@darivreme.com"
        },
        "pickupDetails": {
            "addressBook": {
                "id": "dd560a2c-f1b5-43b7-81bc-2830595122f9"
            },
            "pickupTime": "2025-09-06T20:15:22Z",
            "pickupOrderCode": "ORD123456"
        },
        "address": {
            "rawAddress": "g.k. Strelbishte, Nishava St 111р 1408, Bulgaria",
            "coordinates": {
                "latitude": 42.673758,
                "longitude": 23.298064
            }
        },
        "partnerId": 67915107,
        "cityCode": "SOF",
        "cancellable": True
    }
    
    sample_quote_data = {
        "quote_id": "aff76702-e284-43ab-8ae2-78d0d605d285",
        "original_row": {
            "pickupAddressBookId": "dd560a2c-f1b5-43b7-81bc-2830595122f9",
            "pickupTimeUtc": "2025-09-06T20:15:22Z",
            "deliveryRawAddress": "g.k. Strelbishte, Nishava St 111р 1408, Bulgaria"
        }
    }
    
    sample_client_details = {
        "name": "Test Client",
        "phone": "+359888123456",
        "email": "test@darivreme.com"
    }
    
    # Test logger
    logger = GoogleSheetsLogger(spreadsheet_url, "Glovo-Orders-Summary")
    
    # Log the order
    log_entry = logger.log_order(sample_order_data, sample_quote_data, sample_client_details)
    
    # Print summary
    logger.print_summary()
    
    # Save to Google Sheets
    success = logger.save_to_google_sheets()
    
    if success:
        print(f"\n✅ Google Sheets logging test completed successfully!")
        return True
    else:
        print(f"\n❌ Google Sheets logging test failed")
        return False

if __name__ == "__main__":
    test_google_sheets_logger()
