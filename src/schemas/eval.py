from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class RerankerConfig(BaseModel):
    model_config = ConfigDict(strict=True)
    enable: bool = True
    model: str = "bge-reranker-base"
    input_topk: int = 50
    keep: int = 10
    batch: int = 16
    device: str = "cpu"
    cache: bool = True


class ContextChunk(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str
    source: str
    text: str
    score: float | None = None
    metadata: dict = Field(default_factory=dict)


class RetrievalCandidate(BaseModel):
    model_config = ConfigDict(strict=True)
    query: str
    chunk: ContextChunk
    rank: int
    score: float | None = None
    route: Literal["bm25", "vector", "hybrid", "trigram", "title_trigram"] = "hybrid"


class CaseResult(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str
    mode: str
    tags: list[str] = Field(default_factory=list)
    query: str
    predicted_answer: str
    retrieved_context: list[ContextChunk]
    retrieval_snapshot: list[RetrievalCandidate]
    metrics: dict
    timings: dict


class EvaluationRun(BaseModel):
    model_config = ConfigDict(strict=True)
    profile: str
    driver: str
    reranker: RerankerConfig
    seed: int | None = None
    started_at: str
    finished_at: str | None = None
    overall: dict
    artifact_paths: dict


from enum import Enum
from typing import Any, Union

from pydantic import BaseModel, Field, field_validator, model_validator

# ---- Enumerations -----------------------------------------------------------


class Mode(str, Enum):
    retrieval = "retrieval"
    reader = "reader"
    decision = "decision"


# Optional but useful to catch typos in tags;
# keep open-ended by not enforcing at type level.
KNOWN_TAGS = {"ops_health", "meta_ops", "rag_qa_single", "rag_qa_multi", "db_workflows", "negatives"}

# ---- Helpers ---------------------------------------------------------------


def _ensure_list(v: str | list[str] | None) -> list[str] | None:
    if v is None:
        return None
    if isinstance(v, list):
        return v
    return [v]


# ---- Canonical Gold Case ---------------------------------------------------


class GoldCase(BaseModel):
    """
    Canonical persisted/interchange schema for evaluation items.
    Accepts legacy aliases:
      - id: case_id | query_id
      - query: question
      - gt_answer: response | expected_answer
      - tags: tag (singular)
    """

    id: str = Field(..., alias="id")
    mode: Mode

    # Accept both 'query' and legacy 'question'
    query: str = Field(..., alias="query")

    # Accept plural and singular
    tags: list[str] = Field(..., alias="tags")

    category: str | None = None

    # Reader supervision
    gt_answer: str | None = Field(None, alias="gt_answer")

    # Retrieval supervision
    expected_files: list[str] | None = None
    globs: list[str] | None = None

    # Decision supervision
    expected_decisions: list[str] | None = None

    # Free-form
    notes: str | None = None

    # --- Aliases / normalization bridge (legacy fields) ---
    # We accept extra and remap in a root validator.
    class Config:
        validate_by_name = True
        str_strip_whitespace = True
        validate_assignment = True
        extra = "allow"  # tolerate legacy keys; we'll normalize below

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy(cls, values: dict[str, Any]) -> dict[str, Any]:
        # id aliases
        values.setdefault("id", values.get("case_id", values.get("query_id")))
        # query aliases
        values.setdefault("query", values.get("question"))
        # tags aliases
        if "tags" not in values and "tag" in values:
            values["tags"] = values["tag"]
        # gt_answer aliases
        for k in ("response", "expected_answer"):
            if "gt_answer" not in values and k in values:
                val = values[k]
                # Handle list case (take first element)
                if isinstance(val, list) and val:
                    values["gt_answer"] = val[0]
                else:
                    values["gt_answer"] = val
                break

        # Handle gt_answer being a list directly
        if "gt_answer" in values and isinstance(values["gt_answer"], list) and values["gt_answer"]:
            values["gt_answer"] = values["gt_answer"][0]
        # Normalize list-like fields
        if "tags" in values:
            values["tags"] = _ensure_list(values["tags"]) or []
        for key in ("expected_files", "globs", "expected_decisions"):
            if key in values:
                values[key] = _ensure_list(values[key])
        return values

    @field_validator("tags")
    @classmethod
    def _dedupe_tags(cls, v: list[str]) -> list[str]:
        # Keep order, dedupe
        out, seen = [], set()
        for t in v:
            if t not in seen:
                out.append(t)
                seen.add(t)
        return out or ["rag_qa_single"]

    @model_validator(mode="after")
    def _mode_requirements(self) -> GoldCase:
        mode: Mode = self.mode
        has_reader = bool(self.gt_answer)
        has_retr = bool(self.expected_files or self.globs)
        has_dec = bool(self.expected_decisions)

        if mode == Mode.reader and not has_reader:
            raise ValueError(f"{self.id}: reader mode requires gt_answer")
        # Retrieval mode can have cases without explicit targets (they test general retrieval)
        # if mode == Mode.retrieval and not has_retr:
        #     raise ValueError(f"{self.id}: retrieval mode requires expected_files or globs")
        # Decision mode can have empty expected_decisions (means no decisions yet)
        # if mode == Mode.decision and not has_dec:
        #     raise ValueError(f"{self.id}: decision mode requires expected_decisions")
        return self


# ---- Canonical per-case result --------------------------------------------


class EvidenceSpan(BaseModel):
    text: str
    score: float | None = None
    source_file: str | None = None
    start_idx: int | None = None
    end_idx: int | None = None


class RetrievalHit(BaseModel):
    path: str
    score: float


class EvaluationResult(BaseModel):
    id: str
    mode: Mode
    tags: list[str] = []
    query: str

    # Reader predictions
    predicted_answer: str | None = None
    answer_confidence: float | None = None
    evidence: list[EvidenceSpan] | None = None

    # Retrieval predictions
    retrieved: list[RetrievalHit] | None = None

    # Decision predictions
    predicted_decisions: list[str] | None = None

    # Scoring / bookkeeping
    is_correct: bool | None = None
    error_reason: str | None = None
    runtime_ms: int | None = None
