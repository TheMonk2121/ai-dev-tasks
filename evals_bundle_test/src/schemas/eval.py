from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Literal, override
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic.functional_validators import AfterValidator

if TYPE_CHECKING:
    from src.schemas.validation import ValidationResult

# Reusable constraints
NonEmptyStr = Annotated[str, AfterValidator(lambda s: s if s.strip() else (_ for _ in ()).throw(ValueError("empty")))]


class RerankerConfig(BaseModel):
    model_config: ConfigDict = ConfigDict(strict=True, extra="forbid")
    enable: bool = Field(default=True)
    model: NonEmptyStr = "BAAI/bge-reranker-v2-m3"
    input_topk: int = 40
    keep: int = 10
    batch: int = 16
    device: Literal["cpu", "cuda", "mps"] | None = None
    cache: bool = True


class ContextChunk(BaseModel):
    model_config: ConfigDict = ConfigDict(strict=True, extra="forbid")
    source_id: NonEmptyStr
    text: NonEmptyStr
    start: int | None = None
    end: int | None = None


class RetrievalCandidate(BaseModel):
    model_config: ConfigDict = ConfigDict(strict=True, extra="forbid")
    doc_id: NonEmptyStr
    score: float
    title: str | None = None
    url: str | None = None
    chunk: str


class CaseResult(BaseModel):
    model_config: ConfigDict = ConfigDict(strict=True, extra="forbid")
    case_id: NonEmptyStr
    mode: Literal["rag", "baseline", "oracle"]
    query: NonEmptyStr
    predicted_answer: str | None = None
    retrieved_context: list[ContextChunk] = []
    retrieval_snapshot: list[RetrievalCandidate] = []
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    faithfulness: float | None = None
    answer_latency_ms: int | None = None


class EvaluationRun(BaseModel):
    model_config: ConfigDict = ConfigDict(strict=True, extra="forbid")
    run_id: UUID = Field(default_factory=uuid4)
    started_at: datetime
    finished_at: datetime | None = None
    profile: NonEmptyStr
    pass_id: NonEmptyStr
    reranker: RerankerConfig
    cases: list[CaseResult] = []
    artifact_path: str | None = None
    git_sha: str | None = None
    tags: list[str] = []
    # Additional fields used by callers
    driver: str | None = None
    seed: int | None = None
    overall: dict[str, float] | None = None
    artifact_paths: dict[str, str] | None = None

    @computed_field  # included in dumps/schemas without storing on disk
    def n_cases(self) -> int:
        return len(self.cases)

    @override
    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override to exclude computed fields from serialization."""
        kwargs.setdefault("exclude", set()).add("n_cases")
        return super().model_dump(**kwargs)

    @override
    def model_dump_json(self, **kwargs: Any) -> str:
        """Override to exclude computed fields from JSON serialization."""
        kwargs.setdefault("exclude", set()).add("n_cases")
        return super().model_dump_json(**kwargs)


from enum import Enum
from pathlib import Path

from pydantic import field_validator, model_validator

# ---- Enumerations -----------------------------------------------------------


class Mode(str, Enum):
    retrieval = "retrieval"
    reader = "reader"
    decision = "decision"


# Import settings for dynamic tag validation
from src.schemas.settings import settings

# Optional but useful to catch typos in tags;
# keep open-ended by not enforcing at type level.
KNOWN_TAGS = set(settings.known_tags)

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
        validate_by_name: bool = True
        str_strip_whitespace: bool = False  # Don't strip whitespace to preserve carriage returns
        validate_assignment: bool = True
        extra: str = "allow"  # tolerate legacy keys; we'll normalize below

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy(cls, values: dict[str, Any]) -> dict[str, Any]:
        # id aliases
        _ = values.setdefault("id", values.get("case_id", values.get("query_id")))
        # query aliases
        _ = values.setdefault("query", values.get("question"))
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
        return out  # Don't add default tags - preserve empty list if provided

    @model_validator(mode="after")
    def _mode_requirements(self) -> GoldCase:
        mode: Mode = self.mode
        has_reader = bool(self.gt_answer)
        _ = bool(self.expected_files or self.globs)  # has_retr
        _ = bool(self.expected_decisions)  # has_dec

        if mode == Mode.reader and not has_reader:
            raise ValueError(f"{self.id}: reader mode requires gt_answer")
        # Retrieval mode can have cases without explicit targets (they test general retrieval)
        # if mode == Mode.retrieval and not has_retr:
        #     raise ValueError(f"{self.id}: retrieval mode requires expected_files or globs")
        # Decision mode can have empty expected_decisions (means no decisions yet)
        # if mode == Mode.decision and not has_dec:
        #     raise ValueError(f"{self.id}: decision mode requires expected_decisions")
        return self

    def validate_case(self, config: Any = None) -> ValidationResult:
        """Validate this case against configuration rules."""
        from src.schemas.validation import ValidationConfig, ValidationResult

        if config is None:
            config = ValidationConfig()

        result = ValidationResult(is_valid=True)

        # Check required fields
        if not self.id:
            result.add_error(f"Case {self.id}: Missing required field 'id'")
        if not self.query:
            result.add_error(f"Case {self.id}: Missing required field 'query'")
        if not self.tags:
            result.add_error(f"Case {self.id}: Missing required field 'tags'")

        # Check mode requirements if enabled
        if config.validate_mode_requirements:
            if self.mode == Mode.reader and not self.gt_answer:
                if config.strict_mode:
                    result.add_error(f"Case {self.id}: reader mode requires gt_answer")
                else:
                    result.add_warning(f"Case {self.id}: reader mode missing gt_answer")

        # Check for unknown tags
        if config.unknown_tag_warning:
            unknown_tags = config.get_unknown_tags(self.tags)
            if unknown_tags:
                result.add_unknown_tags(self.id, unknown_tags)
                if config.strict_mode:
                    result.add_error(f"Case {self.id}: unknown tags {unknown_tags}")
                else:
                    result.add_warning(f"Case {self.id}: unknown tags {unknown_tags}")

        # Check file existence if enabled
        if config.check_file_existence and not config.allow_missing_files:
            for file_path in self.expected_files or []:
                if not Path(file_path).exists():
                    result.add_missing_file(self.id, file_path, "file")
                    if config.strict_mode:
                        result.add_error(f"Case {self.id}: missing file {file_path}")
                    else:
                        result.add_warning(f"Case {self.id}: missing file {file_path}")

        return result


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
