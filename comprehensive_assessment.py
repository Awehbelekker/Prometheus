#!/usr/bin/env python3
"""Comprehensive System Assessment for PROMETHEUS"""

import os
import json
from pathlib import Path
from datetime import datetime

def main():
    print("=" * 80)
    print("PROMETHEUS COMPREHENSIVE SYSTEM ASSESSMENT")
    print("=" * 80)

    # 1. Training Results
    print("\n[1] TRAINING RESULTS & HISTORY")
    print("-" * 40)
    training_dir = Path("training_results")
    if training_dir.exists():
        results = list(training_dir.glob("*.json"))
        print(f"Training result files: {len(results)}")
    else:
        print("No training results directory")

    # 2. Backtest Results
    print("\n[2] BACKTEST/LEARNING DATA")
    print("-" * 40)
    backtest_files = list(Path(".").glob("*backtest*.json")) + list(Path(".").glob("*BACKTEST*.json"))
    print(f"Backtest result files: {len(backtest_files)}")
    
    # 3. Continuous Learning
    print("\n[3] CONTINUOUS LEARNING DATA")
    print("-" * 40)
    learning_files = list(Path(".").glob("CONTINUOUS_LEARNING*.json"))
    print(f"Continuous learning files: {len(learning_files)}")

    # 4. Paper Trading
    print("\n[4] PAPER TRADING RESULTS")
    print("-" * 40)
    paper_dir = Path("paper_trading_results")
    if paper_dir.exists():
        paper_files = list(paper_dir.glob("*.json"))
        print(f"Paper trading sessions: {len(paper_files)}")

    # 5. Trading Feedback
    print("\n[5] TRADING FEEDBACK DATA")
    print("-" * 40)
    feedback_dir = Path("trading_feedback")
    if feedback_dir.exists():
        trade_fb = feedback_dir / "trade_feedback.json"
        if trade_fb.exists():
            with open(trade_fb) as f:
                data = json.load(f)
            print(f"Recorded trades with feedback: {len(data)}")
        
        charts_dir = feedback_dir / "charts"
        if charts_dir.exists():
            charts = list(charts_dir.glob("*.png"))
            print(f"Chart snapshots: {len(charts)}")

    # 6. Pretrained Models
    print("\n[6] PRETRAINED TRADING MODELS")
    print("-" * 40)
    models_dir = Path("pretrained_models")
    if models_dir.exists():
        joblib_files = list(models_dir.glob("*.joblib"))
        symbols = set([f.name.split("_")[0] for f in joblib_files])
        print(f"Total models: {len(joblib_files)}")
        print(f"Symbols covered: {len(symbols)}")

    # 7. Knowledge Base
    print("\n[7] AI KNOWLEDGE BASE")
    print("-" * 40)
    kb_file = Path("ai_knowledge_training_data.json")
    if kb_file.exists():
        with open(kb_file) as f:
            data = json.load(f)
        print(f"Knowledge sources: {data.get('knowledge_sources', 0)}")
        print(f"Training examples: {len(data.get('training_examples', []))}")

    # 8. HRM Checkpoints
    print("\n[8] HRM CHECKPOINTS")
    print("-" * 40)
    hrm_dir = Path("hrm_checkpoints")
    if hrm_dir.exists():
        for cp in ["arc_agi_2", "sudoku_extreme", "maze_30x30"]:
            cp_path = hrm_dir / cp / "checkpoint"
            if cp_path.exists():
                size = cp_path.stat().st_size / (1024*1024)
                print(f"  {cp}: {size:.1f} MB")

    # 9. Integrated Repos
    print("\n[9] INTEGRATED REPOSITORIES")
    print("-" * 40)
    repos = [
        ("integrated_repos/GLM-4.5", "GLM-4.5/4.6"),
        ("integrated_repos/GLM-V", "GLM-V (Vision)"),
        ("integrated_repos/crewai", "CrewAI"),
        ("integrated_repos/deepconfupdate", "DeepConf"),
        ("integrated_repos/llm-council", "LLM Council"),
    ]
    for path, name in repos:
        status = "INTEGRATED" if Path(path).exists() else "NOT FOUND"
        print(f"  {name}: {status}")

    # 10. Ollama Models
    print("\n[10] LOCAL LLM MODELS (OLLAMA)")
    print("-" * 40)
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            models = [l.split()[0] for l in lines[1:] if l.strip()]
            for m in models:
                print(f"  - {m}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n" + "=" * 80)
    print("ASSESSMENT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

