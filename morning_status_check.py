#!/usr/bin/env python3
"""
Morning Status Check - Quick review of overnight autonomous operations
"""

import json
import os
from datetime import datetime
import subprocess

def check_overnight_status():
    """Check status of overnight operations"""
    print("🌅 GOOD MORNING! Checking overnight operations...")
    print("=" * 50)
    
    # Check if trading is still active
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        trading_active = 'python.exe' in result.stdout
        print(f"🚀 Trading Status: {'✅ ACTIVE' if trading_active else '❌ STOPPED'}")
    except:
        print("🚀 Trading Status: ❓ UNKNOWN")
    
    # Check overnight summary
    if os.path.exists('overnight_summary.json'):
        with open('overnight_summary.json', 'r') as f:
            summary = json.load(f)
        
        session = summary['autonomous_session']
        print(f"⏰ Autonomous Runtime: {session['total_runtime_hours']:.1f} hours")
        print(f"✅ Enhancements Completed: {len(session['enhancements_completed'])}")
        print("📋 Completed Enhancements:")
        for enhancement in session['enhancements_completed']:
            print(f"   • {enhancement}")
    else:
        print("📋 No overnight summary found")
    
    # Check log file
    if os.path.exists('autonomous_overnight.log'):
        print("\n📝 Recent log entries:")
        with open('autonomous_overnight.log', 'r') as f:
            lines = f.readlines()[-10:]  # Last 10 lines
        for line in lines:
            print(f"   {line.strip()}")
    
    # Check new patterns
    if os.path.exists('visual_ai_patterns.json'):
        try:
            with open('visual_ai_patterns.json', 'r') as f:
                data = json.load(f)
            total_patterns = data.get('total_analyzed', 'Unknown')
            print(f"\n📊 Total Visual AI Patterns: {total_patterns}")
        except:
            print("\n📊 Visual AI Patterns: File exists but unreadable")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Review full logs in autonomous_overnight.log")
    print("2. Check trading performance with: python performance_tracker.py")
    print("3. Monitor positions with: python next_steps_monitor.py")

if __name__ == "__main__":
    check_overnight_status()