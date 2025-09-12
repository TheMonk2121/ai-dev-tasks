from __future__ import annotations
import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Extract Python docstrings and basic symbol metadata for indexing (B-1059 Phase 2 B2).

Outputs JSON to indexing/docstrings_index.json with entries:
{
  "files_indexed": N,
  "symbols": [
     {"path": str, "symbol": str, "kind": "module|class|function", "lineno": int, "doc": str}
  ]
}
"""

@dataclass
class SymbolDoc:
    path: str
    symbol: str
    kind: str  # module | class | function
    lineno: int
    doc: str

def extract_from_file(py_file: Path) -> list[SymbolDoc]:
    symbols: list[SymbolDoc] = []
    try:
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(text)

        # Module docstring
        mod_doc = ast.get_docstring(tree) or ""
        if mod_doc:
            symbols.append(SymbolDoc(str(py_file), py_file.stem, "module", 1, mod_doc))

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                if doc:
                    symbols.append(SymbolDoc(str(py_file), node.name, "class", getattr(node, "lineno", 1), doc))
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                doc = ast.get_docstring(node) or ""
                if doc:
                    symbols.append(SymbolDoc(str(py_file), node.name, "function", getattr(node, "lineno", 1), doc))
    except Exception:
        # Best-effort: skip files that fail to parse
        return symbols
    return symbols

def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "indexing"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "docstrings_index.json"

    # Simple inclusion: index repo Python files excluding common vendor dirs
    exclude_parts = {"venv", ".venv", "node_modules", "__pycache__", "dist", "build"}

    py_files: list[Path] = []
    for p in repo_root.rglob("*.py"):
        parts = set(p.parts)
        if exclude_parts & parts:
            continue
        py_files.append(p)

    symbols: list[SymbolDoc] = []
    for f in py_files:
        symbols.extend(extract_from_file(f))

    payload: dict[str, Any] = {
        "files_indexed": len(py_files),
        "symbols": [asdict(s) for s in symbols],
    }
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"✅ Docstrings indexed: {len(symbols)} symbols from {len(py_files)} files → {out_file}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
