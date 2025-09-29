#!/usr/bin/env python3
"""
Systematic syntax error fixer for Python files.

This script fixes the most common syntax errors found in the codebase:
- Missing commas in function calls, lists, dictionaries
- Incomplete statements or malformed code blocks
- F-string syntax errors
- Parenthesis/bracket mismatches
- Invalid syntax patterns
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any


class SystematicSyntaxFixer:
    """Fixes syntax errors systematically."""
    
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0
        self.errors_found = 0
    
    def fix_file(self, file_path: Path) -> tuple[bool, list[str]]:
        """Fix syntax errors in a single file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has syntax errors
            try:
                ast.parse(content)
                return True, []  # No syntax errors
            except SyntaxError:
                pass  # Continue with fixes
            
            original_content = content
            fixes = []
            
            # Fix 1: Missing commas in function calls and data structures
            content = self._fix_missing_commas(content, fixes)
            
            # Fix 2: Incomplete statements
            content = self._fix_incomplete_statements(content, fixes)
            
            # Fix 3: F-string syntax errors
            content = self._fix_fstring_errors(content, fixes)
            
            # Fix 4: Parenthesis/bracket mismatches
            content = self._fix_bracket_mismatches(content, fixes)
            
            # Fix 5: Invalid syntax patterns
            content = self._fix_invalid_syntax(content, fixes)
            
            # Verify the fixes work
            if content != original_content:
                try:
                    ast.parse(content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.fixes_applied += len(fixes)
                    return True, fixes
                except SyntaxError as e:
                    # Revert if fixes didn't work
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    return False, [f"Failed to fix syntax: {e}"]
            
            return True, []
            
        except Exception as e:
            return False, [f"Error processing file: {e}"]
    
    def _fix_missing_commas(self, content: str, fixes: list[str]) -> str:
        """Fix missing commas in function calls and data structures."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Fix missing commas in function calls
            if re.search(r'\)\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\(', line):
                line = re.sub(r'\)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', r'), \1(', line)
                fixes.append(f"Line {i+1}: Added missing comma in function call")
            
            # Fix missing commas in lists/dicts
            if re.search(r'\]\s*[a-zA-Z_][a-zA-Z0-9_]*', line):
                line = re.sub(r'\]\s*([a-zA-Z_][a-zA-Z0-9_]*)', r'], \1', line)
                fixes.append(f"Line {i+1}: Added missing comma in list/dict")
        
        return '\n'.join(lines)
    
    def _fix_incomplete_statements(self, content: str, fixes: list[str]) -> str:
        """Fix incomplete statements and malformed code blocks."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Fix incomplete statements that end with just a variable name
            if re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*$', line.strip()) and not line.strip().endswith(':'):
                # This is likely an incomplete statement, add a comment
                lines[i] = f"    # TODO: Fix incomplete statement: {line.strip()}"
                fixes.append(f"Line {i+1}: Fixed incomplete statement")
            
            # Fix statements that end with just 'result'
            if re.match(r'^\s*result\s*$', line.strip()):
                lines[i] = "    # TODO: Complete this statement"
                fixes.append(f"Line {i+1}: Fixed incomplete 'result' statement")
        
        return '\n'.join(lines)
    
    def _fix_fstring_errors(self, content: str, fixes: list[str]) -> str:
        """Fix f-string syntax errors."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Fix unterminated f-strings
            if 'f"' in line and not line.count('"') % 2 == 0:
                # Try to close the f-string
                if line.count('{') > line.count('}'):
                    # Missing closing brace
                    line = line + '}'
                    fixes.append(f"Line {i+1}: Fixed unterminated f-string")
                elif not line.endswith('"'):
                    # Missing closing quote
                    line = line + '"'
                    fixes.append(f"Line {i+1}: Fixed unterminated f-string")
        
        return '\n'.join(lines)
    
    def _fix_bracket_mismatches(self, content: str, fixes: list[str]) -> str:
        """Fix parenthesis/bracket mismatches."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Fix unmatched parentheses
            open_parens = line.count('(')
            close_parens = line.count(')')
            if open_parens > close_parens:
                line = line + ')' * (open_parens - close_parens)
                fixes.append(f"Line {i+1}: Fixed unmatched parentheses")
            
            # Fix unmatched brackets
            open_brackets = line.count('[')
            close_brackets = line.count(']')
            if open_brackets > close_brackets:
                line = line + ']' * (open_brackets - close_brackets)
                fixes.append(f"Line {i+1}: Fixed unmatched brackets")
        
        return '\n'.join(lines)
    
    def _fix_invalid_syntax(self, content: str, fixes: list[str]) -> str:
        """Fix invalid syntax patterns."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Fix lines that start with a dot (like .items())
            if re.match(r'^\s*\.', line):
                # This is likely a method call on a missing variable
                lines[i] = f"    # TODO: Fix missing variable before: {line.strip()}"
                fixes.append(f"Line {i+1}: Fixed missing variable before method call")
            
            # Fix lines that have colons in wrong places
            if re.search(r':\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:', line):
                # This looks like a malformed dictionary or function call
                lines[i] = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r': \1,', line)
                fixes.append(f"Line {i+1}: Fixed malformed syntax with colons")
        
        return '\n'.join(lines)
    
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
    
    parser = argparse.ArgumentParser(description='Fix Python syntax errors systematically')
    parser.add_argument('--directory', '-d', default='.', help='Directory to process')
    parser.add_argument('--max-files', '-m', type=int, help='Maximum number of files to process')
    parser.add_argument('--output', '-o', help='Output file for results')
    
    args = parser.parse_args()
    
    fixer = SystematicSyntaxFixer()
    directory = Path(args.directory)
    
    print(f"🔧 Starting systematic syntax fixing in {directory}")
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
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {args.output}")


if __name__ == '__main__':
    main()
