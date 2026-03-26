#!/usr/bin/env python3
"""
Train Meta-Ensemble Model
Learns which AI voters to trust based on actual trade outcomes.

Reads from ai_attribution table (populated by post-trade hooks),
pivots per-voter confidence as features, trains GradientBoosting,
saves to models_pretrained/META_ENSEMBLE_model.pkl.
"""

import sqlite3
import pickle
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score


# AI voter names as they appear in ai_attribution.ai_system column.
# We also include normalized versions so any future voter names map correctly.
VOTERS = [
    "technical", "technical_analysis", "marketresearcher", "quantum",
    "universal_reasoning", "visual_patterns", "opportunityscanner",
    "agents_3", "agents_4", "agents_5", "agents_6", "agents_7",
    "agents_8", "agents_9", "agents_10", "agents_11",
]

DB_CANDIDATES = ["prometheus_learning.db", "prometheus_trading.db"]
OUTPUT_PATH = Path("models_pretrained/META_ENSEMBLE_model.pkl")


def _normalize_voter(name: str) -> str:
    """Normalize ai_system name to a consistent voter key."""
    s = name.lower().strip().replace(" ", "_").replace("-", "_")
    # Handle 'Agents(N)' -> 'agents_N'
    s = s.replace("(", "_").replace(")", "")
    # Handle 'OpportunityScanner(volume_spike)' -> 'opportunityscanner'
    if "opportunityscanner" in s:
        s = "opportunityscanner"
    return s


def load_attribution_data() -> tuple:
    """Load per-trade voter confidence and outcomes from ai_attribution table."""
    rows = []
    for db_path in DB_CANDIDATES:
        if not Path(db_path).exists():
            continue
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # Check if ai_attribution table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_attribution'")
            if not cur.fetchone():
                conn.close()
                continue
            # Use correct column names: ai_system (not source), eventual_pnl (not profit_loss)
            # Group by symbol+timestamp since trade_id is often NULL
            cur.execute("""
                SELECT symbol, timestamp, ai_system, confidence, eventual_pnl
                FROM ai_attribution
                WHERE eventual_pnl IS NOT NULL AND eventual_pnl != 0
            """)
            rows.extend(cur.fetchall())
            conn.close()
            print(f"  Loaded {len(rows)} attribution rows from {db_path}")
        except Exception as e:
            print(f"  Warning: {db_path}: {e}")

    if not rows:
        return np.array([]), np.array([])

    # Discover all unique voter names in the data
    all_voter_names = set()
    for _, _, ai_system, _, _ in rows:
        all_voter_names.add(_normalize_voter(ai_system))

    # Merge discovered voters with predefined list (keeps ordering stable)
    voter_set = list(dict.fromkeys(VOTERS + sorted(all_voter_names)))
    print(f"  Voter features ({len(voter_set)}): {voter_set}")

    # Pivot: each trade event (symbol+timestamp) gets a feature vector
    trades = {}
    for symbol, ts, ai_system, confidence, pnl in rows:
        key = f"{symbol}_{ts}"
        if key not in trades:
            trades[key] = {"label": 1 if pnl > 0 else 0}
        voter_key = _normalize_voter(ai_system)
        trades[key][voter_key] = confidence or 0.0

    # Build feature matrix
    X_list = []
    y_list = []
    for _, data in trades.items():
        features = [data.get(v, 0.0) for v in voter_set]
        X_list.append(features)
        y_list.append(data["label"])

    return np.array(X_list), np.array(y_list), voter_set


def train_meta_model():
    """Train and save the meta-ensemble model."""
    print(f"\n{'='*60}")
    print(f"  META-ENSEMBLE TRAINER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    X, y, voter_names = load_attribution_data()

    if len(X) == 0:
        print("  No ai_attribution data found. Need real trades with voter attribution first.")
        print("  The ai_attribution table is populated by post-trade hooks in the live trading loop.")
        print("  Run some trades first, then retrain.\n")
        return False

    print(f"  Loaded {len(X)} trade outcomes with {len(voter_names)} voter features")
    print(f"  Win rate in data: {y.mean()*100:.1f}%")

    # Check class balance
    if len(np.unique(y)) < 2:
        print(f"  ERROR: Only one class present (all wins or all losses). Need both.")
        return False

    # Train
    model = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.8,
        random_state=42
    )

    # Cross-validate
    n_cv = min(5, len(X))
    if n_cv >= 2:
        scores = cross_val_score(model, X, y, cv=n_cv, scoring='accuracy')
        print(f"  Cross-validation accuracy: {scores.mean()*100:.1f}% (+/- {scores.std()*100:.1f}%)")

    # Fit on all data
    model.fit(X, y)

    # Feature importances
    importances = model.feature_importances_
    ranked = sorted(zip(voter_names, importances), key=lambda x: x[1], reverse=True)
    print(f"\n  Voter Importance Ranking:")
    for voter, imp in ranked:
        bar = "#" * int(imp * 50)
        print(f"    {voter:30s} {imp:.3f} {bar}")

    # Save
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    meta_data = {
        "model": model,
        "voters": voter_names,
        "importances": dict(zip(voter_names, importances.tolist())),
        "train_samples": len(X),
        "train_accuracy": model.score(X, y),
        "trained_at": datetime.now().isoformat()
    }
    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(meta_data, f)

    print(f"\n  Model saved to {OUTPUT_PATH}")
    print(f"  Train accuracy: {model.score(X, y)*100:.1f}%")
    print(f"  Samples: {len(X)}")
    print(f"\n{'='*60}\n")
    return True


if __name__ == "__main__":
    success = train_meta_model()
    sys.exit(0 if success else 1)
