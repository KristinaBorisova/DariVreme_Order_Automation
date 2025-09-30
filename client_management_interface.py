#!/usr/bin/env python3
"""
client_management_interface.py
Client management interface for automated order system.
Provides easy client management and monitoring capabilities.
"""

import os
import sys
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_1_authentication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_2_quota_Config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'step_3_send_order_with_quotaID'))

from sheet_to_json import load_workbook_to_dict

class ClientManagementInterface:
    """Interface for managing clients and monitoring order automation."""
    
    def __init__(self, google_sheets_url: str):
        self.google_sheets_url = google_sheets_url
        self.workbook = None
        self.clients = {}
        self.restaurants = {}
        self.orders = []
        
    def load_data(self):
        """Load all data from Google Sheets."""
        print("📊 Loading data from Google Sheets...")
        self.workbook = load_workbook_to_dict(self.google_sheets_url)
        
        # Load clients
        clients_data = self.workbook.get("Clients", [])
        self.clients = {row["client_id"]: row for row in clients_data}
        
        # Load restaurants
        restaurants_data = self.workbook.get("Restaurants", [])
        self.restaurants = {row["restaurant_id"]: row for row in restaurants_data}
        
        # Load orders
        orders_data = self.workbook.get("Orders", [])
        self.orders = orders_data
        
        print(f"✅ Loaded {len(self.clients)} clients, {len(self.restaurants)} restaurants, {len(self.orders)} orders")
    
    def add_client(self, client_data: Dict[str, Any]) -> bool:
        """Add a new client to the system."""
        try:
            # Validate required fields
            required_fields = [
                "client_id", "client_name", "client_phone", "client_email",
                "delivery_address", "delivery_latitude", "delivery_longitude",
                "restaurant_id", "order_frequency", "order_days", "order_time"
            ]
            
            missing_fields = [field for field in required_fields if field not in client_data]
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Validate client_id is unique
            if client_data["client_id"] in self.clients:
                print(f"❌ Client ID {client_data['client_id']} already exists")
                return False
            
            # Validate restaurant exists
            if client_data["restaurant_id"] not in self.restaurants:
                print(f"❌ Restaurant {client_data['restaurant_id']} not found")
                return False
            
            # Set default values
            client_data.setdefault("is_active", True)
            client_data.setdefault("delivery_details", "")
            client_data.setdefault("last_order_date", None)
            client_data.setdefault("next_order_date", None)
            
            # Add to clients
            self.clients[client_data["client_id"]] = client_data
            
            print(f"✅ Client {client_data['client_name']} added successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error adding client: {e}")
            return False
    
    def update_client(self, client_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing client."""
        if client_id not in self.clients:
            print(f"❌ Client {client_id} not found")
            return False
        
        try:
            # Update client data
            self.clients[client_id].update(updates)
            print(f"✅ Client {client_id} updated successfully")
            return True
        except Exception as e:
            print(f"❌ Error updating client: {e}")
            return False
    
    def deactivate_client(self, client_id: str) -> bool:
        """Deactivate a client (stop automated orders)."""
        return self.update_client(client_id, {"is_active": False})
    
    def activate_client(self, client_id: str) -> bool:
        """Activate a client (resume automated orders)."""
        return self.update_client(client_id, {"is_active": True})
    
    def get_client_orders(self, client_id: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get orders for a specific client."""
        if client_id not in self.clients:
            print(f"❌ Client {client_id} not found")
            return []
        
        cutoff_date = (date.today() - timedelta(days=days_back)).isoformat()
        
        client_orders = [
            order for order in self.orders
            if order.get("client_id") == client_id and order.get("order_date", "") >= cutoff_date
        ]
        
        return sorted(client_orders, key=lambda x: x.get("order_date", ""), reverse=True)
    
    def get_client_summary(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive summary for a client."""
        if client_id not in self.clients:
            return {"error": "Client not found"}
        
        client = self.clients[client_id]
        orders = self.get_client_orders(client_id, 30)
        
        # Calculate statistics
        total_orders = len(orders)
        successful_orders = len([o for o in orders if o.get("order_status") in ["CONFIRMED", "IN_PROGRESS", "DELIVERED"]])
        pending_orders = len([o for o in orders if o.get("order_status") == "PENDING"])
        failed_orders = len([o for o in orders if o.get("order_status") == "FAILED"])
        
        # Get recent orders
        recent_orders = orders[:5]  # Last 5 orders
        
        return {
            "client_info": client,
            "statistics": {
                "total_orders_30d": total_orders,
                "successful_orders": successful_orders,
                "pending_orders": pending_orders,
                "failed_orders": failed_orders,
                "success_rate": (successful_orders / total_orders * 100) if total_orders > 0 else 0
            },
            "recent_orders": recent_orders
        }
    
    def list_clients(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all clients with basic information."""
        clients_list = []
        
        for client_id, client in self.clients.items():
            if active_only and not client.get("is_active", True):
                continue
            
            # Get recent order count
            recent_orders = self.get_client_orders(client_id, 7)  # Last 7 days
            
            clients_list.append({
                "client_id": client_id,
                "client_name": client.get("client_name", "Unknown"),
                "client_email": client.get("client_email", "Unknown"),
                "restaurant_name": self.restaurants.get(client.get("restaurant_id", ""), {}).get("restaurant_name", "Unknown"),
                "order_frequency": client.get("order_frequency", "Unknown"),
                "is_active": client.get("is_active", True),
                "recent_orders_7d": len(recent_orders),
                "last_order_date": client.get("last_order_date"),
                "next_order_date": client.get("next_order_date")
            })
        
        return sorted(clients_list, key=lambda x: x["client_name"])
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get system-wide overview and statistics."""
        active_clients = len([c for c in self.clients.values() if c.get("is_active", True)])
        total_clients = len(self.clients)
        
        # Get orders from last 30 days
        cutoff_date = (date.today() - timedelta(days=30)).isoformat()
        recent_orders = [o for o in self.orders if o.get("order_date", "") >= cutoff_date]
        
        total_orders = len(recent_orders)
        successful_orders = len([o for o in recent_orders if o.get("order_status") in ["CONFIRMED", "IN_PROGRESS", "DELIVERED"]])
        pending_orders = len([o for o in recent_orders if o.get("order_status") == "PENDING"])
        failed_orders = len([o for o in recent_orders if o.get("order_status") == "FAILED"])
        
        # Get orders by status
        orders_by_status = {}
        for order in recent_orders:
            status = order.get("order_status", "UNKNOWN")
            orders_by_status[status] = orders_by_status.get(status, 0) + 1
        
        return {
            "clients": {
                "total": total_clients,
                "active": active_clients,
                "inactive": total_clients - active_clients
            },
            "orders_30d": {
                "total": total_orders,
                "successful": successful_orders,
                "pending": pending_orders,
                "failed": failed_orders,
                "success_rate": (successful_orders / total_orders * 100) if total_orders > 0 else 0
            },
            "orders_by_status": orders_by_status,
            "restaurants": {
                "total": len(self.restaurants),
                "active": len([r for r in self.restaurants.values() if r.get("is_active", True)])
            }
        }
    
    def print_client_list(self, active_only: bool = True):
        """Print a formatted list of clients."""
        clients = self.list_clients(active_only)
        
        print(f"\n📋 {'ACTIVE' if active_only else 'ALL'} CLIENTS")
        print("="*80)
        print(f"{'Name':<20} {'Email':<25} {'Restaurant':<15} {'Frequency':<12} {'Orders 7d':<10} {'Status':<8}")
        print("-"*80)
        
        for client in clients:
            status = "✅ Active" if client["is_active"] else "❌ Inactive"
            print(f"{client['client_name']:<20} {client['client_email']:<25} {client['restaurant_name']:<15} {client['order_frequency']:<12} {client['recent_orders_7d']:<10} {status:<8}")
    
    def print_client_summary(self, client_id: str):
        """Print detailed summary for a specific client."""
        summary = self.get_client_summary(client_id)
        
        if "error" in summary:
            print(f"❌ {summary['error']}")
            return
        
        client = summary["client_info"]
        stats = summary["statistics"]
        recent_orders = summary["recent_orders"]
        
        print(f"\n👤 CLIENT SUMMARY: {client['client_name']}")
        print("="*60)
        print(f"📧 Email: {client['client_email']}")
        print(f"📞 Phone: {client['client_phone']}")
        print(f"🏠 Address: {client['delivery_address']}")
        print(f"🍽️  Restaurant: {self.restaurants.get(client['restaurant_id'], {}).get('restaurant_name', 'Unknown')}")
        print(f"📅 Frequency: {client['order_frequency']}")
        print(f"📆 Days: {client['order_days']}")
        print(f"⏰ Time: {client['order_time']}")
        print(f"🔄 Status: {'✅ Active' if client.get('is_active', True) else '❌ Inactive'}")
        
        print(f"\n📊 STATISTICS (Last 30 days)")
        print("-"*30)
        print(f"Total orders: {stats['total_orders_30d']}")
        print(f"Successful: {stats['successful_orders']}")
        print(f"Pending: {stats['pending_orders']}")
        print(f"Failed: {stats['failed_orders']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        
        if recent_orders:
            print(f"\n📋 RECENT ORDERS")
            print("-"*30)
            for order in recent_orders:
                status_emoji = {
                    "PENDING": "⏳",
                    "CONFIRMED": "✅",
                    "IN_PROGRESS": "🚚",
                    "DELIVERED": "🎉",
                    "FAILED": "❌"
                }.get(order.get("order_status", ""), "❓")
                
                print(f"{status_emoji} {order.get('order_date', 'Unknown')} - {order.get('order_id', 'Unknown')} ({order.get('order_status', 'Unknown')})")
    
    def print_system_overview(self):
        """Print system-wide overview."""
        overview = self.get_system_overview()
        
        print(f"\n🏢 SYSTEM OVERVIEW")
        print("="*50)
        print(f"👥 Clients: {overview['clients']['active']}/{overview['clients']['total']} active")
        print(f"🍽️  Restaurants: {overview['restaurants']['active']}/{overview['restaurants']['total']} active")
        print(f"📦 Orders (30d): {overview['orders_30d']['total']}")
        print(f"✅ Success rate: {overview['orders_30d']['success_rate']:.1f}%")
        
        if overview['orders_by_status']:
            print(f"\n📊 Orders by Status:")
            for status, count in overview['orders_by_status'].items():
                print(f"   {status}: {count}")

def main():
    """Main client management interface."""
    print("👥 Glovo Client Management Interface")
    print("="*50)
    
    # Configuration
    GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
    
    # Initialize interface
    interface = ClientManagementInterface(GOOGLE_SHEETS_URL)
    
    try:
        # Load data
        interface.load_data()
        
        # Print system overview
        interface.print_system_overview()
        
        # Print client list
        interface.print_client_list(active_only=True)
        
        # Example: Get detailed summary for first client
        clients = interface.list_clients(active_only=True)
        if clients:
            first_client_id = clients[0]["client_id"]
            interface.print_client_summary(first_client_id)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
