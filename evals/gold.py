#!/usr/bin/env python3
"""
Gold standard evaluation utilities with JSON/JSONL loader and glob support.
"""

import fnmatch
import importlib.util
import json
import os
import sys
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional, Set


def _norm(p: str) -> str:
    return str(PurePosixPath((p or "").strip().replace("\\", "/"))).lower()


def load_gold_mapping(path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Load gold mapping from JSONL or JSON. Supports file_paths and globs."""
    path = path or os.getenv("GOLD_FILE", "evals/gold.jsonl")
    if not os.path.exists(path):
        alt = os.path.splitext(path)[0] + ".json"
        if os.path.exists(alt):
            path = alt
        else:
            # Fallback: load from dspy-rag-system/eval_gold.py
            mapping: Dict[str, Dict[str, Any]] = {}
            try:
                root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
                eg_path = os.path.join(root, "dspy-rag-system", "eval_gold.py")
                if os.path.exists(eg_path):
                    spec = importlib.util.spec_from_file_location("_eval_gold", eg_path)
                    mod = importlib.util.module_from_spec(spec)  # type: ignore
                    assert spec and spec.loader
                    spec.loader.exec_module(mod)  # type: ignore
                    gold = {}
                    gold.update(getattr(mod, "GOLD", {}))
                    gold.update(getattr(mod, "ADDITIONAL_GOLD", {}))
                    for cid, rule in gold.items():
                        fps = {_norm(p) for p in (rule.get("paths") or [])}
                        globs: List[str] = []
                        for fn in rule.get("filenames") or []:
                            globs.append(f"*/{str(fn).strip().lower()}")
                        ns = rule.get("namespace")
                        if ns:
                            globs.append(f"{str(ns).strip().lower()}/*")
                        mapping[cid] = {"file_paths": fps, "globs": globs}
                    return mapping
            except Exception:
                return {}
    mapping: Dict[str, Dict[str, Any]] = {}
    if path.endswith(".jsonl"):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                cid = row["case_id"]
                fps = {_norm(p) for p in row.get("file_paths", [])}
                globs = [p.strip() for p in row.get("globs", [])]
                mapping[cid] = {"file_paths": fps, "globs": globs}
    else:
        data = json.load(open(path, "r", encoding="utf-8"))
        for cid, row in data.items():
            fps = {_norm(p) for p in row.get("file_paths", [])}
            globs = [p.strip() for p in row.get("globs", [])]
            mapping[cid] = {"file_paths": fps, "globs": globs}
    return mapping


_GOLD: Optional[Dict[str, Dict[str, Any]]] = None


def get_gold() -> Dict[str, Dict[str, Any]]:
    global _GOLD
    if _GOLD is None:
        _GOLD = load_gold_mapping()
    return _GOLD


def gold_hit(case_id: str, retrieved_rows: List[Dict[str, Any]]) -> bool:
    gold = get_gold().get(case_id)
    if not gold or not retrieved_rows:
        return False
    gold_paths: Set[str] = gold["file_paths"]
    globs = gold["globs"]

    def match(fp: str) -> bool:
        nfp = _norm(fp)
        if nfp in gold_paths:
            return True
        return any(fnmatch.fnmatch(nfp, pat.lower()) for pat in globs)

    for r in retrieved_rows if isinstance(retrieved_rows, list) else []:
        fp = r.get("file_path") or r.get("filename") or ""
        if match(fp):
            return True
    # Fallback if caller passed just a list of file paths
    if isinstance(retrieved_rows, list) and retrieved_rows and isinstance(retrieved_rows[0], str):
        return any(match(x) for x in retrieved_rows)
    return False
