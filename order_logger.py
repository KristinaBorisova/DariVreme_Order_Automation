#!/usr/bin/env python3
"""
order_logger.py
Order logging system to track order results in Excel format.
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

class OrderLogger:
    """Class to handle order logging and Excel file management."""
    
    def __init__(self, excel_file_path: str = None):
        """
        Initialize the order logger.
        
        Args:
            excel_file_path: Path to Excel file to log orders (optional)
        """
        self.excel_file_path = excel_file_path
        self.order_log = []
        
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
    
    def save_to_excel(self, output_file: str = None) -> str:
        """
        Save order log to Excel file.
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            Path to saved file
        """
        if not self.order_log:
            print("⚠️  No orders to save")
            return None
        
        # Use provided file or create default
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"order_results_{timestamp}.xlsx"
        
        # Create DataFrame
        df = pd.DataFrame(self.order_log)
        
        # Reorder columns for better readability
        column_order = [
            'timestamp',
            'order_id',
            'quote_id',
            'order_state',
            'client_name',
            'client_phone',
            'client_email',
            'pickup_address_book_id',
            'pickup_time',
            'expected_delivery',
            'delivery_address',
            'quote_price',
            'currency',
            'pickup_order_code',
            'created_at',
            'delivery_latitude',
            'delivery_longitude',
            'partner_id',
            'city_code',
            'cancellable'
        ]
        
        # Reorder columns (only include columns that exist)
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # Save to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Order Results', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Order Results']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ Order log saved to: {output_file}")
        print(f"📊 Total orders logged: {len(self.order_log)}")
        
        return output_file
    
    def append_to_existing_excel(self, excel_file_path: str, sheet_name: str = 'Order Results') -> str:
        """
        Append orders to an existing Excel file.
        
        Args:
            excel_file_path: Path to existing Excel file
            sheet_name: Name of the sheet to append to
            
        Returns:
            Path to updated file
        """
        if not self.order_log:
            print("⚠️  No orders to append")
            return excel_file_path
        
        try:
            # Read existing file if it exists
            if os.path.exists(excel_file_path):
                existing_df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
                print(f"📖 Found existing Excel file with {len(existing_df)} orders")
            else:
                existing_df = pd.DataFrame()
                print(f"📝 Creating new Excel file")
            
            # Create new DataFrame from current log
            new_df = pd.DataFrame(self.order_log)
            
            # Combine dataframes
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Remove duplicates based on order_id
            combined_df = combined_df.drop_duplicates(subset=['order_id'], keep='last')
            
            # Save combined data
            with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
                combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"✅ Orders appended to: {excel_file_path}")
            print(f"📊 Total orders in file: {len(combined_df)}")
            
            return excel_file_path
            
        except Exception as e:
            print(f"❌ Error appending to Excel file: {e}")
            # Fallback to creating new file
            return self.save_to_excel()
    
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

def test_order_logger():
    """Test the order logger with sample data."""
    print("🧪 Testing Order Logger")
    print("=" * 40)
    
    # Create sample order data
    sample_order_data = {
        "trackingNumber": "100010000000",
        "status": {
            "state": "CREATED",
            "createdAt": "2025-09-06T15:39:34.131323196Z"
        },
        "quote": {
            "quoteId": "12345678-1234-1234-1234-123456789012",
            "quotePrice": 8.06,
            "currencyCode": "BGN"
        },
        "contact": {
            "name": "Test Client",
            "phone": "+1234567890",
            "email": "client@example.com"
        },
        "pickupDetails": {
            "addressBook": {
                "id": "12345678-1234-1234-1234-123456789012"
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
        "partnerId": 12345678,
        "cityCode": "SOF",
        "cancellable": True
    }
    
    sample_quote_data = {
        "quote_id": "12345678-1234-1234-1234-123456789012",
        "original_row": {
            "pickupAddressBookId": "12345678-1234-1234-1234-123456789012",
            "pickupTimeUtc": "2025-09-06T20:15:22Z",
            "deliveryRawAddress": "g.k. Strelbishte, Nishava St 111р 1408, Bulgaria"
        }
    }
    
    sample_client_details = {
        "name": "Test Client",
        "phone": "+1234567890",
        "email": "client@example.com"
    }
    
    # Test logger
    logger = OrderLogger()
    
    # Log the order
    log_entry = logger.log_order(sample_order_data, sample_quote_data, sample_client_details)
    
    # Print summary
    logger.print_summary()
    
    # Save to Excel
    output_file = logger.save_to_excel("test_order_results.xlsx")
    
    print(f"\n✅ Order logger test completed!")
    print(f"📁 Test file saved: {output_file}")

if __name__ == "__main__":
    test_order_logger()
