#!/usr/bin/env python3
"""
Fix markdown linting issues in specific files mentioned in linting errors
"""

import re
from pathlib import Path

def fix_markdown_file(file_path: Path) -> bool:
    """Fix markdown linting issues in a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            is_heading = bool(re.match(r'^#{1,6}\s+', line))
            is_list_item = bool(re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line))
            is_fenced_code = line.strip().startswith('```')
            is_blank = not line.strip()
            
            # Remove trailing spaces (MD009)
            line = line.rstrip() + '\n'
            
            # Remove trailing punctuation from headings (MD026) - but only if it's just a colon
            if is_heading and line.rstrip().endswith(':'):
                stripped = line.rstrip()
                # Only remove if it's a simple trailing colon (not part of content like "Status:")
                if stripped[-1] == ':' and not any(x in stripped for x in ['Status:', 'Action:', 'Impact:', 'Details:']):
                    line = stripped[:-1] + '\n'
                # For headings that should have colons removed
                if any(x in stripped for x in ['To Check', 'Recommended', 'Action Required']):
                    line = stripped[:-1] + '\n'
            
            # Add blank line before heading if previous line isn't blank (MD022)
            if is_heading and i > 0:
                prev_line = lines[i - 1] if i > 0 else ''
                if prev_line.strip() and not prev_line.strip().startswith('#'):
                    fixed_lines.append('\n')
            
            fixed_lines.append(line)
            
            # Add blank line after heading if next line exists and isn't blank/heading/list (MD022)
            if is_heading and i < len(lines) - 1:
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                next_is_blank = not next_line.strip()
                next_is_heading = bool(re.match(r'^#{1,6}\s+', next_line))
                next_is_list = bool(re.match(r'^\s*[-*+]\s+', next_line) or re.match(r'^\s*\d+\.\s+', next_line))
                if not next_is_blank and not next_is_heading and not next_is_list:
                    fixed_lines.append('\n')
            
            # Add blank line before list if previous line isn't blank/heading/list (MD032)
            if is_list_item and i > 0:
                prev_line = lines[i - 1] if i > 0 else ''
                prev_is_blank = not prev_line.strip()
                prev_is_heading = bool(re.match(r'^#{1,6}\s+', prev_line))
                prev_is_list = bool(re.match(r'^\s*[-*+]\s+', prev_line) or re.match(r'^\s*\d+\.\s+', prev_line))
                if not prev_is_blank and not prev_is_heading and not prev_is_list:
                    fixed_lines.insert(-1, '\n')
            
            # Add blank line after list if next line exists and isn't blank/list/heading (MD032)
            if is_list_item and i < len(lines) - 1:
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                next_is_blank = not next_line.strip()
                next_is_heading = bool(re.match(r'^#{1,6}\s+', next_line))
                next_is_list = bool(re.match(r'^\s*[-*+]\s+', next_line) or re.match(r'^\s*\d+\.\s+', next_line))
                if not next_is_blank and not next_is_list and not next_is_heading:
                    # Check if this is the last item in the list
                    if i + 1 < len(lines):
                        fixed_lines.append('\n')
            
            # Fix MD031: Add blank lines around fenced code blocks
            if is_fenced_code:
                if i > 0:
                    prev_line = lines[i - 1] if i > 0 else ''
                    if prev_line.strip() and not prev_line.strip().startswith('```'):
                        fixed_lines.insert(-1, '\n')
                if i < len(lines) - 1:
                    next_line = lines[i + 1] if i + 1 < len(lines) else ''
                    if next_line.strip() and not next_line.strip().startswith('```'):
                        fixed_lines.append('\n')
            
            # Fix MD040: Add language to fenced code blocks if missing
            if is_fenced_code and '```' in line and len(line.strip()) == 3:
                # Check if next line is code (not another fence)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip() and not next_line.strip().startswith('```'):
                        # Try to detect language from content
                        if any(keyword in next_line for keyword in ['def ', 'class ', 'import ', 'from ']):
                            line = '```python\n'
                        elif any(keyword in next_line for keyword in ['function', 'const ', 'let ', 'var ']):
                            line = '```javascript\n'
                        elif any(keyword in next_line for keyword in ['SELECT', 'INSERT', 'UPDATE', 'CREATE']):
                            line = '```sql\n'
                        elif '$' in next_line or 'powershell' in next_line.lower():
                            line = '```powershell\n'
                        else:
                            line = '```text\n'
                        fixed_lines[-1] = line
            
            i += 1
        
        # Fix MD012: Remove multiple consecutive blank lines (keep max 1)
        content = ''.join(fixed_lines)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove trailing blank lines
        content = content.rstrip() + '\n'
        
        # Read original to compare
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix specific markdown files"""
    workspace_root = Path(__file__).parent
    
    # Specific files to fix based on linting errors
    files_to_fix = [
        'CRITICAL_ISSUES_STATUS_REPORT.md',
        'FINAL_STATUS_AND_SOLUTIONS.md',
        'TRADING_STATUS_YESTERDAY.md',
    ]
    
    # Also check Enterprise Package
    enterprise_root = workspace_root.parent / 'PROMETHEUS-Enterprise-Package-COMPLETE'
    if enterprise_root.exists():
        files_to_fix.append(enterprise_root / 'POSITION_ANALYSIS_ETHUSD_LTCUSD.md')
    
    fixed_count = 0
    for file_name in files_to_fix:
        if isinstance(file_name, Path):
            file_path = file_name
        else:
            file_path = workspace_root / file_name
        
        if file_path.exists():
            if fix_markdown_file(file_path):
                print(f"Fixed: {file_path.relative_to(workspace_root)}")
                fixed_count += 1
        else:
            print(f"Not found: {file_path}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()

