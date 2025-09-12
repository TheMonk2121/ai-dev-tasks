from __future__ import annotations
import os
import tempfile
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.config.resolve import compose_layers

"""
Property tests for config resolve layering.
"""





@pytest.mark.prop
@given(
    st.dictionaries(
        st.from_regex(r"[A-Z_]{1,10}", fullmatch=True),
        st.from_regex(r"[A-Za-z0-9_\-]{0,20}", fullmatch=True),
        min_size=1,
        max_size=10,
    ),
    st.dictionaries(
        st.from_regex(r"[A-Z_]{1,10}", fullmatch=True),
        st.from_regex(r"[A-Za-z0-9_\-]{0,20}", fullmatch=True),
        min_size=1,
        max_size=10,
    ),
)
@settings(max_examples=10, deadline=200)
def test_compose_layers_precedence(layer1: dict[str, str], layer2: dict[str, str]):
    # Write layers to temp files

    def write_layer(d: dict[str, str]):
        f = tempfile.NamedTemporaryFile("w+", delete=False)
        for k, v in d.items():
            f.write(f"{k}={v}\n")
        f.flush()
        return f.name

    p1 = write_layer(layer1)
    p2 = write_layer(layer2)
    env = compose_layers([p1, p2])
    # Later layers override earlier
    for k in layer1:
        if k in layer2:
            assert env[k] == layer2[k]
        else:
            assert env[k] == layer1[k]