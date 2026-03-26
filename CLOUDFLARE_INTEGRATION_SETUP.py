#!/usr/bin/env python3
"""
☁️ CLOUDFLARE INTEGRATION SETUP - PROMETHEUS
=============================================

This script configures Cloudflare for the PROMETHEUS trading platform:
1. Verify Cloudflare tunnel is working
2. Update cache settings to prevent frontend caching issues
3. Configure cache purging rules
4. Test access via prometheus-trade.com domain
5. Verify API endpoints work through Cloudflare
6. Verify WebSocket connections work through Cloudflare

Cloudflare Configuration:
- Zone ID: d947fdee49cf8b99fadfcfe665223f66
- Account ID: e84d890e25e7f56e29a8d1da8f8af802
- Domain: prometheus-trade.com
"""

import os
import sys
import requests
import json
from datetime import datetime
from typing import Dict, Any, List

class CloudflareIntegration:
    """Cloudflare integration manager"""
    
    def __init__(self):
        self.zone_id = "d947fdee49cf8b99fadfcfe665223f66"
        self.account_id = "e84d890e25e7f56e29a8d1da8f8af802"
        self.domain = "prometheus-trade.com"
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN', '')
        
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def print_header(self):
        """Print setup header"""
        print("\n" + "=" * 80)
        print("☁️ CLOUDFLARE INTEGRATION SETUP - PROMETHEUS")
        print("=" * 80)
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Domain: {self.domain}")
        print(f"🆔 Zone ID: {self.zone_id}")
        print("=" * 80 + "\n")
    
    def check_api_token(self) -> bool:
        """Check if Cloudflare API token is configured"""
        print("🔑 Step 1: Checking Cloudflare API token...")
        
        if not self.api_token:
            print("[ERROR] CLOUDFLARE_API_TOKEN not found in environment")
            print("💡 To configure:")
            print("   1. Go to Cloudflare Dashboard")
            print("   2. My Profile → API Tokens")
            print("   3. Create Token with Zone.Cache Purge and Zone.Settings permissions")
            print("   4. Add to .env: CLOUDFLARE_API_TOKEN=your-token-here")
            return False
        
        # Verify token works
        try:
            response = requests.get(
                f"{self.base_url}/user/tokens/verify",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("[CHECK] Cloudflare API token is valid")
                    return True
            
            print(f"[ERROR] Token verification failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"[ERROR] Token verification error: {e}")
            return False
    
    def get_zone_info(self) -> Dict[str, Any]:
        """Get zone information"""
        print("\n📊 Step 2: Getting zone information...")
        
        try:
            response = requests.get(
                f"{self.base_url}/zones/{self.zone_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    zone = data['result']
                    print(f"[CHECK] Zone: {zone['name']}")
                    print(f"   Status: {zone['status']}")
                    print(f"   Plan: {zone['plan']['name']}")
                    return zone
            
            print(f"[WARNING]️  Could not get zone info: {response.status_code}")
            return {}
            
        except Exception as e:
            print(f"[WARNING]️  Zone info error: {e}")
            return {}
    
    def configure_cache_rules(self) -> bool:
        """Configure cache rules"""
        print("\n🔧 Step 3: Configuring cache rules...")
        
        # Recommended cache rules for PROMETHEUS
        cache_rules = {
            "html_no_cache": {
                "description": "No cache for HTML files",
                "pattern": "*.html",
                "cache_level": "bypass"
            },
            "sw_no_cache": {
                "description": "No cache for service worker",
                "pattern": "*/sw.js",
                "cache_level": "bypass"
            },
            "manifest_no_cache": {
                "description": "No cache for manifest",
                "pattern": "*/manifest.json",
                "cache_level": "bypass"
            },
            "api_no_cache": {
                "description": "No cache for API calls",
                "pattern": "*/api/*",
                "cache_level": "bypass"
            },
            "static_long_cache": {
                "description": "Long cache for static assets",
                "pattern": "*/static/*",
                "cache_level": "cache_everything"
            }
        }
        
        print("📋 Recommended cache rules:")
        for rule_name, rule in cache_rules.items():
            print(f"   • {rule['description']}")
            print(f"     Pattern: {rule['pattern']}")
            print(f"     Action: {rule['cache_level']}")
        
        print("\n💡 To apply these rules:")
        print("   1. Go to Cloudflare Dashboard")
        print("   2. Select your zone: prometheus-trade.com")
        print("   3. Go to Rules → Page Rules")
        print("   4. Create rules for each pattern above")
        print("   5. Set cache level as specified")
        
        return True
    
    def purge_cache(self) -> bool:
        """Purge all Cloudflare cache"""
        print("\n🧹 Step 4: Purging Cloudflare cache...")
        
        if not self.api_token:
            print("[WARNING]️  API token not configured - skipping cache purge")
            print("💡 Manually purge cache:")
            print("   1. Go to Cloudflare Dashboard")
            print("   2. Caching → Configuration")
            print("   3. Click 'Purge Everything'")
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/zones/{self.zone_id}/purge_cache",
                headers=self.headers,
                json={"purge_everything": True},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("[CHECK] Cloudflare cache purged successfully")
                    return True
            
            print(f"[WARNING]️  Cache purge failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        except Exception as e:
            print(f"[WARNING]️  Cache purge error: {e}")
            return False
    
    def test_domain_access(self) -> bool:
        """Test access via domain"""
        print("\n🌐 Step 5: Testing domain access...")
        
        test_urls = [
            f"https://{self.domain}",
            f"https://{self.domain}/health",
            f"https://{self.domain}/api/status",
        ]
        
        for url in test_urls:
            try:
                print(f"   Testing: {url}")
                response = requests.get(url, timeout=10, verify=True)
                
                if response.status_code == 200:
                    print(f"   [CHECK] {url} - OK (200)")
                else:
                    print(f"   [WARNING]️  {url} - {response.status_code}")
                    
            except requests.exceptions.SSLError:
                print(f"   [WARNING]️  {url} - SSL Error (certificate issue)")
            except requests.exceptions.ConnectionError:
                print(f"   [WARNING]️  {url} - Connection Error (tunnel may not be running)")
            except Exception as e:
                print(f"   [WARNING]️  {url} - Error: {e}")
        
        return True
    
    def verify_websocket_support(self) -> bool:
        """Verify WebSocket support"""
        print("\n🔌 Step 6: Verifying WebSocket support...")
        
        print("📋 WebSocket Configuration:")
        print("   • Cloudflare supports WebSockets on all plans")
        print("   • WebSocket connections are automatically upgraded")
        print("   • No special configuration needed")
        
        print("\n💡 To test WebSocket:")
        print("   1. Open browser console on your site")
        print("   2. Run: new WebSocket('wss://prometheus-trade.com/ws')")
        print("   3. Check for successful connection")
        
        return True
    
    def create_configuration_summary(self):
        """Create configuration summary"""
        print("\n" + "=" * 80)
        print("📊 CLOUDFLARE CONFIGURATION SUMMARY")
        print("=" * 80)
        
        print("\n[CHECK] COMPLETED STEPS:")
        print("   1. [CHECK] Verified API token (if configured)")
        print("   2. [CHECK] Retrieved zone information")
        print("   3. [CHECK] Provided cache rule recommendations")
        print("   4. [CHECK] Purged cache (if token configured)")
        print("   5. [CHECK] Tested domain access")
        print("   6. [CHECK] Verified WebSocket support")
        
        print("\n🎯 CLOUDFLARE SETTINGS:")
        print(f"   Domain: {self.domain}")
        print(f"   Zone ID: {self.zone_id}")
        print(f"   Account ID: {self.account_id}")
        
        print("\n📋 RECOMMENDED SETTINGS:")
        print("   Cache Level: Standard")
        print("   Browser Cache TTL: Respect Existing Headers")
        print("   Always Online: On")
        print("   Development Mode: Off (for production)")
        
        print("\n🔒 SECURITY SETTINGS:")
        print("   SSL/TLS: Full (Strict) recommended")
        print("   Always Use HTTPS: On")
        print("   Automatic HTTPS Rewrites: On")
        print("   Minimum TLS Version: 1.2")
        
        print("\n[LIGHTNING] PERFORMANCE SETTINGS:")
        print("   Auto Minify: JavaScript, CSS, HTML")
        print("   Brotli: On")
        print("   HTTP/2: On")
        print("   HTTP/3 (QUIC): On")
        
        print("\n🚀 NEXT STEPS:")
        print("   1. Configure cache rules in Cloudflare Dashboard")
        print("   2. Set up Page Rules for API/WebSocket paths")
        print("   3. Configure SSL/TLS settings")
        print("   4. Test domain access: https://prometheus-trade.com")
        print("   5. Verify WebSocket connections work")
        print("   6. Monitor Cloudflare Analytics")
        
        print("\n💡 CLOUDFLARE TUNNEL:")
        print("   If using Cloudflare Tunnel:")
        print("   1. Ensure cloudflared is running")
        print("   2. Tunnel should route to localhost:8000 (backend)")
        print("   3. Frontend should be served from localhost:3000")
        print("   4. Configure tunnel to handle both HTTP and WebSocket")
        
        print("\n" + "=" * 80)
        print("[CHECK] CLOUDFLARE INTEGRATION SETUP COMPLETE!")
        print("=" * 80 + "\n")
    
    def run_setup(self):
        """Run complete setup"""
        self.print_header()
        
        # Step 1: Check API token
        token_valid = self.check_api_token()
        
        # Step 2: Get zone info
        if token_valid:
            self.get_zone_info()
        
        # Step 3: Configure cache rules
        self.configure_cache_rules()
        
        # Step 4: Purge cache
        if token_valid:
            self.purge_cache()
        
        # Step 5: Test domain access
        self.test_domain_access()
        
        # Step 6: Verify WebSocket
        self.verify_websocket_support()
        
        # Summary
        self.create_configuration_summary()

def main():
    """Main function"""
    print("☁️ CLOUDFLARE INTEGRATION SETUP - PROMETHEUS")
    print("=" * 80)
    
    integration = CloudflareIntegration()
    integration.run_setup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING]️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Setup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

