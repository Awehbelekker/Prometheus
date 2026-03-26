#!/usr/bin/env python3
"""
Add OpenAI API Key to .env file (Simple Version)
===============================================
Interactive script to add OpenAI API key for enhanced AI capabilities
"""

import os
import sys
from pathlib import Path

def add_openai_key():
    """Add OpenAI API key to .env file"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("ERROR: .env file not found!")
        return False
    
    print("OPENAI API KEY CONFIGURATION")
    print("=" * 50)
    print()
    print("To get your OpenAI API key:")
    print("1. Go to: https://platform.openai.com/api-keys")
    print("2. Sign in to your OpenAI account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key (starts with 'sk-')")
    print()
    
    # Get API key from user
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("WARNING: Skipping OpenAI key configuration")
        print("   You can add it later by editing the .env file")
        return False
    
    if not api_key.startswith('sk-'):
        print("WARNING: OpenAI API keys usually start with 'sk-'")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Configuration cancelled")
            return False
    
    # Read current .env file
    try:
        with open(env_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: Could not read .env file: {e}")
        return False
    
    # Update the OpenAI API key
    if "OPENAI_API_KEY=" in content:
        # Replace existing key
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("OPENAI_API_KEY="):
                lines[i] = f"OPENAI_API_KEY={api_key}"
                break
        
        updated_content = '\n'.join(lines)
    else:
        # Add new key
        updated_content = content + f"\nOPENAI_API_KEY={api_key}\n"
    
    # Write updated content
    try:
        with open(env_file, 'w') as f:
            f.write(updated_content)
        
        print("SUCCESS: OpenAI API key added successfully!")
        print(f"   Key: {api_key[:8]}...{api_key[-4:]}")
        return True
        
    except Exception as e:
        print(f"ERROR: Could not write to .env file: {e}")
        return False

def main():
    """Main function"""
    print("PROMETHEUS AI ENHANCEMENT SETUP")
    print("=" * 40)
    print()
    
    success = add_openai_key()
    
    if success:
        print()
        print("CONFIGURATION COMPLETE!")
        print("Next steps:")
        print("1. Restart the server to activate enhanced AI")
        print("2. Test the enhanced AI functions")
        print()
        print("To restart the server:")
        print("1. Stop current server (Ctrl+C)")
        print("2. Run: python unified_production_server.py")
    else:
        print()
        print("Configuration incomplete")
        print("You can manually edit the .env file to add your OpenAI API key")

if __name__ == "__main__":
    main()

