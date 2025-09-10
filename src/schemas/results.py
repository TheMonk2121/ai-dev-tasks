# src/schemas/results.py
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from src.schemas.eval import Mode


class CaseMetrics(BaseModel):
    is_correct: bool
    precision_contrib: Optional[float] = None
    recall_contrib: Optional[float] = None
    f1_contrib: Optional[float] = None


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
    tag: Optional[str] = None
    is_correct: bool
    error_reason: Optional[str] = None
    runtime_ms: Optional[int] = None


class EvaluationSuiteResult(BaseModel):
    suite_name: str
    seed: int
    profile: Optional[str] = None
    metrics: SuiteMetrics
    cases: List[CaseResult]
