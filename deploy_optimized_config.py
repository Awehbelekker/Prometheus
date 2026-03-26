"""
PROMETHEUS Trading Platform - Deploy Optimized Configuration
Safely deploys the optimized paper trading configuration
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

def deploy_optimized_config():
    """Deploy optimized configuration with backup"""
    
    print("="*80)
    print("PROMETHEUS TRADING PLATFORM - CONFIGURATION DEPLOYMENT")
    print("="*80)
    print()
    
    # Paths
    original_config = Path("advanced_paper_trading_config.json")
    optimized_config = Path("advanced_paper_trading_config_optimized.json")
    backup_dir = Path("config_backups")
    
    # Create backup directory
    backup_dir.mkdir(exist_ok=True)
    
    # Step 1: Create backup of original config
    if original_config.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"advanced_paper_trading_config_backup_{timestamp}.json"
        shutil.copy(original_config, backup_path)
        print(f"✅ Backup created: {backup_path}")
        print()
    
    # Step 2: Load and validate optimized config
    try:
        with open(optimized_config, 'r') as f:
            new_config = json.load(f)
        print("✅ Optimized configuration loaded successfully")
        print()
    except Exception as e:
        print(f"❌ Error loading optimized config: {e}")
        return False
    
    # Step 3: Show key changes
    print("KEY CHANGES IN OPTIMIZED CONFIGURATION:")
    print("-" * 80)
    
    changes = new_config.get("optimization_notes", {}).get("changes_from_v1", [])
    for i, change in enumerate(changes, 1):
        print(f"{i}. {change}")
    print()
    
    # Step 4: Show expected improvements
    print("EXPECTED PERFORMANCE IMPROVEMENTS:")
    print("-" * 80)
    
    improvements = new_config.get("optimization_notes", {}).get("expected_improvements", {})
    for metric, improvement in improvements.items():
        print(f"  • {metric.upper()}: {improvement}")
    print()
    
    # Step 5: Deploy new configuration
    try:
        # Copy optimized config to main config
        shutil.copy(optimized_config, original_config)
        print(f"✅ Optimized configuration deployed to: {original_config}")
        print()
    except Exception as e:
        print(f"❌ Error deploying config: {e}")
        return False
    
    # Step 6: Verification
    print("DEPLOYMENT VERIFICATION:")
    print("-" * 80)
    
    try:
        with open(original_config, 'r') as f:
            deployed_config = json.load(f)
        
        # Verify key optimizations
        checks = {
            "Confidence Threshold": deployed_config["trading_parameters"]["confidence_threshold"] == 0.50,
            "Dynamic Position Sizing": deployed_config["advanced_features"]["dynamic_position_sizing"]["enabled"],
            "Multi-Timeframe Confirmation": deployed_config["advanced_features"]["multi_timeframe_confirmation"]["enabled"],
            "ML Win Rate Prediction": deployed_config["advanced_features"]["ml_win_rate_prediction"]["enabled"],
            "Regime Strategy Selection": deployed_config["advanced_features"]["regime_strategy_selection"]["enabled"],
        }
        
        for check_name, result in checks.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status}: {check_name}")
        
        print()
        
        if all(checks.values()):
            print("="*80)
            print("✅ DEPLOYMENT SUCCESSFUL!")
            print("="*80)
            print()
            print("NEXT STEPS:")
            print("  1. Restart PROMETHEUS trading system")
            print("  2. Monitor performance using: python monitor_optimization_performance.py")
            print("  3. Validate improvements over 7-30 days")
            print("  4. Target: Score 95.3+, Win Rate 73.8%, CAGR 19.2%")
            print()
            print("Expected Timeline to #1 Ranking:")
            print("  • Week 1: Initial improvements visible (+2-3 points)")
            print("  • Week 2-3: Strategy optimization stabilizes (+2-3 points)")
            print("  • Week 4: ML model trained and contributing (+1-2 points)")
            print("  • Month 2: Full optimization impact realized (95.3+ score)")
            print("  • Month 3: Validation and documentation for #1 claim")
            print()
            return True
        else:
            print("❌ DEPLOYMENT VERIFICATION FAILED!")
            print("Some optimizations were not properly deployed.")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying deployment: {e}")
        return False

def rollback_config():
    """Rollback to previous configuration"""
    
    print("="*80)
    print("CONFIGURATION ROLLBACK")
    print("="*80)
    print()
    
    backup_dir = Path("config_backups")
    
    if not backup_dir.exists():
        print("❌ No backup directory found")
        return False
    
    # Find latest backup
    backups = sorted(backup_dir.glob("advanced_paper_trading_config_backup_*.json"), reverse=True)
    
    if not backups:
        print("❌ No backup files found")
        return False
    
    latest_backup = backups[0]
    print(f"Latest backup: {latest_backup}")
    print()
    
    # Restore backup
    original_config = Path("advanced_paper_trading_config.json")
    
    try:
        shutil.copy(latest_backup, original_config)
        print(f"✅ Configuration restored from: {latest_backup}")
        return True
    except Exception as e:
        print(f"❌ Error restoring backup: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        success = rollback_config()
    else:
        success = deploy_optimized_config()
    
    sys.exit(0 if success else 1)
