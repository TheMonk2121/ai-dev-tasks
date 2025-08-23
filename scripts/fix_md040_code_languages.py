#!/usr/bin/env python3
"""
Fix MD040 - Fenced code blocks should have a language specified.
Adds language specifications to code blocks that don't have them.
"""

import glob
import re
from typing import Dict, List


def detect_code_language(content: str) -> str:
    """Attempt to detect the language based on content patterns."""
    # Common patterns for different languages
    patterns: Dict[str, List[str]] = {
        "python": [
            r"import\s+\w+",
            r"def\s+\w+\s*\(",
            r"class\s+\w+",
            r"print\s*\(",
            r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
            r"#!/usr/bin/env python",
            r"#!/usr/bin/python",
        ],
        "bash": [
            r"#!/bin/bash",
            r"#!/bin/sh",
            r'echo\s+[\'"]',
            r"cd\s+",
            r"ls\s+",
            r"git\s+",
            r"python3?\s+",
        ],
        "javascript": [
            r"function\s+\w+\s*\(",
            r"const\s+\w+",
            r"let\s+\w+",
            r"var\s+\w+",
            r"console\.log\s*\(",
            r"export\s+",
            r"import\s+",
        ],
        "json": [
            r"^\s*\{",
            r"^\s*\[",
            r'"[^"]*"\s*:',
        ],
        "yaml": [
            r"^\s*\w+:\s*$",
            r"^\s*-\s+\w+",
            r"^\s*#\s+",
        ],
        "markdown": [
            r"^#\s+",
            r"^\*\*[^*]+\*\*",
            r"^\[[^\]]+\]\([^)]+\)",
        ],
        "html": [
            r"<[^>]+>",
            r"<!DOCTYPE",
            r"<html",
            r"<head",
            r"<body",
        ],
        "css": [
            r"^\s*[.#]?\w+\s*\{",
            r"color:\s*",
            r"background:\s*",
            r"font-size:\s*",
        ],
        "sql": [
            r"SELECT\s+",
            r"INSERT\s+INTO",
            r"UPDATE\s+",
            r"DELETE\s+FROM",
            r"CREATE\s+TABLE",
        ],
        "xml": [
            r"<\?xml",
            r"<[A-Z][A-Z0-9]*\s+",
            r"</[A-Z][A-Z0-9]*>",
        ],
    }

    # Count matches for each language
    language_scores: Dict[str, int] = {}
    for lang, lang_patterns in patterns.items():
        score = 0
        for pattern in lang_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            score += len(matches)
        if score > 0:
            language_scores[lang] = score

    # Return the language with the highest score, or 'text' as default
    if language_scores:
        return max(language_scores.keys(), key=lambda k: language_scores[k])
    return "text"

def fix_md040_code_languages():
    """Fix MD040 violations by adding language specifications to code blocks."""
    print("🔧 Fixing MD040 - Fenced Code Block Languages")
    print("=" * 60)

    # Find all markdown files
    markdown_files = []
    for pattern in ["**/*.md", "**/*.markdown"]:
        markdown_files.extend(glob.glob(pattern, recursive=True))

    # Remove files in certain directories
    markdown_files = [
        f
        for f in markdown_files
        if not any(exclude in f for exclude in ["node_modules", ".git", "__pycache__", ".pytest_cache"])
    ]

    print(f"Found {len(markdown_files)} markdown files")

    files_fixed = 0
    files_failed = 0
    files_unchanged = 0
    total_fixes = 0

    for file_path in markdown_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Find all fenced code blocks without language specification
            # Pattern: ``` followed by newline, content, then ```
            code_block_pattern = r"```\n(.*?)```"

            def replace_code_block(match):
                code_content = match.group(1)
                detected_lang = detect_code_language(code_content)
                return f"```{detected_lang}\n{code_content}```"

            # Apply the fix
            content = re.sub(code_block_pattern, replace_code_block, content, flags=re.DOTALL)

            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Count the number of fixes
                original_blocks = len(re.findall(code_block_pattern, original_content, flags=re.DOTALL))
                new_blocks = len(re.findall(r"```\n(.*?)```", content, flags=re.DOTALL))
                fixes = original_blocks - new_blocks

                print(f"✅ Fixed: {file_path} ({fixes} code blocks)")
                files_fixed += 1
                total_fixes += fixes
            else:
                files_unchanged += 1

        except Exception as e:
            print(f"❌ Failed: {file_path} - {str(e)}")
            files_failed += 1

    print("\n📊 Summary:")
    print(f"  Files processed: {len(markdown_files)}")
    print(f"  Files fixed: {files_fixed}")
    print(f"  Files failed: {files_failed}")
    print(f"  Files unchanged: {files_unchanged}")
    print(f"  Total code blocks fixed: {total_fixes}")

    if files_fixed > 0:
        print(f"\n🎉 Successfully fixed {files_fixed} files!")
    else:
        print("\nℹ️  No files needed fixing.")

if __name__ == "__main__":
    fix_md040_code_languages()
