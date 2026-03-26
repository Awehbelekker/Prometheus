#!/usr/bin/env python3
"""
List all Awehbelekker repositories with full details
"""

import requests
import json

def get_all_repos(username="Awehbelekker"):
    """Get all repositories"""
    url = f"https://api.github.com/users/{username}/repos"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            repos = response.json()
            return repos
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    repos = get_all_repos()
    
    print(f"Total repositories found: {len(repos)}\n")
    print("="*80)
    print("ALL REPOSITORIES")
    print("="*80)
    
    high_priority_keywords = ['hrm', 'reasoning', 'universal', 'framework', 'shadow', 
                             'meta', 'ensemble', 'mass', 'trading', 'finance', 
                             'agent', 'workflow', 'ai', 'ml', 'intelligence']
    
    high_priority = []
    all_repos = []
    
    for i, repo in enumerate(repos, 1):
        name = repo['name']
        desc = repo.get('description', '') or ''
        desc_clean = desc.encode('ascii', 'replace').decode('ascii')
        
        all_repos.append({
            'num': i,
            'name': name,
            'description': desc_clean,
            'url': repo['html_url'],
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'language': repo.get('language', 'N/A')
        })
        
        # Check if high priority
        desc_lower = desc.lower()
        name_lower = name.lower()
        relevance = sum(1 for kw in high_priority_keywords if kw in desc_lower or kw in name_lower)
        
        if relevance > 0:
            high_priority.append({
                'num': i,
                'name': name,
                'description': desc_clean,
                'url': repo['html_url'],
                'relevance': relevance
            })
    
    # Print all repositories
    for repo in all_repos:
        print(f"{repo['num']:2d}. {repo['name']}")
        if repo['description']:
            print(f"     {repo['description'][:70]}")
        print(f"     URL: {repo['url']}")
        print(f"     Stars: {repo['stars']}, Forks: {repo['forks']}, Language: {repo['language']}")
        print()
    
    # Print high priority summary
    print("\n" + "="*80)
    print(f"HIGH-PRIORITY REPOSITORIES ({len(high_priority)} found)")
    print("="*80)
    
    for repo in sorted(high_priority, key=lambda x: x['relevance'], reverse=True):
        print(f"\n[{repo['relevance']}/10] {repo['name']}")
        print(f"   {repo['description']}")
        print(f"   {repo['url']}")

