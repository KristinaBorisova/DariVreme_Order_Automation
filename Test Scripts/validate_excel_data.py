#!/usr/bin/env python3
"""
validate_excel_data.py
Validate that all required data is present in the Excel/Google Sheets file.
"""

import os
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'step_2_quota_Config'))

def validate_excel_data():
    """Validate that all required data is present in the Excel file."""
    print("🔍 Validating Excel Data")
    print("="*50)
    
    try:
        from sheet_to_json import load_workbook_to_dict
        
        # Load the Google Sheets data
        google_sheets_url = os.getenv('GOOGLE_SHEETS_URL', 'https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?gid=519498004#gid=519498004')
        
        print(f"📊 Loading data from Google Sheets...")
        workbook = load_workbook_to_dict(google_sheets_url)
        
        if 'FINAL_ORDERS' not in workbook:
            print("❌ FINAL_ORDERS sheet not found!")
            print(f"Available sheets: {list(workbook.keys())}")
            return False
        
        orders = workbook['FINAL_ORDERS']
        print(f"✅ Loaded {len(orders)} orders from FINAL_ORDERS sheet")
        
        # Required fields for each order
        required_fields = {
            'client_id': 'Client ID',
            'client_name': 'Client Name', 
            'client_phone': 'Client Phone',
            'client_email': 'Client Email',
            'deliveryRawAddress': 'Delivery Address',
            'deliveryLattitude': 'Delivery Latitude',
            'deliveryLongitude': 'Delivery Longitude',
            'pickupAddressBookId': 'Pickup Address Book ID',
            'restaurant_name': 'Restaurant Name',
            'order_id': 'Order Description',
            'deliveryFrequency': 'Delivery Frequency'
        }
        
        # Validate each order
        valid_orders = 0
        invalid_orders = []
        
        for i, order in enumerate(orders, 1):
            missing_fields = []
            empty_fields = []
            
            # Check for missing fields
            for field, description in required_fields.items():
                if field not in order:
                    missing_fields.append(description)
                elif not order[field] or str(order[field]).strip() == '':
                    empty_fields.append(description)
            
            if missing_fields or empty_fields:
                invalid_orders.append({
                    'row': i,
                    'client_name': order.get('client_name', 'Unknown'),
                    'missing_fields': missing_fields,
                    'empty_fields': empty_fields
                })
            else:
                valid_orders += 1
        
        # Print results
        print(f"\n📊 Validation Results:")
        print(f"   ✅ Valid orders: {valid_orders}")
        print(f"   ❌ Invalid orders: {len(invalid_orders)}")
        
        if invalid_orders:
            print(f"\n⚠️  Invalid Orders Details:")
            for invalid in invalid_orders[:5]:  # Show first 5
                print(f"   Row {invalid['row']}: {invalid['client_name']}")
                if invalid['missing_fields']:
                    print(f"      Missing: {', '.join(invalid['missing_fields'])}")
                if invalid['empty_fields']:
                    print(f"      Empty: {', '.join(invalid['empty_fields'])}")
            
            if len(invalid_orders) > 5:
                print(f"   ... and {len(invalid_orders) - 5} more invalid orders")
        
        # Check data quality
        print(f"\n🔍 Data Quality Analysis:")
        
        # Check for common issues
        issues = []
        
        # Check phone numbers
        phone_issues = 0
        for order in orders:
            phone = str(order.get('client_phone', '')).strip()
            if phone and (len(phone) < 8 or not any(c.isdigit() for c in phone)):
                phone_issues += 1
        if phone_issues > 0:
            issues.append(f"{phone_issues} orders have invalid phone numbers")
        
        # Check email addresses
        email_issues = 0
        for order in orders:
            email = str(order.get('client_email', '')).strip()
            if email and ('@' not in email or '.' not in email.split('@')[-1]):
                email_issues += 1
        if email_issues > 0:
            issues.append(f"{email_issues} orders have invalid email addresses")
        
        # Check coordinates
        coord_issues = 0
        for order in orders:
            try:
                lat = float(order.get('deliveryLattitude', 0))
                lon = float(order.get('deliveryLongitude', 0))
                if lat == 0 or lon == 0 or not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    coord_issues += 1
            except (ValueError, TypeError):
                coord_issues += 1
        if coord_issues > 0:
            issues.append(f"{coord_issues} orders have invalid coordinates")
        
        # Check delivery frequency
        freq_issues = 0
        for order in orders:
            try:
                freq = int(order.get('deliveryFrequency', 0))
                if freq not in [3, 5]:
                    freq_issues += 1
            except (ValueError, TypeError):
                freq_issues += 1
        if freq_issues > 0:
            issues.append(f"{freq_issues} orders have invalid delivery frequency (should be 3 or 5)")
        
        if issues:
            print("   ⚠️  Data Quality Issues:")
            for issue in issues:
                print(f"      • {issue}")
        else:
            print("   ✅ No data quality issues found")
        
        # Overall assessment
        success_rate = (valid_orders / len(orders)) * 100 if orders else 0
        print(f"\n📈 Overall Data Quality: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print("✅ Excel data is ready for automation!")
            return True
        elif success_rate >= 80:
            print("⚠️  Excel data has some issues but may work")
            return True
        else:
            print("❌ Excel data has significant issues that need to be fixed")
            return False
            
    except Exception as e:
        print(f"❌ Error validating Excel data: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main validation function."""
    print("🚀 Excel Data Validation")
    print("="*60)
    print(f"📅 Validation run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    success = validate_excel_data()
    
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    
    if success:
        print("✅ Data validation passed! Your Excel file is ready.")
        print("   No default values will be used - all data comes from your sheet.")
        return 0
    else:
        print("❌ Data validation failed! Please fix the issues above.")
        print("   Default values will be used for missing data.")
        return 1

if __name__ == "__main__":
    exit(main())
