"""
Quick script to add Polygon.io API key to .env file
"""
import os
from pathlib import Path

def add_polygon_key():
    env_path = Path(".env")
    polygon_key = "kpJXD4QiZcdSqsmkkkgj8XZQZy6eOjr3"
    
    # Read existing .env content
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Check if POLYGON_API_KEY already exists
    polygon_line_exists = False
    for i, line in enumerate(lines):
        if line.startswith('POLYGON_API_KEY='):
            lines[i] = f'POLYGON_API_KEY={polygon_key}\n'
            polygon_line_exists = True
            print(f"Updated existing POLYGON_API_KEY in .env")
            break
    
    # If not found, add it
    if not polygon_line_exists:
        # Add newline if file doesn't end with one
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'
        lines.append(f'POLYGON_API_KEY={polygon_key}\n')
        print(f"Added new POLYGON_API_KEY to .env")
    
    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print(f"Success - Polygon.io API key configured!")
    print(f"Key: {polygon_key}")
    
    # Also set in current environment
    os.environ['POLYGON_API_KEY'] = polygon_key
    print(f"Also set in current environment")

if __name__ == "__main__":
    add_polygon_key()
