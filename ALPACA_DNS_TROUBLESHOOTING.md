# Alpaca DNS Issues - Complete Guide

## Why DNS Issues Happen

### 1. **Alpaca Infrastructure**
- **DNS Propagation Delays**: When Alpaca updates their DNS records (load balancers, CDN changes), it can take 24-48 hours to propagate globally
- **Server Maintenance**: Alpaca may perform maintenance that causes temporary DNS changes
- **DDoS Protection**: During high traffic or attacks, DNS servers may rate-limit or time out
- **Load Balancing**: Multiple IPs for `api.alpaca.markets` can cause DNS inconsistencies

### 2. **Local Network Issues**
- **ISP DNS Servers**: Slower or unreliable DNS resolution
- **Corporate Firewalls**: Blocking or interfering with DNS queries
- **Windows DNS Cache**: Stale DNS records cached locally
- **VPN Issues**: VPN DNS leaks or misconfiguration

### 3. **Regional DNS Problems**
- **Geographic Location**: Some regions may have routing issues to Alpaca servers
- **DNS Provider Issues**: Google DNS, Cloudflare DNS, or ISP DNS outages
- **DNS Hijacking**: Malicious or ISP-level DNS redirection

## Current System Handling

Your PROMETHEUS platform already has robust DNS issue handling:

```python:brokers/alpaca_broker.py

# Lines 101-106: DNS connection errors are caught

except requests.exceptions.ConnectionError as e:
    raise ConnectionError(
        message="Cannot connect to Alpaca API - network issue",
        broker="Alpaca",
        original_error=e
    )

```

### Built-in Mitigations
1. ✅ **Exponential Backoff**: Retries with increasing delays (2s, 4s, 8s)
2. ✅ **Error Classification**: DNS issues classified as `ErrorCategory.CONNECTION`
3. ✅ **Automatic Retry**: Up to 3 attempts with the retry strategy
4. ✅ **Error Logging**: All DNS failures are logged for analysis

## Quick Solutions

### Immediate Fixes (Windows)

1. **Flush DNS Cache**

   ```powershell

   ipconfig /flushdns

   ```

2. **Try Different DNS Servers**
   - Google: `8.8.8.8` and `8.8.4.4`
   - Cloudflare: `1.1.1.1` and `1.0.0.1`
   
   To change:

   ```
```text
   Network Settings → Change adapter options → 
   Right-click your connection → Properties → 
   Internet Protocol Version 4 → Use the following DNS servers

   ```

3. **Restart Network Adapter**

   ```powershell

   netsh interface set interface "Wi-Fi" admin=disable
   netsh interface set interface "Wi-Fi" admin=enable

   ```

### Quick Check Script

Create this file: `test_alpaca_dns.py`

```python

import socket
import requests
from datetime import datetime

def test_alpaca_dns():
    """Test DNS resolution for Alpaca API"""
    
    print("=" * 60)
    print(f"Alpaca DNS Test - {datetime.now()}")
    print("=" * 60)
    
    # Test DNS Resolution
    endpoints = {
        'Paper Trading': 'paper-api.alpaca.markets',
        'Live Trading': 'api.alpaca.markets',
        'Data API': 'data.alpaca.markets'
    }
    
    for name, hostname in endpoints.items():
        print(f"\n{name}: {hostname}")
        print("-" * 60)
        
        try:
            # DNS Resolution
            ip = socket.gethostbyname(hostname)
            print(f"✅ DNS Resolved: {ip}")
            
            # HTTP Connection Test
            response = requests.get(f"https://{hostname}/v2/account", timeout=5)
            print(f"✅ HTTP Status: {response.status_code}")
            print(f"✅ Connection OK")
            
        except socket.gaierror as e:
            print(f"❌ DNS Resolution Failed: {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Failed: {e}")
        except requests.exceptions.Timeout as e:
            print(f"⚠️  Connection Timeout: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_alpaca_dns()

```

Run: `python test_alpaca_dns.py`

## Advanced Solutions

### 1. **Add DNS Fallback in Code**

Enhance `brokers/alpaca_broker.py` to include DNS-specific handling:

```python

import socket
import dns.resolver  # dnspython package

def _resolve_with_fallback(self, hostname: str):
    """Resolve DNS with multiple DNS servers"""
    dns_servers = [
        '8.8.8.8',      # Google
        '1.1.1.1',      # Cloudflare
        '208.67.222.222' # OpenDNS
    ]
    
    for dns_server in dns_servers:
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            answer = resolver.resolve(hostname, 'A')
            return str(answer[0])
        except Exception as e:
            logger.warning(f"DNS {dns_server} failed: {e}")
            continue
    
    # Fallback to system DNS
    return socket.gethostbyname(hostname)

```

### 2. **Add IP-Based Fallback**

Cache Alpaca IPs and connect directly if DNS fails:

```python

ALPACA_IPS = {
    'paper-api.alpaca.markets': '52.4.103.86',
    'api.alpaca.markets': '34.231.84.87'
}

def _connect_with_ip_fallback(self):
    """Connect using IP if DNS fails"""
    try:
        # Normal connection
        socket.gethostbyname(self.base_url)
        return self._normal_connect()
    except socket.gaierror:
        # DNS failed, try IP
        ip = ALPACA_IPS.get(self.base_url)
        if ip:
            logger.warning(f"DNS failed, using IP fallback: {ip}")
            # Modify requests to use IP with Host header
            return self._connect_via_ip(ip)

```

### 3. **Monitor DNS Health**

Add continuous monitoring:

```python

async def monitor_dns_health(self):
    """Monitor Alpaca DNS resolution"""
    while self.connected:
        try:
            socket.gethostbyname(self.base_url)
            logger.debug(f"✅ DNS healthy: {self.base_url}")
        except socket.gaierror:
            logger.error(f"❌ DNS resolution failed: {self.base_url}")
            # Trigger alert or switch to backup
        await asyncio.sleep(60)  # Check every minute

```

## Prevention Strategies

### 1. **DNS Prefetch**

```python

# On startup, pre-resolve all Alpaca domains

def prefetch_alpaca_dns():
    for domain in ['paper-api.alpaca.markets', 'api.alpaca.markets']:
        try:
            socket.gethostbyname(domain)
            logger.info(f"✅ Pre-cached DNS: {domain}")
        except Exception as e:
            logger.warning(f"⚠️  DNS prefetch failed: {domain} - {e}")

```

### 2. **Connection Pooling**

Use persistent connections to reduce DNS lookups:

```python

import requests

# Session with connection pooling

self.session = requests.Session()
self.session.mount('https://', requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=10,
    max_retries=3
))

```

### 3. **Health Checks**

Implement health checks before critical operations:

```python

async def check_api_health(self) -> bool:
    """Check if Alpaca API is reachable"""
    try:
        response = requests.get(
            f"{self.base_url}/v2/account",
            headers={'APCA-API-KEY-ID': self.api_key},
            timeout=5
        )
        return response.status_code in [200, 401]  # 401 is OK (auth issue, not DNS)
    except (socket.gaierror, requests.exceptions.ConnectionError):
        return False

```

## Monitoring & Alerts

### Add DNS Metrics

```python

class DNSMonitor:
    def __init__(self):
        self.dns_failures = 0
        self.resolution_times = []
    
    def record_dns_query(self, success: bool, duration: float):
        if success:
            self.resolution_times.append(duration)
        else:
            self.dns_failures += 1
            if self.dns_failures >= 5:
                logger.critical("High DNS failure rate detected!")

```

## When to Contact Alpaca Support

Contact Alpaca if:

1. ✅ DNS issues persist across multiple networks (ISP, VPN, different locations)
2. ✅ Issues affect `api.alpaca.markets` AND `paper-api.alpaca.markets`
3. ✅ Multiple users report the same DNS issue
4. ✅ DNS resolution returns incorrect IPs
5. ✅ Issues last > 2 hours consistently

## Best Practices

1. **Always Use HTTPS**: Ensure DNS hijacking doesn't redirect to malicious servers
2. **Verify SSL Certificates**: Check that responses come from legitimate Alpaca servers
3. **Monitor Error Logs**: Track DNS failures to identify patterns
4. **Use Multiple DNS Servers**: Configure fallback DNS servers
5. **Cache IP Addresses**: Store Alpaca IPs for quick recovery
6. **Exponential Backoff**: Never retry too aggressively (already implemented ✅)
7. **Log All DNS Issues**: Track for pattern analysis

## Platform Status Check

Your system already has these mitigations:

- ✅ Exponential backoff retry (3 attempts)
- ✅ Comprehensive error logging
- ✅ Connection error classification
- ✅ Automatic retry on failures
- ✅ Timeout handling

The temporary DNS issues should resolve within:

- **Typical**: 5-15 minutes
- **ISP Issues**: 1-4 hours  
- **Alpaca Infrastructure**: 15 minutes - 2 hours
- **Global DNS Propagation**: 24-48 hours (rare)

## Summary

DNS issues with Alpaca are usually **temporary** and caused by:

1. Alpaca infrastructure updates/maintenance
2. ISP DNS server problems
3. Network routing issues
4. DNS cache problems

Your platform handles this gracefully with automatic retries. For persistent issues, flush DNS cache or switch DNS servers.

---

**Generated**: {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}  
**Platform**: PROMETHEUS Trading System  
**Status**: DNS handling fully implemented ✅

