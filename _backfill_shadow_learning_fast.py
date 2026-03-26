import json
import sqlite3
from datetime import datetime

DB = "prometheus_learning.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS learning_outcomes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        symbol TEXT NOT NULL,
        predicted_action TEXT,
        predicted_confidence REAL,
        entry_price REAL,
        exit_price REAL,
        profit_loss REAL,
        profit_pct REAL,
        was_correct INTEGER,
        ai_components TEXT,
        learning_notes TEXT
    )
    """
)

cur.execute(
    """
    SELECT trade_id, symbol, action, confidence, entry_price, exit_price, pnl, pnl_pct, exit_time, exit_reason, ai_components
    FROM shadow_trade_history
    WHERE status='CLOSED' AND exit_price IS NOT NULL AND pnl IS NOT NULL
    ORDER BY exit_time ASC
    """
)
rows = cur.fetchall()

inserted = 0
for trade_id, symbol, action, confidence, entry_price, exit_price, pnl, pnl_pct, exit_time, exit_reason, ai_components in rows:
    note = f"SHADOW outcome | trade_id={trade_id} | exit_reason={exit_reason or 'UNKNOWN'}"
    cur.execute("SELECT 1 FROM learning_outcomes WHERE learning_notes LIKE ? LIMIT 1", (f"%trade_id={trade_id}%",))
    if cur.fetchone():
        continue

    cur.execute(
        """
        INSERT INTO learning_outcomes
        (timestamp, symbol, predicted_action, predicted_confidence, entry_price, exit_price,
         profit_loss, profit_pct, was_correct, ai_components, learning_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            exit_time or datetime.now().isoformat(),
            symbol,
            action,
            confidence,
            entry_price,
            exit_price,
            pnl,
            (float(pnl_pct) / 100.0) if pnl_pct is not None else 0.0,
            1 if (pnl or 0) > 0 else 0,
            ai_components if ai_components else json.dumps([]),
            note,
        ),
    )
    inserted += 1

# Mark one matching prediction as outcome_recorded for each closed shadow trade.
updated = 0
for trade_id, symbol, action, confidence, entry_price, exit_price, pnl, pnl_pct, exit_time, exit_reason, ai_components in rows:
    variants = [symbol]
    if '/' in symbol:
        variants.append(symbol.replace('/', ''))
    if symbol.endswith('-USD'):
        variants.append(symbol.replace('-USD', '/USD'))
        variants.append(symbol.replace('-USD', 'USD'))
    if symbol.endswith('USD') and '/' not in symbol and '-' not in symbol:
        variants.append(symbol[:-3] + '/USD')
    variants = list(dict.fromkeys(variants))

    q = ','.join('?' for _ in variants)
    cutoff = exit_time or datetime.now().isoformat()
    cur.execute(
        f"SELECT id FROM signal_predictions WHERE symbol IN ({q}) AND outcome_recorded=0 AND timestamp <= ? ORDER BY timestamp DESC LIMIT 1",
        variants + [cutoff],
    )
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE signal_predictions SET outcome_recorded=1 WHERE id=?", (row[0],))
        updated += 1

conn.commit()

cur.execute("SELECT COUNT(*) FROM signal_predictions")
total_preds = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM signal_predictions WHERE outcome_recorded=1")
recorded_preds = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM learning_outcomes")
learning_total = cur.fetchone()[0]

print(f"inserted_learning_outcomes={inserted}")
print(f"marked_predictions={updated}")
print(f"signal_predictions_recorded={recorded_preds}/{total_preds}")
print(f"learning_outcomes_total={learning_total}")

conn.close()
