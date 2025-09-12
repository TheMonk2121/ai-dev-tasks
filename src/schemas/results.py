from __future__ import annotations
from pydantic import BaseModel
from src.schemas.eval import Mode
# src/schemas/results.py




class CaseMetrics(BaseModel):
    is_correct: bool
    precision_contrib: float | None = None
    recall_contrib: float | None = None
    f1_contrib: float | None = None


class SuiteMetrics(BaseModel):
    macro_precision: float
    macro_recall: float
    macro_f1: float
    micro_precision: float
    micro_recall: float
    micro_f1: float
    total_cases: int


class CaseResult(BaseModel):
    id: str
    mode: Mode
    tag: str | None = None
    is_correct: bool
    error_reason: str | None = None
    runtime_ms: int | None = None


class EvaluationSuiteResult(BaseModel):
    suite_name: str
    seed: int
    profile: str | None = None
    metrics: SuiteMetrics
    cases: list[CaseResult]
