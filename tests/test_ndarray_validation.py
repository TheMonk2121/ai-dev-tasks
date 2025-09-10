import json
import sys
from pathlib import Path

import numpy as np
import pytest

# Add the dspy-rag-system src to path
# sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))  # REMOVED: DSPy venv consolidated into main project

from dspy_modules.retriever.feature_schema import FusionFeatures


def test_accepts_list_and_serializes_to_json():
    ff = FusionFeatures(
        s_bm25=0.3,
        s_vec=0.5,
        s_title=0.1,
        s_short=0.2,
        r_bm25=0.1,
        r_vec=0.2,
        len_norm=0.9,
        q_vec=[0.0] * 384,
        d_vec=[0.1] * 384,
    )
    js = ff.model_dump_json()
    obj = json.loads(js)
    assert isinstance(obj["q_vec"], list) and len(obj["q_vec"]) == 384


def test_rejects_wrong_shape():
    with pytest.raises(Exception):
        FusionFeatures(
            s_bm25=0.3,
            s_vec=0.5,
            s_title=0.1,
            s_short=0.2,
            r_bm25=0.1,
            r_vec=0.2,
            len_norm=0.9,
            q_vec=[0.0] * 383,
            d_vec=[0.1] * 384,
        )


def test_rejects_non_finite_in_strict_mode(monkeypatch):
    monkeypatch.setenv("EVAL_STRICT_ARRAYS", "1")
    with pytest.raises(Exception):
        FusionFeatures(
            s_bm25=0.3,
            s_vec=0.5,
            s_title=0.1,
            s_short=0.2,
            r_bm25=0.1,
            r_vec=0.2,
            len_norm=0.9,
            q_vec=[float("nan")] * 384,
            d_vec=[0.1] * 384,
        )
