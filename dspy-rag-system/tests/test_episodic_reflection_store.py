import math
from datetime import datetime, timedelta

from src.utils.episodic_reflection_store import (
    EpisodicReflection,
    EpisodicReflectionStore,
    _maybe_json_loads,
)


def test_maybe_json_loads_parses_json_string_and_passes_through_python_types():
    # Already-parsed types should pass through unchanged
    assert _maybe_json_loads({"a": 1}) == {"a": 1}
    assert _maybe_json_loads([1, 2, 3]) == [1, 2, 3]

    # JSON strings should parse
    assert _maybe_json_loads('{"x": 2}') == {"x": 2}
    assert _maybe_json_loads('[1,2]') == [1, 2]

    # Non-JSON strings should return as-is
    assert _maybe_json_loads("not-json") == "not-json"


def _episode(created_at):
    return EpisodicReflection(
        agent="tester",
        task_type="unit",
        summary="s",
        what_worked=["a", "b"],
        what_to_avoid=["c", "d"],
        outcome_metrics={"ok": True},
        source_refs={},
        span_hash="abc",
        created_at=created_at,
        id=1,
    )


def test_get_episodic_context_recency_boost_and_confidence_cap():
    store = EpisodicReflectionStore()

    now = datetime.now()
    episodes = [
        _episode(now - timedelta(days=1)),  # recent, triggers boost
        _episode(now - timedelta(days=10)),
        _episode(None),  # missing timestamp handled safely
    ]

    # Monkeypatch retrieval to avoid DB
    store.retrieve_similar_episodes = lambda q, a=None: episodes  # type: ignore

    ctx = store.get_episodic_context("query")

    # Base confidence is len(episodes)/max_episodes_retrieved = 3/3 = 1.0, boost would make 1.2 but capped to 1.0
    assert math.isclose(ctx.confidence_score, 1.0, rel_tol=1e-6)

    # Bullets compressed and deduped, limited to max items
    assert len(ctx.what_worked_bullets) <= store.max_what_worked_items
    assert len(ctx.what_to_avoid_bullets) <= store.max_what_to_avoid_items


def test_get_episodic_context_partial_confidence_with_recent_episode():
    store = EpisodicReflectionStore()

    now = datetime.now()
    episodes = [
        _episode(now - timedelta(days=1)),  # recent
    ]

    store.retrieve_similar_episodes = lambda q, a=None: episodes  # type: ignore

    ctx = store.get_episodic_context("query")

    # Base confidence is 1/3 ~= 0.333..., boosted by 1.2 = 0.4 (approx)
    assert 0.39 <= ctx.confidence_score <= 0.41


def test_generate_reflection_from_task_defaults_when_none_passed():
    store = EpisodicReflectionStore()
    refl = store.generate_reflection_from_task(
        task_description="desc",
        input_text="in",
        output_text="out",
        agent="agent",
        task_type="type",
        outcome_metrics=None,
        source_refs=None,
    )

    assert refl.outcome_metrics.get("success") is True
    assert "task_description" in refl.source_refs
