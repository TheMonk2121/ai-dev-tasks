#!/usr/bin/env python3
"""
Normalize metadata headers across markdown files to the minimal schema:
- Keep only CONTEXT_REFERENCE and up to 3 MODULE_REFERENCE lines
- Remove deprecated tags (SYSTEM_REFERENCE, WORKFLOW_*, METADATA_*, BACKLOG_*, IMPLEMENTATION_*, LOCAL_CONTEXT_INDEX, MEMORY_CONTEXT, *_additional_resources, *_advanced_features, lens-based files, etc.)
- Skip files under 600_archives/

Usage:
  python3 scripts/normalize_metadata_headers.py --root .
"""
import argparse
import re
from pathlib import Path

KEEP_CONTEXT = "<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->"
MODULE_PATTERN = re.compile(r"<!--\s*MODULE_REFERENCE:\s*([^>]+)\s*-->")
CONTEXT_PATTERN = re.compile(r"<!--\s*CONTEXT_REFERENCE:\s*([^>]+)\s*-->")
HTML_COMMENT_PATTERN = re.compile(r"<!--\s*([^:>]+):[^>]*-->")

def is_deprecated_module(value: str) -> bool:
    v = value.strip()
    if not v:
        return True
    lowered = v.lower()
    blocked_suffixes = ["_additional_resources.md", "_advanced_features.md"]
    if any(lowered.endswith(s) for s in blocked_suffixes):
        return True
    # Drop references to split-module style filenames we consolidated
    split_markers = [
        "400_system-overview_",
        "400_deployment-environment-guide_",
        "400_integration-patterns-guide_",
        "400_migration-upgrade-guide_",
        "400_performance-optimization-guide_",
        "400_testing-strategy-guide_",
        "400_few-shot-context-examples_",
        "400_contributing-guidelines_",
    ]
    if any(lowered.startswith(m) for m in split_markers):
        return True
    # Drop project deliverable module refs
    if lowered.startswith("b-011-") or lowered.startswith("b-049-") or lowered.startswith("b-072-"):
        return True
    if "_lens_" in lowered:
        return True
    return False

def rewrite_header(lines: list) -> list:
    kept = []
    module_values = []
    i = 0
    # gather leading HTML comment header block (first 50 lines)
    header_end = 0
    for idx, line in enumerate(lines[:50]):
        if not line.strip().startswith("<!--") and line.strip():
            header_end = idx
            break
    if header_end == 0:
        header_end = min(50, len(lines))

    # scan header for context/module
    for line in lines[:header_end]:
        m_ctx = CONTEXT_PATTERN.search(line)
        m_mod = MODULE_PATTERN.search(line)
        if m_ctx:
            # ignore existing value; we enforce single canonical keep later
            continue
        if m_mod:
            val = m_mod.group(1).strip()
            if not is_deprecated_module(val):
                module_values.append(val)

    # de-dup and cap modules to 3
    seen = set()
    normalized_modules = []
    for v in module_values:
        if v in seen:
            continue
        seen.add(v)
        normalized_modules.append(v)
        if len(normalized_modules) == 3:
            break

    # Build new header block
    new_header = [KEEP_CONTEXT + "\n"]
    for v in normalized_modules:
        new_header.append(f"<!-- MODULE_REFERENCE: {v} -->\n")

    # Drop all other metadata comments in header
    body_start = header_end
    body = []
    for line in lines[body_start:]:
        if HTML_COMMENT_PATTERN.search(line):
            # preserve only module/context occurrences elsewhere if needed
            if MODULE_PATTERN.search(line) or CONTEXT_PATTERN.search(line):
                # drop occurrences outside header to avoid noise
                continue
        body.append(line)

    # Ensure a blank line after header
    if body and body[0].strip():
        new_header.append("\n")

    return new_header + body

def process_file(path: Path):
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(True)
    new_lines = rewrite_header(lines)
    if new_lines != lines:
        path.write_text(''.join(new_lines), encoding="utf-8")
        return True
    return False

def main():
    ap = argparse.ArgumentParser(description="Normalize metadata headers in markdown files")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root)
    changed = 0
    for p in root.rglob("*.md"):
        # skip archives
        if "600_archives" in p.parts:
            continue
        try:
            changed |= process_file(p)
        except Exception:
            continue
    print("Header normalization complete")

if __name__ == "__main__":
    main()


