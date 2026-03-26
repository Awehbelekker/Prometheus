#!/usr/bin/env python3
"""
Discover and analyze Awehbelekker repositories
"""

import requests
import json
from pathlib import Path

def discover_repositories(username="Awehbelekker"):
    """Discover all repositories by Awehbelekker"""
    print(f"Discovering repositories for {username}...")
    
    url = f"https://api.github.com/users/{username}/repos"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            repos = response.json()
            print(f"\n[OK] Found {len(repos)} repositories:\n")
            
            for i, repo in enumerate(repos, 1):
                try:
                    name = repo.get('name', 'Unknown')
                    desc = repo.get('description', 'No description') or 'No description'
                    # Clean description of problematic Unicode characters
                    desc_clean = desc.encode('ascii', 'replace').decode('ascii')
                    
                    print(f"{i}. {name}")
                    print(f"   Description: {desc_clean}")
                    print(f"   URL: {repo['html_url']}")
                    print(f"   Stars: {repo['stargazers_count']}, Forks: {repo['forks_count']}")
                    print(f"   Language: {repo.get('language', 'N/A')}")
                    
                    # Check relevance
                    description = desc.lower()
                    name_lower = name.lower()
                    keywords = ['hrm', 'reasoning', 'ai', 'ml', 'trading', 'finance', 
                               'universal', 'framework', 'shadow', 'meta', 'ensemble',
                               'mass', 'computation', 'intelligence', 'agent', 'workflow']
                    
                    relevance = sum(1 for kw in keywords if kw in description or kw in name_lower)
                    if relevance > 0:
                        print(f"   [HIGH] Relevance: {relevance}/10")
                    print()
                except Exception as e:
                    print(f"   [ERROR] Failed to process repo {i}: {e}")
                    print()
            
            return repos
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []

if __name__ == "__main__":
    repos = discover_repositories()
    
    if repos:
        print("\n" + "="*60)
        print("HIGH-PRIORITY REPOSITORIES FOR PROMETHEUS")
        print("="*60)
        
        high_priority = []
        for repo in repos:
            desc = repo.get('description', '').lower()
            name = repo['name'].lower()
            
            if any(kw in desc or kw in name for kw in 
                   ['hrm', 'reasoning', 'universal', 'framework', 'shadow', 
                    'meta', 'ensemble', 'mass', 'trading', 'finance']):
                high_priority.append(repo)
        
        if high_priority:
            for repo in high_priority:
                print(f"\n[HIGH] {repo['name']}")
                print(f"   {repo.get('description', 'No description')}")
                print(f"   {repo['html_url']}")
        else:
            print("\nNo high-priority repositories found based on keywords")
    else:
        print("\n[WARNING] Could not discover repositories")
        print("   This could mean:")
        print("   1. Username doesn't exist")
        print("   2. No public repositories")
        print("   3. Network/API issue")
        print("\n   Manual check: https://github.com/Awehbelekker?tab=repositories")
