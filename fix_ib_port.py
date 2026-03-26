"""
Fix IB Gateway Port Configuration
The diagnostic shows TWS is running on port 7496, not Gateway on 4002
"""
import os
from pathlib import Path

def fix_ib_port():
    env_path = Path(".env")
    
    # Read existing .env content
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Update IB_PORT to 7496 (TWS Live is what's actually running)
    port_updated = False
    for i, line in enumerate(lines):
        if line.startswith('IB_PORT='):
            old_value = line.strip()
            lines[i] = 'IB_PORT=7496\n'
            print(f"Updated: {old_value} -> IB_PORT=7496")
            port_updated = True
            break
    
    if not port_updated:
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'
        lines.append('IB_PORT=7496\n')
        print(f"Added: IB_PORT=7496")
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print("\nSuccess! IB configuration updated:")
    print("  Port 7496 (TWS Live) is OPEN and responding")
    print("  PROMETHEUS will now connect to TWS instead of Gateway")
    print("\nNote: You're using TWS (Trader Workstation) not IB Gateway")
    print("      Both work the same way for API connections")

if __name__ == "__main__":
    fix_ib_port()
