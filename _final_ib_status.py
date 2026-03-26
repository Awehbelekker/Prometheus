import sqlite3
import socket
import urllib.request
import json

# Broker counts
db = sqlite3.connect('prometheus_learning.db')
cur = db.cursor()
cur.execute('SELECT broker, COUNT(*) FROM trade_history GROUP BY broker')
print('BROKER_COUNTS:', cur.fetchall())
cur.execute("SELECT timestamp, symbol, action, broker FROM trade_history WHERE broker LIKE '%IB%' OR broker='Interactive Brokers' ORDER BY timestamp DESC LIMIT 10")
print('LATEST_IB_TRADES:', cur.fetchall())
db.close()

# IB port health
s = socket.socket()
s.settimeout(2)
code = s.connect_ex(('127.0.0.1', 4002))
s.close()
print('IB_PORT_4002_OPEN:', code == 0, 'code:', code)

# Live trading health
d = json.loads(urllib.request.urlopen('http://localhost:8000/api/live-trading/status', timeout=8).read().decode())
print('LIVE_STATUS:', d)
