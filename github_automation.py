#!/usr/bin/env python3
"""
github_automation.py
Production-ready automation script for GitHub Actions.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_3_send_order_with_quotaID'))

def setup_logging():
    """Setup logging for GitHub Actions."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'glovo_automation.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def load_configuration():
    """Load configuration from environment variables."""
    config = {
        'glovo_client_id': os.getenv('GLOVO_CLIENT_ID'),
        'glovo_client_secret': os.getenv('GLOVO_CLIENT_SECRET'),
        'glovo_api_url': os.getenv('GLOVO_API_URL', 'https://stageapi.glovoapp.com'),
        'google_sheets_url': os.getenv('GOOGLE_SHEETS_URL'),
        'rate_limit_per_sec': float(os.getenv('RATE_LIMIT_PER_SEC', '2.0')),
        'max_orders_per_run': int(os.getenv('MAX_ORDERS_PER_RUN', '50'))
    }
    
    # Validate required configuration
    required_fields = ['glovo_client_id', 'glovo_client_secret', 'google_sheets_url']
    missing_fields = [field for field in required_fields if not config[field]]
    
    if missing_fields:
        raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
    
    return config

def update_authentication_config(config: Dict[str, Any]):
    """Update the authentication configuration with environment variables."""
    try:
        # Update the config.py file with environment variables
        config_path = os.path.join(os.path.dirname(__file__), 'step_1_authentication', 'config.py')
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace the hardcoded values with environment variables
        content = content.replace(
            'API_URL = "https://stageapi.glovoapp.com/oauth/token"',
            f'API_URL = "{config["glovo_api_url"]}/oauth/token"'
        )
        
        # Update token service with environment variables
        token_service_path = os.path.join(os.path.dirname(__file__), 'step_1_authentication', 'token_service.py')
        
        with open(token_service_path, 'r') as f:
            token_content = f.read()
        
        # Replace hardcoded credentials with environment variables
        token_content = token_content.replace(
            '"clientId": "175482686405285",',
            f'"clientId": "{config["glovo_client_id"]}",'
        )
        token_content = token_content.replace(
            '"clientSecret": "dc190e6d0e4f4fc79e4021e4b981e596"',
            f'"clientSecret": "{config["glovo_client_secret"]}"'
        )
        
        with open(token_service_path, 'w') as f:
            f.write(token_content)
        
        logging.info("✅ Authentication configuration updated")
        
    except Exception as e:
        logging.error(f"❌ Failed to update authentication config: {e}")
        raise

def run_automation(config: Dict[str, Any], logger: logging.Logger):
    """Run the complete automation workflow."""
    try:
        logger.info("🚀 Starting Glovo Order Automation")
        logger.info(f"📅 Run started at: {datetime.now().isoformat()}")
        
        # Step 1: Authentication
        logger.info("🔐 Step 1: Authentication")
        from token_service import get_bearer_token
        
        token = get_bearer_token()
        if not token:
            raise Exception("Authentication failed - no token received")
        
        logger.info("✅ Authentication successful")
        
        # Step 2: Load data from Google Sheets
        logger.info("📊 Step 2: Loading data from Google Sheets")
        from sheet_to_json import load_workbook_to_dict
        from POST_create_quote_id import process_orders, iter_orders_from_memory
        
        workbook = load_workbook_to_dict(config['google_sheets_url'])
        sheet_name = list(workbook.keys())[0]
        
        logger.info(f"📋 Loaded {len(workbook[sheet_name])} orders from Google Sheets")
        
        # Limit orders per run to prevent overwhelming the API
        all_rows = list(iter_orders_from_memory(workbook, sheet_name=sheet_name))
        limited_rows = all_rows[:config['max_orders_per_run']]
        
        if len(all_rows) > config['max_orders_per_run']:
            logger.warning(f"⚠️  Limited to {config['max_orders_per_run']} orders per run (total available: {len(all_rows)})")
        
        # Step 3: Create quotes
        logger.info("💰 Step 3: Creating quotes")
        quote_summary = process_orders(limited_rows, rate_limit_per_sec=config['rate_limit_per_sec'])
        
        logger.info(f"Quote creation completed:")
        logger.info(f"   - Total processed: {quote_summary['total']}")
        logger.info(f"   - Successful quotes: {len(quote_summary['successes'])}")
        logger.info(f"   - Failed quotes: {len(quote_summary['failures'])}")
        
        if not quote_summary['successes']:
            logger.warning("⚠️  No successful quotes created")
            return {
                'success': False,
                'message': 'No successful quotes created',
                'quote_summary': quote_summary
            }
        
        # Step 4: Create orders
        logger.info("📦 Step 4: Creating orders with Google Sheets logging")
        from send_order_with_quote_id import (
            extract_quote_ids_from_successes,
            process_orders_from_quotes
        )
        
        quote_data_list = extract_quote_ids_from_successes(quote_summary['successes'])
        
        # Client details are now extracted from Google Sheets data in the quote_data_list
        # No need for hardcoded client details
        
        order_results = process_orders_from_quotes(
            quote_data_list=quote_data_list,
            rate_limit_per_sec=config['rate_limit_per_sec'],
            log_orders=True,
            use_google_sheets=True,
            google_sheets_url=config['google_sheets_url']
        )
        
        logger.info(f"Order creation completed:")
        logger.info(f"   - Total processed: {order_results['total_processed']}")
        logger.info(f"   - Successful orders: {len(order_results['successful_orders'])}")
        logger.info(f"   - Failed orders: {len(order_results['failed_orders'])}")
        logger.info(f"   - Success rate: {order_results['success_rate']:.1f}%")
        
        # Step 5: Save results
        logger.info("💾 Step 5: Saving results")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"automation_results_{timestamp}.json"
        
        final_results = {
            "automation_run": {
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "config": {
                    "max_orders_per_run": config['max_orders_per_run'],
                    "rate_limit_per_sec": config['rate_limit_per_sec']
                }
            },
            "data_source": {
                "google_sheets_url": config['google_sheets_url'],
                "sheet_name": sheet_name,
                "total_orders_available": len(all_rows),
                "orders_processed": len(limited_rows)
            },
            "quote_summary": quote_summary,
            "order_results": order_results
        }
        
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Results saved to: {results_file}")
        
        # Logging information
        if order_results.get('google_sheets_success'):
            logger.info("📊 Orders saved to Google Sheets: 'Glovo-Orders-Summary'")
        elif order_results.get('excel_file'):
            logger.info(f"📊 Orders saved to Excel: {order_results['excel_file']}")
        
        return {
            'success': True,
            'message': f'Automation completed successfully. {len(order_results["successful_orders"])} orders created.',
            'results_file': results_file,
            'final_results': final_results
        }
        
    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'message': f'Automation failed: {str(e)}',
            'error': str(e)
        }

def main():
    """Main function for GitHub Actions automation."""
    logger = setup_logging()
    
    try:
        logger.info("🤖 GitHub Actions Glovo Automation Started")
        
        # Load configuration
        config = load_configuration()
        logger.info("✅ Configuration loaded successfully")
        
        # Update authentication config
        update_authentication_config(config)
        
        # Run automation
        result = run_automation(config, logger)
        
        if result['success']:
            logger.info("🎉 Automation completed successfully!")
            logger.info(f"📊 Summary: {result['message']}")
            sys.exit(0)
        else:
            logger.error("❌ Automation failed!")
            logger.error(f"💥 Error: {result['message']}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
