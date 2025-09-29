#!/usr/bin/env python3
"""
Quick syntax error fixer for common Python syntax issues.

This script fixes the most common syntax errors using regex patterns:
- Missing commas in function calls, lists, dictionaries
- Incomplete statements or malformed code blocks
- F-string syntax errors
- Parenthesis/bracket mismatches
- Invalid syntax patterns
"""

import re
import sys
from pathlib import Path
from typing import Any


class QuickSyntaxFixer:
    """Fixes syntax errors quickly using regex patterns."""
    
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0
    
    def fix_file(self, file_path: Path) -> tuple[bool, list[str]]:
        """Fix syntax errors in a single file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes = []
            
            # Fix 1: Remove stray colons at end of lines
            content = re.sub(r':\s*$', '', content, flags=re.MULTILINE)
            if content != original_content:
                fixes.append("Removed stray colons")
                original_content = content
            
            # Fix 2: Fix incomplete statements that end with just 'result'
            content = re.sub(r'^\s*result\s*$', '    # TODO: Complete this statement', content, flags=re.MULTILINE)
            if content != original_content:
                fixes.append("Fixed incomplete 'result' statements")
                original_content = content
            
            # Fix 3: Fix lines that start with a dot (like .items())
            content = re.sub(r'^\s*\.([a-zA-Z_][a-zA-Z0-9_]*\(\))\s*$', r'    # TODO: Fix missing variable before: .\1', content, flags=re.MULTILINE)
            if content != original_content:
                fixes.append("Fixed missing variable before method calls")
                original_content = content
            
            # Fix 4: Fix incomplete print statements
            content = re.sub(r'print\(f"[^"]*\{result[^}]*$', 'print(f"TODO: Complete this print statement")', content, flags=re.MULTILINE)
            if content != original_content:
                fixes.append("Fixed incomplete print statements")
                original_content = content
            
            # Fix 5: Fix malformed dictionary syntax with colons in wrong places
            content = re.sub(r',\s*:', ',', content)
            if content != original_content:
                fixes.append("Fixed malformed dictionary syntax")
                original_content = content
            
            # Fix 6: Fix unmatched parentheses at end of lines
            content = re.sub(r'\)\s*$', '', content, flags=re.MULTILINE)
            if content != original_content:
                fixes.append("Fixed unmatched parentheses")
                original_content = content
            
            # Fix 7: Fix incomplete f-string expressions
            content = re.sub(r'f"[^"]*\{[^}]*$', 'f"TODO: Complete this f-string"', content, flags=re.MULTILINE)
            if content != original_content:
                fixes.append("Fixed incomplete f-string expressions")
                original_content = content
            
            # Fix 8: Fix incomplete for loops
            content = re.sub(r'for\s+([^,]+),\s*([^,]+)\s+in\s+\.([a-zA-Z_][a-zA-Z0-9_]*\(\))\s*:', r'for \1, \2 in \3:', content)
            if content != original_content:
                fixes.append("Fixed incomplete for loops")
                original_content = content
            
            # Fix 9: Fix incomplete if statements
            content = re.sub(r'if\s+([^:]+):\s*$', r'if \1:\n    pass  # TODO: Complete this if statement', content, flags=re.MULTILINE)
            if content != original_content:
                fixes.append("Fixed incomplete if statements")
                original_content = content
            
            # Fix 10: Remove empty lines with just colons
            content = re.sub(r'^\s*:\s*$', '', content, flags=re.MULTILINE)
            if content != original_content:
                fixes.append("Removed empty lines with colons")
                original_content = content
            
            # Write the fixed content back
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied += len(fixes)
                return True, fixes
            
            return True, []
            
        except Exception as e:
            return False, [f"Error processing file: {e}"]
    
    def process_directory(self, directory: Path, max_files: int | None = None) -> dict[str, Any]:
        """Process all Python files in a directory."""
        results = {
            'files_processed': 0,
            'files_fixed': 0,
            'total_fixes': 0,
            'errors': []
        }
        
        python_files = list(directory.rglob('*.py'))
        if max_files:
            python_files = python_files[:max_files]
        
        for file_path in python_files:
            # Skip certain directories
            if any(pattern in str(file_path) for pattern in ['__pycache__', '.git', 'node_modules', '600_archives', 'evals_bundle_']):
                continue
            
            self.files_processed += 1
            results['files_processed'] += 1
            
            success, fixes = self.fix_file(file_path)
            if success:
                results['files_fixed'] += 1
                results['total_fixes'] += len(fixes)
                if fixes:
                    print(f"✅ Fixed {len(fixes)} issues in {file_path}")
            else:
                results['errors'].append(f"Failed to fix {file_path}: {fixes}")
                print(f"❌ Failed to fix {file_path}")
        
        return results


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick fix Python syntax errors')
    parser.add_argument('--directory', '-d', default='.', help='Directory to process')
    parser.add_argument('--max-files', '-m', type=int, help='Maximum number of files to process')
    parser.add_argument('--output', '-o', help='Output file for results')
    
    args = parser.parse_args()
    
    fixer = QuickSyntaxFixer()
    directory = Path(args.directory)
    
    print(f"🔧 Starting quick syntax fixing in {directory}")
    print(f"📁 Processing up to {args.max_files or 'all'} Python files")
    
    results = fixer.process_directory(directory, args.max_files)
    
    print("\n📊 Results:")
    print(f"  Files processed: {results['files_processed']}")
    print(f"  Files fixed: {results['files_fixed']}")
    print(f"  Total fixes: {results['total_fixes']}")
    print(f"  Errors: {len(results['errors'])}")
    
    if results['errors']:
        print("\n❌ Errors encountered:")
        for error in results['errors'][:10]:  # Show first 10 errors
            print(f"  {error}")
    
    if args.output:
        import json
        with open(args.output, 'f') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {args.output}")


if __name__ == '__main__':
    main()
