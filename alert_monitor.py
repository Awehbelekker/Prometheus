"""
PROMETHEUS Automated Alert Monitor
Polls the live trading server and triggers alerts for:
  - System downtime / service degradation
  - Drawdown threshold breaches
  - Account value changes
  - Regime changes (via regime exposure manager)

Sends alerts to console + log file. Can be extended with email/webhook.

Usage:
    python alert_monitor.py                       # Run monitor (default 30s interval)
    python alert_monitor.py --interval 60         # Custom interval in seconds
    python alert_monitor.py --webhook URL         # Send alerts to a webhook
"""

import sys, os, json, time, argparse, logging, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log_file = LOG_DIR / "alert_monitor.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("prometheus_alerts")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE = "http://localhost:8000"

THRESHOLDS = {
    "drawdown_warn_pct": -5.0,       # Warn when account drops >5% from peak
    "drawdown_critical_pct": -10.0,   # Critical at >10%
    "min_buying_power": 5000.0,       # Warn if buying power drops below this
    "max_latency_ms": 2000.0,         # Warn if server latency exceeds this
    "min_uptime_pct": 99.0,           # Warn if calculated uptime drops
}


# ---------------------------------------------------------------------------
# State tracker
# ---------------------------------------------------------------------------
class AlertState:
    def __init__(self):
        self.peak_value = 0.0
        self.last_value = 0.0
        self.last_services = {}
        self.consecutive_failures = 0
        self.alerts_sent = 0
        self.started_at = datetime.now(timezone.utc)
        self.last_alert_times = {}   # alert_key -> timestamp (cooldown)

    def should_alert(self, key: str, cooldown_seconds: int = 300) -> bool:
        """Rate-limit alerts: one per key per cooldown period."""
        now = time.time()
        last = self.last_alert_times.get(key, 0)
        if now - last >= cooldown_seconds:
            self.last_alert_times[key] = now
            return True
        return False


state = AlertState()


# ---------------------------------------------------------------------------
# Alert dispatch
# ---------------------------------------------------------------------------
def send_alert(level: str, title: str, message: str, webhook_url: str = None):
    """Send alert to console, log, and optionally a webhook."""
    icon = {"INFO": "ℹ️", "WARN": "⚠️", "CRITICAL": "🚨"}.get(level, "📢")
    full = f"{icon} [{level}] {title}: {message}"

    if level == "CRITICAL":
        logger.critical(full)
    elif level == "WARN":
        logger.warning(full)
    else:
        logger.info(full)

    state.alerts_sent += 1

    if webhook_url:
        _post_webhook(webhook_url, level, title, message)


def _post_webhook(url: str, level: str, title: str, message: str):
    """POST alert as JSON to a webhook endpoint."""
    payload = json.dumps({
        "level": level,
        "title": title,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "prometheus-alert-monitor",
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        logger.error(f"Webhook delivery failed: {e}")


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def fetch_json(path: str, timeout: int = 10) -> dict | None:
    try:
        req = urllib.request.Request(API_BASE + path)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def check_health(webhook_url: str = None):
    data = fetch_json("/health")
    if data is None:
        state.consecutive_failures += 1
        if state.consecutive_failures >= 2 and state.should_alert("server_down"):
            send_alert("CRITICAL", "Server Down",
                       f"Cannot reach {API_BASE}/health ({state.consecutive_failures} consecutive failures)",
                       webhook_url)
        return

    state.consecutive_failures = 0

    # Latency check
    latency = data.get("latency_ms", {}).get("avg_last_1000", 0)
    if latency > THRESHOLDS["max_latency_ms"] and state.should_alert("high_latency"):
        send_alert("WARN", "High Latency",
                   f"Server avg latency {latency:.0f}ms exceeds {THRESHOLDS['max_latency_ms']}ms",
                   webhook_url)

    # Service checks
    services = data.get("services", {})
    for svc, ok in services.items():
        prev = state.last_services.get(svc)
        if prev is True and ok is False:
            # Service went down
            if state.should_alert(f"svc_down_{svc}"):
                send_alert("CRITICAL", "Service Down",
                           f"Service '{svc}' changed from OK → DOWN", webhook_url)
        elif prev is False and ok is True:
            send_alert("INFO", "Service Recovered",
                       f"Service '{svc}' is back online", webhook_url)
    state.last_services = dict(services)


def check_trading(webhook_url: str = None):
    data = fetch_json("/api/health/trading-system")
    if data is None:
        return

    hc = data.get("health_checks", {})
    alp = hc.get("alpaca_connection", {})

    # Account value tracking
    value = alp.get("account_value", 0)
    if value > 0:
        if value > state.peak_value:
            state.peak_value = value

        if state.peak_value > 0:
            dd_pct = ((value - state.peak_value) / state.peak_value) * 100
            if dd_pct < THRESHOLDS["drawdown_critical_pct"] and state.should_alert("dd_critical"):
                send_alert("CRITICAL", "Drawdown Breach",
                           f"Account {dd_pct:.2f}% from peak (${state.peak_value:,.2f} → ${value:,.2f})",
                           webhook_url)
            elif dd_pct < THRESHOLDS["drawdown_warn_pct"] and state.should_alert("dd_warn", 600):
                send_alert("WARN", "Drawdown Warning",
                           f"Account {dd_pct:.2f}% from peak (${state.peak_value:,.2f} → ${value:,.2f})",
                           webhook_url)

        state.last_value = value

    # Buying power
    bp = alp.get("buying_power", 0)
    if 0 < bp < THRESHOLDS["min_buying_power"] and state.should_alert("low_bp", 1800):
        send_alert("WARN", "Low Buying Power",
                   f"Buying power ${bp:,.2f} below ${THRESHOLDS['min_buying_power']:,.2f}",
                   webhook_url)

    # Trading blocked
    if alp.get("trading_blocked") and state.should_alert("trading_blocked"):
        send_alert("CRITICAL", "Trading Blocked",
                   "Alpaca reports trading is BLOCKED", webhook_url)

    # Summary check — any component not ready?
    summary = data.get("summary", {})
    for key, ok in summary.items():
        if ok is not True and state.should_alert(f"summary_{key}", 600):
            send_alert("WARN", "Component Not Ready",
                       f"{key} = {ok}", webhook_url)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def monitor_loop(interval: int = 30, webhook_url: str = None):
    logger.info(f"PROMETHEUS Alert Monitor started — polling every {interval}s")
    logger.info(f"Thresholds: {json.dumps(THRESHOLDS)}")
    logger.info(f"Webhook: {webhook_url or '(none — console only)'}")
    logger.info(f"Log file: {log_file}")

    # Initial connection test
    data = fetch_json("/health")
    if data:
        logger.info(f"Server reachable — uptime {data.get('uptime_seconds', 0):.0f}s, status {data.get('status')}")
    else:
        logger.warning("Server not reachable on startup — will keep retrying")

    while True:
        try:
            check_health(webhook_url)
            check_trading(webhook_url)
        except Exception as e:
            logger.error(f"Monitor cycle error: {e}")

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="PROMETHEUS Automated Alert Monitor")
    parser.add_argument("--interval", type=int, default=30, help="Poll interval in seconds")
    parser.add_argument("--webhook", type=str, default=None, help="Webhook URL for alerts")
    args = parser.parse_args()

    try:
        monitor_loop(interval=args.interval, webhook_url=args.webhook)
    except KeyboardInterrupt:
        logger.info(f"Monitor stopped. Total alerts sent: {state.alerts_sent}")


if __name__ == "__main__":
    main()
