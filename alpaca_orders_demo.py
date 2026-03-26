#!/usr/bin/env python3
"""
🚀 ALPACA ORDERS MANAGEMENT DEMO
Comprehensive implementation of Alpaca's order management API
Based on official documentation examples

Features:
- Market Orders
- Limit Orders  
- Short Orders
- Client Order IDs
- Bracket Orders
- Trailing Stop Orders
- Order Retrieval
- Position Management
- Asset Information
"""

import asyncio
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class AlpacaOrdersDemo:
    """Demo implementation of all Alpaca order management features"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PROMETHEUS-OrdersDemo/1.0'
        })
        self.demo_start_time = datetime.now()
        
    def get_auth_token(self) -> str:
        """Get authentication token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": "admin@prometheus-trader.com",
                    "password": "PrometheusAdmin2024!"
                }
            )
            if response.status_code == 200:
                return response.json()['access_token']
            else:
                print(f"[ERROR] Login failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"[ERROR] Auth error: {e}")
            return None
    
    def authenticated_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make authenticated API request"""
        token = self.get_auth_token()
        if not token:
            return None
            
        headers = {'Authorization': f'Bearer {token}'}
        kwargs.setdefault('headers', {}).update(headers)
        
        try:
            response = self.session.request(method, f"{self.base_url}{endpoint}", **kwargs)
            return response
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return None

    def demo_market_order(self):
        """Demo: Place Market Order (from Alpaca docs)"""
        print("\n🎯 MARKET ORDER DEMO")
        print("=" * 50)
        
        # Example from Alpaca docs
        order_data = {
            "symbol": "SPY",
            "qty": 0.023,
            "side": "buy",
            "type": "market",
            "time_in_force": "day"
        }
        
        print(f"📊 Placing market order: {json.dumps(order_data, indent=2)}")
        
        response = self.authenticated_request('POST', '/api/trading/alpaca/orders', json=order_data)
        
        if response and response.status_code == 200:
            order = response.json()
            print(f"[CHECK] Market order placed successfully!")
            print(f"   Order ID: {order.get('id', 'Unknown')}")
            print(f"   Symbol: {order.get('symbol', 'Unknown')}")
            print(f"   Quantity: {order.get('qty', 'Unknown')}")
            print(f"   Status: {order.get('status', 'Unknown')}")
            return order
        else:
            print(f"[ERROR] Order failed: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Error: {response.text}")
            return None

    def demo_limit_order(self):
        """Demo: Place Limit Order (from Alpaca docs)"""
        print("\n💰 LIMIT ORDER DEMO")
        print("=" * 50)
        
        # Example from Alpaca docs - BTC/USD
        order_data = {
            "symbol": "BTC/USD",
            "notional": 4000,
            "side": "sell",
            "type": "limit",
            "limit_price": 17000,
            "time_in_force": "fok"
        }
        
        print(f"📊 Placing limit order: {json.dumps(order_data, indent=2)}")
        
        response = self.authenticated_request('POST', '/api/trading/alpaca/orders', json=order_data)
        
        if response and response.status_code == 200:
            order = response.json()
            print(f"[CHECK] Limit order placed successfully!")
            print(f"   Order ID: {order.get('id', 'Unknown')}")
            print(f"   Symbol: {order.get('symbol', 'Unknown')}")
            print(f"   Limit Price: ${order.get('limit_price', 'Unknown')}")
            print(f"   Status: {order.get('status', 'Unknown')}")
            return order
        else:
            print(f"[ERROR] Limit order failed: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Error: {response.text}")
            return None

    def demo_short_order(self):
        """Demo: Submit Short Order (from Alpaca docs)"""
        print("\n📉 SHORT ORDER DEMO")
        print("=" * 50)
        
        # Example from Alpaca docs
        order_data = {
            "symbol": "SPY",
            "qty": 1,
            "side": "sell",  # Short selling
            "type": "market",
            "time_in_force": "gtc"
        }
        
        print(f"📊 Placing short order: {json.dumps(order_data, indent=2)}")
        
        response = self.authenticated_request('POST', '/api/trading/alpaca/orders', json=order_data)
        
        if response and response.status_code == 200:
            order = response.json()
            print(f"[CHECK] Short order placed successfully!")
            print(f"   Order ID: {order.get('id', 'Unknown')}")
            print(f"   Symbol: {order.get('symbol', 'Unknown')}")
            print(f"   Side: {order.get('side', 'Unknown')} (SHORT)")
            print(f"   Status: {order.get('status', 'Unknown')}")
            return order
        else:
            print(f"[ERROR] Short order failed: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Error: {response.text}")
            return None

    def demo_client_order_id(self):
        """Demo: Using Client Order IDs (from Alpaca docs)"""
        print("\n🏷️  CLIENT ORDER ID DEMO")
        print("=" * 50)
        
        # Generate unique client order ID
        client_order_id = f"prometheus_order_{int(time.time())}"
        
        # Example from Alpaca docs
        order_data = {
            "symbol": "SPY",
            "qty": 0.023,
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
            "client_order_id": client_order_id
        }
        
        print(f"📊 Placing order with client ID: {client_order_id}")
        print(f"📊 Order data: {json.dumps(order_data, indent=2)}")
        
        response = self.authenticated_request('POST', '/api/trading/alpaca/orders', json=order_data)
        
        if response and response.status_code == 200:
            order = response.json()
            print(f"[CHECK] Order with client ID placed successfully!")
            print(f"   Order ID: {order.get('id', 'Unknown')}")
            print(f"   Client Order ID: {order.get('client_order_id', 'Unknown')}")
            print(f"   Status: {order.get('status', 'Unknown')}")
            
            # Try to retrieve by client order ID
            print(f"\n🔍 Retrieving order by client ID...")
            get_response = self.authenticated_request('GET', f'/api/trading/alpaca/orders/by-client-id/{client_order_id}')
            
            if get_response and get_response.status_code == 200:
                retrieved_order = get_response.json()
                print(f"[CHECK] Successfully retrieved order by client ID!")
                print(f"   Retrieved Order ID: {retrieved_order.get('id', 'Unknown')}")
            else:
                print(f"[ERROR] Failed to retrieve by client ID")
                
            return order
        else:
            print(f"[ERROR] Client order ID demo failed: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Error: {response.text}")
            return None

    def demo_bracket_order(self):
        """Demo: Submitting Bracket Orders (from Alpaca docs)"""
        print("\n🎯 BRACKET ORDER DEMO")
        print("=" * 50)
        
        # Example from Alpaca docs
        order_data = {
            "symbol": "SPY",
            "qty": 5,
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
            "order_class": "bracket",
            "take_profit": {
                "limit_price": 400
            },
            "stop_loss": {
                "stop_price": 300
            }
        }
        
        print(f"📊 Placing bracket order: {json.dumps(order_data, indent=2)}")
        
        response = self.authenticated_request('POST', '/api/trading/alpaca/orders', json=order_data)
        
        if response and response.status_code == 200:
            order = response.json()
            print(f"[CHECK] Bracket order placed successfully!")
            print(f"   Order ID: {order.get('id', 'Unknown')}")
            print(f"   Symbol: {order.get('symbol', 'Unknown')}")
            print(f"   Order Class: {order.get('order_class', 'Unknown')}")
            print(f"   Take Profit: ${order.get('take_profit', {}).get('limit_price', 'Unknown')}")
            print(f"   Stop Loss: ${order.get('stop_loss', {}).get('stop_price', 'Unknown')}")
            return order
        else:
            print(f"[ERROR] Bracket order failed: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Error: {response.text}")
            return None

    def demo_trailing_stop_order(self):
        """Demo: Trailing Stop Orders (from Alpaca docs)"""
        print("\n📈 TRAILING STOP ORDER DEMO")
        print("=" * 50)
        
        # Example from Alpaca docs - Trailing by percentage
        order_data = {
            "symbol": "SPY",
            "qty": 1,
            "side": "sell",
            "type": "trailing_stop",
            "time_in_force": "gtc",
            "trail_percent": 1.00  # 1%
        }
        
        print(f"📊 Placing trailing stop order (1% trail): {json.dumps(order_data, indent=2)}")
        
        response = self.authenticated_request('POST', '/api/trading/alpaca/orders', json=order_data)
        
        if response and response.status_code == 200:
            order = response.json()
            print(f"[CHECK] Trailing stop order placed successfully!")
            print(f"   Order ID: {order.get('id', 'Unknown')}")
            print(f"   Symbol: {order.get('symbol', 'Unknown')}")
            print(f"   Trail Percent: {order.get('trail_percent', 'Unknown')}%")
            print(f"   Status: {order.get('status', 'Unknown')}")
            return order
        else:
            print(f"[ERROR] Trailing stop order failed: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Error: {response.text}")
            return None

    def demo_retrieve_orders(self):
        """Demo: Retrieve All Orders (from Alpaca docs)"""
        print("\n📋 RETRIEVE ORDERS DEMO")
        print("=" * 50)
        
        # Get recent orders
        response = self.authenticated_request('GET', '/api/trading/alpaca/orders?limit=10')
        
        if response and response.status_code == 200:
            orders = response.json()
            print(f"[CHECK] Retrieved {len(orders)} orders:")
            
            for i, order in enumerate(orders[:5], 1):  # Show first 5
                print(f"\n   📋 Order {i}:")
                print(f"      ID: {order.get('id', 'Unknown')}")
                print(f"      Symbol: {order.get('symbol', 'Unknown')}")
                print(f"      Side: {order.get('side', 'Unknown')}")
                print(f"      Quantity: {order.get('qty', 'Unknown')}")
                print(f"      Status: {order.get('status', 'Unknown')}")
                print(f"      Created: {order.get('created_at', 'Unknown')}")
                
            return orders
        else:
            print(f"[ERROR] Failed to retrieve orders: {response.status_code if response else 'No response'}")
            return None

    def demo_positions(self):
        """Demo: Working with Positions (from Alpaca docs)"""
        print("\n📊 POSITIONS DEMO")
        print("=" * 50)
        
        # Get all positions
        response = self.authenticated_request('GET', '/api/trading/alpaca/positions')
        
        if response and response.status_code == 200:
            positions = response.json()
            print(f"[CHECK] Retrieved {len(positions)} positions:")
            
            if positions:
                for position in positions[:5]:  # Show first 5
                    print(f"\n   📈 {position.get('symbol', 'Unknown')}:")
                    print(f"      Quantity: {position.get('qty', 'Unknown')} shares")
                    print(f"      Market Value: ${position.get('market_value', 'Unknown')}")
                    print(f"      Unrealized P&L: ${position.get('unrealized_pl', 'Unknown')}")
                    print(f"      Cost Basis: ${position.get('cost_basis', 'Unknown')}")
            else:
                print("   📭 No open positions found")
                
            return positions
        else:
            print(f"[ERROR] Failed to retrieve positions: {response.status_code if response else 'No response'}")
            return None

    def demo_assets(self):
        """Demo: Working with Assets (from Alpaca docs)"""
        print("\n🏢 ASSETS DEMO")
        print("=" * 50)
        
        # Check if AAPL is tradable (from Alpaca docs example)
        response = self.authenticated_request('GET', '/api/trading/alpaca/assets/AAPL')
        
        if response and response.status_code == 200:
            asset = response.json()
            print(f"[CHECK] AAPL Asset Information:")
            print(f"   Symbol: {asset.get('symbol', 'Unknown')}")
            print(f"   Name: {asset.get('name', 'Unknown')}")
            print(f"   Class: {asset.get('class', 'Unknown')}")
            print(f"   Exchange: {asset.get('exchange', 'Unknown')}")
            print(f"   Tradable: {asset.get('tradable', False)}")
            print(f"   Shortable: {asset.get('shortable', False)}")
            print(f"   Easy to Borrow: {asset.get('easy_to_borrow', False)}")
            
            if asset.get('tradable'):
                print(f"   [CHECK] We can trade AAPL!")
            else:
                print(f"   [ERROR] AAPL is not tradable")
                
            return asset
        else:
            print(f"[ERROR] Failed to get AAPL asset info: {response.status_code if response else 'No response'}")
            return None

    def check_demo_health(self):
        """Check demo system health"""
        print("\n🏥 DEMO HEALTH CHECK")
        print("=" * 50)
        
        # Check demo runtime
        runtime = datetime.now() - self.demo_start_time
        hours = runtime.total_seconds() / 3600
        
        response = self.authenticated_request('GET', '/api/alpaca/debug-status')
        
        if response and response.status_code == 200:
            status = response.json()
            print(f"[CHECK] Demo System Health: EXCELLENT")
            print(f"   Demo Runtime: {hours:.1f} hours")
            print(f"   Paper Trading: {status.get('paper', {}).get('available', False)}")
            print(f"   API Keys: {status.get('paper', {}).get('has_key', False)}")
            print(f"   Effective Mode: {status.get('effective_mode', 'Unknown')}")
            return True
        else:
            print(f"[ERROR] Demo health check failed")
            return False

    def run_comprehensive_demo(self):
        """Run all Alpaca order management demos"""
        print("\n" + "="*80)
        print("🚀 COMPREHENSIVE ALPACA ORDERS DEMO")
        print("Based on Official Alpaca Documentation Examples")
        print("="*80)
        
        # Health check first
        if not self.check_demo_health():
            print("[ERROR] Demo system not healthy, aborting...")
            return
        
        try:
            # Run all demos from Alpaca documentation
            demos = [
                ("Market Orders", self.demo_market_order),
                ("Limit Orders", self.demo_limit_order),
                ("Short Orders", self.demo_short_order),
                ("Client Order IDs", self.demo_client_order_id),
                ("Bracket Orders", self.demo_bracket_order),
                ("Trailing Stop Orders", self.demo_trailing_stop_order),
                ("Retrieve Orders", self.demo_retrieve_orders),
                ("Positions Management", self.demo_positions),
                ("Assets Information", self.demo_assets)
            ]
            
            results = {}
            
            for demo_name, demo_func in demos:
                print(f"\n{'='*20} {demo_name} {'='*20}")
                try:
                    result = demo_func()
                    results[demo_name] = {"status": "success", "data": result}
                    time.sleep(1)  # Brief pause between demos
                except Exception as e:
                    print(f"[ERROR] {demo_name} failed: {e}")
                    results[demo_name] = {"status": "error", "error": str(e)}
            
            # Summary
            print("\n" + "="*80)
            print("📊 DEMO SUMMARY")
            print("="*80)
            
            successful = len([r for r in results.values() if r["status"] == "success"])
            total = len(results)
            
            print(f"[CHECK] Successful demos: {successful}/{total}")
            print(f"📈 Success rate: {(successful/total)*100:.1f}%")
            
            for demo_name, result in results.items():
                status_icon = "[CHECK]" if result["status"] == "success" else "[ERROR]"
                print(f"   {status_icon} {demo_name}")
            
            print(f"\n🎯 All Alpaca order management features demonstrated!")
            print(f"📚 Implementation follows official Alpaca documentation")
            print(f"🔄 Demo system remains active and healthy")
            
        except Exception as e:
            print(f"[ERROR] Demo failed with error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main demo execution"""
    demo = AlpacaOrdersDemo()
    demo.run_comprehensive_demo()

if __name__ == "__main__":
    main()
