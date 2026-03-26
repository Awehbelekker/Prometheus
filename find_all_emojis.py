#!/usr/bin/env python3
"""
Find all emoji characters in unified_production_server.py
"""

import re

print("="*80)
print("FINDING ALL EMOJI CHARACTERS IN unified_production_server.py")
print("="*80)

# Read the file
with open('unified_production_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Common emoji ranges
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002700-\U000027BF"  # dingbats
    "]+", flags=re.UNICODE
)

# Also check for specific Unicode characters
specific_emojis = {
    '\u2705': 'WHITE HEAVY CHECK MARK',
    '\u26A0': 'WARNING SIGN',
    '\U0001F680': 'ROCKET',
    '\U0001F4A1': 'LIGHT BULB',
    '\u2728': 'SPARKLES',
    '\U0001F525': 'FIRE',
    '\u26A1': 'HIGH VOLTAGE',
    '\U0001F4CA': 'BAR CHART',
    '\U0001F4C8': 'CHART INCREASING',
    '\U0001F4C9': 'CHART DECREASING',
    '\U0001F4B0': 'MONEY BAG',
    '\U0001F4B8': 'MONEY WITH WINGS',
    '\U0001F4B5': 'DOLLAR BANKNOTE',
    '\u2705': 'CHECK MARK',
    '\u274C': 'CROSS MARK',
    '\u2139': 'INFORMATION',
    '\U0001F6A8': 'POLICE CAR LIGHT',
    '\U0001F6D1': 'STOP SIGN',
    '\U0001F4E1': 'SATELLITE ANTENNA',
    '\U0001F310': 'GLOBE WITH MERIDIANS',
    '\U0001F4DA': 'BOOKS',
    '\U0001F517': 'LINK',
    '\U0001F9E0': 'BRAIN',
    '\U0001F916': 'ROBOT',
}

found_emojis = []

for line_num, line in enumerate(lines, 1):
    # Check with regex
    matches = emoji_pattern.findall(line)
    if matches:
        for match in matches:
            found_emojis.append((line_num, match, line.strip()))
    
    # Check for specific emojis
    for emoji, name in specific_emojis.items():
        if emoji in line:
            found_emojis.append((line_num, emoji, line.strip()))

if found_emojis:
    print(f"\nFound {len(found_emojis)} emoji characters:\n")
    for line_num, emoji, line_content in found_emojis:
        # Get Unicode code point
        code_point = f"U+{ord(emoji):04X}"
        print(f"Line {line_num}: {emoji} ({code_point})")
        print(f"  Content: {line_content[:100]}...")
        print()
else:
    print("\n✓ No emoji characters found!")

print("="*80)
print("SEARCH COMPLETE")
print("="*80)

