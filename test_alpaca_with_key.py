"""
Test Alpaca Connection with Your Key
"""
import asyncio
import os

async def test_alpaca_live():
    """Test your Alpaca LIVE API key"""
    print("\n" + "="*70)
    print("TESTING ALPACA CONNECTION")
    print("="*70)
    
    # Your key
    api_key = "AKMMN6U5DXKTM7A2UEAAF4ZQ5Z"
    
    # Need to get secret key from Alpaca dashboard
    print("\n[INFO] To complete the test, you need:")
    print("1. Your API Key: AKMMN6U5DXKTM7A2UEAAF4ZQ5Z ✓ (you provided)")
    print("2. Your Secret Key: (please copy from Alpaca dashboard)")
    print("\nOn the Alpaca page, you should see:")
    print("  - Key: AKMMN6U5DXKTM7A2UEAAF4ZQ5Z")
    print("  - Secret: [Click 'Reveal' to see it]")
    print("\nPaste your secret key here, then press Enter:")
    
    try:
        secret_key = input("Secret Key: ").strip()
        
        if not secret_key:
            print("\n[ERROR] No secret key provided")
            return False
        
        print("\n[INFO] Testing connection...")
        
        from brokers.alpaca_broker import AlpacaBroker
        
        # IMPORTANT: This is LIVE trading endpoint!
        config = {
            'api_key': api_key,
            'secret_key': secret_key,
            'paper_trading': False  # FALSE because your endpoint is LIVE!
        }
        
        broker = AlpacaBroker(config)
        connected = await broker.connect()
        
        if not connected:
            print("[FAILED] Could not connect")
            return False
        
        print("[SUCCESS] Connected to Alpaca LIVE account!")
        
        # Get account info
        account = await broker.get_account()
        
        print("\n" + "="*70)
        print("ACCOUNT INFORMATION (LIVE)")
        print("="*70)
        print(f"Account Status: {account.status}")
        print(f"Equity: ${float(account.equity):,.2f}")
        print(f"Cash: ${float(account.cash):,.2f}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")
        print("="*70)
        
        # Save to .env
        print("\n[INFO] Saving keys to .env file...")
        
        # Read current .env
        env_content = ""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
        
        # Update or add keys
        lines = env_content.split('\n')
        new_lines = []
        found_api = False
        found_secret = False
        
        for line in lines:
            if line.startswith('ALPACA_API_KEY='):
                new_lines.append(f'ALPACA_API_KEY={api_key}')
                found_api = True
            elif line.startswith('ALPACA_SECRET_KEY='):
                new_lines.append(f'ALPACA_SECRET_KEY={secret_key}')
                found_secret = True
            else:
                new_lines.append(line)
        
        if not found_api:
            new_lines.append(f'ALPACA_API_KEY={api_key}')
        if not found_secret:
            new_lines.append(f'ALPACA_SECRET_KEY={secret_key}')
        
        with open('.env', 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("[SUCCESS] Keys saved to .env file!")
        
        print("\n" + "="*70)
        print("⚠️  IMPORTANT WARNING")
        print("="*70)
        print("This is a LIVE TRADING account!")
        print("Any trades will use REAL MONEY!")
        print("\nFor testing, consider:")
        print("1. Use paper trading account first")
        print("2. Start with small amounts ($100-500)")
        print("3. Enable simulation mode first")
        print("="*70)
        
        return True
        
    except KeyboardInterrupt:
        print("\n[CANCELLED] Test cancelled by user")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_alpaca_live())
