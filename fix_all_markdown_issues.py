#!/usr/bin/env python3
"""
Comprehensive markdown linting fixer
Fixes: MD022, MD032, MD026, MD012, MD031, MD040, MD009
"""

import re
from pathlib import Path

def fix_markdown_file(file_path: Path) -> bool:
    """Fix all markdown linting issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Fix MD012: Remove multiple consecutive blank lines (keep max 1)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Fix MD009: Remove trailing spaces
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]
        content = '\n'.join(lines)
        
        # Fix MD026: Remove trailing punctuation from headings (colons, periods, etc.)
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            if re.match(r'^#{1,6}\s+', line):
                # Remove trailing punctuation (:, ., !, ?)
                stripped = line.rstrip()
                if stripped and stripped[-1] in ':!?.':
                    # Only remove if it's simple trailing punctuation
                    # Keep if it's part of content like "Status:" in bold
                    if not any(x in stripped for x in ['**Status:**', '**Action:**', '**Impact:**', '**Details:**']):
                        line = stripped[:-1]
            fixed_lines.append(line)
        content = '\n'.join(fixed_lines)
        
        # Fix MD022 and MD032: Add blank lines around headings and lists
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            is_heading = bool(re.match(r'^#{1,6}\s+', line))
            is_list_item = bool(re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line))
            is_fenced_code = line.strip().startswith('```')
            is_blank = not line.strip()
            
            # Add blank line before heading if previous line isn't blank/heading
            if is_heading and i > 0:
                prev_line = lines[i - 1] if i > 0 else ''
                if prev_line.strip() and not re.match(r'^#{1,6}\s+', prev_line):
                    fixed_lines.append('')
            
            fixed_lines.append(line)
            
            # Add blank line after heading if next line exists and isn't blank/heading/list
            if is_heading and i < len(lines) - 1:
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                next_is_blank = not next_line.strip()
                next_is_heading = bool(re.match(r'^#{1,6}\s+', next_line))
                next_is_list = bool(re.match(r'^\s*[-*+]\s+', next_line) or re.match(r'^\s*\d+\.\s+', next_line))
                if not next_is_blank and not next_is_heading and not next_is_list:
                    fixed_lines.append('')
            
            # Add blank line before list if previous line isn't blank/heading/list
            if is_list_item and i > 0:
                prev_line = lines[i - 1] if i > 0 else ''
                prev_is_blank = not prev_line.strip()
                prev_is_heading = bool(re.match(r'^#{1,6}\s+', prev_line))
                prev_is_list = bool(re.match(r'^\s*[-*+]\s+', prev_line) or re.match(r'^\s*\d+\.\s+', prev_line))
                if not prev_is_blank and not prev_is_heading and not prev_is_list:
                    fixed_lines.insert(-1, '')
            
            # Add blank line after list if next line exists and isn't blank/list/heading
            if is_list_item and i < len(lines) - 1:
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                next_is_blank = not next_line.strip()
                next_is_heading = bool(re.match(r'^#{1,6}\s+', next_line))
                next_is_list = bool(re.match(r'^\s*[-*+]\s+', next_line) or re.match(r'^\s*\d+\.\s+', next_line))
                if not next_is_blank and not next_is_list and not next_is_heading:
                    # Check if this is the last item in the list
                    if i + 1 < len(lines):
                        fixed_lines.append('')
            
            # Fix MD031: Add blank lines around fenced code blocks
            if is_fenced_code:
                if i > 0:
                    prev_line = lines[i - 1] if i > 0 else ''
                    if prev_line.strip() and not prev_line.strip().startswith('```'):
                        fixed_lines.insert(-1, '')
                if i < len(lines) - 1:
                    next_line = lines[i + 1] if i + 1 < len(lines) else ''
                    if next_line.strip() and not next_line.strip().startswith('```'):
                        fixed_lines.append('')
            
            # Fix MD040: Add language to fenced code blocks if missing
            if is_fenced_code and '```' in line and len(line.strip()) == 3:
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip() and not next_line.strip().startswith('```'):
                        if any(k in next_line for k in ['def ', 'class ', 'import ', 'from ', 'python']):
                            line = '```python\n'
                        elif any(k in next_line for k in ['function', 'const ', 'let ', 'var ', 'javascript']):
                            line = '```javascript\n'
                        elif any(k in next_line for k in ['SELECT', 'INSERT', 'UPDATE', 'CREATE', 'sql']):
                            line = '```sql\n'
                        elif '$' in next_line or 'powershell' in next_line.lower() or 'Get-' in next_line or 'Set-' in next_line:
                            line = '```powershell\n'
                        elif 'bash' in next_line.lower() or '#!/bin' in next_line:
                            line = '```bash\n'
                        else:
                            line = '```text\n'
                        fixed_lines[-1] = line
            
            i += 1
        
        content = '\n'.join(fixed_lines)
        
        # Final cleanup: Remove multiple consecutive blank lines again
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove trailing blank lines
        content = content.rstrip() + '\n'
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fix specific markdown files"""
    workspace_root = Path(__file__).parent
    
    files_to_fix = [
        'CRITICAL_ISSUES_STATUS_REPORT.md',
        'FINAL_STATUS_AND_SOLUTIONS.md',
        'TRADING_STATUS_YESTERDAY.md',
        'CURRENT_SYSTEM_STATUS.md',
    ]
    
    fixed_count = 0
    for file_name in files_to_fix:
        file_path = workspace_root / file_name
        if file_path.exists():
            if fix_markdown_file(file_path):
                print(f"Fixed: {file_name}")
                fixed_count += 1
        else:
            print(f"Not found: {file_name}")
    
    # Also fix Enterprise Package file
    enterprise_file = workspace_root.parent / 'PROMETHEUS-Enterprise-Package-COMPLETE' / 'POSITION_ANALYSIS_ETHUSD_LTCUSD.md'
    if enterprise_file.exists():
        if fix_markdown_file(enterprise_file):
            print(f"Fixed: {enterprise_file.name}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()

