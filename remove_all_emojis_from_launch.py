#!/usr/bin/env python3
"""
Remove all emoji characters from launch_ultimate_prometheus_LIVE_TRADING.py
"""

import re

filename = "launch_ultimate_prometheus_LIVE_TRADING.py"

print("=" * 80)
print(f"REMOVING ALL EMOJI CHARACTERS FROM {filename}")
print("=" * 80)

# Read the file
print("\n1. Reading file...")
with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"   Original file size: {len(content)} characters")

# Define emoji pattern (covers most common emoji ranges)
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U00002600-\U000026FF"  # Miscellaneous Symbols
    "\U00002700-\U000027BF"  # Dingbats
    "]+",
    flags=re.UNICODE
)

# Find all emojis
emojis = emoji_pattern.findall(content)
print(f"\n2. Found {len(emojis)} emoji characters")

# Remove emojis
print("\n3. Removing emojis...")
cleaned_content = emoji_pattern.sub('', content)

# Also remove common Unicode emoji escapes
cleaned_content = cleaned_content.replace('\\u2705', '')  # [CHECK]
cleaned_content = cleaned_content.replace('\\u26A0', '')  # [WARNING]️
cleaned_content = cleaned_content.replace('\\u274C', '')  # [ERROR]
cleaned_content = cleaned_content.replace('\\u2705\\uFE0F', '')  # [CHECK] with variation selector
cleaned_content = cleaned_content.replace('\\u26A0\\uFE0F', '')  # [WARNING]️ with variation selector

print(f"   Removed {len(content) - len(cleaned_content)} characters")
print(f"   New file size: {len(cleaned_content)} characters")

# Create backup
print("\n4. Creating backup...")
backup_filename = f"{filename}.backup"
with open(backup_filename, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"   Backup created: {backup_filename}")

# Write cleaned content
print("\n5. Writing cleaned file...")
with open(filename, 'w', encoding='utf-8') as f:
    f.write(cleaned_content)
print("   File written successfully")

print("\n" + "=" * 80)
print("EMOJI REMOVAL COMPLETE")
print("=" * 80)
print(f"\nRemoved {len(emojis)} emoji characters")
print(f"Backup saved as: {backup_filename}")
print("\nYou can now restart the server:")
print("  python unified_production_server.py")
print("=" * 80)

