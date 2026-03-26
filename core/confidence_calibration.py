"""
Confidence Calibration Module.
Maps raw confidence (0.7-0.9) to realistic probability of winning,
based on historical shadow trading outcomes.

Problem: System assigns high confidence to losing trades.
Solution: Learn actual win rates per confidence bin and apply correction.
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, Tuple

LEARNING_DB = Path("prometheus_learning.db")


def calculate_confidence_calibration() -> Dict[str, float]:
    """
    Analyze shadow_trade_history (ground truth) to compute correction factor
    for each confidence bucket.
    
    Returns: Dict mapping confidence (as string "0.7"-"0.8"-"0.9") to calibration_factor
    """
    if not LEARNING_DB.exists():
        return {}
    
    db = sqlite3.connect(str(LEARNING_DB))
    db.row_factory = sqlite3.Row
    
    try:
        # Bucket trades by confidence level
        rows = db.execute("""
            SELECT 
              ROUND(confidence, 1) as conf_bucket,
              COUNT(*) as total_trades,
              SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
              AVG(confidence) as avg_conf
            FROM shadow_trade_history
            WHERE exit_price IS NOT NULL
            GROUP BY ROUND(confidence, 1)
            ORDER BY conf_bucket
        """).fetchall()
        
        calibration = {}
        for row in rows:
            bucket = f"{row['conf_bucket']:.1f}"
            if row['total_trades'] >= 3:  # Need at least 3 trades to trust the bin
                actual_win_pct = row['wins'] / row['total_trades']
                # If actual win rate is 40%, but we expected 75% (raw confidence),
                # multiply by 0.40/0.75 ≈ 0.53 to deflate the signal
                raw_conf = row['avg_conf']
                correction_factor = actual_win_pct / max(raw_conf, 0.01)
                calibration[bucket] = round(min(correction_factor, 1.0), 3)  # cap at 1.0
        
        db.close()
        return calibration
    except Exception as e:
        print(f"Calibration error: {e}")
        return {}


def apply_calibration(raw_confidence: float, calibration: Dict[str, float]) -> float:
    """
    Apply learned calibration to a raw confidence score.
    
    Example:
        Confidence 0.78 but history shows 0.78-bucket trades only win 40% of time.
        Return 0.78 * 0.50 = 0.39 (more honest)
    """
    bucket = f"{raw_confidence:.1f}"
    if bucket in calibration:
        return raw_confidence * calibration[bucket]
    # If no data for this bucket, use nearby bucket or assume 0.6 (conservative)
    return raw_confidence * 0.6


def save_calibration_config(calibration: Dict[str, float]):
    """Save calibration factors to disk for use by trading engine."""
    try:
        Path("confidence_calibration.json").write_text(json.dumps(calibration, indent=2))
    except Exception as e:
        print(f"Failed to save calibration: {e}")


if __name__ == "__main__":
    calibration = calculate_confidence_calibration()
    if calibration:
        print("Confidence Calibration Factors:")
        for bucket, factor in sorted(calibration.items()):
            print(f"  Confidence {bucket}: multiply by {factor}")
        save_calibration_config(calibration)
    else:
        print("No calibration data available yet")
