#!/usr/bin/env python3
"""
🧹 COMPONENT CLEANUP UTILITY
PROMETHEUS Trading Platform - Remove Unused Components

This script identifies and removes unused React components to optimize the codebase.
"""

import os
import re
import json
from pathlib import Path
from typing import Set, Dict, List

class ComponentCleanup:
    def __init__(self, frontend_path: str):
        self.frontend_path = Path(frontend_path)
        self.components_path = self.frontend_path / "src" / "components"
        self.src_path = self.frontend_path / "src"
        
        # Components that should never be removed (core components)
        self.protected_components = {
            'App.tsx',
            'Login.tsx',
            'UserDashboard.tsx',
            'UnifiedCockpitAdminDashboard.tsx',
            'UserRegistration.tsx',
            'InternalPaperTrading.tsx',
            'RealTimeWealthTracker.tsx',
            'TradingCommandCenter.tsx',
            'ErrorBoundary.tsx',
            'NavigationButton.tsx',
            'LoadingCard.tsx',
            'MobileNavigation.tsx'
        }
        
        self.used_components: Set[str] = set()
        self.all_components: Set[str] = set()
        self.unused_components: Set[str] = set()
        
    def scan_components(self) -> None:
        """Scan all component files in the components directory."""
        print("🔍 Scanning component files...")
        
        for file_path in self.components_path.rglob("*.tsx"):
            if file_path.is_file():
                component_name = file_path.name
                self.all_components.add(component_name)
                print(f"   📄 Found: {component_name}")
        
        print(f"📊 Total components found: {len(self.all_components)}")
    
    def find_component_usage(self) -> None:
        """Find which components are actually used in the codebase."""
        print("\n🔍 Analyzing component usage...")
        
        # Scan all TypeScript/JavaScript files
        for file_path in self.src_path.rglob("*.{tsx,ts,jsx,js}"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Find import statements
                    import_pattern = r"import\s+(?:\{[^}]*\}|\w+)\s+from\s+['\"]([^'\"]+)['\"]"
                    imports = re.findall(import_pattern, content)
                    
                    for import_path in imports:
                        # Extract component name from import path
                        if './components/' in import_path or '../components/' in import_path:
                            component_file = Path(import_path).name
                            if not component_file.endswith('.tsx'):
                                component_file += '.tsx'
                            
                            if component_file in self.all_components:
                                self.used_components.add(component_file)
                                print(f"   [CHECK] Used: {component_file} (in {file_path.name})")
                    
                    # Also check for direct component references
                    for component in self.all_components:
                        component_name = component.replace('.tsx', '')
                        if re.search(rf'\b{component_name}\b', content):
                            self.used_components.add(component)
                            
                except Exception as e:
                    print(f"   [WARNING]️ Error reading {file_path}: {e}")
        
        print(f"📊 Components in use: {len(self.used_components)}")
    
    def identify_unused_components(self) -> None:
        """Identify components that are not used anywhere."""
        print("\n🧹 Identifying unused components...")
        
        self.unused_components = self.all_components - self.used_components - self.protected_components
        
        print(f"📊 Unused components found: {len(self.unused_components)}")
        
        if self.unused_components:
            print("\n🗑️ UNUSED COMPONENTS:")
            for component in sorted(self.unused_components):
                print(f"   [ERROR] {component}")
        else:
            print("   [CHECK] No unused components found!")
    
    def generate_cleanup_report(self) -> Dict:
        """Generate a detailed cleanup report."""
        report = {
            "total_components": len(self.all_components),
            "used_components": len(self.used_components),
            "protected_components": len(self.protected_components),
            "unused_components": len(self.unused_components),
            "cleanup_candidates": list(self.unused_components),
            "protected_list": list(self.protected_components),
            "used_list": list(self.used_components)
        }
        
        return report
    
    def create_backup(self) -> str:
        """Create a backup of components before cleanup."""
        import shutil
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.frontend_path / f"components_backup_{timestamp}"
        
        print(f"\n💾 Creating backup at: {backup_path}")
        shutil.copytree(self.components_path, backup_path)
        
        return str(backup_path)
    
    def remove_unused_components(self, confirm: bool = False) -> None:
        """Remove unused components (with confirmation)."""
        if not self.unused_components:
            print("[CHECK] No components to remove!")
            return
        
        if not confirm:
            print("\n[WARNING]️ DRY RUN - Components that would be removed:")
            for component in sorted(self.unused_components):
                component_path = self.components_path / component
                print(f"   🗑️ Would remove: {component_path}")
            return
        
        print(f"\n🗑️ Removing {len(self.unused_components)} unused components...")
        
        removed_count = 0
        for component in self.unused_components:
            component_path = self.components_path / component
            try:
                if component_path.exists():
                    os.remove(component_path)
                    print(f"   [CHECK] Removed: {component}")
                    removed_count += 1
                else:
                    print(f"   [WARNING]️ Not found: {component}")
            except Exception as e:
                print(f"   [ERROR] Error removing {component}: {e}")
        
        print(f"\n🎉 Cleanup complete! Removed {removed_count} components.")
    
    def run_analysis(self) -> Dict:
        """Run the complete component analysis."""
        print("🧹 PROMETHEUS COMPONENT CLEANUP UTILITY")
        print("=" * 50)
        
        self.scan_components()
        self.find_component_usage()
        self.identify_unused_components()
        
        report = self.generate_cleanup_report()
        
        print("\n📊 CLEANUP SUMMARY:")
        print(f"   📄 Total Components: {report['total_components']}")
        print(f"   [CHECK] Used Components: {report['used_components']}")
        print(f"   🛡️ Protected Components: {report['protected_components']}")
        print(f"   🗑️ Unused Components: {report['unused_components']}")
        
        return report

def main():
    """Main execution function."""
    frontend_path = "frontend"
    
    if not os.path.exists(frontend_path):
        print("[ERROR] Frontend directory not found!")
        return
    
    cleanup = ComponentCleanup(frontend_path)
    report = cleanup.run_analysis()
    
    # Save report
    with open("component_cleanup_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Report saved to: component_cleanup_report.json")
    
    # Ask user if they want to proceed with cleanup
    if report['unused_components'] > 0:
        print("\n🤔 Would you like to:")
        print("1. Create backup and remove unused components")
        print("2. Just create backup")
        print("3. Exit without changes")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            backup_path = cleanup.create_backup()
            print(f"[CHECK] Backup created: {backup_path}")
            
            confirm = input("\n[WARNING]️ Confirm removal of unused components? (yes/no): ").strip().lower()
            if confirm == "yes":
                cleanup.remove_unused_components(confirm=True)
            else:
                print("[ERROR] Cleanup cancelled.")
        
        elif choice == "2":
            backup_path = cleanup.create_backup()
            print(f"[CHECK] Backup created: {backup_path}")
        
        else:
            print("👋 Exiting without changes.")
    
    print("\n🎉 Component analysis complete!")

if __name__ == "__main__":
    main()
