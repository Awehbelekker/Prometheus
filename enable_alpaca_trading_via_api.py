"""
Enable Alpaca Trading via API
Directly updates the account configuration to enable trading
"""

import os
import requests
import json

print("=" * 80)
print("🔧 ENABLE ALPACA TRADING VIA API")
print("=" * 80)
print()

api_key = os.getenv('ALPACA_LIVE_KEY', 'AKNGMUQPQGCFKRMTM5QG')
api_secret = os.getenv('ALPACA_LIVE_SECRET', '7dNZf4igDG89MBp9dAzd7IabiAxsCIMEvgaCH0Pb')
base_url = 'https://api.alpaca.markets'

headers = {
    'APCA-API-KEY-ID': api_key,
    'APCA-API-SECRET-KEY': api_secret,
    'Content-Type': 'application/json'
}

# Get current configuration
print("📊 CURRENT CONFIGURATION:")
config_url = f"{base_url}/v2/account/configurations"
response = requests.get(config_url, headers=headers)

if response.status_code == 200:
    current_config = response.json()
    print(json.dumps(current_config, indent=2))
    print()
    print(f"   suspend_trade: {current_config.get('suspend_trade')}")
    print()
else:
    print(f"[ERROR] Failed to get configuration: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

# Update configuration to enable trading
print("🔄 UPDATING CONFIGURATION TO ENABLE TRADING...")
print()

new_config = {
    "suspend_trade": False,  # Enable trading
    "dtbp_check": current_config.get("dtbp_check", "entry"),
    "fractional_trading": current_config.get("fractional_trading", True),
    "no_shorting": current_config.get("no_shorting", False),
    "pdt_check": current_config.get("pdt_check", "entry"),
    "trade_confirm_email": current_config.get("trade_confirm_email", "all")
}

print("📝 NEW CONFIGURATION:")
print(json.dumps(new_config, indent=2))
print()

# Send PATCH request to update configuration
response = requests.patch(config_url, headers=headers, json=new_config)

if response.status_code == 200:
    updated_config = response.json()
    print("[CHECK] CONFIGURATION UPDATED SUCCESSFULLY!")
    print()
    print("📊 UPDATED CONFIGURATION:")
    print(json.dumps(updated_config, indent=2))
    print()
    
    if updated_config.get('suspend_trade') == False:
        print("=" * 80)
        print("🎉 SUCCESS! TRADING IS NOW ENABLED!")
        print("=" * 80)
        print()
        print("[CHECK] suspend_trade: False")
        print("[CHECK] Alpaca trading is now active")
        print()
        print("NEXT STEPS:")
        print("1. Wait 30 seconds for changes to propagate")
        print("2. Run: python FINAL_TRADING_VERIFICATION_TEST.py")
        print("3. Verify: 'Trade Suspended by User: False'")
        print("4. Restart PROMETHEUS for full trading")
        print()
    else:
        print("[WARNING]️ WARNING: suspend_trade is still True")
        print("   The update may not have taken effect")
        print("   Contact Alpaca support for assistance")
else:
    print(f"[ERROR] FAILED TO UPDATE CONFIGURATION")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text}")
    print()
    print("POSSIBLE REASONS:")
    print("1. API permissions - keys may not have configuration access")
    print("2. Account restrictions - may need manual approval")
    print("3. Compliance hold - contact Alpaca support")
    print()
    print("SOLUTION:")
    print("Contact Alpaca support to manually enable trading")
    print("Email: support@alpaca.markets")
    print("Account: 910544927")

print()
print("=" * 80)

