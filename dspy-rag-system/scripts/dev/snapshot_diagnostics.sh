#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
ART="$ROOT/.diagnostics"; mkdir -p "$ART"

# 1) Pyright / BasedPyright (JSON) → count "error" diagnostics
pyright --outputjson > "$ART/pyright.json" || true
python3 - <<'PY'
import json, sys, pathlib
p = pathlib.Path(".diagnostics/pyright.json")
if not p.exists():
    print("PYRIGHT_ERRORS=0"); sys.exit(0)
j = json.loads(p.read_text())
diags = j.get("generalDiagnostics", [])
err = sum(1 for d in diags if d.get("severity") == "error")
print(f"PYRIGHT_ERRORS={err}")
PY

# 2) Ruff (JSON) → total + F821
ruff check --output-format json > "$ART/ruff.json" || true
python3 - <<'PY'
import json, pathlib
p = pathlib.Path(".diagnostics/ruff.json")
if not p.exists():
    print("RUFF_TOTAL=0"); print("RUFF_F821=0"); quit()
r = json.loads(p.read_text())
print(f"RUFF_TOTAL={len(r)}")
print(f"RUFF_F821={sum(1 for x in r if x.get('code')=='F821')}")
PY

# 3) Runtime-level syntax/import compile check (excludes tests + experiments)
python3 - <<'PY'
import sys, pathlib, py_compile, traceback, os, re
roots = ["dspy-rag-system/src"]
exclude = re.compile(r"/(tests|scripts/dev/experiments)/")
errs = 0
for root in roots:
    for p in pathlib.Path(root).rglob("*.py"):
        if exclude.search(str(p)): continue
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception:
            errs += 1
print(f"COMPILE_ERRORS={errs}")
PY

# 4) Tier-1 import sanity (backbone shouldn't throw ImportError)
python3 - <<'PY'
import sys, importlib
sys.path.insert(0, "dspy-rag-system/src")
tier1 = [
    "dspy_modules.cursor_model_router",
    "dspy_modules.vector_store",
    "dspy_modules.document_processor",
]
ok = True
for m in tier1:
    try:
        importlib.import_module(m)
    except Exception as e:
        ok = False
print("TIER1_IMPORT_OK=" + ("1" if ok else "0"))
PY
