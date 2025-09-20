# src/schemas/settings.py
from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class EvaluationSettings(BaseSettings):
    """Configuration settings for evaluation system."""

    # File paths
    gold_cases_path: str = Field(default="evals/datasets/gold_cases.jsonl", description="Path to gold cases JSONL file")
    manifest_path: str = Field(
        default="evals/metrics/manifests/manifest.json", description="Path to evaluation manifest file"
    )
    results_output_dir: str = Field(
        default="evals/metrics/baseline_evaluations", description="Directory for evaluation results"
    )

    # Validation settings
    validation_strict: bool = Field(default=True, description="Enable strict validation mode")
    allow_missing_files: bool = Field(default=False, description="Allow cases with missing target files")
    unknown_tag_warning: bool = Field(default=True, description="Show warnings for unknown tags")
    check_file_existence: bool = Field(default=True, description="Check if expected files actually exist")

    # Evaluation limits
    max_cases_per_eval: int = Field(default=100, ge=1, le=1000, description="Maximum cases per evaluation run")
    default_sample_size: int = Field(default=50, ge=1, le=500, description="Default sample size for evaluations")

    # Performance settings
    concurrency_limit: int = Field(default=3, ge=1, le=10, description="Maximum concurrent evaluation tasks")
    timeout_seconds: int = Field(default=300, ge=30, le=3600, description="Timeout for individual evaluations")

    # Model settings
    default_model: str = Field(
        default="anthropic.claude-3-haiku-20240307-v1:0", description="Default model for evaluations"
    )
    fallback_model: str = Field(
        default="anthropic.claude-3-sonnet-20240229-v1:0", description="Fallback model for difficult cases"
    )

    # Known tags (configurable)
    known_tags: list[str] = Field(
        default=[
            "ops_health",
            "meta_ops",
            "rag_qa_single",
            "rag_qa_multi",
            "db_workflows",
            "negatives",
            "rag",
            "dspy",
            "memory",
            "context",
            # Additional tags from validation errors
            "ops",
            "evaluation",
            "evals",
            "rehydration",
            "prd",
            "workflow",
            "documentation",
            "ragchecker",
            "metrics",
            "baseline",
            "shell",
            "integration",
            "setup",
            "canary",
            "deployment",
            "percentage",
            "db",
            "vector",
            "index",
            "ivfflat",
            "fts",
            "tsquery",
            "postgresql",
            "pgvector",
            "ann",
            "cosine",
            "rrf",
            "fusion",
            "ranking",
            "migration",
            "resilience",
            "chunking",
            "embeddings",
            "configuration",
            "pipeline",
            "retrieval",
            "hybrid",
            "search",
            "reranker",
            "cross-encoder",
            "citations",
            "extraction",
            "scoring",
            "teleprompter",
            "optimization",
            "enforcement",
            "grounding",
            "multi-hop",
            "hyde",
            "prf",
            "gates",
            "promotion",
            "quality",
            "thresholds",
            "manifest",
            "template",
            "oracle",
            "provenance",
            "tracking",
            "leakage",
            "meta",
            "runbook",
            "manifests",
            "blocking",
            "negative",
            "quantum",
            "entanglement",
            "mars",
            "api-key",
            "time-travel",
            "dependencies",
        ],
        description="List of known/valid tags",
        json_schema_extra={"type": "array", "items": {"type": "string"}},
    )

    @field_validator("known_tags", mode="before")
    @classmethod
    def parse_known_tags(cls, v: str | list[str] | None) -> list[str]:
        """Parse known_tags from string or list."""
        if v is None:
            return []

        if isinstance(v, list):
            return v

        if v == "[]":
            return []

        # Try to parse as JSON array
        import json

        try:
            parsed: Any = json.loads(v)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
            else:
                return [str(parsed)]
        except json.JSONDecodeError:
            # If not JSON, split by comma
            return [tag.strip() for tag in v.split(",") if tag.strip()]

    class Config:
        env_file: str = ".env"
        env_prefix: str = "EVAL_"
        case_sensitive: bool = False
        extra: str = "ignore"

    def get_gold_cases_path(self) -> Path:
        """Get gold cases path as Path object."""
        return Path(self.gold_cases_path)

    def get_manifest_path(self) -> Path:
        """Get manifest path as Path object."""
        return Path(self.manifest_path)

    def get_results_dir(self) -> Path:
        """Get results directory as Path object."""
        return Path(self.results_output_dir)

    def is_tag_known(self, tag: str) -> bool:
        """Check if a tag is in the known tags list."""
        return tag.lower() in [t.lower() for t in self.known_tags]


# Global settings instance
settings = EvaluationSettings()
