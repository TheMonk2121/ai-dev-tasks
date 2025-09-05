#!/usr/bin/env python3
"""
Lightweight dead code finder for Python files in the repo.

Heuristic approach:
- Collect top-level function and class definitions via AST.
- For each symbol, search repo for references using ripgrep (rg) with word boundaries.
- If no references other than its own definition line are found, flag as potentially dead.

Notes:
- This is conservative and may miss dynamic usages or aliasing/import indirections.
- It ignores dunder and private (leading underscore) names by default.
- It counts references anywhere in the repo (including tests) as usage.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Iterable, List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCAN_DIRS = ["src", "dspy-rag-system", "scripts"]  # primary code locations


def iter_python_files(root: str) -> Iterable[str]:
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache", ".pytest_cache"}
    for base, dirs, files in os.walk(root):
        # prune skip dirs
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".") and d != "dist"]
        for f in files:
            if f.endswith(".py") and not f.endswith("_pb2.py"):
                yield os.path.join(base, f)


def iter_target_files(root: str) -> Iterable[str]:
    # Prefer scanning common code directories for definitions to keep runtime reasonable.
    yielded = set()
    for d in SCAN_DIRS:
        p = os.path.join(root, d)
        if os.path.isdir(p):
            for f in iter_python_files(p):
                yielded.add(os.path.abspath(f))
                yield f
    # Also include top-level .py files at repo root
    for f in os.listdir(root):
        if f.endswith(".py"):
            path = os.path.join(root, f)
            ap = os.path.abspath(path)
            if ap not in yielded:
                yield path


@dataclass
class Symbol:
    kind: str  # "function" | "class"
    name: str
    filepath: str
    line: int


def collect_symbols(pyfile: str) -> List[Symbol]:
    with open(pyfile, "r", encoding="utf-8", errors="ignore") as f:
        src = f.read()
    try:
        tree = ast.parse(src, filename=pyfile)
    except SyntaxError:
        return []

    symbols: List[Symbol] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            symbols.append(Symbol("function", node.name, pyfile, node.lineno))
        elif isinstance(node, ast.AsyncFunctionDef):
            symbols.append(Symbol("function", node.name, pyfile, node.lineno))
        elif isinstance(node, ast.ClassDef):
            symbols.append(Symbol("class", node.name, pyfile, node.lineno))
    return symbols


def rg_search(pattern: str, root: str) -> List[Tuple[str, int, str]]:
    """Run ripgrep and return list of (file, line, text)."""
    try:
        cmd = [
            "rg",
            "-n",
            "--no-ignore-vcs",
            "--hidden",
            "--glob",
            "!**/.git/**",
            "--glob",
            "!**/__pycache__/**",
            "--glob",
            "!**/.venv/**",
            "--glob",
            "!**/venv/**",
            pattern,
            root,
        ]
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return []
    results: List[Tuple[str, int, str]] = []
    for line in out.splitlines():
        # Format: path:line:match
        parts = line.split(":", 2)
        if len(parts) == 3:
            path, lineno, text = parts
            try:
                results.append((os.path.abspath(path), int(lineno), text))
            except ValueError:
                continue
    return results


def is_interesting(name: str) -> bool:
    if not name:
        return False
    if name.startswith("__") and name.endswith("__"):
        return False  # dunder
    if name.startswith("_"):
        return False  # private by convention
    return True


def find_potentially_dead(root: str) -> List[Tuple[Symbol, List[Tuple[str, int, str]]]]:
    symbols: List[Symbol] = []
    for py in iter_target_files(root):
        symbols.extend(collect_symbols(py))

    candidates: List[Tuple[Symbol, List[Tuple[str, int, str]]]] = []
    for sym in symbols:
        if not is_interesting(sym.name):
            continue
        # Word boundary search; use -F? Better use regex with boundaries.
        # Escape the name for regex safety.
        escaped = re.escape(sym.name)
        pattern = rf"\b{escaped}\b"
        hits = rg_search(pattern, root)
        # Exclude the definition line itself (common false-positive)
        filtered = [h for h in hits if not (h[0] == os.path.abspath(sym.filepath) and h[1] == sym.line)]
        if not filtered:
            candidates.append((sym, hits))
    return candidates


def main() -> int:
    root = REPO_ROOT
    candidates = find_potentially_dead(root)
    if not candidates:
        print("No obvious dead top-level functions/classes found.")
        return 0

    print("Potentially dead code (top-level functions/classes with no references):\n")
    for sym, hits in sorted(candidates, key=lambda x: (x[0].filepath, x[0].line)):
        rel = os.path.relpath(sym.filepath, root)
        print(f"- {sym.kind}: {sym.name}  ->  {rel}:{sym.line}")
    print("\nNote: This is heuristic. Review before deleting. Consider dynamic uses, CLI entrypoints, and imports.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
