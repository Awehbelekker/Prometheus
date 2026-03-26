import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(3)
result = s.connect_ex(('127.0.0.1', 4002))
s.close()
if result == 0:
    print("Port 4002: OPEN - IB Gateway is running")
else:
    print(f"Port 4002: CLOSED (code {result}) - IB Gateway NOT running")

# Also check other common IB ports
for port in [4001, 7496, 7497]:
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.settimeout(2)
    r = s2.connect_ex(('127.0.0.1', port))
    s2.close()
    status = "OPEN" if r == 0 else "CLOSED"
    print(f"Port {port}: {status}")
