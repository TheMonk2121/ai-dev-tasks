from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path

#!/usr/bin/env python3
"""
Build a repo-local Python import graph and export JSON for visualization.

Outputs:
- metrics/visualizations/import_graph.json

Heuristics:
- Parses AST to collect absolute and relative imports.
- Resolves imports to repo files where possible (excludes third-party).
- Excludes common non-source directories (venv, .git, __pycache__, site-packages).

Usage:
    python scripts/code_map.py [--root PATH] [--out PATH]
"""

EXCLUDE_DIRS = {
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".cursor",
    ".vscode",
    ".idea",
    "site-packages",
}

def iter_python_files(root: Path, includes: list[Path] | None = None) -> list[Path]:
    files: list[Path] = []
    # If includes provided, walk each include path; otherwise, walk the root
    roots = [root]
    if includes:
        roots = [root / inc for inc in includes]
    for walk_root in roots:
        if not walk_root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(walk_root):
            # prune excluded dirs in-place for efficiency
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            # also skip any directory path containing site-packages or venv substrings
            rel_dir = Path(dirpath).relative_to(root)
            skip = any(part in EXCLUDE_DIRS for part in rel_dir.parts)
            if skip:
                continue
            for fn in filenames:
                if fn.endswith(".py"):
                    files.append(Path(dirpath) / fn)
    return files

def safe_parse(path: Path) -> ast.AST | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return ast.parse(text, filename=str(path))
    except Exception:
        return None

def collect_imports(tree: ast.AST) -> list[tuple[str, int, int]]:
    """Returns list of (imported_module, level, lineno).
    level=0 for absolute, >0 for relative.
    """
    out: list[tuple[str, int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name  # e.g., package.sub
                out.append((mod, 0, getattr(node, "lineno", -1)))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""  # may be empty for relative-only
            out.append((mod, node.level or 0, getattr(node, "lineno", -1)))
    return out

def resolve_relative_import(src: Path, root: Path, module: str, level: int) -> Path | None:
    """Resolve a relative import to a file path if possible.
    Example: from .utils import x with level=1.
    """
    # start from the directory of src, then go up `level-1` times (ImportFrom semantics)
    # If level=1, base is src.parent; level=2 -> src.parent.parent; etc.
    base = src.parent
    for _ in range(level - 1):
        base = base.parent
        if base == base.parent:
            break
    target = base
    if module:
        for part in module.split("."):
            target = target / part

    # Try file.py then pkg/__init__.py
    candidates = [target.with_suffix(".py"), target / "__init__.py"]
    for cand in candidates:
        try:
            cand.relative_to(root)
        except ValueError:
            # out of repo
            continue
        if cand.exists():
            return cand
    return None

def resolve_absolute_import(root: Path, module: str) -> Path | None:
    """Resolve an absolute import to a repo file using best-effort heuristics."""
    if not module:
        return None

    # Try progressively shorter tails of the module path to find a file.
    parts = module.split(".")
    # Walk from full to shorter prefixes for package/__init__.py
    for end in range(len(parts), 0, -1):
        pkg_path = root.joinpath(*parts[:end])
        init_py = pkg_path / "__init__.py"
        if init_py.exists():
            return init_py
    # Try module.py using full path
    mod_file = root.joinpath(*parts).with_suffix(".py")
    if mod_file.exists():
        return mod_file

    # If not found, try to locate by tail match (e.g., scripts.x)
    tail = parts[-1]
    matches: list[Path] = [p for p in root.rglob(f"{tail}.py") if is_repo_path(root, p)]
    if len(matches) == 1:
        return matches[0]
    # If multiple matches, try to match more of the path
    for end in range(len(parts), 1, -1):
        tail_path = Path(*parts[-end:]).with_suffix(".py")
        deeper = [p for p in root.rglob(str(tail_path)) if is_repo_path(root, p)]
        if len(deeper) == 1:
            return deeper[0]
    return None

def is_repo_path(root: Path, p: Path) -> bool:
    try:
        rel = p.relative_to(root)
    except ValueError:
        return False
    return not any(part in EXCLUDE_DIRS for part in rel.parts)

def build_graph(root: Path, includes: list[Path] | None = None) -> dict:
    py_files = iter_python_files(root, includes)
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    # Pre-populate nodes
    for f in py_files:
        rel = str(f.relative_to(root))
        nodes[rel] = {
            "id": rel,
            "imports": 0,
            "imported_by": 0,
            "type": "file",
        }

    # Build edges
    for f in py_files:
        rel_src = str(f.relative_to(root))
        tree = safe_parse(f)
        if not tree:
            continue
        imports = collect_imports(tree)
        for mod, level, lineno in imports:
            target: Path | None = None
            if level > 0:
                target = resolve_relative_import(f, root, mod, level)
            else:
                target = resolve_absolute_import(root, mod)
            if target and is_repo_path(root, target):
                rel_tgt = str(target.relative_to(root))
                if rel_tgt not in nodes:
                    # might be a package __init__.py that wasn't picked up if empty
                    nodes[rel_tgt] = {"id": rel_tgt, "imports": 0, "imported_by": 0, "type": "file"}
                edges.append(
                    {
                        "source": rel_src,
                        "target": rel_tgt,
                        "type": "import",
                        "line": lineno,
                        "import_type": "relative" if level > 0 else "absolute",
                    }
                )

    # Compute basic stats
    out_edges_by_src: dict[str, int] = {k: 0 for k in nodes}
    in_edges_by_tgt: dict[str, int] = {k: 0 for k in nodes}
    for e in edges:
        out_edges_by_src[e["source"]] = out_edges_by_src.get(e["source"], 0) + 1
        in_edges_by_tgt[e["target"]] = in_edges_by_tgt.get(e["target"], 0) + 1
    for n in nodes.values():
        n["imports"] = out_edges_by_src.get(n["id"], 0)
        n["imported_by"] = in_edges_by_tgt.get(n["id"], 0)

    graph = {
        "nodes": list(nodes.values()),
        "edges": edges,
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "root": str(root),
        },
    }
    return graph

def main() -> None:
    parser = argparse.ArgumentParser(description="Build repo import graph")
    parser.add_argument("--root", type=str, default=".", help="Repo root (default: .)")
    parser.add_argument("--out", type=str, default="metrics/visualizations/import_graph.json", help="Output JSON path")
    parser.add_argument(
        "--include", type=str, default="", help="Comma-separated subpaths to include (relative to root)"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    includes = [Path(p.strip()) for p in args.include.split(",") if p.strip()]
    graph = build_graph(root, includes if includes else None)
    out_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} with {graph['stats']['nodes']} nodes and {graph['stats']['edges']} edges")

if __name__ == "__main__":
    main()
