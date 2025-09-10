# src/schemas/settings.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class EvaluationSettings(BaseSettings):
    """Configuration settings for evaluation system."""

    # File paths
    gold_cases_path: str = Field(default="evals/gold/v1/gold_cases.jsonl", description="Path to gold cases JSONL file")
    manifest_path: str = Field(default="evals/gold/v1/manifest.json", description="Path to evaluation manifest file")
    results_output_dir: str = Field(
        default="metrics/baseline_evaluations", description="Directory for evaluation results"
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
        ],
        description="List of known/valid tags",
    )

    class Config:
        env_file = ".env"
        env_prefix = "EVAL_"
        case_sensitive = False
        extra = "ignore"

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
