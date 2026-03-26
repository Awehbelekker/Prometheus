#!/usr/bin/env python3
"""
Cloudflare DNS Configuration Script for PROMETHEUS Trading Platform
Automatically configures all required DNS records for the trading platform.
"""

import os
import requests
import json
from typing import Dict, List, Optional

class CloudflareDNSManager:
    def __init__(self, zone_id: str, account_id: str, api_token: str):
        self.zone_id = zone_id
        self.account_id = account_id
        self.api_token = api_token
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def get_tunnel_cname_target(self) -> str:
        """Get the CNAME target for Cloudflare tunnel"""
        tunnel_id = "5ad70171-4c9d-4cd0-8c83-93031bb10484"
        return f"{tunnel_id}.cfargotunnel.com"
    
    def list_dns_records(self) -> List[Dict]:
        """List all DNS records in the zone"""
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()["result"]
        else:
            print(f"[ERROR] Failed to list DNS records: {response.text}")
            return []
    
    def create_dns_record(self, record_type: str, name: str, content: str, 
                         proxied: bool = True, ttl: int = 1) -> bool:
        """Create a DNS record"""
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records"
        
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "proxied": proxied,
            "ttl": ttl
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print(f"[CHECK] Created {record_type} record: {name} -> {content}")
            return True
        else:
            print(f"[ERROR] Failed to create {record_type} record {name}: {response.text}")
            return False
    
    def update_dns_record(self, record_id: str, record_type: str, name: str, 
                         content: str, proxied: bool = True, ttl: int = 1) -> bool:
        """Update an existing DNS record"""
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}"
        
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "proxied": proxied,
            "ttl": ttl
        }
        
        response = requests.put(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print(f"[CHECK] Updated {record_type} record: {name} -> {content}")
            return True
        else:
            print(f"[ERROR] Failed to update {record_type} record {name}: {response.text}")
            return False
    
    def setup_prometheus_dns(self) -> bool:
        """Set up all required DNS records for PROMETHEUS Trading Platform"""
        print("🚀 Setting up PROMETHEUS Trading Platform DNS records...")
        
        # Get tunnel CNAME target
        tunnel_target = self.get_tunnel_cname_target()
        print(f"🔗 Tunnel target: {tunnel_target}")
        
        # Required DNS records
        dns_records = [
            # Main domain (root)
            {"type": "CNAME", "name": "prometheus-trade.com", "content": tunnel_target, "proxied": True},
            
            # Application subdomains
            {"type": "CNAME", "name": "app", "content": tunnel_target, "proxied": True},
            {"type": "CNAME", "name": "api", "content": tunnel_target, "proxied": True},
            {"type": "CNAME", "name": "ws", "content": tunnel_target, "proxied": True},
            {"type": "CNAME", "name": "admin", "content": tunnel_target, "proxied": True},
            {"type": "CNAME", "name": "trade", "content": tunnel_target, "proxied": True},
            {"type": "CNAME", "name": "docs", "content": tunnel_target, "proxied": True},
            
            # Additional utility subdomains
            {"type": "CNAME", "name": "www", "content": tunnel_target, "proxied": True},
            {"type": "CNAME", "name": "dashboard", "content": tunnel_target, "proxied": True},
            {"type": "CNAME", "name": "portal", "content": tunnel_target, "proxied": True},
        ]
        
        # Get existing records
        existing_records = self.list_dns_records()
        existing_names = {record["name"]: record for record in existing_records}
        
        success_count = 0
        total_count = len(dns_records)
        
        for record in dns_records:
            record_name = record["name"]
            full_name = record_name if record_name.endswith(".com") else f"{record_name}.prometheus-trade.com"
            
            if full_name in existing_names:
                # Update existing record
                existing_record = existing_names[full_name]
                if (existing_record["content"] != record["content"] or 
                    existing_record["proxied"] != record["proxied"]):
                    
                    if self.update_dns_record(
                        existing_record["id"],
                        record["type"],
                        record_name,
                        record["content"],
                        record["proxied"]
                    ):
                        success_count += 1
                else:
                    print(f"[CHECK] DNS record already correct: {full_name}")
                    success_count += 1
            else:
                # Create new record
                if self.create_dns_record(
                    record["type"],
                    record_name,
                    record["content"],
                    record["proxied"]
                ):
                    success_count += 1
        
        print(f"\n📊 DNS Setup Summary:")
        print(f"   [CHECK] Successful: {success_count}/{total_count}")
        print(f"   [ERROR] Failed: {total_count - success_count}/{total_count}")
        
        if success_count == total_count:
            print("\n🎉 All DNS records configured successfully!")
            print("\n🌐 Your PROMETHEUS Trading Platform is now accessible at:")
            print("   • https://prometheus-trade.com (Main Platform)")
            print("   • https://app.prometheus-trade.com (Application)")
            print("   • https://api.prometheus-trade.com (API Backend)")
            print("   • https://admin.prometheus-trade.com (Admin Dashboard)")
            print("   • https://trade.prometheus-trade.com (Trading Interface)")
            print("   • https://docs.prometheus-trade.com (Documentation)")
            return True
        else:
            print(f"\n[WARNING]️ Some DNS records failed to configure. Please check manually.")
            return False

def main():
    """Main function to set up Cloudflare DNS"""
    print("🔧 PROMETHEUS Trading Platform - Cloudflare DNS Setup")
    print("=" * 60)
    
    # Load configuration from environment or prompt
    zone_id = os.getenv("CLOUDFLARE_ZONE_ID", "d947fdee49cf8b99fadfcfe665223f66")
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "e84d890e25e7f56e29a8d1da8f8af802")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    
    if not api_token:
        print("[ERROR] CLOUDFLARE_API_TOKEN environment variable is required")
        print("   Please set it with a token that has Zone:Edit permissions")
        return False
    
    # Initialize DNS manager
    dns_manager = CloudflareDNSManager(zone_id, account_id, api_token)
    
    # Set up DNS records
    success = dns_manager.setup_prometheus_dns()
    
    if success:
        print("\n[CHECK] DNS configuration completed successfully!")
        print("🚀 Your PROMETHEUS Trading Platform should be accessible within a few minutes.")
    else:
        print("\n[ERROR] DNS configuration encountered some issues.")
        print("   Please check the Cloudflare dashboard manually.")
    
    return success

if __name__ == "__main__":
    main()
