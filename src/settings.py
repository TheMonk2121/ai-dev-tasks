from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EvalSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_prefix="")

    # Core eval controls
    EVAL_PROFILE: str = "default"
    EVAL_DRIVER: str = "local"
    RAGCHECKER_USE_REAL_RAG: int = 1
    POSTGRES_DSN: SecretStr | None = None
    EVAL_CONCURRENCY: int = 8

    # Reranker defaults
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANKER_TOPK: int = 40
    RERANKER_KEEP: int = 10
    RERANKER_DEVICE: str | None = None
    RERANKER_CACHE: int = 1

    # LLM
    DSPY_MODEL: str = "openai:gpt-4o-mini"

    # Ollama configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.1:8b"
    OLLAMA_TIMEOUT: int = 30

    # Logfire
    LOGFIRE_TOKEN: SecretStr | None = None

    # Optional timeseries sinks (default off)
    EVAL_TIMESERIES_SINK: bool = False
    EVAL_TIMESERIES_CASES: bool = False


def load_eval_settings() -> EvalSettings:
    return EvalSettings()
