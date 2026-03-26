"""
IB Gateway Configuration Fix
Automatically configures IB Gateway for API access on port 4002
"""

import os
import shutil
from datetime import datetime

print("=" * 70)
print("IB GATEWAY CONFIGURATION FIX")
print("=" * 70)

# Configuration file path
config_file = r"C:\Jts\ibgateway\1040\jts.ini"
backup_file = config_file + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not os.path.exists(config_file):
    print(f"❌ Configuration file not found: {config_file}")
    print("   Please make sure IB Gateway is installed")
    exit(1)

print(f"\n📁 Configuration file: {config_file}")
print(f"💾 Creating backup: {backup_file}")

# Create backup
shutil.copy2(config_file, backup_file)
print("✅ Backup created")

# Read current configuration
with open(config_file, 'r') as f:
    lines = f.readlines()

print("\n🔍 Current Configuration:")
for line in lines:
    if any(key in line for key in ['LocalServerPort', 'TrustedIPs', 'ApiOnly']):
        print(f"   {line.strip()}")

# Update configuration
new_lines = []
in_ibgateway_section = False
port_updated = False
trusted_ips_found = False
api_only_found = False

for line in lines:
    # Track which section we're in
    if line.strip() == '[IBGateway]':
        in_ibgateway_section = True
        new_lines.append(line)
        continue
    elif line.strip().startswith('[') and line.strip() != '[IBGateway]':
        # Entering a new section - add missing settings if needed
        if in_ibgateway_section:
            if not port_updated:
                new_lines.append('LocalServerPort=4002\n')
                print("   ➕ Added: LocalServerPort=4002")
            if not trusted_ips_found:
                new_lines.append('TrustedIPs=127.0.0.1\n')
                print("   ➕ Added: TrustedIPs=127.0.0.1")
            if not api_only_found:
                new_lines.append('ApiOnly=true\n')
                print("   ➕ Added: ApiOnly=true")
        in_ibgateway_section = False
        new_lines.append(line)
        continue
    
    # Update settings in IBGateway section
    if in_ibgateway_section:
        if line.startswith('LocalServerPort='):
            new_lines.append('LocalServerPort=4002\n')
            port_updated = True
            print("   ✏️  Updated: LocalServerPort=4002")
        elif line.startswith('TrustedIPs='):
            # Keep existing trusted IPs but ensure 127.0.0.1 is included
            current_ips = line.split('=')[1].strip()
            if '127.0.0.1' not in current_ips:
                if current_ips:
                    new_ips = current_ips + ',127.0.0.1'
                else:
                    new_ips = '127.0.0.1'
                new_lines.append(f'TrustedIPs={new_ips}\n')
                print(f"   ✏️  Updated: TrustedIPs={new_ips}")
            else:
                new_lines.append(line)
            trusted_ips_found = True
        elif line.startswith('ApiOnly='):
            new_lines.append('ApiOnly=true\n')
            api_only_found = True
            print("   ✏️  Updated: ApiOnly=true")
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

# Handle case where we're still in IBGateway section at end of file
if in_ibgateway_section:
    if not port_updated:
        new_lines.append('LocalServerPort=4002\n')
        print("   ➕ Added: LocalServerPort=4002")
    if not trusted_ips_found:
        new_lines.append('TrustedIPs=127.0.0.1\n')
        print("   ➕ Added: TrustedIPs=127.0.0.1")
    if not api_only_found:
        new_lines.append('ApiOnly=true\n')
        print("   ➕ Added: ApiOnly=true")

# Write updated configuration
with open(config_file, 'w') as f:
    f.writelines(new_lines)

print("\n✅ Configuration file updated successfully!")

print("\n📋 Updated Configuration:")
with open(config_file, 'r') as f:
    for line in f:
        if any(key in line for key in ['LocalServerPort', 'TrustedIPs', 'ApiOnly']):
            print(f"   {line.strip()}")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("1. ✅ Configuration file has been updated")
print("2. 🔄 Start IB Gateway and log in")
print("3. ⚙️  Go to: Configure → Settings → API → Settings")
print("4. ✅ Verify 'Enable ActiveX and Socket Clients' is CHECKED")
print("5. ✅ Verify Socket port shows: 4002")
print("6. 💾 Click Apply, then OK")
print("7. ⏳ Wait 10 seconds for settings to activate")
print("8. 🧪 Run: python ib_connection_diagnostic.py")
print("=" * 70)

