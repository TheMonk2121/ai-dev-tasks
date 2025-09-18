#!/usr/bin/env python3
"""
DEPRECATED: This file has been moved to 600_archives/ as it's no longer needed.

Migrate relative imports to absolute imports across the repository.

This script systematically converts relative imports to absolute imports
following PEP 8 recommendations and project standards.

STATUS: DEPRECATED - Migration completed successfully. This file is no longer needed
and has been moved to 600_archives/ for historical reference only.
"""

import ast
import re
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

def find_relative_imports(file_path: Path) -> list[tuple[int, str, str]]:
    """Find relative imports in a Python file.
    
    Returns:
        List of (line_number, original_import, suggested_absolute_import)
    """
    relative_imports: list[tuple[int, str, str]] = []
    
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level > 0:  # Relative import
                    line_num = node.lineno
                    module = node.module or ""
                    
                    # Calculate absolute path
                    current_depth = len(file_path.parts) - len(PROJECT_ROOT.parts)
                    
                    # Build absolute import path
                    if current_depth <= 1:
                        # File is in project root or one level deep
                        abs_path = f"src.{module}" if file_path.parts[-2] == "src" else module
                    else:
                        # File is deeper, need to calculate relative path to src
                        rel_path = file_path.relative_to(PROJECT_ROOT)
                        if str(rel_path).startswith("src/"):
                            abs_path = f"src.{module}"
                        elif str(rel_path).startswith("scripts/"):
                            abs_path = f"scripts.{module}"
                        elif str(rel_path).startswith("evals/"):
                            abs_path = f"evals.{module}"
                        else:
                            abs_path = module
                    
                    # Get the original import line
                    lines = content.split('\n')
                    original_line = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    relative_imports.append((line_num, original_line.strip(), abs_path))
    
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file_path}: {e}")
    
    return relative_imports

def convert_relative_to_absolute(file_path: Path, dry_run: bool = True) -> list[str]:
    """Convert relative imports to absolute imports in a file.
    
    Args:
        file_path: Path to the Python file
        dry_run: If True, only show what would be changed
        
    Returns:
        List of changes made
    """
    changes: list[str] = []
    relative_imports = find_relative_imports(file_path)
    
    if not relative_imports:
        return changes
    
    if dry_run:
        print(f"\n📁 {file_path.relative_to(PROJECT_ROOT)}")
        for line_num, original, abs_path in relative_imports:
            print(f"  Line {line_num}: {original}")
            print(f"  → Would change to: from {abs_path} import ...")
        changes = [f"Would convert {len(relative_imports)} relative imports"]  # Count for dry run
        return changes
    
    # Read file content
    with open(file_path, encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process each relative import
    for line_num, original, abs_path in relative_imports:
        line_idx = line_num - 1
        if line_idx < len(lines):
            original_line = lines[line_idx]
            
            # Extract the import part after 'from'
            if 'from ' in original_line and ' import ' in original_line:
                # Replace relative import with absolute
                new_line = re.sub(
                    r'from \.+(?= import)',
                    f'from {abs_path}',
                    original_line
                )
                
                if new_line != original_line:
                    lines[line_idx] = new_line
                    changes.append(f"Line {line_num}: {original_line.strip()} → {new_line.strip()}")
    
    # Write back if changes were made
    if changes:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    return changes

def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate relative imports to absolute imports")
    _ = parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    _ = parser.add_argument("--path", type=str, help="Specific path to process (default: entire project)")
    _ = parser.add_argument("--exclude", nargs="+", default=["600_archives", "venv", ".venv", "__pycache__"], 
                       help="Directories to exclude")
    
    args = parser.parse_args()
    
    # Determine paths to process
    if args.path:
        target_paths = [PROJECT_ROOT / args.path]
    else:
        target_paths = [
            PROJECT_ROOT / "src",
            PROJECT_ROOT / "scripts", 
            PROJECT_ROOT / "evals",
            PROJECT_ROOT / "tests"
        ]
    
    # Find all Python files
    python_files: list[Path] = []
    for target_path in target_paths:
        if target_path.exists():
            for py_file in target_path.rglob("*.py"):
                # Skip excluded directories
                if not any(excluded in py_file.parts for excluded in args.exclude):
                    python_files.append(py_file)
    
    print(f"🔍 Found {len(python_files)} Python files to analyze")
    
    total_changes = 0
    files_with_changes = 0
    
    for py_file in python_files:
        changes = convert_relative_to_absolute(py_file, dry_run=args.dry_run)
        if changes:
            files_with_changes += 1
            total_changes += len(changes)
            
            if not args.dry_run:
                print(f"\n✅ {py_file.relative_to(PROJECT_ROOT)}")
                for change in changes:
                    print(f"  {change}")
    
    print("\n📊 Summary:")
    print(f"  Files processed: {len(python_files)}")
    print(f"  Files with changes: {files_with_changes}")
    print(f"  Total changes: {total_changes}")
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")
    else:
        print("\n✅ Migration complete!")

if __name__ == "__main__":
    main()
