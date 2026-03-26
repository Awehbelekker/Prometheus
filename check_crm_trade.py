from ib_insync import IB
import time

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=105)
time.sleep(1)

fills = ib.fills()
crm_fills = [f for f in fills if f.contract.symbol == 'CRM']

if crm_fills:
    f = crm_fills[-1]
    entry_price = f.execution.avgPrice
    qty = f.execution.shares
    comm = f.commissionReport.commission if f.commissionReport else 0.0
    
    print("\n" + "="*60)
    print("CRM TRADE PROFIT ANALYSIS")
    print("="*60)
    print(f"\nTrade Execution:")
    print(f"  Time: {f.time}")
    print(f"  Entry Price: ${entry_price:.2f}")
    print(f"  Quantity: {qty} shares")
    print(f"  Commission: ${comm:.2f}")
    print(f"  Total Cost: ${(entry_price * qty + comm):.2f}")
    
    print(f"\nPROFIT TARGETS:")
    print(f"  +5% Target:  ${(entry_price * 1.05):.2f} = ${(entry_price * 0.05 * qty):.2f} profit")
    print(f"  +10% Target: ${(entry_price * 1.10):.2f} = ${(entry_price * 0.10 * qty):.2f} profit")
    print(f"  +15% Target: ${(entry_price * 1.15):.2f} = ${(entry_price * 0.15 * qty):.2f} profit")
    
    print(f"\nRISK MANAGEMENT:")
    print(f"  Stop Loss (-1.5%): ${(entry_price * 0.985):.2f} = ${(entry_price * -0.015 * qty):.2f} loss")
    print(f"  Emergency Stop (-3%): ${(entry_price * 0.97):.2f} = ${(entry_price * -0.03 * qty):.2f} loss")
    
    print("\n" + "="*60)
else:
    print("No CRM fills found")

ib.disconnect()
