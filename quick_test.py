import asyncio
import aiohttp
import json

async def test_trading_analysis():
    async with aiohttp.ClientSession() as session:
        data = {
            'symbol': 'AAPL', 
            'market_data': {'current_price': 150.25}, 
            'analysis_type': 'sentiment'
        }
        async with session.post('http://localhost:5000/trading-analysis', json=data) as resp:
            print('Status:', resp.status)
            if resp.status == 200:
                result = await resp.json()
                print('Response:', json.dumps(result, indent=2))
            else:
                print('Error:', await resp.text())

asyncio.run(test_trading_analysis())
