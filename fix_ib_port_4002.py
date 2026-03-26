"""
Fix IB Port - User's TWS is on port 4002
"""
from pathlib import Path

env_path = Path(".env")

if env_path.exists():
    with open(env_path, 'r') as f:
        lines = f.readlines()
else:
    lines = []

# Update IB_PORT to 4002 (from 7496)
port_updated = False
for i, line in enumerate(lines):
    if line.startswith('IB_PORT='):
        old_value = line.strip()
        lines[i] = 'IB_PORT=4002\n'
        print(f"Updated: {old_value} -> IB_PORT=4002")
        port_updated = True
        break

if not port_updated:
    if lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'
    lines.append('IB_PORT=4002\n')
    print(f"Added: IB_PORT=4002")

with open(env_path, 'w') as f:
    f.writelines(lines)

print("\n[SUCCESS] IB port updated to 4002")
print("Your TWS API Settings show port 4002 - now PROMETHEUS will connect correctly!")
