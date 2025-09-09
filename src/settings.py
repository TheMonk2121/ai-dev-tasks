from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class EvalSettings(BaseSettings):
    # Core eval controls
    EVAL_PROFILE: str = "default"
    EVAL_DRIVER: str = "local"
    RAGCHECKER_USE_REAL_RAG: bool = True
    POSTGRES_DSN: SecretStr | None = None
    EVAL_CONCURRENCY: int = 3

    # Reranker
    RERANKER_MODEL: str = "bge-reranker-base"
    RERANKER_TOPK: int = 50
    RERANKER_KEEP: int = 10
    RERANKER_DEVICE: str = "cpu"
    RERANKER_CACHE: bool = True

    # Model routing
    DSPY_MODEL: str = "gpt-4o-mini"

    # Optional timeseries sinks (default off)
    EVAL_TIMESERIES_SINK: bool = False
    EVAL_TIMESERIES_CASES: bool = False

    class Config:
        env_file = ".env"


def load_eval_settings() -> EvalSettings:
    return EvalSettings()
