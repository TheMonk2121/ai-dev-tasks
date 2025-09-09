# 300_evals/ssot/schema.py
from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel

Lifecycle = Literal["draft", "live", "archived"]
Direction = Literal[">=", "<="]
RunKind = Literal["ragchecker", "calibrate", "reader_debug"]


class MetricSpec(BaseModel):
    key: str  # "f1", "precision", "recall", "faithfulness", etc.
    target: Optional[float] = None
    direction: Direction = ">="
    tolerance: float = 0.0


class PassConfig(BaseModel):
    FEW_SHOT_K: int = 0
    FEW_SHOT_SELECTOR: str = "none"
    FEW_SHOT_SEED: int = 42
    EVAL_COT: int = 0
    EVAL_DISABLE_CACHE: int = 1
    DSPY_TELEPROMPT_CACHE: Literal["true", "false"] = "false"
    TEMPERATURE: float = 0
    MAX_WORKERS: int = 3  # <= your "limited concurrency" invariant
    RATE_LIMIT_PROFILE: str = "stable"  # "stable" | "aggressive"


class RunSpec(BaseModel):
    kind: RunKind
    script: str  # path under repo
    args: List[str] = []  # optional CLI args (kept minimal; env drives most)


class EvalPass(BaseModel):
    id: str
    name: str
    description: str
    lifecycle: Lifecycle = "live"
    tags: List[str] = []
    config_layers: List[str] = []  # composition order: base < stable < delta_*
    config: PassConfig
    run: RunSpec
    metrics: List[MetricSpec] = []  # gates
    expected_files: List[str] = []  # optional sanity constraints

    # Optional audit fields (filled at generate/run time)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    version: Optional[str] = None


class EvalSuite(BaseModel):
    id: str
    title: str
    passes: List[EvalPass]

    # Optional audit fields (filled at generate time)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: Optional[str] = None
