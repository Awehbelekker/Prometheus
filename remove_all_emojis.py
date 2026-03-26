#!/usr/bin/env python3
"""
Remove all emoji characters from unified_production_server.py
"""

import re
import shutil

print("="*80)
print("REMOVING ALL EMOJI CHARACTERS FROM unified_production_server.py")
print("="*80)

# Backup the file first
print("\n1. Creating backup...")
shutil.copy2('unified_production_server.py', 'unified_production_server.py.backup')
print("   Backup created: unified_production_server.py.backup")

# Read the file
print("\n2. Reading file...")
with open('unified_production_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

original_length = len(content)
print(f"   Original file size: {original_length} characters")

# Define emoji pattern (comprehensive)
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

# Count emojis before removal
emojis_found = emoji_pattern.findall(content)
print(f"\n3. Found {len(emojis_found)} emoji characters")

# Remove emojis
print("\n4. Removing emojis...")
cleaned_content = emoji_pattern.sub('', content)

# Also remove specific Unicode characters that might not be caught
specific_chars_to_remove = [
    '\u2705',  # [CHECK] WHITE HEAVY CHECK MARK
    '\u26A0',  # [WARNING]️ WARNING SIGN
    '\u2728',  # ✨ SPARKLES
    '\u26A1',  # [LIGHTNING] HIGH VOLTAGE
    '\u274C',  # [ERROR] CROSS MARK
    '\u2139',  # [INFO]️ INFORMATION
    '\uFE0F',  # VARIATION SELECTOR-16 (makes emojis colorful)
]

for char in specific_chars_to_remove:
    cleaned_content = cleaned_content.replace(char, '')

new_length = len(cleaned_content)
removed = original_length - new_length

print(f"   Removed {removed} characters")
print(f"   New file size: {new_length} characters")

# Write the cleaned content
print("\n5. Writing cleaned file...")
with open('unified_production_server.py', 'w', encoding='utf-8') as f:
    f.write(cleaned_content)

print("   File written successfully")

print("\n" + "="*80)
print("EMOJI REMOVAL COMPLETE")
print("="*80)
print(f"\nRemoved {removed} emoji characters")
print("Backup saved as: unified_production_server.py.backup")
print("\nYou can now restart the server:")
print("  python unified_production_server.py")
print("="*80)

