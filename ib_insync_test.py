#!/usr/bin/env python
"""Test IB connection using ib_insync library"""
import asyncio
from ib_insync import IB, util

print("="*65)
print("🔬 IB_INSYNC CONNECTION TEST")
print("="*65)

async def test_connection():
    ib = IB()
    
    # Try different configurations
    configs = [
        (4002, 0, "Gateway Live, Client 0"),
        (4002, 1, "Gateway Live, Client 1"),
        (4002, 99, "Gateway Live, Client 99"),
    ]
    
    for port, client_id, desc in configs:
        print(f"\n📡 Testing: {desc}")
        try:
            await ib.connectAsync(
                host='127.0.0.1',
                port=port,
                clientId=client_id,
                timeout=10,
                readonly=False
            )
            
            if ib.isConnected():
                print(f"  ✅ CONNECTED!")
                
                # Get account info
                print("\n💰 Account Summary:")
                accounts = ib.managedAccounts()
                print(f"  Accounts: {accounts}")
                
                # Request account values
                ib.reqAccountSummary()
                await asyncio.sleep(2)
                
                summary = ib.accountSummary()
                for item in summary:
                    if item.tag in ['NetLiquidation', 'TotalCashValue', 'BuyingPower']:
                        print(f"  {item.tag}: ${float(item.value):,.2f}")
                
                # Get positions
                print("\n📈 Positions:")
                positions = ib.positions()
                if positions:
                    for pos in positions:
                        print(f"  • {pos.contract.symbol}: {pos.position} @ ${pos.avgCost:.2f}")
                else:
                    print("  No positions")
                
                ib.disconnect()
                return True
                
        except asyncio.TimeoutError:
            print(f"  ⏰ Timeout after 10s")
        except ConnectionRefusedError:
            print(f"  ❌ Connection refused")
        except Exception as e:
            print(f"  ❌ Error: {type(e).__name__}: {e}")
        
        if ib.isConnected():
            ib.disconnect()
    
    return False

def main():
    util.startLoop()
    
    success = asyncio.get_event_loop().run_until_complete(test_connection())
    
    print("\n" + "="*65)
    if success:
        print("✅ IB CONNECTION SUCCESSFUL!")
    else:
        print("❌ ALL CONNECTION ATTEMPTS FAILED")
        print()
        print("Troubleshooting:")
        print("1. Multiple IB Gateway instances detected - try closing extras")
        print("2. Check API is enabled in IB Gateway settings")
        print("3. Restart IB Gateway after changing settings")
        print("4. Check Windows Firewall isn't blocking connections")
    print("="*65)

if __name__ == "__main__":
    main()

