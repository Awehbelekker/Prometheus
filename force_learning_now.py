"""
🧠 PROMETHEUS FORCE LEARNING
Run this anytime to trigger an immediate learning cycle
"""
import subprocess
import sys
import os
from datetime import datetime

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("🧠 PROMETHEUS FORCE LEARNING - IMMEDIATE CYCLE")
print("=" * 70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Check which learning script exists
learning_scripts = [
    'ultimate_learning_fixed_v2.py',
    'ultimate_learning_fixed.py', 
    'advanced_learning_backtest.py',
    'run_continuous_learning_backtest.py'
]

learning_script = None
for script in learning_scripts:
    if os.path.exists(script):
        learning_script = script
        break

if not learning_script:
    print("❌ No learning script found!")
    print("   Looking for:", learning_scripts)
    sys.exit(1)

print(f"📚 Using learning script: {learning_script}")
print()

# Run the learning engine
try:
    print("🔄 Starting learning cycle (this may take 1-5 minutes)...")
    print("-" * 70)
    
    result = subprocess.run(
        [sys.executable, learning_script],
        timeout=300,  # 5 minute max
        capture_output=False
    )
    
    print("-" * 70)
    if result.returncode == 0:
        print("\n✅ Learning cycle completed successfully!")
    else:
        print(f"\n⚠️ Learning cycle finished with code: {result.returncode}")
        
except subprocess.TimeoutExpired:
    print("\n⏰ Learning cycle timed out after 5 minutes")
    print("   Learning may still be running in background")
except KeyboardInterrupt:
    print("\n🛑 Learning interrupted by user")
except Exception as e:
    print(f"\n❌ Error: {e}")

print()
print("=" * 70)
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
