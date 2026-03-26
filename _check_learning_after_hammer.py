import sqlite3
from datetime import datetime, timedelta

DB = "prometheus_learning.db"


def has_table(cur, name):
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def print_section(title):
    print("\n" + "=" * 12 + f" {title} " + "=" * 12)


conn = sqlite3.connect(DB)
cur = conn.cursor()

print_section("TABLES")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for row in cur.fetchall():
    print(row[0])


def table_columns(table_name):
    cur.execute(f"PRAGMA table_info({table_name})")
    return [r[1] for r in cur.fetchall()]


def first_existing(candidates, cols):
    for c in candidates:
        if c in cols:
            return c
    return None

print_section("SHADOW SUMMARY")
cur.execute(
    """
    SELECT COUNT(*),
           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END),
           SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END),
           ROUND(COALESCE(SUM(pnl), 0), 2),
           MIN(exit_time),
           MAX(exit_time)
    FROM shadow_trade_history
    WHERE status='CLOSED'
    """
)
print("all_closed:", cur.fetchone())

cur.execute(
    """
    SELECT COUNT(*),
           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END),
           SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END),
           ROUND(COALESCE(SUM(pnl), 0), 2),
           MIN(exit_time),
           MAX(exit_time)
    FROM shadow_trade_history
    WHERE status='CLOSED' AND exit_time >= datetime('now', '-3 day')
    """
)
print("last_3_days:", cur.fetchone())

print_section("RECENT CLOSED SHADOW TRADES")
cur.execute(
    """
    SELECT symbol, action, ROUND(entry_price, 4), ROUND(exit_price, 4),
           ROUND(pnl, 2), exit_reason, timestamp, exit_time
    FROM shadow_trade_history
    WHERE status='CLOSED'
    ORDER BY exit_time DESC
    LIMIT 20
    """
)
for row in cur.fetchall():
    print(row)

if has_table(cur, "learning_outcomes"):
    print_section("LEARNING OUTCOMES SUMMARY")
    cols = table_columns("learning_outcomes")
    print("columns:", cols)

    ts_col = first_existing(["timestamp", "created_at", "time"], cols)
    pnl_col = first_existing(["profit_loss", "pnl", "realized_pnl", "return_pct"], cols)
    success_col = first_existing(["success", "is_success", "outcome"], cols)

    select_parts = ["COUNT(*)"]
    if success_col:
        select_parts.append(f"SUM(CASE WHEN {success_col}=1 THEN 1 ELSE 0 END)")
        select_parts.append(f"SUM(CASE WHEN {success_col}=0 THEN 1 ELSE 0 END)")
    else:
        select_parts.append("NULL")
        select_parts.append("NULL")
    if pnl_col:
        select_parts.append(f"ROUND(COALESCE(SUM({pnl_col}),0),2)")
    else:
        select_parts.append("NULL")
    if ts_col:
        select_parts.append(f"MIN({ts_col})")
        select_parts.append(f"MAX({ts_col})")
    else:
        select_parts.append("NULL")
        select_parts.append("NULL")

    cur.execute(f"SELECT {', '.join(select_parts)} FROM learning_outcomes")
    print("all_learning_outcomes:", cur.fetchone())

    if ts_col:
        cur.execute(
            f"SELECT {', '.join(select_parts)} FROM learning_outcomes WHERE {ts_col} >= datetime('now', '-3 day')"
        )
        print("learning_outcomes_last_3_days:", cur.fetchone())

    print_section("RECENT LEARNING OUTCOMES")

    display_cols = [c for c in ["id", "timestamp", "symbol", "signal", "success", "profit_loss", "confidence", "entry_price", "exit_price"] if c in cols]
    if not display_cols:
        display_cols = cols[:8]

    order_col = ts_col or display_cols[0]
    query = f"SELECT {', '.join(display_cols)} FROM learning_outcomes ORDER BY {order_col} DESC LIMIT 20"
    cur.execute(query)
    for row in cur.fetchall():
        print(row)
else:
    print_section("LEARNING OUTCOMES")
    print("Table not present")

if has_table(cur, "signal_predictions"):
    print_section("SIGNAL PREDICTIONS LAST 3D")
    pcols = table_columns("signal_predictions")
    print("columns:", pcols)

    ts_col = "timestamp" if "timestamp" in pcols else None
    if ts_col:
        cur.execute(
            "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM signal_predictions WHERE timestamp >= datetime('now','-3 day')"
        )
        print("predictions_last_3_days:", cur.fetchone())

    conf_col = first_existing(["confidence", "score", "model_confidence"], pcols)
    sym_col = first_existing(["symbol", "ticker", "asset"], pcols)
    act_col = first_existing(["signal", "action", "prediction"], pcols)

    if ts_col and conf_col and sym_col and act_col:
        print_section("LOW-CONFIDENCE PREDICTIONS LAST 3D")
        cur.execute(
            f"SELECT {sym_col}, {act_col}, ROUND({conf_col},4), {ts_col} "
            f"FROM signal_predictions WHERE {ts_col} >= datetime('now','-3 day') "
            f"ORDER BY {conf_col} ASC, {ts_col} DESC LIMIT 20"
        )
        for row in cur.fetchall():
            print(row)

if has_table(cur, "risk_adaptation_log"):
    print_section("RISK ADAPTATION LAST 7D")
    rcols = table_columns("risk_adaptation_log")
    print("columns:", rcols)
    rts = first_existing(["timestamp", "created_at", "time"], rcols)
    if rts:
        cur.execute(
            f"SELECT COUNT(*), MIN({rts}), MAX({rts}) FROM risk_adaptation_log WHERE {rts} >= datetime('now','-7 day')"
        )
        print("risk_adapt_events_last_7d:", cur.fetchone())

        sel = [c for c in ["timestamp", "symbol", "action", "reason", "old_value", "new_value", "metric", "value"] if c in rcols]
        if sel:
            cur.execute(
                f"SELECT {', '.join(sel)} FROM risk_adaptation_log WHERE {rts} >= datetime('now','-7 day') ORDER BY {rts} DESC LIMIT 20"
            )
            for row in cur.fetchall():
                print(row)

if has_table(cur, "learning_patterns"):
    print_section("LEARNING PATTERNS LAST 7D")
    lcols = table_columns("learning_patterns")
    print("columns:", lcols)
    lts = first_existing(["timestamp", "created_at", "time"], lcols)
    if lts:
        cur.execute(
            f"SELECT COUNT(*), MIN({lts}), MAX({lts}) FROM learning_patterns WHERE {lts} >= datetime('now','-7 day')"
        )
        print("pattern_events_last_7d:", cur.fetchone())

conn.close()
print("\nDone")
