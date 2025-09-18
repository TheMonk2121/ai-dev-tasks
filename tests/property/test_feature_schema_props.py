from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra import numpy as hnp

from src.dspy_modules.retriever.feature_schema import FusionFeatures

from ._regression_capture import record_case

#!/usr/bin/env python3
"""
Property-based tests for FusionFeatures serialization.
"""



_float_arrays = hnp.arrays(
    dtype=hnp.floating_dtypes(sizes=(32, 64)), shape=hnp.array_shapes(min_dims=1, max_dims=1, min_side=0, max_side=8)
)


@pytest.mark.prop
@given(q=_float_arrays, d=_float_arrays)
@settings(max_examples=20, deadline=100)
def test_numpy_arrays_serialize_to_lists(q: np.ndarray, d: np.ndarray) -> None:
    # Create FusionFeatures with all required fields
    ff = FusionFeatures(
        s_bm25=0.5,
        s_vec=0.6,
        s_title=0.7,
        s_short=0.8,
        r_bm25=0.9,
        r_vec=1.0,
        len_norm=0.5,
        q_vec=q if q.size == 384 else None,
        d_vec=d if d.size == 384 else None,
    )
    dumped: Any = ff.model_dump()
    qv: Any = dumped.get("q_vec")
    dv: Any = dumped.get("d_vec")
    if q.size == 0 or q.size != 384:
        if not (qv is None or qv == []):
            record_case("test_feature_schema_q_empty_or_wrong", {"q_size": int(q.size), "dump_len": 0 if qv is None else len(qv)})
        assert qv is None or qv == []
    else:
        if not (isinstance(qv, list) and len(qv) == q.size):
            record_case("test_feature_schema_q_len", {"q_size": int(q.size), "dump_len": 0 if qv is None else len(qv)})
        assert isinstance(qv, list) and len(qv) == q.size
    if d.size == 0 or d.size != 384:
        if not (dv is None or dv == []):
            record_case("test_feature_schema_d_empty_or_wrong", {"d_size": int(d.size), "dump_len": 0 if dv is None else len(dv)})
        assert dv is None or dv == []
    else:
        if not (isinstance(dv, list) and len(dv) == d.size):
            record_case("test_feature_schema_d_len", {"d_size": int(d.size), "dump_len": 0 if dv is None else len(dv)})
        assert isinstance(dv, list) and len(dv) == d.size