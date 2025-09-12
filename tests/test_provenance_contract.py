from __future__ import annotations

import pytest

from src.memory.guards import rows_to_dtos
from src.memory.models import Answer, Provenance, RetrievedChunk


def _row(ok: bool = True) -> dict:
    md = {
        "ingest_run_id": "run-123" if ok else None,
        "chunk_variant": "v1" if ok else None,
        "source_path": "docs/file.md",
        "chunk_id": "abc123",
    }
    return {"chunk_id": "abc123", "text": "hello world", "score": 0.9, "metadata": md}


def test_rows_to_dtos_enforces_required_provenance():
    chunks = rows_to_dtos([_row(ok=True)], run_id="r1", producer="test", version="v1", strict=True)
    assert len(chunks) == 1
    c = chunks[0]
    assert isinstance(c, RetrievedChunk)
    assert c.provenance.ingest_run_id == "run-123"
    assert c.provenance.chunk_variant == "v1"


def test_rows_to_dtos_raises_on_missing_provenance():
    with pytest.raises(ValueError):
        _ = rows_to_dtos([_row(ok=False)], run_id="r1", producer="test", version="v1", strict=True)


def test_answer_forbids_extra_fields():
    prov = Provenance(
        run_id="r1",
        ingest_run_id="run-123",
        chunk_variant="v1",
        source_path="docs/file.md",
        tool="t",
        version="v1",
    )
    chunk = RetrievedChunk(chunk_id="c1", text="x", score=0.1, provenance=prov)
    answer_model = Answer(text="ok", citations=[], retrieved_context=[chunk])
    assert answer_model.text == "ok"
    # model is extra='forbid'; constructing via dict with unknown fields should fail
    with pytest.raises(Exception):
        Answer(**{**answer_model.model_dump(), "unknown": 1})
