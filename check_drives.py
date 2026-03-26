#!/usr/bin/env python
"""Simple drive checker - runs without PROMETHEUS imports"""
import os
import sys

# Avoid importing PROMETHEUS modules
if __name__ == "__main__":
    print("=" * 60)
    print("DRIVE CHECK UTILITY")
    print("=" * 60)
    
    # Check all possible drives
    print("\n📀 Available Drives:")
    for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            try:
                total = os.popen(f'powershell "(Get-PSDrive {letter}).Used + (Get-PSDrive {letter}).Free"').read()
                print(f"  ✓ {drive} - Accessible")
            except:
                print(f"  ✓ {drive}")
    
    # Check D: drive specifically
    print("\n📂 D: Drive Contents:")
    d_drive = "D:\\"
    if os.path.exists(d_drive):
        try:
            items = os.listdir(d_drive)
            for item in sorted(items):
                full_path = os.path.join(d_drive, item)
                is_dir = "📁" if os.path.isdir(full_path) else "📄"
                print(f"  {is_dir} {item}")
            
            # Search for GPT/OSS related folders
            print("\n🔍 Searching for GPT-OSS related folders:")
            for item in items:
                item_lower = item.lower()
                if any(x in item_lower for x in ['gpt', 'oss', 'llm', 'model', 'ai', 'ollama', 'hugging']):
                    print(f"  🎯 Found: {item}")
                    sub_path = os.path.join(d_drive, item)
                    if os.path.isdir(sub_path):
                        try:
                            sub_items = os.listdir(sub_path)[:10]
                            for sub in sub_items:
                                print(f"      └── {sub}")
                            if len(os.listdir(sub_path)) > 10:
                                print(f"      └── ... and {len(os.listdir(sub_path))-10} more")
                        except:
                            pass
        except Exception as e:
            print(f"  ❌ Error reading D: - {e}")
    else:
        print("  ❌ D: drive not accessible")
    
    print("\n" + "=" * 60)
