#!/usr/bin/env python3
"""
Fix common markdown linting issues:
- MD022: Headings should be surrounded by blank lines
- MD032: Lists should be surrounded by blank lines
- MD026: Remove trailing punctuation from headings
- MD012: Remove multiple consecutive blank lines
- MD031: Add blank lines around fenced code blocks
- MD040: Add language to fenced code blocks
"""

import re
import os
from pathlib import Path

def fix_markdown_file(file_path: Path) -> bool:
    """Fix markdown linting issues in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix MD012: Remove multiple consecutive blank lines (keep max 1)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Fix MD026: Remove trailing punctuation from headings (:, ., !, ?)
        # But preserve headings that end with punctuation that's part of the content
        lines = content.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines):
            # Check if it's a heading
            if re.match(r'^#{1,6}\s+', line):
                # Remove trailing punctuation (:, ., !, ?) but keep if it's part of content
                # Only remove if it's at the very end
                if line.rstrip().endswith((':', '.', '!', '?')):
                    # Check if it's a simple trailing punctuation (not part of content)
                    stripped = line.rstrip()
                    if stripped[-1] in ':!?':
                        # Remove trailing punctuation
                        line = stripped[:-1] + line[len(stripped):]
            fixed_lines.append(line)
        content = '\n'.join(fixed_lines)
        
        # Fix MD022 and MD032: Add blank lines around headings and lists
        lines = content.split('\n')
        fixed_lines = []
        prev_line_was_blank = False
        
        for i, line in enumerate(lines):
            is_heading = bool(re.match(r'^#{1,6}\s+', line))
            is_list_item = bool(re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line))
            is_fenced_code = line.strip().startswith('```')
            is_blank = not line.strip()
            
            # Add blank line before heading if previous line isn't blank
            if is_heading and i > 0 and not prev_line_was_blank:
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
            if is_list_item and i > 0 and not prev_line_was_blank:
                prev_line = lines[i - 1] if i > 0 else ''
                prev_is_heading = bool(re.match(r'^#{1,6}\s+', prev_line))
                prev_is_list = bool(re.match(r'^\s*[-*+]\s+', prev_line) or re.match(r'^\s*\d+\.\s+', prev_line))
                if not prev_is_heading and not prev_is_list:
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
                if i > 0 and not prev_line_was_blank:
                    fixed_lines.insert(-1, '')
                if i < len(lines) - 1:
                    next_line = lines[i + 1] if i + 1 < len(lines) else ''
                    if next_line.strip() and not next_line.strip().startswith('```'):
                        fixed_lines.append('')
            
            # Fix MD040: Add language to fenced code blocks if missing
            if is_fenced_code and '```' in line and len(line.strip()) == 3:
                # Check if next line is code (not another fence)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip() and not next_line.strip().startswith('```'):
                        # Try to detect language from content
                        if any(keyword in next_line for keyword in ['def ', 'class ', 'import ', 'from ']):
                            line = '```python'
                        elif any(keyword in next_line for keyword in ['function', 'const ', 'let ', 'var ']):
                            line = '```javascript'
                        elif any(keyword in next_line for keyword in ['SELECT', 'INSERT', 'UPDATE', 'CREATE']):
                            line = '```sql'
                        else:
                            line = '```text'
                        fixed_lines[-1] = line
            
            prev_line_was_blank = is_blank
        
        content = '\n'.join(fixed_lines)
        
        # Final cleanup: Remove multiple consecutive blank lines again
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix markdown files in the workspace"""
    workspace_root = Path(__file__).parent
    
    # Find all markdown files
    md_files = []
    for root, dirs, files in os.walk(workspace_root):
        # Skip archive directories
        if 'ARCHIVE' in root or '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                md_files.append(Path(root) / file)
    
    print(f"Found {len(md_files)} markdown files")
    
    fixed_count = 0
    for md_file in md_files:
        if fix_markdown_file(md_file):
            print(f"Fixed: {md_file.relative_to(workspace_root)}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()

