#!/usr/bin/env python3
"""
Unified Evaluation Settings

Consolidates all evaluation configuration into a single, typed settings class
with proper validation and environment precedence handling.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator  # type: ignore
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class EvalSettings(BaseSettings):
    """Unified evaluation system configuration with proper precedence handling."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
        str_strip_whitespace=True,
    )

    # === Profile and Driver Configuration ===
    EVAL_PROFILE: Literal["gold", "real", "mock"] = Field(
        default="gold",
        description="Evaluation profile: gold (curated cases), real (full dataset), mock (synthetic)"
    )
    EVAL_DRIVER: Literal["dspy_rag", "synthetic"] = Field(
        default="dspy_rag",
        description="Evaluation driver: dspy_rag (real system), synthetic (mock data)"
    )
    RAGCHECKER_USE_REAL_RAG: bool = Field(
        default=True,
        description="Use real RAG system instead of synthetic data"
    )

    # === Database Configuration ===
    POSTGRES_DSN: str = Field(
        default="postgresql://danieljacobs@localhost:5432/ai_agency",
        description="PostgreSQL connection string"
    )
    DATABASE_URL: str | None = Field(
        default=None,
        description="Alternative database URL (falls back to POSTGRES_DSN)"
    )

    # === File Paths ===
    GOLD_CASES_PATH: str = Field(
        default="evals/data/gold/v1/gold_cases_121.jsonl",
        description="Path to gold test cases"
    )
    EVAL_MANIFEST_PATH: str = Field(
        default="evals/metrics/manifests/manifest.json",
        description="Path to evaluation manifest"
    )
    EVAL_RESULTS_OUTPUT_DIR: str = Field(
        default="evals/metrics/baseline_evaluations",
        description="Directory for evaluation results"
    )

    # === Performance Configuration ===
    EVAL_CONCURRENCY: int = Field(
        default=8,
        ge=1,
        le=16,
        description="Number of concurrent evaluation tasks"
    )
    EVAL_MAX_WORKERS: int = Field(
        default=3,
        ge=1,
        le=8,
        description="Maximum number of worker processes"
    )
    EVAL_SEED: int = Field(
        default=42,
        description="Random seed for reproducible evaluations"
    )
    EVAL_TEMP: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM generation"
    )
    EVAL_TOP_P: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Top-p for LLM generation"
    )

    # === Model Configuration ===
    DSPY_MODEL: str = Field(
        default="anthropic.claude-3-haiku-20240307-v1:0",
        description="DSPy model identifier"
    )
    RERANKER_MODEL: str = Field(
        default="BAAI/bge-reranker-v2-m3",
        description="Cross-encoder reranker model"
    )
    RERANKER_TOPK: int = Field(
        default=40,
        ge=1,
        le=100,
        description="Top-K candidates for reranking"
    )
    RERANKER_KEEP: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of candidates to keep after reranking"
    )

    # === Retrieval Configuration ===
    READER_DOCS_BUDGET: int = Field(
        default=16,
        ge=1,
        le=32,
        description="Maximum documents for reader"
    )
    CONTEXT_BUDGET_TOKENS: int = Field(
        default=4500,
        ge=1000,
        le=8000,
        description="Maximum context tokens"
    )
    SENTENCE_MAX_PER_DOC: int = Field(
        default=12,
        ge=1,
        le=20,
        description="Maximum sentences per document"
    )
    MIN_RERANK_SCORE: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Minimum rerank score threshold"
    )
    PATH_ALLOWLIST: str = Field(
        default="",
        description="Comma-separated list of allowed file paths"
    )
    RERANK_ENABLE: bool = Field(
        default=True,
        description="Enable cross-encoder reranking"
    )

    # === Reader Configuration ===
    READER_ABSTAIN: bool = Field(
        default=True,
        description="Allow reader to abstain from answering"
    )
    READER_ENFORCE_SPAN: bool = Field(
        default=True,
        description="Enforce span-based answers"
    )
    READER_PRECHECK: bool = Field(
        default=True,
        description="Enable pre-check for answer quality"
    )
    READER_PRECHECK_MIN_OVERLAP: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum token overlap for pre-check"
    )

    # === Evaluation Configuration ===
    EVAL_STRICT_VARIANTS: bool = Field(
        default=True,
        description="Enforce strict variant consistency"
    )
    SAVE_CANDIDATES_MAX: int = Field(
        default=60,
        ge=1,
        le=200,
        description="Maximum candidates to save"
    )
    EVAL_EXPECT_RUN_ID: str = Field(
        default="",
        description="Expected run ID for variant consistency"
    )
    RAGCHECKER_PROGRESS_LOG: str = Field(
        default="",
        description="Path to progress log file"
    )
    ORACLE_CTX_J_MIN: float = Field(
        default=0.28,
        ge=0.0,
        le=1.0,
        description="Minimum Jaccard similarity for oracle context"
    )

    # === Quality Gates ===
    RETRIEVAL_PRECISION_THRESHOLD: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Minimum retrieval precision threshold"
    )
    RETRIEVAL_MACRO_PRECISION_THRESHOLD: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum retrieval macro precision threshold"
    )
    READER_F1_THRESHOLD: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        description="Minimum reader F1 threshold"
    )

    # === AWS Configuration ===
    AWS_REGION: str = Field(
        default="us-east-1",
        description="AWS region for Bedrock"
    )
    AWS_ACCESS_KEY_ID: str | None = Field(
        default=None,
        description="AWS access key ID"
    )
    AWS_SECRET_ACCESS_KEY: str | None = Field(
        default=None,
        description="AWS secret access key"
    )

    # === Observability ===
    LOGFIRE_TOKEN: str | None = Field(
        default=None,
        description="Logfire token for observability"
    )
    EVAL_TIMESERIES_SINK: bool = Field(
        default=False,
        description="Enable timeseries data collection"
    )
    EVAL_TIMESERIES_CASES: bool = Field(
        default=False,
        description="Enable per-case timeseries data"
    )

    @field_validator("POSTGRES_DSN", "DATABASE_URL")
    @classmethod
    def validate_dsn(cls, v: str | None) -> str | None:  # type: ignore
        """Validate database connection string."""
        if v is None:
            return None
        if v.startswith("mock://"):
            return v
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("DSN must start with postgresql:// or postgres://")
        return v

    @field_validator("PATH_ALLOWLIST")
    @classmethod
    def validate_path_allowlist(cls, v: str) -> str:  # type: ignore
        """Validate and normalize path allowlist."""
        if not v:
            return ""
        # Normalize paths and remove duplicates
        paths = [p.strip() for p in v.split(",") if p.strip()]
        return ",".join(sorted(set(paths)))

    @model_validator(mode="after")
    def validate_profile_consistency(self) -> EvalSettings:  # type: ignore
        """Validate profile-specific configuration consistency."""
        if self.EVAL_PROFILE == "mock":
            if self.EVAL_DRIVER != "synthetic":
                raise ValueError("Mock profile requires EVAL_DRIVER=synthetic")
            if self.RAGCHECKER_USE_REAL_RAG:
                raise ValueError("Mock profile requires RAGCHECKER_USE_REAL_RAG=False")
            if not self.POSTGRES_DSN.startswith("mock://"):
                raise ValueError("Mock profile requires mock DSN")
        elif self.EVAL_PROFILE in ("gold", "real"):
            if self.EVAL_DRIVER != "dspy_rag":
                raise ValueError("Gold/real profiles require EVAL_DRIVER=dspy_rag")
            if not self.RAGCHECKER_USE_REAL_RAG:
                raise ValueError("Gold/real profiles require RAGCHECKER_USE_REAL_RAG=True")
            if self.POSTGRES_DSN.startswith("mock://"):
                raise ValueError("Gold/real profiles require real DSN, not mock://")

        return self

    def get_database_url(self) -> str:
        """Get the effective database URL."""
        return self.DATABASE_URL or self.POSTGRES_DSN

    def get_gold_cases_path(self) -> Path:
        """Get gold cases path as Path object."""
        return Path(self.GOLD_CASES_PATH)

    def get_results_dir(self) -> Path:
        """Get results directory as Path object."""
        return Path(self.EVAL_RESULTS_OUTPUT_DIR)

    def get_manifest_path(self) -> Path:
        """Get manifest path as Path object."""
        return Path(self.EVAL_MANIFEST_PATH)

    def is_mock_profile(self) -> bool:
        """Check if this is a mock profile."""
        return self.EVAL_PROFILE == "mock"

    def is_real_rag_enabled(self) -> bool:
        """Check if real RAG is enabled."""
        return self.RAGCHECKER_USE_REAL_RAG and self.EVAL_DRIVER == "dspy_rag"

    def get_environment_dict(self) -> dict[str, str]:
        """Get environment variables dictionary for subprocess calls."""
        env_dict = {}
        for field_name, _field_info in self.__class__.model_fields.items():
            value = getattr(self, field_name)
            if value is not None:
                if isinstance(value, bool):
                    env_dict[field_name] = "1" if value else "0"
                else:
                    env_dict[field_name] = str(value)
        return env_dict

    def apply_to_environment(self) -> None:
        """Apply settings to current process environment."""
        for key, value in self.get_environment_dict().items():
            os.environ[key] = value

    @classmethod
    def from_profile(cls, profile: str, **overrides: Any) -> EvalSettings:
        """Create settings from profile with overrides."""
        # Load profile-specific defaults
        profile_defaults = cls._get_profile_defaults(profile)
        profile_defaults.update(overrides)
        return cls(**profile_defaults)

    @classmethod
    def _get_profile_defaults(cls, profile: str) -> dict[str, Any]:
        """Get profile-specific default values."""
        if profile == "mock":
            return {
                "EVAL_PROFILE": "mock",
                "EVAL_DRIVER": "synthetic",
                "RAGCHECKER_USE_REAL_RAG": False,
                "POSTGRES_DSN": "mock://test",
                "EVAL_CONCURRENCY": 3,
                "EVAL_MAX_WORKERS": 1,
            }
        elif profile == "gold":
            return {
                "EVAL_PROFILE": "gold",
                "EVAL_DRIVER": "dspy_rag",
                "RAGCHECKER_USE_REAL_RAG": True,
                "EVAL_CONCURRENCY": 8,
                "EVAL_MAX_WORKERS": 3,
            }
        elif profile == "real":
            return {
                "EVAL_PROFILE": "real",
                "EVAL_DRIVER": "dspy_rag",
                "RAGCHECKER_USE_REAL_RAG": True,
                "EVAL_CONCURRENCY": 8,
                "EVAL_MAX_WORKERS": 3,
            }
        else:
            raise ValueError(f"Unknown profile: {profile}")


# Global settings instance (lazy initialization)
eval_settings: EvalSettings | None = None

def get_eval_settings() -> EvalSettings:
    """Get the global eval settings instance, creating it if necessary."""
    global eval_settings
    if eval_settings is None:
        eval_settings = EvalSettings()
    return eval_settings
