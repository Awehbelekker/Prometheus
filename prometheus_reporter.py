"""
PROMETHEUS WhatsApp Reporter
Daily + weekly trading reports sent via WhatsApp (CallMeBot — free).

SETUP (one-time, 2 minutes):
  1. On your phone, save +34 644 82 70 96 as a WhatsApp contact
  2. Send this exact message to that contact:
       I allow callmebot to send me messages
  3. You will receive your API key — copy it
  4. Add to .env:  CALLMEBOT_API_KEY=your_key_here

Usage:
  python prometheus_reporter.py            # send today's daily report
  python prometheus_reporter.py --weekly   # send full weekly breakdown
  python prometheus_reporter.py --test     # send a test ping
  python prometheus_reporter.py --alert "System restarted"  # custom alert
"""

import os
import sys
import sqlite3
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
DB_PATH = ROOT / "prometheus_learning.db"

WHATSAPP_NUMBER = os.environ.get("CALLMEBOT_PHONE", "+27645755210")
CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY", "")  # set in .env after setup
CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"

STARTING_CAPITAL = float(os.environ.get("STARTING_CAPITAL", "211.0"))


# ── WhatsApp sender ───────────────────────────────────────────────────────────

def send_whatsapp(message: str) -> bool:
    if not CALLMEBOT_API_KEY:
        print("[REPORTER] CALLMEBOT_API_KEY not set in .env — cannot send WhatsApp.")
        print("[REPORTER] Message that would have been sent:")
        print(message)
        return False
    try:
        encoded = urllib.parse.quote(message)
        url = f"{CALLMEBOT_URL}?phone={WHATSAPP_NUMBER}&text={encoded}&apikey={CALLMEBOT_API_KEY}"
        req = urllib.request.urlopen(url, timeout=15)
        status = req.getcode()
        if status == 200:
            print(f"[REPORTER] WhatsApp sent ✅ ({len(message)} chars)")
            return True
        else:
            print(f"[REPORTER] WhatsApp returned HTTP {status}")
            return False
    except Exception as e:
        print(f"[REPORTER] WhatsApp send failed: {e}")
        return False


# ── DB helpers ────────────────────────────────────────────────────────────────

def _db():
    return sqlite3.connect(str(DB_PATH))


def get_todays_trades():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*),
               SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END),
               SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END),
               ROUND(SUM(profit_loss), 2),
               ROUND(AVG(profit_loss), 2)
        FROM trade_history
        WHERE date(timestamp) = ? AND profit_loss != 0
    """, (today,))
    row = cur.fetchone()
    conn.close()
    return {
        "trades": row[0] or 0,
        "wins": row[1] or 0,
        "losses": row[2] or 0,
        "pnl": row[3] or 0.0,
        "avg_pnl": row[4] or 0.0,
    }


def get_weekly_trades():
    monday = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    conn = _db()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*),
               SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END),
               ROUND(SUM(profit_loss), 2),
               ROUND(AVG(profit_loss), 2),
               ROUND(MAX(profit_loss), 2),
               ROUND(MIN(profit_loss), 2)
        FROM trade_history
        WHERE date(timestamp) >= ? AND profit_loss != 0
    """, (monday,))
    row = cur.fetchone()

    # Best and worst trade symbols
    cur.execute("""
        SELECT symbol, ROUND(profit_loss, 2)
        FROM trade_history
        WHERE date(timestamp) >= ? AND profit_loss != 0
        ORDER BY profit_loss DESC LIMIT 1
    """, (monday,))
    best = cur.fetchone()

    cur.execute("""
        SELECT symbol, ROUND(profit_loss, 2)
        FROM trade_history
        WHERE date(timestamp) >= ? AND profit_loss != 0
        ORDER BY profit_loss ASC LIMIT 1
    """, (monday,))
    worst = cur.fetchone()

    # Per asset class
    cur.execute("""
        SELECT
            CASE WHEN symbol LIKE '%USD%' OR symbol LIKE '%BTC%' OR symbol LIKE '%-USD'
                 THEN 'Crypto' ELSE 'Equity' END as cls,
            COUNT(*),
            SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END),
            ROUND(SUM(profit_loss), 2)
        FROM trade_history
        WHERE date(timestamp) >= ? AND profit_loss != 0
        GROUP BY cls
    """, (monday,))
    by_class = {r[0]: {"trades": r[1], "wins": r[2], "pnl": r[3]} for r in cur.fetchall()}

    conn.close()
    wins = row[1] or 0
    trades = row[0] or 0
    return {
        "trades": trades,
        "wins": wins,
        "losses": trades - wins,
        "pnl": row[2] or 0.0,
        "avg_pnl": row[3] or 0.0,
        "best_pnl": row[4] or 0.0,
        "worst_pnl": row[5] or 0.0,
        "best_symbol": best[0] if best else "N/A",
        "worst_symbol": worst[0] if worst else "N/A",
        "by_class": by_class,
    }


def get_cumulative_stats():
    conn = _db()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*),
               SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END),
               ROUND(SUM(profit_loss), 2)
        FROM trade_history WHERE profit_loss != 0
    """)
    row = cur.fetchone()

    # 30-day win rate trend
    four_weeks = []
    for w in range(4):
        end = (datetime.now() - timedelta(weeks=w)).strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(weeks=w+1)).strftime("%Y-%m-%d")
        cur.execute("""
            SELECT COUNT(*), SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END)
            FROM trade_history
            WHERE date(timestamp) BETWEEN ? AND ? AND profit_loss != 0
        """, (start, end))
        r = cur.fetchone()
        t, w_count = r[0] or 0, r[1] or 0
        four_weeks.append(round(w_count / t * 100, 1) if t > 0 else None)

    # Top performing AI systems
    cur.execute("""
        SELECT ai_system, ROUND(win_rate*100,1), ROUND(avg_pnl,2), total_signals
        FROM ai_system_metrics
        WHERE date = (SELECT MAX(date) FROM ai_system_metrics)
        ORDER BY win_rate DESC LIMIT 3
    """)
    top_ai = cur.fetchall()

    # Guardian blocks today
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT COUNT(*), protection_layer
        FROM guardian_blocks
        WHERE date(timestamp) = ?
        GROUP BY protection_layer ORDER BY COUNT(*) DESC LIMIT 1
    """, (today,))
    blocks = cur.fetchone()

    # Latest equity
    cur.execute("""
        SELECT current_equity, daily_pnl, drawdown_pct
        FROM guardian_state ORDER BY id DESC LIMIT 1
    """)
    gs = cur.fetchone()

    conn.close()
    total = row[0] or 0
    wins = row[1] or 0
    return {
        "total_trades": total,
        "total_wins": wins,
        "total_pnl": row[2] or 0.0,
        "overall_wr": round(wins / total * 100, 1) if total > 0 else 0,
        "weekly_wr_trend": list(reversed(four_weeks)),  # oldest → newest
        "top_ai": top_ai,
        "blocks_today": blocks[0] if blocks else 0,
        "blocks_layer": blocks[1] if blocks else None,
        "current_equity": gs[0] if gs else 0.0,
        "daily_pnl": gs[1] if gs else 0.0,
        "drawdown_pct": gs[2] if gs else 0.0,
    }


def get_benchmark_returns(days=7):
    """Fetch SPY, QQQ, BTC weekly returns via yfinance."""
    try:
        import yfinance as yf
        results = {}
        start = (datetime.now() - timedelta(days=days+2)).strftime("%Y-%m-%d")
        for sym in ["SPY", "QQQ", "BTC-USD"]:
            try:
                hist = yf.Ticker(sym).history(start=start, auto_adjust=True)
                if len(hist) >= 2:
                    ret = (hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100
                    results[sym] = round(ret, 1)
            except Exception:
                pass
        return results
    except ImportError:
        return {}


# ── Report generators ─────────────────────────────────────────────────────────

def build_daily_report() -> str:
    today = get_todays_trades()
    stats = get_cumulative_stats()
    wr = round(today["wins"] / today["trades"] * 100) if today["trades"] > 0 else 0
    equity = stats["current_equity"] or STARTING_CAPITAL
    ret_pct = round((equity - STARTING_CAPITAL) / STARTING_CAPITAL * 100, 1)

    # System uptime
    uptime_str = _get_uptime()

    # Alerts
    alerts = []
    if stats["drawdown_pct"] and stats["drawdown_pct"] > 10:
        alerts.append(f"Drawdown {stats['drawdown_pct']:.1f}%")
    if stats["blocks_today"] > 10:
        alerts.append(f"{stats['blocks_today']} trades blocked (Layer {stats['blocks_layer']})")

    alert_line = "Alerts: " + " | ".join(alerts) if alerts else "No alerts"

    pnl_sign = "+" if today["pnl"] >= 0 else ""
    day_wr = f"{wr}% WR" if today["trades"] > 0 else "No trades"

    lines = [
        f"PROMETHEUS Daily | {datetime.now().strftime('%b %d')}",
        f"Capital: ${equity:.0f} ({ret_pct:+.1f}% all-time)",
        f"Today: {today['trades']} trades | {today['wins']}W {today['losses']}L | PnL: {pnl_sign}${today['pnl']:.2f}",
        f"Win Rate (overall): {stats['overall_wr']}% ({stats['total_trades']} trades)",
        f"System: {uptime_str}",
        alert_line,
    ]

    # Add 4-week win rate trend if we have data
    trend = [f"{x}%" if x else "--" for x in stats["weekly_wr_trend"]]
    if any(x != "--" for x in trend):
        lines.append(f"WR Trend (4w): {' > '.join(trend)}")

    return "\n".join(lines)


def build_weekly_report() -> str:
    week = get_weekly_trades()
    stats = get_cumulative_stats()
    benchmarks = get_benchmark_returns(days=7)

    equity = stats["current_equity"] or STARTING_CAPITAL
    ret_pct = round((equity - STARTING_CAPITAL) / STARTING_CAPITAL * 100, 1)
    week_wr = round(week["wins"] / week["trades"] * 100, 1) if week["trades"] > 0 else 0

    # Monday date
    monday = datetime.now() - timedelta(days=datetime.now().weekday())
    period = f"{monday.strftime('%b %d')} - {datetime.now().strftime('%b %d')}"

    # Benchmark lines
    bench_parts = []
    for sym, ret in benchmarks.items():
        bench_parts.append(f"{sym}: {ret:+.1f}%")
    bench_line = " | ".join(bench_parts) if bench_parts else "N/A (yfinance unavailable)"

    # PROMETHEUS vs benchmark this week
    prom_week_pct = round(week["pnl"] / equity * 100, 1) if equity > 0 else 0

    # Win rate trend
    trend = stats["weekly_wr_trend"]
    trend_str = " > ".join([f"{x}%" if x else "--" for x in trend])
    if trend[-1] and trend[0] and trend[-1] > trend[0]:
        learning = "IMPROVING"
    elif trend[-1] and trend[0] and trend[-1] < trend[0]:
        learning = "DECLINING"
    else:
        learning = "STABLE"

    # Asset class breakdown
    cls_lines = []
    for cls, d in week["by_class"].items():
        cls_wr = round(d["wins"] / d["trades"] * 100) if d["trades"] > 0 else 0
        cls_lines.append(f"  {cls}: {d['trades']} trades | {cls_wr}% WR | ${d['pnl']:.2f}")

    # Top AI
    ai_lines = []
    for ai in stats["top_ai"][:2]:
        ai_lines.append(f"  {ai[0]}: {ai[1]}% acc | avg ${ai[2]}")

    lines = [
        f"PROMETHEUS Weekly | {period}",
        f"",
        f"CAPITAL",
        f"  Equity: ${equity:.0f} ({ret_pct:+.1f}% all-time)",
        f"",
        f"THIS WEEK",
        f"  {week['trades']} trades | {week['wins']}W {week['losses']}L | {week_wr}% WR",
        f"  PnL: {'+'if week['pnl']>=0 else ''}{week['pnl']:.2f} ({prom_week_pct:+.1f}%)",
        f"  Best: {week['best_symbol']} +${week['best_pnl']:.2f}",
        f"  Worst: {week['worst_symbol']} -${abs(week['worst_pnl']):.2f}",
        f"",
        f"VS MARKET (7d)",
        f"  PROMETHEUS: {prom_week_pct:+.1f}%",
        f"  {bench_line}",
        f"",
        f"ASSET CLASS",
    ] + cls_lines + [
        f"",
        f"AI LEARNING",
        f"  4-week WR trend: {trend_str}",
        f"  Status: {learning}",
    ] + (ai_lines if ai_lines else ["  No AI metrics yet"]) + [
        f"",
        f"Overall: {stats['overall_wr']}% WR | {stats['total_trades']} trades | ${stats['total_pnl']:.2f} total PnL",
    ]

    return "\n".join(lines)


def _get_uptime() -> str:
    """Check if the server is responding on port 8000."""
    import socket
    try:
        s = socket.create_connection(("127.0.0.1", 8000), timeout=2)
        s.close()
        return "Running"
    except OSError:
        return "OFFLINE"


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Load .env
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

    args = sys.argv[1:]

    if "--test" in args:
        msg = f"PROMETHEUS Test Ping | {datetime.now().strftime('%Y-%m-%d %H:%M')}\nSystem is online. Reports are working."
        print(msg)
        send_whatsapp(msg)

    elif "--alert" in args:
        idx = args.index("--alert")
        alert_text = args[idx + 1] if idx + 1 < len(args) else "Alert"
        msg = f"PROMETHEUS ALERT | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{alert_text}"
        print(msg)
        send_whatsapp(msg)

    elif "--weekly" in args:
        report = build_weekly_report()
        print(report)
        send_whatsapp(report)

    else:
        report = build_daily_report()
        print(report)
        send_whatsapp(report)
