#!/usr/bin/env python3
"""
Conservative syntax error fixer for Python files.

This script fixes only the most obvious and safe syntax errors:
- Missing commas in function calls (only when clearly missing)
- F-string syntax errors (only when clearly malformed)
- Parenthesis/bracket mismatches (only when clearly wrong)
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any


class ConservativeSyntaxFixer:
    """Fixes only the most obvious syntax errors conservatively."""
    
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0
        self.errors_found = 0
    
    def fix_file(self, file_path: Path) -> tuple[bool, list[str]]:
        """Fix syntax errors in a single file conservatively."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_applied = []
            
            # Apply only the most conservative fixes
            content, fixes = self.fix_obvious_f_string_errors(content)
            fixes_applied.extend(fixes)
            
            content, fixes = self.fix_obvious_bracket_mismatches(content)
            fixes_applied.extend(fixes)
            
            content, fixes = self.fix_obvious_missing_commas(content)
            fixes_applied.extend(fixes)
            
            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixes_applied += len(fixes_applied)
                return True, fixes_applied
            
            return False, []
            
        except Exception as e:
            return False, [f"Error processing file: {e}"]
    
    def fix_obvious_f_string_errors(self, content: str) -> tuple[str, list[str]]:
        """Fix only obvious f-string syntax errors."""
        fixes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Fix f-string with missing closing brace (only if it's obvious)
            # Pattern: f"text {variable" -> f"text {variable}"
            if 'f"' in line and line.count('{') > line.count('}'):
                # Only fix if there's exactly one missing closing brace
                missing_braces = line.count('{') - line.count('}')
                if missing_braces == 1:
                    # Find the last { and add }
                    last_brace_pos = line.rfind('{')
                    if last_brace_pos != -1:
                        line = line[:last_brace_pos+1] + '}' + line[last_brace_pos+1:]
                        if line != original_line:
                            fixes.append(f"Line {i+1}: Fixed f-string missing closing brace")
            
            lines[i] = line
        
        return '\n'.join(lines), fixes
    
    def fix_obvious_bracket_mismatches(self, content: str) -> tuple[str, list[str]]:
        """Fix only obvious bracket mismatches."""
        fixes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Fix obvious bracket mismatches
            # Pattern: [text} -> [text]
            if '[' in line and '}' in line and ']' not in line:
                line = line.replace('}', ']')
                if line != original_line:
                    fixes.append(f"Line {i+1}: Fixed bracket mismatch")
            
            # Pattern: {text] -> {text}
            if '{' in line and ']' in line and '}' not in line:
                line = line.replace(']', '}')
                if line != original_line:
                    fixes.append(f"Line {i+1}: Fixed brace mismatch")
            
            lines[i] = line
        
        return '\n'.join(lines), fixes
    
    def fix_obvious_missing_commas(self, content: str) -> tuple[str, list[str]]:
        """Fix only obvious missing commas in function calls."""
        fixes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Fix missing commas in function calls (only when very obvious)
            # Pattern: function(arg1 arg2) -> function(arg1, arg2)
            # Only fix if there are exactly two arguments without comma
            if re.search(r'\([^)]*[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*[^)]*\)', line):
                # Count arguments - only fix if there are exactly 2 without comma
                args_match = re.search(r'\(([^)]+)\)', line)
                if args_match:
                    args = args_match.group(1)
                    # Only fix if there are exactly 2 arguments without comma
                    if args.count(',') == 0 and len(args.split()) == 2:
                        line = re.sub(r'(\w+)\s+(\w+)', r'\1, \2', line)
                        if line != original_line:
                            fixes.append(f"Line {i+1}: Added missing comma in function call")
            
            lines[i] = line
        
        return '\n'.join(lines), fixes
    
    def scan_and_fix_directory(self, directory: Path, exclude_patterns: list[str] | None = None) -> dict[str, Any]:
        """Scan directory and fix syntax errors conservatively."""
        if exclude_patterns is None:
            exclude_patterns = ['__pycache__', '.git', 'node_modules', '600_archives', 'evals_bundle_']
        
        results = {
            'files_processed': 0,
            'files_fixed': 0,
            'total_fixes': 0,
            'errors': []
        }
        
        print(f"Scanning {directory} for syntax errors...")
        
        for py_file in directory.rglob('*.py'):
            # Skip excluded patterns
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue
            
            # Check if file has syntax errors first
            try:
                with open(py_file, encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                continue  # No syntax errors, skip
            except SyntaxError:
                pass  # Has syntax errors, proceed to fix
            except Exception:
                continue  # Other errors, skip
            
            results['files_processed'] += 1
            
            # Try to fix the file
            fixed, fixes = self.fix_file(py_file)
            
            if fixed:
                results['files_fixed'] += 1
                results['total_fixes'] += len(fixes)
                print(f"Fixed {py_file}: {len(fixes)} fixes applied")
                for fix in fixes:
                    print(f"  - {fix}")
            else:
                results['errors'].append(f"Could not fix {py_file}")
        
        return results


def main():
    """Main function to run conservative syntax error fixing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix syntax errors in Python files conservatively")
    parser.add_argument("--directory", default=".", help="Directory to scan (default: current directory)")
    parser.add_argument("--output", help="Output file for detailed results")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist")
        return 1
    
    fixer = ConservativeSyntaxFixer()
    results = fixer.scan_and_fix_directory(directory)
    
    print(f"\n{'='*60}")
    print("CONSERVATIVE SYNTAX FIXING RESULTS")
    print(f"{'='*60}")
    print(f"Files processed: {results['files_processed']}")
    print(f"Files fixed: {results['files_fixed']}")
    print(f"Total fixes applied: {results['total_fixes']}")
    
    if results['errors']:
        print("\nErrors encountered:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")
    
    return 0 if results['files_fixed'] > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
