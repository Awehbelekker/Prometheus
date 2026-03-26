#!/usr/bin/env python3
"""
PROMETHEUS Portfolio Rebalancer
================================
Liquidates idle stablecoins and deploys cash into high-conviction positions
based on regime-aware allocation targets.

Usage:
    python rebalance_portfolio.py              # Dry run (show plan)
    python rebalance_portfolio.py --execute    # Execute liquidations + buys
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Stablecoins — always safe to liquidate (pegged to $1, no alpha)
STABLECOIN_SYMBOLS = {'USDCUSD', 'USDTUSD', 'USDC/USD', 'USDT/USD'}

# Target allocation per asset class (regime-aware defaults for sideways regime)
# These are the high-conviction picks from the watchlist
TARGET_PICKS = [
    # symbol,   weight,  reason
    ('QQQ',     0.20,    'NASDAQ-100 index — tech exposure'),
    ('SPY',     0.15,    'S&P 500 broad market'),
    ('AAPL',    0.10,    'Mega-cap tech leader'),
    ('MSFT',    0.10,    'Enterprise + cloud + AI'),
    ('NVDA',    0.10,    'AI semiconductor dominance'),
    ('BTC/USD', 0.10,    'Digital gold — 24/7 crypto'),
    ('ETH/USD', 0.05,    'Smart contract platform'),
]


async def get_alpaca_client():
    """Get Alpaca trading client."""
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        # Match the same key lookup order as the live trader
        api_key = (os.getenv('ALPACA_LIVE_KEY') or
                   os.getenv('ALPACA_LIVE_API_KEY') or
                   os.getenv('ALPACA_API_KEY') or
                   os.getenv('APCA_API_KEY_ID') or
                   os.getenv('ALPACA_KEY'))
        api_secret = (os.getenv('ALPACA_LIVE_SECRET') or
                      os.getenv('ALPACA_LIVE_SECRET_KEY') or
                      os.getenv('ALPACA_SECRET_KEY') or
                      os.getenv('APCA_API_SECRET_KEY') or
                      os.getenv('ALPACA_SECRET'))

        from alpaca.trading.client import TradingClient
        
        # Detect paper vs live from key prefix
        is_paper = api_key.startswith('PK') if api_key else True
        client = TradingClient(api_key, api_secret, paper=is_paper)
        logger.info(f"Alpaca client: {'paper' if is_paper else 'LIVE'} (key: {api_key[:4]}...)")
        return client
    except Exception as e:
        logger.error(f"Failed to create Alpaca client: {e}")
        return None


async def get_positions(client):
    """Get all current positions."""
    positions = client.get_all_positions()
    result = {}
    for p in positions:
        result[p.symbol] = {
            'symbol': p.symbol,
            'qty': float(p.qty),
            'market_value': float(p.market_value),
            'avg_entry': float(p.avg_entry_price),
            'current_price': float(p.current_price),
            'unrealized_pl': float(p.unrealized_pl),
            'unrealized_plpc': float(p.unrealized_plpc),
        }
    return result


async def get_account(client):
    """Get account details."""
    acct = client.get_account()
    return {
        'equity': float(acct.equity),
        'cash': float(acct.cash),
        'buying_power': float(acct.buying_power),
    }


def build_rebalance_plan(positions: dict, account: dict):
    """Build rebalance plan: liquidate stablecoins, deploy into targets."""
    plan = {'liquidate': [], 'buy': [], 'keep': []}
    
    # 1. Find stablecoins to liquidate
    freed_cash = 0
    for sym, pos in positions.items():
        if sym in STABLECOIN_SYMBOLS:
            plan['liquidate'].append({
                'symbol': sym,
                'qty': pos['qty'],
                'value': pos['market_value'],
                'reason': 'Stablecoin — no alpha, freeing capital',
            })
            freed_cash += pos['market_value']
        else:
            plan['keep'].append(pos)
    
    # 2. Calculate deployable capital
    total_deployable = account['cash'] + freed_cash
    
    # Reserve $5 as buffer to avoid margin issues
    reserve = 5.0
    deployable = max(0, total_deployable - reserve)
    
    plan['freed_cash'] = freed_cash
    plan['total_deployable'] = total_deployable
    plan['deployable_after_reserve'] = deployable
    
    # 3. Build buy orders based on target weights
    # Normalize weights for the picks we'll actually buy
    # Skip picks we already hold enough of
    existing_values = {pos['symbol']: pos['market_value'] for pos in plan['keep']}
    equity = account['equity']
    
    buys = []
    total_weight = 0
    for symbol, weight, reason in TARGET_PICKS:
        # Normalize symbol for comparison
        alpaca_sym = symbol.replace('/', '')
        current_value = existing_values.get(alpaca_sym, 0)
        target_value = equity * weight
        
        # Only buy if we need more exposure
        needed = target_value - current_value
        if needed > 2.0:  # Minimum $2 to avoid dust orders
            buys.append({
                'symbol': symbol,
                'target_weight': weight,
                'target_value': target_value,
                'current_value': current_value,
                'needed': needed,
                'reason': reason,
            })
            total_weight += weight
    
    # Allocate deployable cash proportionally to needs
    total_needed = sum(b['needed'] for b in buys)
    for b in buys:
        if total_needed > 0:
            allocation = min(b['needed'], deployable * (b['needed'] / total_needed))
        else:
            allocation = 0
        b['allocation'] = round(allocation, 2)
        if b['allocation'] >= 1.0:
            plan['buy'].append(b)
    
    return plan


def print_plan(plan: dict, account: dict, positions: dict):
    """Print the rebalance plan."""
    print("\n" + "=" * 70)
    print("  PROMETHEUS PORTFOLIO REBALANCER")
    print("=" * 70)
    
    print(f"\n  Account Equity:  ${account['equity']:>10.2f}")
    print(f"  Cash:            ${account['cash']:>10.2f}")
    print(f"  Buying Power:    ${account['buying_power']:>10.2f}")
    
    # Current positions
    print(f"\n  CURRENT POSITIONS ({len(positions)}):")
    print(f"  {'Symbol':<12} {'Value':>10} {'P/L':>10} {'Status':<20}")
    print(f"  {'-'*55}")
    for sym, pos in positions.items():
        status = "STABLECOIN (idle)" if sym in STABLECOIN_SYMBOLS else "Active"
        print(f"  {sym:<12} ${pos['market_value']:>9.2f} ${pos['unrealized_pl']:>9.2f} {status}")
    
    # Liquidations
    if plan['liquidate']:
        print(f"\n  LIQUIDATE ({len(plan['liquidate'])} stablecoins):")
        for liq in plan['liquidate']:
            print(f"    SELL {liq['qty']:.4f} {liq['symbol']:<12} (${liq['value']:.2f}) - {liq['reason']}")
        print(f"    Total freed: ${plan['freed_cash']:.2f}")
    
    # Deployable
    print(f"\n  DEPLOYABLE CAPITAL:")
    print(f"    Existing cash:   ${plan['total_deployable'] - plan['freed_cash']:.2f}")
    print(f"    From stablecoins: ${plan['freed_cash']:.2f}")
    print(f"    Reserve:          $5.00")
    print(f"    Total to deploy:  ${plan['deployable_after_reserve']:.2f}")
    
    # Buy orders
    if plan['buy']:
        print(f"\n  BUY ORDERS ({len(plan['buy'])}):")
        print(f"  {'Symbol':<12} {'Allocate':>10} {'Target%':>9} {'Current':>10} {'Reason':<30}")
        print(f"  {'-'*75}")
        for b in plan['buy']:
            print(f"  {b['symbol']:<12} ${b['allocation']:>9.2f} {b['target_weight']*100:>7.0f}% ${b['current_value']:>9.2f} {b['reason']}")
        total_allocated = sum(b['allocation'] for b in plan['buy'])
        print(f"  {'TOTAL':<12} ${total_allocated:>9.2f}")
    else:
        print(f"\n  No buy orders needed (all positions at target)")
    
    return plan


async def execute_plan(client, plan: dict, dry_run: bool = True):
    """Execute the rebalance plan."""
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    
    if dry_run:
        print(f"\n  DRY RUN — no orders submitted. Use --execute to trade.")
        return
    
    print(f"\n  EXECUTING REBALANCE PLAN...")
    
    # Step 1: Liquidate stablecoins
    for liq in plan['liquidate']:
        try:
            symbol = liq['symbol']
            qty = liq['qty']
            
            order = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC,
            )
            result = client.submit_order(order)
            print(f"    SOLD {qty:.4f} {symbol} — Order ID: {result.id}")
            logger.info(f"Liquidated {qty} {symbol}")
        except Exception as e:
            print(f"    FAILED to sell {symbol}: {e}")
            logger.error(f"Liquidation failed for {symbol}: {e}")
    
    # Wait for liquidations to settle
    if plan['liquidate']:
        print(f"    Waiting 3s for settlement...")
        await asyncio.sleep(3)
    
    # Step 2: Execute buy orders
    for b in plan['buy']:
        try:
            symbol = b['symbol']
            amount = b['allocation']
            
            if amount < 1.0:
                print(f"    SKIP {symbol} — allocation too small (${amount:.2f})")
                continue
            
            order = MarketOrderRequest(
                symbol=symbol,
                notional=round(amount, 2),
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC if '/' in symbol else TimeInForce.DAY,
            )
            result = client.submit_order(order)
            print(f"    BOUGHT ${amount:.2f} of {symbol} — Order ID: {result.id}")
            logger.info(f"Bought ${amount:.2f} of {symbol}")
        except Exception as e:
            print(f"    FAILED to buy {symbol}: {e}")
            logger.error(f"Buy failed for {symbol}: {e}")
    
    print(f"\n  Rebalance complete.")


async def main():
    dry_run = '--execute' not in sys.argv
    
    client = await get_alpaca_client()
    if not client:
        print("Failed to connect to Alpaca. Check API keys.")
        return
    
    account = await get_account(client)
    positions = await get_positions(client)
    plan = build_rebalance_plan(positions, account)
    print_plan(plan, account, positions)
    await execute_plan(client, plan, dry_run=dry_run)


if __name__ == '__main__':
    asyncio.run(main())
