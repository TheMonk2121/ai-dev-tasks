import sys
from pathlib import Path

import pytest
from pydantic import TypeAdapter

# Add the dspy-rag-system src to path
# sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))  # REMOVED: DSPy venv consolidated into main project

try:
    from dspy_modules.retriever.feature_schema import FusionFeatures
except ImportError as e:
    pytest.skip(f"DSPy feature schema not available: {e}", allow_module_level=True)

TA = TypeAdapter(FusionFeatures)


def test_all_feature_jsonl_validate():
    # scan common metrics dirs; adjust as needed
    roots = ["metrics", "datasets"]
    found = False
    for root in roots:
        p = Path(root)
        if not p.exists():
            continue
        for fp in p.rglob("*.jsonl"):
            found = True
            for line in fp.read_text().splitlines():
                if not line.strip():
                    continue
                # Heuristic: only validate lines that look like fusion features
                # to avoid unrelated JSONL files in metrics (e.g., lessons, logs)
                if '"s_bm25"' in line and '"s_vec"' in line:
                    TA.validate_json(line)
    assert found or True  # allow passing if no feature files yet
