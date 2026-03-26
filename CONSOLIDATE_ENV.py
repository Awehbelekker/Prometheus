#!/usr/bin/env python3
"""
Consolidate all .env files into single .env
Reads all .env files and merges into primary .env
"""

import os
from pathlib import Path
from collections import OrderedDict

def read_env_file(filepath):
    """Read .env file and return as dict"""
    env_vars = OrderedDict()
    if not os.path.exists(filepath):
        return env_vars
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    env_vars[key] = value
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    
    return env_vars

def write_env_file(filepath, env_vars):
    """Write .env file from dict"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

def consolidate_env_files():
    """Consolidate all .env files into primary .env"""
    base_dir = Path(__file__).parent
    
    # Primary .env file
    primary_env = base_dir / ".env"
    
    # Find all .env files
    env_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip archive and cache directories
        if 'ARCHIVE' in root or '__pycache__' in root or '.git' in root:
            continue
        
        for file in files:
            if file == '.env' or file.endswith('.env'):
                filepath = Path(root) / file
                if filepath != primary_env:
                    env_files.append(filepath)
    
    print(f"Found {len(env_files)} additional .env files to merge")
    print(f"Primary .env: {primary_env}")
    print()
    
    # Read primary .env
    consolidated = read_env_file(primary_env)
    print(f"Primary .env has {len(consolidated)} variables")
    
    # Merge all other .env files
    merged_count = 0
    for env_file in env_files:
        print(f"Reading: {env_file.relative_to(base_dir)}")
        env_vars = read_env_file(env_file)
        
        for key, value in env_vars.items():
            if key not in consolidated:
                consolidated[key] = value
                merged_count += 1
                print(f"  Added: {key}")
            elif consolidated[key] != value:
                print(f"  Conflict: {key} (keeping primary value)")
    
    print()
    print(f"Total variables: {len(consolidated)}")
    print(f"New variables added: {merged_count}")
    
    # Write consolidated .env
    if merged_count > 0:
        # Backup original
        if primary_env.exists():
            backup = base_dir / ".env.backup"
            with open(primary_env, 'r') as src, open(backup, 'w') as dst:
                dst.write(src.read())
            print(f"Backed up original to: {backup}")
        
        write_env_file(primary_env, consolidated)
        print(f"[OK] Consolidated .env written to: {primary_env}")
    else:
        print("[OK] No new variables to merge")
    
    # Create .env.example template
    example_env = base_dir / ".env.example"
    example_vars = OrderedDict()
    for key, value in consolidated.items():
        # Mask sensitive values
        if any(sensitive in key.upper() for sensitive in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'API']):
            example_vars[key] = "YOUR_" + key.upper() + "_HERE"
        else:
            example_vars[key] = value
    
    write_env_file(example_env, example_vars)
    print(f"[OK] Created .env.example template: {example_env}")
    
    return consolidated

if __name__ == "__main__":
    print("=" * 80)
    print("CONSOLIDATING .ENV FILES")
    print("=" * 80)
    print()
    
    consolidated = consolidate_env_files()
    
    print()
    print("=" * 80)
    print("CONSOLIDATION COMPLETE")
    print("=" * 80)

