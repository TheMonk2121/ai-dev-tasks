from __future__ import annotations
import os
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.schemas.settings import EvaluationSettings
#!/usr/bin/env python3
"""
Property tests for EvaluationSettings parsing behavior.
"""





@pytest.mark.prop
@given(st.lists(st.from_regex(r"[A-Za-z_][A-Za-z0-9_]{0,11}", fullmatch=True), min_size=1, max_size=10))
@settings(max_examples=10, deadline=100)
def test_known_tags_parsing_variants(tags):
    csv = ",".join(tags)
    os.environ.pop("EVAL_KNOWN_TAGS", None)
    s1 = EvaluationSettings(known_tags=tags)
    assert s1.known_tags == tags
    # CSV via env
    os.environ["EVAL_KNOWN_TAGS"] = csv
    s2 = EvaluationSettings()
    assert set(s2.known_tags) == set(tags)
    os.environ.pop("EVAL_KNOWN_TAGS", None)


@pytest.mark.prop
def test_settings_defaults_nonempty_known_tags():
    # Ensure env is not forcing empty
    os.environ.pop("EVAL_KNOWN_TAGS", None)
    s = EvaluationSettings()
    assert isinstance(s.known_tags, list)
    assert len(s.known_tags) > 0